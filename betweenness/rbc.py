"""
Algorithms to compute Routing Betweenness Centrality of vertices and edges, groups, and sequences.

Input:
G - the subject graph
routingFunction(u,v,t) - the probability that v will forward to u a message with a destination address t. 
communicationWeights - matrix

Output:
delta matrix O(n^3) storage - delta[s,v,t] is the probability that a message sent from s to t will pass through v.

Preconditions:
routingFunction represents a routing scheme without loops.
"""
 
from topology.graph import *
from numpy import *
import copy
from brandes import WeightedBetweenness as WeightedUlrik
from utils import *
import networkx as NX

class Bullet:pass


class ShortestPathRoutingFunction(object):
    def __init__(self,G):
        uAlg = WeightedUlrik(G)
        self._routingTable=uAlg.getRoutingTable()
        self._d = uAlg.distance
        
    def __call__(self,s,u,v,t):
        if self._d[s,t] == self._d[s,u] + 1 + self._d[v,t]:
            uChildren = self._routingTable[u,t]
            if v in uChildren:
                return 1.0 / len(uChildren)
            else:
                return 0.0
        else:
            return 0.0


#def nxRoutingDAG(G,R,s,r,t):
    #assert isinstance(G,NX.Graph)
    #DAG = NX.DiGraph() 
    #for (u,v,w) in G.edges():
        ##consider routing direction for farmost vertices to appear first on the topological order
        #if R(s,u,v,t):
            #DAG.add_edge(u,v)
        #if R(s,v,u,t):
            #DAG.add_edge(v,u)                    
    #assert NX.dag.is_directed_acyclic_graph(DAG), "the routing function R contains loops."
    #return DAG

def nxRoutingDAG(G,R,t):
    assert isinstance(G,NX.Graph)
    DAG = NX.DiGraph() 
    for (u,v,w) in G.edges():
        if R(u,u,v,t):
            DAG.add_edge(u,v)
        if R(v,v,u,t):
            DAG.add_edge(v,u)                    
    assert NX.dag.is_directed_acyclic_graph(DAG), "the routing function R contains loops."
    return DAG
    


class AbstractBetweennessAlgorithm(object):
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix()):
        assert isinstance(G, GraphAsMatrix)
        self._G = G 
        if routingFunction==None:
            self._RF = ShortestPathRoutingFunction(G)
        else:
            self._RF = routingFunction
        self._CW = CW
        self._n = self._G.getNumberOfVertices()
        self._V = range(self._n)
        pass

    def getDelta(self,s,_,t):raise "Method not implemented"

    def getTargetDependency(self,_,t):
        result=0.0;
        for i in self._V:
            result+=self.getDelta(i,_,t)*self._CW[i,t]
        return result

    def getSourceDependency(self,s,_):
        result=0.0;
        for i in self._V:
            result+=self.getDelta(s,_,i)*self._CW[s,i]
        return result

    def getBetweenness(self,_):
        result=0.0;
        for s in self._V:
            for t in self._V:
                result+=self.getDelta(s,_,t)*self._CW[s,t]
        return result
    
    

class VRBC(AbstractBetweennessAlgorithm):
    """
    computes betweenness of vertices
    Precondition: routingFunction is loop-free
    """
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix()):
        super(VRBC,self).__init__(G,routingFunction,CW)
        pass

    def getDelta(self,s,v,t):
        """
        Running time: O(m)
        """
        if s==v or v==t :
            result=1.0
        else:            
            predecessor = [int(w) for w in self._G.getVertex(v).getSuccessors()]            
            P = [(u,self._RF(s,u,v,t)) for u in predecessor]
            P = filter(lambda x: x[1]>0,P)
            delta = [self.getDelta(s,u[0],t) for u in P]
            P = [u[1] for u in P]
            result = reduce(add,map(mul,delta,P),0)
        return result



