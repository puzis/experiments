import opus7.graphAsMatrix 
import opus7.vertex
import opus7.edge

class Vertex(object):
    def __init__(self,theVertex):
        assert isinstance(theVertex,opus7.vertex.Vertex)
        self._v = theVertex

    def __int__(self):
        return self._v.__int__()

    def getNumber(self):
        return self._v.getNumber()

    def getSuccessors(self):
        return self._v.getSuccessors()

    def getWeight(self):
        return self._v.getWeight()

    def getEmanatingEdges(self):
        return self._v.getEmanatingEdges()

class Edge(object):
    def __init__(self,e):
        assert isinstance(e, opus7.edge.Edge)
        self._e = e
    
    def getWeight(self):
        return self._e.getWeight()

    def getV0(self):
        return self._e.getV0()

    def getV1(self):
        return self._e.getV1()

    

class GraphAsMatrix(object):
    """
    A proxi Graph class. 
    Current version delegates to opus7.graphAsMatrix.GraphAsMatrix with 1000 as a maximal number of vertices.
    """
    
    def __init__(self):
        self._G=opus7.graphAsMatrix.GraphAsMatrix(1000)
    
    def addVertex(self,index,weight=None):
        self._G.addVertex(index,weight)
        #self._G.add_node(index)
        
    def addEdge(self,v1,v2,weight=None):
        self._G.addEdge(v1,v2,weight)
    
    def getNumberOfVertices(self):
        return self._G.getNumberOfVertices()
    
    def getNumberOfEdges(self):
        return self._G.getNumberOfEdges()
    
    def getVertex(self,index):
        return Vertex(self._G.getVertex(index))
    
    def getVertices(self):
        return [Vertex(v) for v in self._G.getVertices()]
    
    def isEdge(self,v1,v2):
        return self._G.isEdge(v1,v2)
    
    def getEdge(self,v1,v2):
        return Edge(self._G.getEdge(v1,v2))

    def getEdges(self):
        return [Edge(e) for e in self._G.getEdges()]
    
    
