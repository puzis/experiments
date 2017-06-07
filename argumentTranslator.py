def _framedFunction(obj,f,transFunction):
    def translatedMethod(*args):
        new_args = map(transFunction,args)
        new_args[0:0] = [obj]
        return apply(f,new_args)
    return translatedMethod


def createClassTranslation(objType,transFunction):
    class ClassTranslation(objType):
        def __init__(self,*args):
            if (hasattr(objType,"__init__")):
                apply(objType.__init__,(self,)+args)
            for attr in dir(objType):
                f = getattr(objType,attr)
                if callable(f) and attr!="__class__":
                    new_f = _framedFunction(self,f,transFunction)
                    setattr(self,attr,new_f)
    return ClassTranslation


def createObjectTranslation(obj,transFunction):
    class ObjectTranslation(object):
        def __init__(self):
            for attr in dir(obj.__class__):
                f = getattr(obj.__class__,attr)
                if callable(f) and attr!="__class__":
                    new_f = _framedFunction(obj,f,transFunction)
                    setattr(self,attr,new_f)
    return ObjectTranslation()
                

def createDictionaryTranslation(dictionary,types):
    def transFunction(obj):
        if(isinstance(obj,types)):
            return dictionary[obj]
        else:
            return obj
    return transFunction
            


    