class SRBC(VRBC):    
    """
    computes betweenness of sequences 
    Precondition: routingFunction is loop-free
    """
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix(),VRBCAlg=VRBC):
        super(SRBC,self).__init__(G,routingFunction,CW)
        self._vrbc=VRBCAlg(G,routingFunction,CW)
    
    def getDelta(self,s,seq,t):
        """
        Running time: O(m)
        """
        if not iterable(seq): 
            return self._vrbc.getDelta(s,seq,t)
        elif len(seq)==0:
            return 1
        elif len(seq)==1:
            return self._vrbc.getDelta(s,seq[0],t)
        elif len(seq)>1:
            if seq[-1]==seq[-2]:
                return self.getDelta(s,seq[:-1],t)
            else:
                v = seq[-1]
                predecessor = [int(w) for w in self._G.getVertex(v).getSuccessors()]            
                P = [(u,self._RF(s,u,v,t)) for u in predecessor]
                P = filter(lambda x: x[1]>0,P)
                delta = [self.getDelta(s,seq[:-1]+(u,),t) for u,puv in P]
                puvs = [puv for u,puv in P]
                result = reduce(add,map(mul,delta,puvs),0)
                return result

class GRBC(VRBC):    
    """
    computes betweenness of groups 
    Precondition: routingFunction is loop-free
    """
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix()):
        super(GRBC,self).__init__(G,routingFunction,CW)
    
    def getDelta(self,s,group,t): 
        """
        Running time: O(m)
        """
        if not iterable(group):group=frozenset([group])
        if s in group or t in group:
            result=1.0
        else:
            Q=[s]
            delta={s:1.0}
            groupDelta=0.0
            while len(Q)>0:
                v=Q.pop(0)
                #all vertices adjacent to v
                successors = [int(w) for w in self._G.getVertex(v).getSuccessors()]       
                #the probability of forwarding from v on the way from s to t
                successors = [(u,self._RF(s,v,u,t)) for u in successors]
                #only successors with positive forwarding probability
                successors = filter(lambda x: x[1],successors)
                for (u,pu) in successors:                
                    if u in group:
                        groupDelta+=pu*delta.get(v,0.0)
                    else:
                        delta[u]=delta.get(u,0.0)+pu*delta.get(v,0.0)
                        Q.append(u)
            result=groupDelta
        return result


    

class StatefullVRBC(VRBC):
    """
    computes betweenness of vertices
    caches results of its four functions
    Precondition: routingFunction is loop-free
    """    
    
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix()):
        super(StatefullVRBC,self).__init__(G,routingFunction,CW)
        self._cache={}
        pass
                
    def _doCache(self,f,**argsmap):
        k=(argsmap.get('s',Bullet),argsmap['v'],argsmap.get('t',Bullet))
        args=filter(lambda x:x!=Bullet,k)        
        if not self._cache.has_key(k):
            self._cache[k]=f(*args)
        return self._cache[k]
    
    def getDelta(self,s,v,t):
        return self._doCache(super(StatefullVRBC,self).getDelta,s=s,v=v,t=t)
    
    def getTargetDependency(self,v,t):
        return self._doCache(super(StatefullVRBC,self).getTargetDependency,v=v,t=t)

    def getSourceDependency(self,s,v):
        return self._doCache(super(StatefullVRBC,self).getSourceDependency,s=s,v=v)

    def getBetweenness(self,v):
        return self._doCache(super(StatefullVRBC,self).getBetweenness,v=v)


class StatefullSRBC(SRBC):
    """
    computes betweenness of sequences
    caches results of its four functions for input sequences of bounded length
    Precondition: routingFunction is loop-free 
    """
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix(),CechableSequenceLen=Inf):
        super(StatefullSRBC,self).__init__(G,routingFunction,CW)
        self._maxLen = CechableSequenceLen
        self._cache={}
        pass
    
    def _doCache(self,f,**argsmap):
        s = argsmap.get('s',Bullet)
        seq = argsmap['seq']
        t = argsmap.get('t',Bullet)                 
        k = (s,seq,t)
        if not iterable(seq): seq=[seq]
        args = [s,seq,t]
        args = filter(lambda x:x!=Bullet,k)        
        if len(seq)<=self._maxLen:
            if not self._cache.has_key(k):
                self._cache[k]=f(*args)
            return self._cache[k]
        else:  
            return f(*args)
    
    def getDelta(self,s,seq,t):
        return self._doCache(super(StatefullSRBC,self).getDelta,s=s,seq=seq,t=t)
    
    def getTargetDependency(self,seq,t):
        return self._doCache(super(StatefullSRBC,self).getTargetDependency,seq=seq,t=t)

    def getSourceDependency(self,s,seq):
        return self._doCache(super(StatefullSRBC,self).getSourceDependency,s=s,seq=seq)

    def getBetweenness(self,seq):
        return self._doCache(super(StatefullSRBC,self).getBetweenness,seq=seq)







