from brandes import WeightedBetweenness as WeightedUlrik
import copy
import utils
from numpy import *
    

class DataWorkshop(object):
    """
    version 1.0
    
    A set of data structures and algorithms required for betweenness calculations.
    given:
    G=(V,E) - undirected unweighted graph n = |V|, m = |E|

    O(1) retrieved data:
    B(x) - individual vertex betweenness
    d{x,y} - distance between vertices x and y
    sigma{x,y} - number of shortest pathes between x and y
    delta(x,w,y) - sigma{x,w}*sigma{w,y}/sigma{x,y}
    delta(x,w,.) - sum of delta(x,w,y) for all y in V
    PB{x,y} - sum of delta(v,x,y,u) for all v,u in V
    cc(x) - the cost of x (IPS)
    {} - curly braces indicate unknown/unimportant order of arguments

    other data:
    AverageSigma
    AverageDistance
    PathDispersion
    
    """
    def __init__(self, graph, WC=utils.DefaultCommMatrix(),statusBar=False,delayPrecomputation=False):
        """
        (GroupBasedAlgorithm, Graph) -> GroupBasedAlgorithm
        Performs precomputation O(n^3 + nm)
        Why +nm ? may be it works on multigraphs too :)

        (impl: consider just-in-time calculation of PB values)
        """
        self._n = graph.getNumberOfVertices()
        #self._subsets = set(range(0))

        #single Ulrik traversal O(nm)
        GB = WeightedUlrik(graph,WC,statusBar=statusBar)
        #the graph itself is never referenced after this line
        self._d = GB.distance
        self._deltaDot = GB.getDeltaDotMatrix()
        self._sigma = GB.sigma
        self._routingTable = GB.getRoutingTable()
        
        #todo delay create PathBetweenness matrix 
        if delayPrecomputation:
            self._PB = utils.DelayedNDArray(getter=self.computePairBetweenness,placeholder=-1,shape=(self._n,self._n),dtype=float,order='C')
        else:
            self._PB = ndarray(shape=(self._n,self._n),dtype=float,order='C');
            self._PB.fill(nan)
            if not delayPrecomputation:
                progressCount = 0
                for s0 in range(self._n):
                    if statusBar:
                        progressCount+=1
                        statusBar.updateStatus("%d %%"%(100.0*progressCount/self._n))
                    for s1 in range(self._n):
                        self._PB[s0,s1]=self.computePairBetweenness(s0,s1)
                
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        result = "<DataWorkshop: n="+ str(self._n) +"\n"
        result += "Distance: \n"
        result += utils.matrixStr(self._d) + "\n"
        result += "Routing table: \n"
        result += utils.matrixStr(self._routingTable) + "\n"
        result += "Sigma: \n"
        result += utils.matrixStr(self._sigma) + "\n"
        result += "Path betweenness: \n"
        result += utils.matrixStr(self._PB) + "\n"
        result += ">"
        return result
    
    def getNumberOfVertices(self):
        return self._n

    @property
    def betweenness(self):
        """ no reference escaping """
        return utils.VirtualList(self._n,lambda i:self.PB[i,i])

    @property
    def distance(self):
        """ reference escaping """
        return self._d

    def getDeltaDotMatrix(self):
        """ reference escaping """
        return self._deltaDot

    @property
    def sigma(self):
        """ reference escaping """
        return self._sigma

    @property
    def PB(self):
        """ reference escaping """
        return self._PB
        #return utils.VirtualList(len(self._PB),self.computePairBetweenness)
        #return utils.DelayedMDMatrix(lambda indices:self.computePairBetweenness(indices[0],indices[1]),self._PB,nan,True)
        #return utils.VirtualList(lambda indices:self.computePairBetweenness(indices[0],indices[1]))
        #return UnmutableList(
            #lambda : len(self._PB),
            #lambda s0: UnmutableList(
                #lambda : len(self._PB[s0]),
                #lambda s1 : self.computePairBetweenness(s0,s1)
                #)
            #)
        #return self._PB
    
    def getRoutingTable(self):
        return self._routingTable
    
    def getB(self,v):        
        return self.PB[v,v]

    def getDistance(self,u,v):        
        return self._d[u,v]

    def getSigma(self,u,v):
        return self._sigma[u,v]

    def computePairBetweenness(self,s0,s1=None):
        """
        (x,y)  ->Path Betweenness of (x,y)
        ((x,y))->Path Betweenness of (x,y)
        this function computes PB(x,y) if it was not computed yet.
        """
        if s1==None:s1=s0[1];s0=s0[0]; #if given only one argument it should be a two tuple
        
        #calculate PB
        #Note that PB(u,v)=PB(v,u)
        #Every path is counted only once for s0!=s1 because :
        #delta(v,s0,s1)>0 => delta(v,s1,s0)=0
        #delta(v,s1,s0)>0 => delta(v,s0,s1)=0
        result = 0.0
        for u in range(self._n):
            #calculate Delta(u,{s0,s1},*)
            dd1 = self._deltaDot[u,s1] * self.getDelta(u,s0,s1)
            #paths from s0 and s1 already counted in deltaDot matrix
            result += dd1
        #when s0=s1 every path is counted twice (in both directions)
        #if s0==s1: self._PB[s0][s1] /= 2
        return result

    def getDelta(self,u,w,v=None):
        """
        (GroupBasedAlgorithm, int,int,int) -> float
        @return - percentage of shortest paths from u to v passing throug w
        @time - O(1)
        """
        if v==None :
            return self._deltaDot[u,w]
        elif self._sigma[u,v]==0 or self._sigma[u,w]==0 or self._sigma[w,v]==0:
            return 0.0
        elif (self._d[u,v]==self._d[u,w]+self._d[w,v]):
            return 1.0 * self._sigma[u,w]*self._sigma[w,v]/self._sigma[u,v]
        else:
            return 0.0

    def getAverageSigma(self,sourceGroup = None, targetGroup = None, filterFunction = lambda x,y : x!=y):
        if (sourceGroup==None):
            sourceGroup = range(self._n)
        if (targetGroup==None):
            targetGroup = range(self._n)
        s = 0.0
        c = 0.0
        for i in sourceGroup:
            for j in targetGroup:
                if(filterFunction(i,j)):
                    c+=1
                    s+=self.getSigma(i,j)
        return s/c
    def getAverageDistance(self,sourceGroup = None, targetGroup = None, filterFunction = lambda x,y : x!=y):
        if (sourceGroup==None):
            sourceGroup = range(self._n)
        if (targetGroup==None):
            targetGroup = range(self._n)
        s = 0.0
        c = 0.0
        for i in sourceGroup:
            for j in targetGroup:
                if(filterFunction(i,j)):
                    c+=1
                    s+=self.getDistance(i,j)
        return s/c                    
    def getPathDispersion(self,middleGroup = None,sourceGroup = None,targetGroup=None,filterFunction = lambda x,y : x!=y):
        if (sourceGroup==None):
            sourceGroup = range(self._n)
        if (targetGroup==None):
            targetGroup = range(self._n)
        if (middleGroup==None):
            middleGroup = range(self._n)
        fragmented = 0
        recoverable = 0
        for v in sourceGroup:
            for u in targetGroup:
                s = 0
                for w in middleGroup:
                    if 0<self.getDelta(v,w,u)<1:
                        s+=self.getDelta(v,w,u)
                fragmented += s
                if s==1:
                    recoverable += s
        return (fragmented, recoverable)
    
    def isValidSequence(self, vertices):
        return self.getDistance(vertices[0],vertices[-1])==reduce(add,map(self.getDistance,vertices[:-1],vertices[1:]),0)

    
