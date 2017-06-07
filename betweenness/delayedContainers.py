
class UnmutableList(object):
    def __init__(self,lenf,getf):
        self._getf = getf
        self._lenf = lenf
    
    def __getitem__(self,key):
        return self._getf(key)

    def __iterator__(self):
        print "iterating.."
        for i in range(self._lenf()):
            rslt = self._getf(i)
            yield rslt
            
            
if (__name__=="__main__"):
    print "Test UnmutableList delayed iterator"
    s = UnmutableList(
        lambda :3,
        lambda index:index*2
        )
    itr = iter(s)
    assert(itr.next()==0)
    assert(itr.next()==2)
    assert(itr.next()==4)
    print "OK"