class FasterVRBC(StatefullVRBC):
    """
    computes betweenness of vertices
    caches results of its four functions
    Precondition: routingFunction is loop-free and source independent
    """    
    
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix()):
        """
        Running time: O(nm)
        """
        super(FasterVRBC,self).__init__(G,routingFunction,CW)
        self._computeBetweenness()
        pass
    
    def _computeBetweenness(self):
        rb=dict([(int(v),0.0) for v in self._V])
        for t in self._V:
            t=int(t)            
            #each t defines a DAG
            DAG = nxRoutingDAG(self._G._G,self._RF,t)
            L = NX.dag.topological_sort(DAG)
            
            delta=dict([(int(v),0.0) for v in self._V])
            for v in L:
                delta[v]+=self._CW[v,t]
                for u in DAG.successors(v):
                    delta[u]+=delta[v]*self._RF(v,v,u,t)
                rb[v]+=delta[v]
                pass
            
            for v in self._V:
                self._doCache(lambda x,y: delta[v],v=v,t=t)
        for v in self._V:
            self._doCache(lambda x: rb[v],v=v)
    


class FasterSRBC(SRBC):
    """
    computes betweenness of sequences using delta chaining. 
    If VRBCAlg uses cache results this class performs getBetweenness and getTargetDependency 
    an order of n faster than SRBC
    Precondition: routingFunction is loop-free and source independent
    """
    
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix(),VRBCAlg=StatefullVRBC):
        super(FasterSRBC,self).__init__(G,routingFunction,CW)
        self._vrbc=VRBCAlg(G,routingFunction,CW)
        pass
    
    def getDelta(self,s,seq,t):
        # todo use recursion to cache intermediate results
        if not iterable(seq):seq=(seq,)
        if len(seq)==0:
            return 1;
        else:
            result=self._vrbc.getDelta(s,seq[0],t)
            for i in range(len(seq)-1):
                result*=self._vrbc.getDelta(seq[i],seq[i+1],t)
            return result
    
    def getTargetDependency(self,seq,t):
        if not iterable(seq):seq=(seq,)
        result=self._vrbc.getTargetDependency(seq[0],t)*self.getDelta(seq[0],seq,t)
        return result

    def getBetweenness(self,seq):
        if not iterable(seq):seq=(seq,)
        result=0.0;
        for t in self._V:
            result+=self.getTargetDependency(seq,t)
        return result


class FasterGRBC(GRBC):
    """
    computes betweenness of groups
    Precondition: routingFunction is loop-free and source independent
    """    
    
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix()):
        super(FasterGRBC,self).__init__(G,routingFunction,CW)
        
    def getTargetDependency(self,group,t):
        """
        Running time: O(m)
        """
        if not iterable(group):group=frozenset([group])
        gtd=0
        t=int(t)            
        #t defines a DAG
        DAG = nxRoutingDAG(self._G._G,self._RF,t)
        L = NX.dag.topological_sort(DAG)
        
        delta=dict([(int(v),0.0) for v in self._V])
        for v in L:
            delta[v]+=self._CW[v,t]
            if (v in group):
                gtd+=delta[v]
                delta[v]=0
            for u in DAG.successors(v):
                delta[u]+=delta[v]*self._RF(v,v,u,t)
            pass
        return gtd

    def getBetweenness(self,group):
        """
        Running time: O(nm)
        """
        if not iterable(group):group=frozenset([group])
        grb=0
        for t in self._V:
            grb+=self.getTargetDependency(group,t)
        return grb







