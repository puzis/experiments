from candidatesBasedAlgorithm import *
import copy
from heapq import *
    
class AbstractElection(object):
    ##State access
    def getResult(self):raise NotImplementedError()
    def getNumberOfCandidates(self):raise NotImplementedError()

    ##Pruning heuristics management
    def getUtility(self):raise NotImplementedError()
    def utilityHeuristic(self,cost):raise NotImplementedError()
    def setUtilityHeuristic(self,func):raise NotImplementedError()

    def getCost(self):raise NotImplementedError()
    def costHeuristic(self,cost):raise NotImplementedError()
    def setCostHeuristic(self,func):raise NotImplementedError()
    
   
    @staticmethod
    def listUtilityHeuristics():raise NotImplementedError()
    
  
    
    ##Transition heuristics management:
    def acceptNext(self):raise NotImplementedError()
    def rejectNext(self):raise NotImplementedError()

    def setTransitionHeuristic(self,func):raise NotImplementedError()
    def listTransitionHeuristics():raise NotImplementedError()

    
    ##Shortcut transitions:
    def accept(self,p):raise NotImplementedError()
    def suspend(self,p):raise NotImplementedError()
    def favor(self,p):raise NotImplementedError()
    def remove(self,p):raise NotImplementedError()
    def consider(self,p):raise NotImplementedError()
    def reject(self,p):raise NotImplementedError()
    

    
class Undoable(object):
    def __init__(self,stateProperties):
        assert isinstance(stateProperties,list)
        self._undoStack = []
        self._stateProperties = stateProperties
        
    def mark(self):
        """
        copy current state and save it in a stack
        """
        copiedState = {}
        for attr in self._stateProperties:
            attrValue = getattr(self,attr)
            copiedState[attr]=copy.deepcopy(attrValue,{}) 
        self._undoStack.append(copiedState)
        
    def undo(self):
        """
        retrieve previosly saved state and use it
        """
        copiedState = self._undoStack.pop()
        for attr in self._stateProperties:
            setattr(self,attr,copiedState[attr])

    def undoAll(self):
        """
        performs undo while the states stack is not empty
        """
        while len(self._undoStack)>0:
            self.undo()
        
        
        
