import decimal
import numpy
from operator import *
from random import *
from weakref import ref


def randomCombination(sequences):
    result=[]
    indices = [[i for x in xrange(len(sequences[i]))] for i in xrange(len(sequences))]
    indices = reduce(concat,indices,[])
    shuffle(indices)
    for i in indices:
        result.append(sequences[i].pop(0))
    return result

def cp(*sequences):
    sequences=list(sequences)
    return reduce(lambda x,y:[l+[e] for e in y for l in x],[[[]]]+sequences)

######################################################################
######################################################################



def defaultSetter(key,value):
    raise TypeError("Array does not support assignment")
def defaultGetter(key):
    raise TypeError("Array does not support retrieval")
def defaultIter():
    raise TypeError("Array does not support iteration")
def defaultDelete(key):
    raise TypeError("Array does not support deletion")
def defaultContains(item):
    raise TypeError("Array does not support containment queries")


class NoneIterator(object):
    def __init__(self,length):
        self._len = length;
        self._pos = 0;
    def __iter__(self):
        return self
    def next(self):
        if (self._pos>=self._len):
            raise StopIteration()
        else:
            self._pos+=1
            return None

class NoneMatrix(object):
    def __init__(self,dimentions=(numpy.Inf,)):
        self._dim = dimentions
    def __len__(self):
        return self._dim[0]
    def __getitem__(self,key):
        return None
    def __setitem__(self,key,value):
        pass
    def __delitem__(self,key):
        pass
    def __iter__(self):
        return NoneIterator(self._dim[0])
    def __contains__(self,item):
        return False
        
class DelayedIterator(object):
    def __init__(self,length=None,getter = defaultGetter,key_iter=None):
        self._getter = getter

        if key_iter==None:
            self._key_iter = iter(xrange(length))
        else:
            self._key_iter = key_iter

    def __iter__(self):
        return self

    def next(self):
        k = self._key_iter.next()
        return self._getter(k)



class VirtualList(object):
    """
    This class is usefull for controling access to sequences.
    Simulates basic sequence behavior.
    """
    def __init__(self,length,getter=defaultGetter,setter=defaultSetter,contains=defaultContains,delete=defaultDelete):
        self._getter=getter        
        self._setter=setter
        self._contains=contains
        self._delete=delete
        self._len=length
    def __len__(self):
        return self._len
    def __getitem__(self,key):
        return self._getter(key)
    def __setitem__(self,key,value):
        self._setter(key,value)
    def __delitem__(self,key):
        self._delete(key)
    def __iter__(self):
        return DelayedIterator(self._len,self._getter)
    def __contains__(self,item):
        return self._contains(item)
    def __str__(self):
        return str([self[i] for i in range(len(self))])

class DelayedNDArray(numpy.ndarray):
    
    def __new__(subtype,getter,placeholder,shape,dtype=float, buffer=None,offset=0, strides=None, order=None):
        self=numpy.ndarray.__new__(subtype,shape,dtype,buffer,offset,strides,order)
        if self != None:
            self._placeholder = placeholder
            self._getter = getter
            self.fill(self._placeholder)        
        return self
        
    def __init__(self,getter,placeholder,shape,dtype=float, buffer=None,offset=0, strides=None, order=None):
        numpy.ndarray.__init__(self,shape,dtype,buffer,offset,strides,order)
        self._placeholder = placeholder
        self._getter = getter
        self.fill(self._placeholder)        
    
    def __getitem__(self,key):
        result=numpy.ndarray.__getitem__(self,key)
        if result == self._placeholder:
            result = self._getter(key)
            self[key]=result
        return result
    
    def __deepcopy__(self,memo,_nil=[]):
        result = numpy.ndarray.__deepcopy__(self,memo)
        result._placeholder = self._placeholder
        result._getter = self._getter
        return result
    
            