class ContributionSRBC(FasterSRBC):
    """
    computes contribution of a sequence to group betweenness of inner group
    Precondition: routingFunction is loop-free and source independent
    
    Accepts a predefined set of vertices (candidates) (subset of or equal to V).
    Maintains a set of vertices (M) and a corresponding data structure of size O(|V|*|candidates|^2)
    M can be updated only by accepting new vertices. Call add(v) to add v to M.
    All methods compute SRBC with respect to M. That is accounting for all communication paths that do not traverse M.
    In all methods the seq argument must be subset of candidates.
    In all methods the s argument must be in candidates
    In all methods the t argument must be in V 
    In all methods the v argument must be in candidates 
    """

    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix(),candidates=None):
        super(ContributionSRBC,self).__init__(G,routingFunction,CW,VRBCAlg=StatefullVRBC)
        if candidates==None: candidates=range(self._n)        
        self._candidates = frozenset(candidates)
        self._M = set([])        
        for u in candidates:
            for t in xrange(self._n):
                for s in candidates:
                    self.getDelta(s, u, t)
                self.getTargetDependency(u, t)
            self.getBetweenness(u)
        pass
    
    
    def add(self,v):
        assert v in self._candidates
        cache = {}
        vrbc=self._vrbc
        for u in self._candidates:
            if u==v:
                cache[(Bullet,u,Bullet)] = 0
                for t in xrange(self._n):
                    cache[(Bullet,u,t)] = 0 
                    for s in self._candidates:                    
                        cache[(s,u,t)] = 0 
            else:                        
                cache[(Bullet,u,Bullet)] = self.getBetweenness(u) - self.getBetweenness((u,v)) - self.getBetweenness((v,u)) 
                for t in xrange(self._n):
                    cache[(Bullet,u,t)] = self.getTargetDependency(u,t) - self.getTargetDependency((u,v),t) - self.getTargetDependency((v,u),t)  
                    for s in self._candidates:                    
                        cache[(s,u,t)] = self.getDelta(s,u,t) - self.getDelta(s,(u,v),t) - self.getDelta(s,(v,u),t)
        vrbc._cache.update(cache)
        self._M.add(v)
        pass
    
    def getMembers(self):
        return frozenset(self._M)
    
    def getDelta(self,s,seq,t):
        if not iterable(seq):seq=(seq,)
        assert set(seq) <= self._candidates  
        assert s in self._candidates
        return super(ContributionSRBC,self).getDelta(s,seq,t)

    def getTargetDependency(self,seq,t):
        if not iterable(seq):seq=(seq,)
        assert set(seq) <= self._candidates  
        return super(ContributionSRBC,self).getTargetDependency(seq,t)

    def getSourceDependency(self,s,seq):
        if not iterable(seq):seq=(seq,)
        assert set(seq) <= self._candidates  
        assert s in self._candidates
        return super(ContributionSRBC,self).getSourceDependency(s,seq)

    def getBetweenness(self,seq):
        if not iterable(seq):seq=(seq,)
        assert set(seq) <= self._candidates  
        return super(ContributionSRBC,self).getBetweenness(seq)


class FasterGRBCWithPrecomputation(AbstractBetweennessAlgorithm):    
    """
    computes betweenness of groups using candidates contribution and delta chaining. 
    If VRBCAlg uses cache results this class performs getBetweenness and getTargetDependency 
    an order of n faster than GRBC
    
    Precondition: routingFunction is loop-free and source independent
    """
    def __init__(self,G,routingFunction=None,CW=DefaultCommMatrix(),candidates=None):
        super(FasterGRBCWithPrecomputation,self).__init__(G,routingFunction,CW)
        self._csrbc=ContributionSRBC(G, routingFunction, CW, candidates)
        pass
    
    def getDelta(self,s,group,t):
        if not iterable(group):group=frozenset([group])

        csrbc = copy.deepcopy(self._csrbc)
        rslt=0
        for v in group:
            rslt+=csrbc.getDelta(s,v,t)
            csrbc.add(v)
        return rslt

    def getTargetDependency(self,group,t):
        if not iterable(group):group=frozenset([group])

        csrbc = copy.deepcopy(self._csrbc)
        rslt=0
        for v in group:
            rslt+=csrbc.getTargetDependency(v,t)
            csrbc.add(v)
        return rslt

    def getSourceDependency(self,s,group):
        if not iterable(group):group=frozenset([group])

        csrbc = copy.deepcopy(self._csrbc)
        rslt=0
        for v in group:
            rslt+=csrbc.getSourceDependency(s,v)
            csrbc.add(v)
        return rslt

    def getBetweenness(self,group):
        if not iterable(group):group=frozenset([group])

        csrbc = copy.deepcopy(self._csrbc)
        rslt=0
        for v in group:
            rslt+=csrbc.getBetweenness(v)
            csrbc.add(v)
        return rslt
            

    
