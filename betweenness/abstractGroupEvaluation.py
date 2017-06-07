



class AbstractGroupEvaluation(object):
    """
    required api of group evaluation algorithm to be used for search
    represent a single group with add operation but with no remove operation
    """
    pass

class BasicSet(object):
    def getMembers(self):raise NotImplementedError()
    def getGB(self):raise NotImplementedError()
    def add(self,v):raise NotImplementedError()
    def remove(self,v):raise NotImplementedError()
    def update(self,iterable):
        for x in iterable: 
            self.add(x)
    def difference_update(self,iterable):
        for x in iterable:
            self.remove(x)
    def __repr__(self):
        n = self._dw.getNumberOfVertices() #UNSAFE!!!
        return "Group" + "<" + repr(self.getMembers()) + ",%.2f,%.2f"%(self.getUtility(),self.getCost())+">"
    def __str__(self):
        return self.__repr__()
    def __iter__(self):
        return iter(self.getMembers())
    def __getitem__(self,index):
        return self.getMembers()[index]
    def __len__(self):
        return len(self.getMembers())
    def __cmp__(self,other):
        if other!=None:
            return self.getGB() - other.getGB()
        else :
            return 1



    def add(self,party):raise NotImplementedError()
    def getMembers(self):raise NotImplementedError()
    def getUtility(self):raise NotImplementedError()
    def getUtilityOf(self,party):raise NotImplementedError()
    def getCost(self):raise NotImplementedError()
    def getCostOf(self):raise NotImplementedError()
