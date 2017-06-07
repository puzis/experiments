import random
import utils
from abstractGroupEvaluation import AbstractGroupEvaluation
from abstractGroupEvaluation import BasicSet
import networkx as NX
from topology.graph import *


class ProxyGraph:
    def __init__(self,G):
        if isinstance(G,GraphAsMatrix):
            self._G=G._G
        elif isinstance(G,NS.Graph):
            self._G=G
        else:
            self._G=NX.Graph(G)

        s = self._G.nodes_iter().next()
        self._dfsGraph = NX.MultiGraph()
        self._dfs(s)

        self._F = NX.MultiGraph()
        self._linked = set([])
        discoveryEdges = [e for e in self._dfsGraph.edges() if e[2]=='discover']
        for e in discoveryEdges:
            self._F.add_node(e)
        for v in self._dfsGraph.nodes():
            for e in self._dfsGraph.in_edges_iter(v):
                if e[2]=='back':
                    self._F.add_node(e)
                    u = e[0]
                    while u != v:
                        for x in self._dfsGraph.in_edges_iter(u):
                            if x[2]=='discover':
                                f = x
                        self._F.add_edge(e,f)
                        if f not in self._linked:
                            self._linked.add(f)
                            u = f[0]
                        else:
                            u = v


    def _dfs(self,v,u=None):
        if self._dfsGraph.has_node(v):
            if not self._dfsGraph.has_edge(v,u):
                self._dfsGraph.add_edge(u,v,'back')
        else:
            self._dfsGraph.add_node(v)
            if u!=None:
                self._dfsGraph.add_edge(u,v,'discover')
            for w in self._G.neighbors(v):
                #if w!=u:
                    self._dfs(w,v)

    def getEdgeComponents(self):
        components = NX.component.connected_components(self._F)
        result = frozenset([frozenset([frozenset(e[0:2]) for e in component]) for component in components])
        return result





