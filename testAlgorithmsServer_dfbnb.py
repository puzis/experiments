import unittest
from xmlrpclib import *
import sys

import topology
from topology.representation import getPajekRepr
from topology import graphBuilder
from betweenness import *

def withretry(f):
  def new_f(*args):
    time.sleep(0.05)
    try:
      return f(*args)
    except:
      time.sleep(10)
      return f(*args)
  return new_f


class JDFBnBTest(unittest.TestCase):

    def setUp(self):
      self.testGraphs={}

      G_line = topology.graph.GraphAsMatrix()
      for v in range(7):
        G_line.addVertex(v)
      for v in range(6):
        G_line.addEdge(v,v+1)
      self.testGraphs["line"]=G_line

      G_clique = topology.graph.GraphAsMatrix()
      for v in range(7):
        G_clique.addVertex(v)
      for v in range(7):
        for u in range(v,7):
          if(u!=v) : G_clique.addEdge(u,v)
      self.testGraphs["clique"]=G_clique

      G_7 = topology.graph.GraphAsMatrix()
      for v in range(7):
        G_7.addVertex(v)
      for v in range(6):
        G_7.addEdge(v,v+1)
      G_7.addEdge(0,2) ; G_7.addEdge(4,6)
      self.testGraphs["middle V"]=G_7

      G_7 = topology.graph.GraphAsMatrix()
      for v in range(6):
        G_7.addVertex(v)
      for v in range(5):
        G_7.addEdge(v,v+1)
      G_7.addEdge(0,5)
      G_7.addEdge(0,3)
      self.testGraphs["CrossedCircle"]=G_7

      self.server = ServerProxy("http://localhost:8080")

    def tearDown(self):
      pass

    def test_JDFBNB_Instantiation(self):
      for (title,G) in self.testGraphs.items():
        serv = self.server
        net_id = serv.Network.importNetwork(title,getPajekRepr(G), "net")
        for c in [0,1,2]:
          for st in [0,1]:
            for uh in [0,1,2]:
              for ch in [0,1,2]:
                for eo in [0,1,2,3]:
                  sys.stdout.write(title+","+str(c)+","+str(st)+","+str(uh)+","+str(ch)+","+str(eo))
                  for ol in range(17):
                    if st==0:
                      b = 3.0
                    elif st==1:
                      b = G.getNumberOfVertices()*5.0
                    if not withretry(serv.Dfbnb.dfbnbInit)(net_id,c,st,b,eo,uh,ch,ol):
                      raise "analyze fialed"
                    sys.stdout.write(".")
                  sys.stdout.write("\n")
      pass

    def test_JDFBNB_OptimalResult_size(self):
      for (title,G) in self.testGraphs.items():
        serv = self.server
        net_id = withretry(serv.Network.importNetwork)(title,getPajekRepr(G),"net")
        c=0  #only betweenness
        st=0 #cost = size
        for b in [1.0,2.0,3.0]:
          dw = DataWorkshop(G)
          s = StaticSet(dw)
          election = UndoableCandidatesElection(s,int(b),range(dw.getNumberOfVertices()))
          search = OptimalElectionSearch(election,b)
          while(search.hasNext()):search.next()
          pyResult = search.getOptimalValue()

          for uh in [0,1,2]:
            for ch in [0,1,2]:
              for eo in [0,1,2,3]:
                sys.stdout.write(title+","+str(b)+","+str(c)+","+str(st)+","+str(uh)+","+str(ch)+","+str(eo))
                for ol in [0,1,2,3,4,5,6]:
                  dfbnb = self.server.Dfbnb
                  if not withretry(dfbnb.dfbnbInit)(net_id,c,st,b,eo,uh,ch,ol):
                    raise "analyze fialed"
                  n=withretry(dfbnb.dfbnbCalculate)(net_id)
                  jResult = withretry(dfbnb.dfbnbGetBestUtility)(net_id)
                  self.assertAlmostEqual(jResult,pyResult)
                  sys.stdout.write(".")
                  pass
                sys.stdout.write("\n")
        pass
      pass


    def test_JDFBNB_OptimalResult_randomGraphs(self):
      for n in range(5,10,1):
        G = topology.graphBuilder.createRandomBAGraph(n,2)
        title = "test"

        serv = self.server
        net_id = withretry(serv.Network.importNetwork)(title,getPajekRepr(G),"net")
        c=0  #only betweenness
        st=0 #cost = size
        for b in [1.0,2.0,3.0]:
          dw = DataWorkshop(G)
          s = StaticSet(dw)
          election = UndoableCandidatesElection(s,int(b),range(dw.getNumberOfVertices()))
          search = OptimalElectionSearch(election,b)
          while(search.hasNext()):search.next()
          pyResult = search.getOptimalValue()

          for uh in [0,1,2]:
            for ch in [0,1,2]:
              for eo in [0,1,2,3]:
                sys.stdout.write(title+","+str(b)+","+str(c)+","+str(st)+","+str(uh)+","+str(ch)+","+str(eo))
                for ol in [0,1,2,3,4,5,6]:
                  dfbnb = self.server.Dfbnb
                  if not withretry(dfbnb.dfbnbInit)(net_id,c,st,b,eo,uh,ch,ol):
                    raise "analyze fialed"
                  n=withretry(dfbnb.dfbnbCalculate)(net_id)
                  jResult = withretry(dfbnb.dfbnbGetBestUtility)(net_id)
                  self.assertAlmostEqual(jResult,pyResult)
                  sys.stdout.write(".")
                sys.stdout.write("\n")

        pass
      pass


if __name__ == "__main__":
    while(True):
        unittest.main()