class UndoableCandidatesElection(AbstractElection,Undoable):
    """
    Does not consider group cost.
    Heristic bounds are based on group size. 
    """
    def __init__(self,group,targetSize,candidates,stateFields = ["_group","_candidates"],epsilon=0):
        """
        candidates must be list of unique immutable items
        """
        assert isinstance(group,AbstractGroupEvaluation)
        assert isinstance(candidates,list)
        assert isinstance(targetSize,int)
        
        Undoable.__init__(self,stateFields)

        self._size = targetSize
        self._group = group
        self._candidates = list(set(candidates))
        
        self.setUtilityHeuristic(UndoableCandidatesElection.listUtilityHeuristics()[0])
        self.setTransitionHeuristic(UndoableCandidatesElection.listTransitionHeuristics()[0])

        self._hEpsilon = epsilon
        
        #self.mark()
    def __repr__(self):
        return "<" + repr(self._group) + "," + repr(self._candidates) + ">"
    
    def getHeuristicWeight(self):return self._hEpsilon
    def setHeuristicWeight(self,w): self._hEpsilon=w
    heuristicWeight = property(getHeuristicWeight,setHeuristicWeight)
    
    def getResult(self):
        return self._group

    def getUtility(self):
        return self._group.getUtility()
    
    def getCost(self):
        return self._group.getCost()
    
    def getNumberOfCandidates(self):
        return len(self._candidates)
    
    
    def rejectNext(self):
        vBest = self._getBest(self)

        #remove vBest from candidates
        self._candidates.remove(vBest)
        
        return vBest

    def acceptNext(self):
        vBest = self._getBest(self)

        #remove vBest from candidates
        self._candidates.remove(vBest)

        #add vBest to the group
        self._group.add(vBest)
        
        return vBest
        
    def reject(self,p):
        if "__iter__" in dir(p):
            p=set(p)
        else:
            p=set([p])
        self._candidates=list(set(self._candidates) - p) #filter(lambda x: x not in p,self._candidates)
        heapify(self._candidates)

    def remove(self,p):
        if "__iter__" in dir(p):
            p=set(p)
        else:
            p=set([p])
        for v in p:
            self._group.remove(v)

    ##Heuristic for choosing next candidate
    def setTransitionHeuristic(self,func):
        self._getBest = func
        
    @staticmethod
    def listTransitionHeuristics():
        #3/8/2008
        #return [UndoableCandidatesElection.TransitionHeuristic1, UndoableCandidatesElection.TransitionHeuristic2, UndoableCandidatesElection.TransitionHeuristic3]
        return [UndoableCandidatesElection.TransitionHeuristic1, UndoableCandidatesElection.TransitionHeuristic2] #without transition 2
    def TransitionHeuristic1(self):
        #get candidate with highest utility 
        candidates = [(self._group.getUtilityOf(x),x) for x in self._candidates]
        vBest = max(candidates)
        return vBest[1]   
    
    def TransitionHeuristic2(self):
        #get candidate with highest utility per cost
        candidates = [(self._group.getUtilityOf(x)/self._group.getCostOf(x),x) for x in self._candidates]
        vBest = max(candidates)
        return vBest[1]
    
    def TransitionHeuristic3(self):
        #get candidate with lowest cost
        candidates = [(self._group.getCostOf(x),x) for x in self._candidates]
        vBest = min(candidates)
        return vBest[1]  
  
    ##Heuristic Utility Management
    def setUtilityHeuristic(self,func):
        self._getUtilityUperBound = func
    @staticmethod
    def listUtilityHeuristics():
        return [UndoableCandidatesElection.utilityHeuristic0,UndoableCandidatesElection.utilityHeuristic1,UndoableCandidatesElection.utilityHeuristic2]
        
    def utilityHeuristic(self,cost):
        #f = wh+g
        return (1+self._hEpsilon) * self._getUtilityUperBound(self,cost) +  self.getUtility()
    
    def utilityHeuristic0(self,budget):
        """
        returns trivial upper bound on the remaining utility.
        """
        if len(self._candidates)==0: return 0
        else: return inf
        
    def utilityHeuristic1(self,budget):
        """
        returns upper bound on the remaining utility.
        return: maximum utility per unit of cost times the remaining budget 
        """
        if len(self._candidates)==0: return 0

        #maximum utility per unit of cost
        candidates = [(self._group.getUtilityOf(x)/self._group.getCostOf(x),x) for x in self._candidates]
        rslt = max(candidates) 
        rslt = rslt[0]
        
        #maximum possible utility for a budget
        rslt *= (budget - self._group.getCost())
        return rslt 

    
    def utilityHeuristic2(self,budget):
        """
        returns upper bound on the remaining utility.
        
        """        
        remainingBudget = budget - self._group.getCost()
        rslt=0
        candidates = [(-self._group.getUtilityOf(x)/self._group.getCostOf(x),x) for x in self._candidates]
        heapify(candidates)
        while remainingBudget>0 and len(candidates)>0:
            (upc,v)=heappop(candidates)
            upc=-upc
            cost = min(remainingBudget,self._group.getCostOf(v))            
            rslt+=upc*cost
            remainingBudget-=cost
        return rslt
    
    ##Heuristic Cost Management
    def setCostHeuristic(self,func):
        self._getCostLowerBound = func
    @staticmethod
    def listCostHeuristics():
        return [UndoableCandidatesElection.costHeuristic0,UndoableCandidatesElection.costHeuristic1,UndoableCandidatesElection.costHeuristic2]
       
    def costHeuristic(self,utility):
        #f = wh+g
        return (1 - self._hEpsilon) * self._getCostLowerBound(self,utility) +  self.getCost()
    
    def costHeuristic0(self,utility):
        """
        returns trivial lower bound on the required cost.
        """
        return 0
        
        
    def costHeuristic1(self,utility):
        """
        returns lower bound on the required cost.
        return: minimum cost per utility times requiring utility
        """
        if len(self._candidates)==0: return 0

        #minimum cost per utility
        candidates = [(self._group.getCostOf(x)/self._group.getUtilityOf(x),x) for x in self._candidates]
        rslt = min(candidates) 
        rslt = rslt[0]
        
        #minimum possible cost to reach the target utility
        rslt *= (utility - self._group.getUtility())
        return rslt 

    
    def costHeuristic2(self,utility):
        """
        returns lower bound on the remaining cost.
        
        """        
        remainingUtility = utility - self._group.getUtility()
        rslt=0
        candidates = [(self._group.getCostOf(x)/self._group.getUtilityOf(x),x) for x in self._candidates]
        heapify(candidates)
        while remainingUtility>0 and len(candidates)>0:
            (costPerUtility,v)=heappop(candidates)
            utility = min(remainingUtility,self._group.getUtilityOf(v))            
            rslt+=costPerUtility*utility
            remainingUtility-=utility
        return rslt

    def _normalize(self,p):
        if not "__iter__" in dir(p):
            p = [p]
        p = tuple(sorted(set(p)))
        return p;




