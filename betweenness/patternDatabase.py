from gbcPruning import *
from .subsets import MonosizeLexIterator
 

class UndoablePartyElection(AbstractElection,Undoable):
    def __init__(self,group,targetSize,candidates,maxPartySize,stateFields = ["_group","_parties"]):
        """
        constructs all possible parties up to maxPartySize
        """
        assert isinstance(group,AbstractGroupEvaluation)
        assert isinstance(candidates,list)
        assert isinstance(targetSize,int)
        
        Undoable.__init__(self,stateFields)
        
        self._size = targetSize
        self._maxPartySize = maxPartySize
        self._group = group        
        
        self._parties = [[]]
        self.consider(candidates)
        
        self.setUtilityHeuristic(UndoablePartyElection.listUtilityHeuristics()[0])
        self.setTransitionHeuristic(UndoablePartyElection.listTransitionHeuristics()[0])

    def _normalize(self,p):
        if not "__iter__" in dir(p):
            p = [p]
        p = tuple(sorted(set(p)))
        return p;

    def getResult(self):
        return self._group

    def getUtility(self):
        return self._group.getUtility()
    
    def getNumberOfCandidates(self):
        if len(self._parties)>0:
            return len(self._parties[0])
        else:
            return 0

    def accept(self,cList):
        self.favor(cList)
        self.reject(cList)
    def favor(self,cList):
        self._group.update(cList)        
    def consider(self,cList):
        existingCandidates = [x[1][0] for x in self._parties[0]]
        candidates = list(set(cList).union(existingCandidates))
        
        self._parties = []
        for i in range(1,min(self._maxPartySize+1,len(candidates)+1,self._size+1)):
            ##create all possible parties of size i
            i_parties = []
            itr = MonosizeLexIterator(i,len(candidates))
            while(itr.hasNext()):
                nextSubset = itr.next()
                party = self._normalize([candidates[candidateIndex] for candidateIndex in nextSubset])
                i_parties.append((-self._group.getUtilityOf(party),party))            
            heapify(i_parties)
            self._parties.append(i_parties)
            
    def reject(self,cList):
        removedCandidates = set(cList)
        newParties = []
        for i in range(len(self._parties)):
            i_parties = self._parties[i]
            i_parties = filter(#only keep parties that distinct to cList
                lambda pInfo: len(removedCandidates.intersection(pInfo[1]))==0,
                i_parties)
            if(len(i_parties)>0):
                i_parties = [(-self._group.getUtilityOf(x[1]),x[1]) for x in i_parties]
                heapify(i_parties)
                newParties.append(i_parties)
            else:
                self._parties = newParties
                return 
            
        self._parties = newParties

    def rejectNext(self):
        vInfo = self._getNextElement(self)
        self.reject([vInfo[1]])
    def acceptNext(self):
        vInfo = self._getNextElement(self)
        self.accept([vInfo[1]])

    ##Heuristic for choosing next candidate
    @staticmethod
    def listTransitionHeuristics():
        return [UndoablePartyElection.getNextElement1,UndoablePartyElection.getNextElement2]
    def setTransitionHeuristic(self,func):
        self._getNextElement = func
    def getNextElement1(self):
        """
        Candidate chosen is the leading candidate.
        Parties are reconstructed.
        """
        pInfo = self._parties[0][0]
        vInfo = (pInfo[0],pInfo[1][0])
        return vInfo
        
    def getNextElement2(self):
        """
        Candidate chosen is the head of leading party.
        Parties are reconstructed.
        """
        pInfo = self._parties[min(len(self._parties)-1,self._size)][0]
        pCandidates = [(-self._group.getUtilityOf(x),x) for x in pInfo[1]]
        return min(pCandidates)


    ##Heuristic Utility Management
    @staticmethod
    def listUtilityHeuristics():
        return [UndoablePartyElection.utilityHeuristic3]
    def setUtilityHeuristic(self,func):
        self._getUtilityUperBound = func
    def utilityHeuristic(self,cost):
        return self._getUtilityUperBound(self,cost)        
    def utilityHeuristic3(self,groupSize):
        #while calculating heuristic pop parties from queue
        rslt = self._group.getUtility()
        posiblyElected = set(self._group.getMembers())
        freePositions = int(groupSize) - len(posiblyElected)
        popped = []
        while(freePositions>0 and self.getNumberOfCandidates()>0):
            partySize = min(freePositions,len(self._parties))
            while (len(self._parties[partySize-1])==0):
                partySize-=1
            pInfo = heappop(self._parties[partySize-1])
            popped.append(pInfo)
            #all parties chosen for the heuristic should be distinct for tighter bound
            if(len(posiblyElected.intersection(pInfo[1]))==0):
                posiblyElected.update(pInfo[1])
                freePositions -= partySize
                rslt += -pInfo[0]
                
        #put back to queue all candidate parties 
        members = self._group.getMembers()
        for pInfo in popped:
            heappush(self._parties[len(pInfo[1])-1],pInfo)
        return rslt

