from aima.search import *
from utils import *
from candidatesBasedAlgorithm import *
from abstractGroupEvaluation import *


class State(AbstractGroupEvaluation):
    def __init__(self,group,candidates):
        self._group=group;
        self._candidates=candidates;

    def getMembers(self):
        return self._group.getMembers();
    
    def getUtility(self):
        return self._group.getGB();
    
    def getUtilityOf(self,party):raise NotImplementedError()
    def getCost(self):raise NotImplementedError()
    def getCostOf(self):raise NotImplementedError()
    

class KeyPalayerProblem(Problem):
    
    def __init__(self, graph, targetSize, initialSet):
        assert isinstance(initialSet,AbstractGroupEvaluation)
        self._G = graph;
        self._k = targetSize;
        Problem.__init__(self,initialSet,None);
        
    def successor(self, state):
        result = [(('add',x),
        