"""
A proxi Graph class.
Current version delegates to networkx.XGraph with integer nodes (vertices).
An internal dictionary is maintained to support vertex weights.
Edge weights are supported by networkx.XGraph.
"""

import networkx as NX
from edgeInfo import EdgeInfo
from vertexInfo import VertexInfo
import copy

class Vertex(object):
    def __init__(self,graph,index,weight):
        assert isinstance(graph,GraphAsMatrix)
        self._G = graph
        self._index = index
        self._weight = weight

    def __int__(self):
        return self._index

    def __eq__(self,other):
        if not isinstance(other,Vertex): return False;
        return self.getNumber() == other.getNumber();

    def __ne__(self,other):
        return not self.__eq__(other)

    def getNumber(self):
        return self._index

    def getSuccessors(self):
        return [Vertex(self._G,v,self._G.vertexWeights[v]) for v in self._G._G.neighbors(self._index)]

    def getPredecessors(self):
        return [Vertex(self._G,v,self._G.vertexWeights[v]) for v in self._G._G.neighbors(self._index)]

    def getNeighbors(self):
        return [Vertex(self._G,v,self._G.vertexWeights[v]) for v in self._G._G.neighbors(self._index)]

    def getWeight(self):
        return self._weight

    def setWeight(self,w):
        self._weight=w
        self._G.vertexWeights[self._index]=w

    def getEmanatingEdges(self):
        return [Edge(self._G,e[0],e[1]) for e in self._G._G.edges_iter([self._index])]

class Edge(object):
    def __init__(self,graph,v0,v1,weight=1):
        assert isinstance(graph,GraphAsMatrix)
        self._G = graph
        self._v0 = v0
        self._v1 = v1
        self._weight = weight

    def getWeight(self):
        return self._weight

    def getV0(self):
        return self._G.getVertex(self._v0)

    def getV1(self):
        return self._G.getVertex(self._v1)

    @property
    def V0Index(self):
        return self._v0

    @property
    def V1Index(self):
        return self._v1


class GraphAsMatrix:

    def __init__(self,nxgraph=None,vertexWeights={},directed=False):

        if directed:
            self._G = NX.DiGraph()
        else:
            self._G = NX.Graph()


        self.vertexWeights={}

        if isinstance(nxgraph,GraphAsMatrix):
            vertexWeights=nxgraph.vertexWeights
            nxgraph=nxgraph._G

        if isinstance(nxgraph,NX.Graph):
            for v in nxgraph.nodes_iter():
                self.addVertex(v,vertexWeights.get(v,VertexInfo()))
            for e in nxgraph.edges_iter():
                self.addEdge(*e)



    def addVertex(self,index,weight=VertexInfo()):
        self._G.add_node(index)
        self.vertexWeights[index]=weight

    def addEdge(self,v1,v2,weight=EdgeInfo()):
        self._G.add_edge(v1,v2,weight)

    def deleteEdge(self,e):
        assert isinstance(e,Edge)
        self._G.remove_edge(e.getV0().getNumber(),e.getV1().getNumber())


    def getNumberOfVertices(self):
        return self._G.number_of_nodes()

    def getNumberOfEdges(self):
        return self._G.number_of_edges()

    def getVertex(self,index):
        return Vertex(self,index,self.vertexWeights[index])

    def getVertices(self):
        return [Vertex(self,v,self.vertexWeights[v]) for v in self._G.nodes_iter()]

    def isEdge(self,v1,v2):
        return self._G.has_edge(v1,v2)

    def getEdge(self,v1,v2):
        return Edge(self,v1,v2,self._G.get_edge_data(v1,v2))

    def getEdges(self):
        return [Edge(self,e[0],e[1],self._G.get_edge_data(e[0],e[1])) for e in self._G.edges_iter()]
