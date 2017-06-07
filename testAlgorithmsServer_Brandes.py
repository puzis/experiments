import unittest
from xmlrpclib import *
import sys

import topology
from topology.representation import getPajekRepr
from topology import graphBuilder
from betweenness import *



class BetweennessTest(unittest.TestCase):

    def setUp(self):
        self.tests=[]

        G_line = topology.graph.GraphAsMatrix()
        for v in range(7):
            G_line.addVertex(v)
        for v in range(6):
            G_line.addEdge(v,v+1)
        self.tests.append(("line",
            (G_line,                                            #the network
            (12.00, 22.00, 28.00, 30.00, 28.00, 22.00, 12.00),  #Vertex betweenness
            (                                                   #groups and their GBC
                ([3],30.0),                                     #[group], GBC
                ([2],28.0),
                ([2,3],34.0),
                ([2,4],38.0),
                ([0,2,3],36.0)
            ),
            (
                utils.ReadOnlyArray(2,(                         #Comm. Weights matrix
                    (0,0,0,0,0,0,1),
                    (0,0,0,0,0,0,0),
                    (0,0,0,0,0,0,0),
                    (0,0,0,0,0,0,0),
                    (0,0,0,0,0,0,0),
                    (0,0,0,0,0,0,0),
                    (0,0,0,0,0,0,0))),

                (1.0,1.0,1.0,1.0,1.0,1.0,1.0)                   #Resulting BC values
            )
            ),"GRAPH_AS_HASH_MAP","BFS"))                                           #Directed?, shortest path alg

        G_line = topology.graph.GraphAsMatrix()
        for v in range(7):
            G_line.addVertex(v)
        for v in range(6):
            G_line.addEdge(v,v+1)
        self.tests.append(("line-directed",
            (G_line,                                            #the network
            (6.00, 11.00, 14.00, 15.00, 14.00, 11.00, 6.00),  #Vertex betweenness
            (                                                   #groups and their GBC
                ([3],30.0),                                     #[group], GBC
                ([2],28.0),
                ([2,3],34.0),
                ([2,4],38.0),
                ([0,2,3],36.0)
            ),
            ),"DI_GRAPH_AS_HASH_MAP","BFS"))                                           #Directed?, shortest path alg

        G_clique = topology.graph.GraphAsMatrix()
        for v in range(7):
            G_clique.addVertex(v)
        for v in range(7):
            for u in range(v,7):
                if(u!=v) : G_clique.addEdge(u,v)
        self.tests.append(("clique",
            (G_clique,
            (12.00, 12.00, 12.00, 12.00, 12.00, 12.00, 12.00), #Vertex betweenness
            (
                ([3],12.0),
                ([2],12.0),
                ([2,3],22.0),
                ([2,4],22.0),
                ([0,2,3],30.0)
            )
            ),"GRAPH_AS_HASH_MAP","BFS"))                                           #Directed?, shortest path alg


        G_7 = topology.graph.GraphAsMatrix()
        for v in range(7):
            G_7.addVertex(v)
        for v in range(6):
            G_7.addEdge(v,v+1)
        G_7.addEdge(0,2) ; G_7.addEdge(4,6)
        self.tests.append(("middle V",
            (G_7,
            (12.00, 12.00, 28.00, 30.00, 28.00, 12.00, 12.00), #Vertex betweenness
            (
                ([3],30.0),
                ([2],28.0),
                ([2,3],34.0),
                ([2,4],38.0),
                ([0,2,3],36.0)
            )
            ),"GRAPH_AS_HASH_MAP","BFS"))                                           #Directed?, shortest path alg

        G_7 = topology.graph.GraphAsMatrix()
        for v in range(6):
            G_7.addVertex(v)
        for v in range(5):
            G_7.addEdge(v,v+1)
        G_7.addEdge(0,5)
        G_7.addEdge(0,3)
        self.tests.append(("CrossedCircle",
            (G_7,
            (16.6667, 11.6667, 11.6667, 16.6667, 11.6667, 11.6667), #Vertex betweenness
            (
                ([3],16.6667),
                ([2],11.6667),
                ([2,3],20.3333),
                ([2,4],20),
                ([0,2,3],28)),

            (utils.ReadOnlyArray(2,(
                    (0,0,0,0,0,0),
                    (0,0,0,0,1,0),
                    (0,0,0,0,0,1),
                    (0,0,0,0,0,0),
                    (0,0,0,0,0,0),
                    (0,0,1,0,0,0))),

                (2.0000,1.6667,2.3333,2.0000,1.6667,2.3333)
            )
            ),"GRAPH_AS_HASH_MAP","BFS"))                                           #Directed?, shortest path alg


        G_7 = topology.graph.GraphAsMatrix()
        for v in range(6):
            G_7.addVertex(v)
        for v in range(5):
            G_7.addEdge(v,v+1,topology.graph.EdgeInfo(defaults={"latency":1}))
        G_7.addEdge(0,5,topology.graph.EdgeInfo(defaults={"latency":1}))
        G_7.addEdge(0,3,topology.graph.EdgeInfo(defaults={"latency":2}))


        self.tests.append(("CrossedCircle-weighted",
            (G_7,
            (14.0, 13.0, 13.0, 14.0, 13.0, 13.0), #Vertex betweenness
            (
                ([3],16.6667),
                ([2],11.6667),
                ([2,3],20.3333),
                ([2,4],20),
                ([0,2,3],28)),

            (utils.ReadOnlyArray(2,(
                    (0,0,0,0,0,0),
                    (0,0,0,0,1,0),
                    (0,0,0,0,0,1),
                    (0,0,0,0,0,0),
                    (0,0,0,0,0,0),
                    (0,0,1,0,0,0))),

                (1.5,2,2.5,1.5,2,2.5)
            )
            ),"GRAPH_AS_HASH_MAP","DIJKSTRA"))                                           #Directed?, shortest path alg
        self.server = ServerProxy("http://localhost:8080")

    def tearDown(self):
        pass

    def test_JBrandes_Betweenness(self):
        """
        Test Ulrik algorithm for all vertices betweenness
        """
        for test in self.tests:
            G = test[1][0]
            print test[2]
            netstr = getPajekRepr(G)
            net_id = self.server.Network.importNetwork(test[0],netstr,"net",test[2])
            alg_id = self.server.Brandes.create(net_id,-1,range(G.getNumberOfVertices()),test[3])
            bc = self.server.Brandes.getBetweenness(alg_id)
            self.server.Brandes.destroy(alg_id)
            self.server.Network.destroy(net_id)

            for i in range(G.getNumberOfVertices()):
                self.assertAlmostEqual(bc[i],test[1][1][i],3,"%f != %f for %d in %s"%(bc[i],test[1][1][i],i,test[0]))

    def test_JBrandes_CW(self):
        for test in self.tests:
            if len(test[1])>=4:
                G = test[1][0]
                import csv
                dial = csv.excel()
                dial.delimiter=' ';
                cwstrio = csv.StringIO()
                cwcsv = csv.writer(cwstrio,dial)
                cwcsv.writerows(test[1][3][0])
                net_id = self.server.Network.importNetwork(test[0],getPajekRepr(G),"net")
                alg_id = self.server.Brandes.create(net_id,cwstrio.getvalue(),test[3])
                bc = self.server.Brandes.getBetweenness(alg_id)
                #self.server.Brandes.destroy(alg_id)
                #self.server.Network.destroy(net_id)

                for i in range(G.getNumberOfVertices()):
                    self.assertAlmostEqual(bc[i],test[1][3][1][i],3,"%f != %f for %d in %s"%(bc[i],test[1][3][1][i],i,test[0]+" WC"))

    def test_JBrandes_vs_PyBetweenness_ConsistencyOnRandomConnectedGraphs(self):
        for n in range(10,20,1):
            G = graphBuilder.createRandomBAGraph(n, 2)
            PyBC = DataWorkshop(G).betweenness
            net_id = self.server.Network.importNetwork("test",getPajekRepr(G),"net")
            alg_id = self.server.Brandes.create(net_id,'')
            JBC    = self.server.Brandes.getBetweenness(alg_id)
            #self.server.Brandes.destroy(alg_id)
            #self.server.Network.destroy(net_id)

            for i in range(n):
                self.assertAlmostEqual(PyBC[i],JBC[i],8,"%f != %f for %d in graph of size %d"%(PyBC[i],JBC[i],i,n))
            sys.stdout.write(".")

    def test_JBrandes_vs_PyBetweenness_ConsistencyOnRandomDisconnectedGraphs(self):
        for n in range(10,20,1):
            G = graphBuilder.createRandomGraph(n, 0.8)
            PyBC = DataWorkshop(G).betweenness
            net_id = self.server.Network.importNetwork("test",getPajekRepr(G),"net")
            alg_id = self.server.Brandes.create(net_id,'')
            JBC    = self.server.Brandes.getBetweenness(alg_id)
            #self.server.Brandes.destroy(alg_id)
            #self.server.Network.destroy(net_id)

            for i in range(n):
                self.assertAlmostEqual(PyBC[i],JBC[i],8,"%f != %f for %d in graph of size %d"%(PyBC[i],JBC[i],i,n))
            sys.stdout.write(".")


    def test_JBrandes_GBC(self):
        """
        Test Candidate based algorithm for group betweenness
        """
        for testGraph in self.tests :
            G = testGraph[1][0]
            for testSet in testGraph[1][2]:
                net_id = self.server.Network.importNetwork("test",getPajekRepr(G),"net")
                alg_id = self.server.Brandes.create(net_id,-1,range(G.getNumberOfVertices()),"BFS",False,testSet[0])
                actual = self.server.Brandes.getGBC(alg_id)
                expected=testSet[1]
                self.assertAlmostEqual(actual,expected,3,"%f != %f for %s in %s"%(actual,expected,testSet[0],testGraph[0]))




if __name__ == "__main__":
    while(True):
        unittest.main()

