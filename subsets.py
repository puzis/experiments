


    
             

class MonosizeLexIterator(object):
    """
    (self, size, universeSize, client = None)
    # defined members :
    # _stack - stack of next set elements
    # _universeSize
    # _clientSet -
    # _hasClient
    """
    
    def __init__(self, size, universeSize, client = None):
        # client - a user object that supports add(item) remove(item) methods
        # if given assumed to be an empty set and is promissed to
        # contain the next subset in lexicographical order after every
        # call to next()
        self._size = size
        self._clientSet = client
        self._stack = range(0)
        self._universeSize = universeSize
        self.firstSet = range(0,size)
        self.lastSet = range(universeSize-size,universeSize)
        self._started = False

    def __iter__(self):
        return self;
    def first(self):
        for x in range(0,self._size):
            self._stack.append(x)
            if (self._clientSet!=None): self._clientSet.add(x)
        if (self._clientSet!=None) : return self._clientSet
        else : return self._stack
    def next(self):
        # returns list representing the next subset in lexicographical order
        # unless a client object was specifies in wich case returns the
        # client object
        if not self._started :
            self._started = True
            return  self.first()
        if self._stack==self.lastSet:
            raise StopIteration()
        
        removed = self._removeElements()
        
        top = self._stack.pop()
        if (self._clientSet!=None) : self._clientSet.remove(top)

        self._addElements(range(top+1,top+1+removed))
        
        if (self._clientSet!=None) : return self._clientSet
        else : return self._stack
        
    def hasNext(self):
        return self._stack!=self.lastSet
    
    def _removeElements(self):
        i = self._universeSize - 1
        while (i==self._stack[len(self._stack)-1]) :
            i = i-1
            x = self._stack.pop()            
            if (self._clientSet!=None) : self._clientSet.remove(x)                
        return self._universeSize - i
    
    def _addElements(self,elems):
        for x in elems:
            self._stack.append(x)            
            if self._clientSet!=None : self._clientSet.add(x)



class FilteredMLI(object):
    def __init__(self, size, universeSize, client = None, filterFunction=(lambda x : True)):
        # client - a user object that supports add(item) remove(item) methods
        # if given assumed to be an empty set and is promissed to
        # contain the next subset in lexicographical order after every
        # call to next()
        self._size = size
        self._clientSet = client
        self._stack = range(0)
        self._universeSize = universeSize
        self._eof = False
        self._started = False
        self._filter = filterFunction
        self._addMemberCount = 0

    def __iter__(self):
        return self
    def next(self):
        if self._started :
            #return self._removeElements(self._universeSize - 1)
            return self._next(-1,self._universeSize - 1)
        else:
            self._started = True
            #return self._insertElements(-1)
            return self._next(1,-1)
    def hasNext(self):
        return not(self._eof)
    
    def _removeLast(self):
        top = self._stack.pop()
        if (self._clientSet!=None) : self._clientSet.remove(top)
        return top
    def _insertElement(self,x):
        self._stack.append(x)
        if self._clientSet!=None : self._clientSet.add(x)
    def _getSet(self):
        if self._clientSet!=None : return self._clientSet
        else : return self._stack
    def _removeElements(self,upperBound):
        last = len(self._stack)-1
        if(last <= -1): #relaxed ==
            self._eof=True
            if self._clientSet!=None : return self._clientSet
            else : return self._stack
        elif(self._stack[last] == upperBound):
            self._removeLast()
            return self._removeElements(upperBound-1)
        else:
            lowerBound = self._removeLast()
            return self._insertElements(lowerBound)
    def _insertElements(self,lowerBound):        
        x = lowerBound+1        
        if(len(self._stack)==self._size):
            return self._getSubset()
        elif(x>=self._universeSize): #relaxed ==
            return self._removeElements(lowerBound-1)
        elif(self._filter(x)):
            self._insertElement(x)
            return self._insertElements(x)
        else:
            return self._insertElements(x)
    def _next(self,action,bound):
        #recurtion reduced to a loop to avoid STACK OVERFLOW!!!
        #why the hell python does not optimizes tail calls!? (with -O option...)
        #"do everything" function, to get a bit performance :) since
        #the code already sucks :(
        #
        #some explanations:
        #action (of course) may be remove=-1 or insert =1
        #bound is lowerBound for insert action and upperBound for remove
        #the loop exits only when the next set is constructed or
        #end of iteration reached in which case empty set should be returned 
        result = None
        while(result==None):
            length = len(self._stack)            
            if (action == -1): #should we remove items?
                if(length <= 0): #relaxed ==
                    #nothing to remove => end of iteration
                    self._eof=True
                    #return the current (empty ) set.
                    result = self._getSet()
                else:
                    #remove the last element
                    lastel = self._removeLast()                    
                    if(lastel == bound):
                        #can not insert, proceed with remove
                        bound = bound - 1
                        #action = -1  #stays the same 
                    else:
                        #construct the next set
                        bound = lastel
                        action = 1 #insert
            elif (action == 1):
                if(length==self._size):
                    #got the whole set return it
                    result = self._getSet()
                else:
                    #current candidate to enter the set
                    x = bound + 1
                    if (x>=self._universeSize): #relaxed ==
                        #no more candidates available
                        #go back and try another way
                        bound = bound - 1
                        action = -1 #remove
                    elif(self._filter(x)):
                        #insert element
                        self._insertElement(x)
                        self._addMemberCount+=1
                        #proceed with next insert
                        bound = x
                        #action = 1 #"insert"
                    else:
                        #nothing to insert proceed next
                        bound = x
                        #action = 1 #"insert"
            else:
                assert(False) #for debuging 
        return result
                  

            
    
        
import unittest
class SubsetsTest(unittest.TestCase):

    def testMonosizeLexIterator(self):
        itr = MonosizeLexIterator(3,5)
        self.assertEquals(itr.next(),[0,1,2])
        itr.next()
        itr.next()
        self.assertEquals(itr.next(),[0,2,3])

    def testMonosizeLexIteratorWithClient(self):
        s = set(range(0))
        itr = MonosizeLexIterator(3,5,s)
        self.assertEquals(itr.next(),set([0,1,2]))
        itr.next()
        self.assertEquals(s,set([0,1,3]))
        self.assertEquals(itr.next(),set([0,1,4]))
        itr.next()
        self.assertEquals(s,set([0,2,3]))
    def testHasNext(self):        
        itr = MonosizeLexIterator(3,5)
        while(itr.hasNext()):
            print itr.next()

    def testFilteredMLI(self):
        fitr = FilteredMLI(3,6,None,(lambda x: (x!=5 and x!=4)))
        while (fitr.hasNext()):
            print fitr.next()
    
if __name__ == "__main__":
    unittest.main()
    
