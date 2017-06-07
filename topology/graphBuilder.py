
import random
import copy
from vertexInfo import VertexInfo
from edgeInfo import EdgeInfo
from topology.graph import GraphAsMatrix


class TopologyModel(object):
    def __init__(self,G):
        self._G = G
        self._vertexInfoGen = VertexInfo
        self._edgeInfoGen = EdgeInfo

    def generateClique(self,k):
        rslt = []
        n = self._G.getNumberOfVertices()
        for i in range(n,int(n+k)):
            self._G.addVertex(i,self._vertexInfoGen())
            rslt.append(i)
            for j in range(n,i):
                self._G.addEdge(i,j,self._edgeInfoGen())
        return rslt

    def setVertexInfoGenerator(self,viGen):
        self._vertexInfoGen = viGen

    def setEdgeInfoGenerator(self,eiGen):
        self._edgeInfoGen = eiGen

    def addVertex(self,n):
        self._G.addVertex(n,self._vertexInfoGen())

    def addEdge(self,s,t):
        self._G.addEdge(s,t,self._edgeInfoGen())

    def generateRandomLinks(self,sources,targets,k):
        """
        generates k random links.
        good for sparce graphs.
        """
        rslt =[]
        for i in range(k):
            ok = False
            while not ok:
                s = random.choice(sources)
                t = random.choice(targets)
                if (s!= t and (not self._G.isEdge(s,t))):
                    self.addEdge(s,t)
                    rslt.append((s,t))
                    ok = True
        return rslt

    def generateLinksWithProbability(self,sources,targets,p):
        """
        connects s to t with probability p.
        good for dense graphs.
        """
        rslt =[]
        for s in sources:
            for t in targets:
                if(s!= t and (not self._G.isEdge(s,t))):
                    if (random.random()<p):
                        self.addEdge(s,t)
                        rslt.append((s,t))
        return rslt

    def generatePath(self,s,t,l):
        vertices=[]
        n=self._G.getNumberOfVertices()
        for i in range(l-1):
            self.addVertex(n)
            vertices.append(n)
            self.addEdge(s,n)
            s=n
            n=n+1
        self.addEdge(s,t)
        return vertices

class BAModel(TopologyModel):
    def __init__(self,G):
        TopologyModel.__init__(self,G)
        self._carry = 0
        self._d = 2

    def setDegree(self,d):
        self._d = d

    def generateVertex(self):
        n = self._G.getNumberOfVertices()
        self.addVertex(n)
        self._carry += self._d
        self.connect(n)
        return n

    def connect(self,source):
        m=self._G.getNumberOfEdges()
        edges = list(self._G.getEdges())
        while(self._carry>=1):
            r2= random.randint(0,1)
            e = random.choice(edges)
            if r2==0:
                target = e.getV0().getNumber()
            else:
                target = e.getV1().getNumber()
            if(source != target and not(self._G.isEdge(source,target))):
                self.addEdge(source,target)
                self._carry-=1




class LayeredModel(TopologyModel):
    def __init__(self,G):
        TopologyModel.__init__(self,G)

    def addLayerWithUniformConnectivity(self,prevLayer,layerSize,degreeDist):
        """
            (LayeredModel,sequence,int,int())->list of vertices
            adds layerSize vertices to the graph
            each new vertex will be randomly connected to vertices from previosLayer
        """
        vertices = []
        n = self._G.getNumberOfVertices()
        for i in range(n,n+layerSize):
            self.addVertex(i)
            self.connectUniform(i,degreeDist(),copy.copy(prevLayer))
            vertices.append(i)
        return vertices

    def addChildrenLayer(self,prevLayer,minChildren,maxChildren):
        vertices = []
        n = self._G.getNumberOfVertices()
        for i in prevLayer:
            for j in range(random.randint(minChildren,maxChildren)):
                self.addVertex(n)
                self.addEdge(i,n)
                vertices.append(n)
                n+=1
        return vertices

    def duplicateLayerWithSourceLinkOnly(self,prevLayer):
        vertices = []
        n = self._G.getNumberOfVertices()
        for i in range(len(prevLayer)):
            v=n+i
            self.addVertex(v)
            self.addEdge(v,prevLayer[i])
            vertices.append(v)
        return vertices

    def duplicateLayerWithHighInterconnection(self,prevLayer):
        vertices = []
        n = self._G.getNumberOfVertices()
        v2 = n
        #duplicate vertices in prevLayer
        for v1 in prevLayer:
            self.addVertex(v2)
            #duplicate edges of v2
            neighbours = self._G.getVertex(v1).getSuccessors()
            neighbours = map(lambda x:x.getNumber(),neighbours)
            #save current edge info generator to copy info of duplicated edges
            tmpeigen = self._edgeInfoGen
            for u in neighbours:
                self._edgeInfoGen = lambda : copy.deepcopy(self._G.getEdge(v1,u).getWeight())
                self.addEdge(v2,u)
            self._edgeInfoGen = tmpeigen
            #edge from vertex to its' clone will use default info generator
            if not self._G.isEdge(v2,v1):
                self.addEdge(v2,v1)
            vertices.append(v2)
            v2=v2+1
        return vertices

    def connectUniform(self,source,d,targets):
        """
            (LayeredModel,int,int,sequence)->[(source,v1),(source,v2),...]
            Uniformly connects source with targets bby d links
        """
        edges=[]
        i=0
        while(i<d):
            t = random.choice(targets)
            targets.remove(t)
            if(not self._G.isEdge(source,t)):
                self.addEdge(source,t)
                edges.append((source,t))
                i+=1
        return edges


def createRandomBAGraph(n,d,graphType=GraphAsMatrix):
    G = graphType()
    ba = BAModel(G)
    ba.generateClique(int(d+1))
    ba.setDegree(d)
    for i in range(n-int(d+1)): #add n vertices
        ba.generateVertex()
    return G



def createRandomGraph(n,d,graphType=GraphAsMatrix):
    G = graphType()
    tm = TopologyModel(G)
    for i in range(n):
        tm.addVertex(i)
    vertices = map(int,G.getVertices())
    tm.generateRandomLinks(vertices,vertices,int(n*d))
    return G

def createATwoRouteGraph(l,k1,k2,graphType=GraphAsMatrix):
    """
    (l,k1,k2)->a graph with 2+l*k1+l*k2 vertices
    Generates a graph in which s' connected to t' with
    k1 vertex disjoint paths with low redundancy and
    k2 vertex disjoint paths with high redundancy
    """
    G = graphType()
    tm = LayeredModel(G)
    s=G.getNumberOfVertices()
    t=s+1
    tm.addVertex(s)
    tm.addVertex(t)

    for i in range(k1):
        tm.generatePath(s,t,l)

    if k2>0:
        path=tm.generatePath(s,t,l)
        for i in range(k2-1):
            tm.duplicateLayerWithHighInterconnection(path)
    return G

def createRangedSmallWorld(n, k, p, l, graphType=GraphAsMatrix):
    G = graphType()
    if False: assert isinstance(G,GraphAsMatrix)
    tm = TopologyModel(G)
    nlist = range(n)
    for u in nlist:
        tm.addVertex(u)
    for u in nlist:
        for v in range(k):
            tm.addEdge(u,(u+v)%n)

    for u in nlist:
        if random.random() < p:
            w = random.choice(nlist)
            while w == u or G.isEdge(u, w):
                w = random.choice(nlist)
            tm.generatePath(u,w,l)
    return G