class UndoableElectionIteration(object):
    """
    Traverses the all subsets of size <size> in Lexicographic order.
    Next returns the next subset of size <size>
    """
    def __init__(self,election,size):
        assert isinstance(election,AbstractElection)
        assert isinstance(election,Undoable)
        assert isinstance(size,int)
        
        self._election = election
        self._size = size
        self._maxgb = self._election.getUtility()
        self._optimalSet = copy.deepcopy(self._election.getResult())
        self._iterationStarted = False
        self._iterationEnded = False
        self._election.mark()


    def __iter__(self):
        return self
    
    def next(self):
        if(self._iterationEnded):
            return self._election.getResult()

        if(not(self._iterationStarted)):
            for i in range(self._size):
                self._election.mark()
                self._election.acceptNext()
            self._iterationStarted = True
            return self._election.getResult()

        self._election.undo()
        k=1
        cc = self._election.getNumberOfCandidates()
        while(k==cc):
            self._election.undo()
            k+=1
            cc = self._election.getNumberOfCandidates()
        self._election.rejectNext()
        cc = self._election.getNumberOfCandidates()
        if(cc==self._size==k):
            self._iterationEnded=True
        for i in range(k):
            self._election.mark()
            self._election.acceptNext()
        return self._election.getResult()

    def hasNext(self):
        return not(self._iterationEnded)


def _backoff():
    pass 
def _goDeeper():
    pass


class OptimalElectionSearch(object):        
    def __init__(self,election,budget):
        assert isinstance(election,AbstractElection)
        assert isinstance(election,Undoable)        
        
        self._election = election
        self._budget = budget
        self._maxgb = self._election.getUtility()
        self._optimalSet = copy.deepcopy(self._election.getResult())
        self._bof = True
        self._eof = False
        self._backoffCondition = OptimalElectionSearch.backoffCondition1
        self._statistics = {}
        self._statistics["acceptNext"] = 0
        self._statistics["rejectNext"] = 0
        self._statistics["returns"] = 0

    def hasNext(self):
        return not(self._eof)
    
    def restart(self):
        self._bof = True
        self._eof = False
        self._election.undoAll()
        
    def next(self):
        if(self._bof):
            self._election.mark() #remember the election original state it will be reproduced when the search is over
            self._bof = False
        return self._next(_goDeeper,self._budget)
        
    def _next(self,action,budget):
        """
        cost of vertices MUST be a positive number (>0)!
        required = remainingBudget
        length = cost
        """
 
        while(True):
            cost=self._election.getResult().getCost()
            if(action == _backoff): #should we remove items?
                if(cost==0):
                    #the result set is empty! -> end of iteration
                    self._eof = True
                    #return the election to its original state
                    self._election.undo()
                    #return the current (empty) set.
                    return self._updateAndReturn(self._election.getResult())
                else:
                    #remove the last item
                    self._election.undo()
                    ##we've checked with him let's check without him
                    ##it must be the one we just undid 
                    self._statistics["rejectNext"]+=1
                    self._election.rejectNext() 
                    #print self._election
                    
                    ##start insertions
                    ##required as is
                    action = _goDeeper 
            elif(action==_goDeeper):# so we should add items...                  
                if self._election.getNumberOfCandidates()<=0:
                    action = _backoff
                elif(self.backoffCondition()):
                    #not this one nor any one after him can't help us
                    action = _backoff
                else:                        
                    #this one might help us
                    self._election.mark()
                    self._statistics["acceptNext"]+=1
                    self._election.acceptNext()
                    #print self._election
                    
                    #action = _goDeeper #continue inserting
                    if self._election.getResult().getCost()>budget:
                        #not a valid result!
                        action = _backoff
                    else:
                        return self._updateAndReturn(self._election.getResult())
            else:
                assert(False)
                        


    @property
    def statistics(self):
        return self._statistics
    

    def getOptimalSet(self):
        return set(self._optimalSet)

    def getOptimalValue(self):
        return self._maxgb

    def __iter__(self):
        return self

    def _updateAndReturn(self,s):
        assert isinstance(s,AbstractGroupEvaluation)
        gb = s.getUtility()
        m = s.getMembers()
        if(gb > self._maxgb):
            self._maxgb = gb
            self._optimalSet = copy.deepcopy(m)
        self._statistics["returns"]+=1
        return s

    ##Pruning method
    def setBackoffCondition(self,filterFunction):
        self._backoffCondition = filterFunction
    def backoffCondition(self):
        return self._backoffCondition(self)
    
    @staticmethod
    def listBackoffConditions():
        return [OptimalElectionSearch.backoffCondition0, OptimalElectionSearch.backoffCondition1, OptimalElectionSearch.backoffCondition2, OptimalElectionSearch.backoffCondition3]
    
    def backoffCondition0(self):
        return False
    
    def backoffCondition1(self):
        f = self._election.utilityHeuristic(self._budget)
        return self._maxgb >= f
    
    def backoffCondition2(self):
        f = self._election.costHeuristic(self._maxgb)
        return self._budget <= f
    
    def backoffCondition3(self):
        return self.backoffCondition1() or self.backoffCondition2()
        
