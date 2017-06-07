import random
import utils
from  numpy import *
from abstractGroupEvaluation import AbstractGroupEvaluation
from abstractGroupEvaluation import BasicSet

class WeightedBetweenness(object):
    """
    Betweenness calculation based on
    Ulrik Brandes' "Faster Algorithm for Betweenness Centrality" 2001.
    Algorithm was modified to inlude end points in path counting
    Algorithm was modified to compute Group Betweenness Centrality of a given group.
    Algorithm was generalized to accomodate "Communication Weights" (network usage habits).
    """
    
    def __init__(self, graph, CW=None, statusBar=False, group=set([])):
        if CW==None : CW=utils.DefaultCommMatrix();
        #assert isinstance(graph,Graph) #TODO4
        self._group=group
        self._GB = 0
        
        n = graph.getNumberOfVertices()
        m = graph.getNumberOfEdges()
    
        V = range(n)
        self._G = graph
        self._distance=      ndarray(shape=(n,n),dtype=float  ,order='C')
        self._deltaDot=      ndarray(shape=(n,n),dtype=float  ,order='C')
        self._sigma=         ndarray(shape=(n,n),dtype=integer,order='C')
        self._routingTable = ndarray(shape=(n,n),dtype=object ,order='C')
        
        
        progressCount = 0
        for s in V:
            if statusBar:
                progressCount+=1
                statusBar.updateStatus("%d %%"%(100.0*progressCount/n))
    
            S = []
            #P = array([None for w in V],object,order='C');
            P = ndarray(shape=(n),dtype=object,order='C');
            for i in xrange(n):P[i]=[];
            sigma = array([0 for t in V],integer,order='C') 
            #sigma = ndarray(shape=(n),dtype=integer,order='C');
            #sigma.fill(0);
            sigma[int(s)] = 1
            d = array([NaN for t in V],float,order='C')
            #d = ndarray(shape=(n),dtype=float,order='C')
            #d.fill(NaN)
            d[int(s)]=0
            delta = array([0.0 for t in V],float,order='C')
            #delta = ndarray(shape=(n),dtype=float,order='C')
            #delta.fill(0)
            Q = []
            
            #Phase 1 BFS
            Q.append(s)
            while(len(Q)>0):
                v = Q.pop(0)
                S.append(v)
                for w in self._G.getVertex(v).getSuccessors():
                    w=int(w)
                    
                    #w found for the first time?
                    if (isnan(d[w])) :
                        Q.append(w)
                        d[w] = d[v] + 1
                    #shortest path to w via v?
                    if d[w]==d[v]+1 :
                        assert(d[w]<Inf)
                        sigma[w] += sigma[v]
                        P[w].append(v)
                        
            #Phase 2
            #The algorithm heart
            #S returns vertices in order of non-increasing distance from s
            while(len(S)>0):
                w = S.pop()
                w=int(w)
                
                #update routing table of w to s 
                if (s==w):
                    self._routingTable[w,s] = [s]
                else:
                    self._routingTable[w,s] = P[w]
                    
                #update deltaDot    
                delta[w]+=CW[s,w]
                for v in P[w] :
                    if w not in self._group :
                        delta[v] += delta[w]*sigma[v]/sigma[w]
                    else :                            
                        delta[v] += 0  #customization point
                        
                #Group calculations    
                if (w in self._group) :
                    #Dana's group betweenness
                    self._GB+=delta[int(w)]
                    
                        
            self._sigma[s]=sigma
            self._distance[s]=d
            self._deltaDot[s]=delta
    
    @property
    def distance(self):
        return self._distance
    
    def getDeltaDotMatrix(self):
        return self._deltaDot

    @property
    def sigma(self):
        return self._sigma
    
    def getRoutingTable(self):
        return self._routingTable
    
    def getGB(self):
        return self._GB
        

    
    
################################################################################
class StaticSet(AbstractGroupEvaluation,BasicSet):
            """
            Object of this class is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.
            
            In later versions it is expected to have all set's
            functionality and actualy extend Set class
            """                

            def __init__(self,G,members=set([])):
                self._G = G
                self._members = set([])
                self._gb = 0
                self._parties = {}
                for m in members:
                    self.add(m)
                
            def getGB(self):
                if self._gb<0:
                    ##update group betweenness value                        
                    gbalg = WeightedUlrik(G,group=self._members)
                    self._gb = gbalg.getGB() 
                    self._updated = True
                return self._gb
            def getUtility(self):
                return self.getGB()
            def getMembers(self):
                return self._members
            def add(self,party):
                self._gb=-1
                if "__iter__" in dir(party):
                    self._members.update(party)
                else:
                    self._members.add(party)
            def remove(self,party):
                self._gb=-1
                if "__iter__" in dir(party):
                    self._members.difference_update(party)
                else:
                    self._members.remove(party)                    
            def getUtilityOf(self,party):
                """
                (list of potential members)->float
                Calculates the exact contribution of party to GBC of current set.
                """
                ##if party is a single element make a list from it
                if "__iter__" not in dir(party):
                    party = [party]
                ##transform party into hashable object 
                party = tuple(sorted(party))
                
                if not self._parties.has_key(party):
                    s = party
                    ##update group betweenness value
                    cbalg = CandidatesBasedAlgorithm(self._dw,s)
                    for x in s:
                        cbalg.addVertex(x)
                    self._parties[party] = cbalg.getGB()
                return self._parties[party]
            def getCost(self):
                return len(self.getMembers())
            def getCostOf(self):
                if not "__iter__" in dir(party):
                    party = [party]
                return len(party)
################################################################################