class DelayedContainer(object):
    """
    This class represents a delayed contaner like xrange. 
    It is mostly efficient for data structures (matrices) 
    where the computation cost of each element is very 
    high and it might never be needed, however, once an 
    element was accessed it will probably be accessed again
    shortly.

    Simulates basic sequence behavior.
    """
    def __init__(self,getter=defaultGetter,setter=defaultSetter,contains=defaultContains,delete=defaultDelete,key_iter=defaultIter):
        self._getter=getter
        self._setter=setter
        self._delete=delete
        self._contains=contains
        self._key_iter = key_iter
        self._memory={}
        
    def __len__(self):        
        """
        returns the length of a list of keys constructed using a shallow copy of supplied key iterator        
        """
        return len([k for k in copy.copy(self._key_iter)])

    def __getitem__(self,key):
        """
        returns the result of a call to getter with this key 
        if the key was retrieved for the first time otherwise
        returns the result of the last call with this key.
        
        Note: the getter function if called only once for each key,
        this includes implicit calls such as iteration.
        """
        if not self._memory.has_key(key):
            self._memory[key]=self._getter(key)
        return self._memory[key]
    
    def __setitem__(self,key,value):
        self._setter(key,value)
        self._memory[key]=value
    def __delitem__(self,key):
        self._delete(key)
        del self._memory[key]
    def __iter__(self):
        return DelayedIterator(getter=self.__getitem__,key_iter=copy.copy(self._key_iter))    
    def __deepcopy__(self,memo,_nil=[]):
        for x in self: pass
        return copy.deepcopy(self._memory)
        
    

class DefaultCommMatrix(object):
    def __getitem__(self,i):
        if i[0]==i[1]:
            return 0; 
        else: 
            return 1;
        
class ReadOnlyArray(object):
    def __init__(self,dims,data):
        self._data = data
        self._dims = dims
        
    def __getitem__(self,indices):
        result = self._data
        c=0
        if "__iter__" not in dir(indices):
            indices = [indices]
        for i in indices:
            c+=1
            result=result[i]
        if  c < self._dims:
            return ReadOnlyArray(c,result)
        else:
            return result;
    
    def __len__(self):
        return len(self._data)
    
    
def matrixStr(matrix):
    reprM = []
    maxCellWidth = 1
    maxcol = 0
    ##create represenations of each cell includibng indices
    for i in range(len(matrix)):
        row = matrix[i]
        if (len(row)>maxcol):
            maxcol=len(row)
        reprRow=[str(i)+"|"] + [str(cell) for cell in row]
        reprM.append(reprRow)
    reprM[0:0]=[[str(len(matrix)) + "X" + str(maxcol)] + [str(x) for x in range(maxcol)]]
    
    ##find the maximum cell length for proper layout
    for reprRow in reprM:
        for reprCell in reprRow:
            if maxCellWidth<len(reprCell):
                maxCellWidth=len(reprCell)
    maxCellWidth+=1

    ##adjust all cells to max length (align to right)
    reprM = [[(" "*(maxCellWidth-len(reprCell))) + reprCell for reprCell in reprRow] for reprRow in reprM]

    ##add a separator row
    reprM[1:1] = [["-"*maxCellWidth for x in range(maxcol+1)]]
    
    ##create the final representation
    result = ""
    for reprRow in reprM:
        for reprCell in reprRow:
            result += str(reprCell) 
        result += "\n"
    return result




def cacheResults(ignoreSelf=True,cache={}):
    """
    A method decorator that memorizes the returned values of the original method to save up running time.
    The precondition is that the returned value is a function of the input arguments only and does not 
    depend on the object state. Returned values are stored in a dictionary hosted by the type object 
    provided and are keyed by the tuple of input arguments. Future implementations may support keyword
    arguments, chaching the returned values within a bounded container, emptying the cache and more.
    
    Caution: using cacheResults prevents the call arguments from being garbage collected!
    
    cache - the dictionary wich hold the caches. 
    ignoreSelf - specifies whether to use or ignore the first function argument when caching the returned values     
    """
    def decorator(f):
        def new_f(*args):
            if not cache.has_key(args[ignoreSelf:]):   #True is evaluated as 1 and False as 0
                cache[args[ignoreSelf:]]=f(*args) 
            return cache[args[ignoreSelf:]]
        new_f.func_name=f.func_name
        return new_f    
    return decorator

def branchIfFalse(conditionFunc, altStreamFunc):
    """
    A method decorator that first evaluates the conditionFunc on the arguments
    if the condition is satisfied then the decorated function is executed regularly 
    otherwise altStreamFunc is executed on the same arguments.
    
    May also be used for validation of input arguments.
    """
    def decorator(mainStreamFunc):
        def new_f(*args):
            if conditionFunc(*args):
                return mainStreamFunc(*args) 
            else:
                return altStreamFunc(*args)            
        new_f.func_name=mainStreamFunc.func_name
        return new_f    
    return decorator

