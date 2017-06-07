
from topology import graphBuilder
from betweenness import *
from topology.graph import GraphAsMatrix
import subsets
import os
import time
from topology import representation
import argumentTranslator
import sys
import random
from betweenness.candidatesBasedAlgorithm import StaticSet
from betweenness.candidatesBasedAlgorithm import DinamicSet
from betweenness.candidatesBasedAlgorithm import OptimizedDinamicSet
from betweenness.gbcPruning import UndoableCandidatesElection,AbstractElection,OptimalElectionSearch
from xmlrpclib import *
from topology import graphBuilder
#graphnameprefix = raw_input("Graph name prefix:")
graphnameprefix="testrun"


#Graph generation :
#ns = input("Initial Number of vertices :")
ns = 50
#ni = input("Number of vertices increment:")
ni = 50
#nr = input("Repetitions:")
nr = 50

#d = input("Graph density (>1)(recommended 1.2-1.5) :")
d = 1.5

#gm=input("Graph generation model [0:BA,1:Uniform]:")
gm=0
#r = input("Number of networks of the same size :")
r = 1



#ks = input("Initial set size :")
ks = 1
#ki = input("Set size increment:")
ki = 2
#kr = input("Repetitions:")
kr = 10


#rg = input("Number of random groups of each size:")
rg = 3; 


maxtime = 3600

#serveruri=raw_input("Please enter XML-RPC server uri:")
serveruri='http://localhost:8080/'
server=ServerProxy(serveruri)


resultf = file(graphnameprefix + "_%d.txt"%time.time(),"w")
#print "Graph#   \tn\td\tSetSize\tAlg\tTime\tResult\tNodes\tLeafs"
#resultf.write("Graph#\tn\td\tSetSize\tAlg\tTime\tResult\tNodes\tLeafs\n")
print "Graph#   \tn\td\tAlg\tTime\tMemory\tgroup\tResult\tnodeCount\tResult2"
resultf.write("Graph#\tn\td\tAlg\tTime\tMemory\tgroup\tGBC\tnodeCount\tResult2\n")




for i in range(nr):
  n = ns + i*ni
  for _r in range(r):


    #########################################################################
    # Python network generation  
    models = [("BA",graphBuilder.createRandomBAGraph),("Uniform",graphBuilder.createRandomGraph)]    
    G = models[gm][1](n,d)
    G.__id = time.time()    

    #########################################################################
    # Java network import and analysis  
    g_id = server.Network.importNetwork(graphnameprefix, representation.getPajekRepr(G))
    if g_id == -1: sys.stdout.write("%s"%("Error in importNetwork (\d:\d) \n"%(G.__id,g_id))); continue    
  #  fgrbc_alg_id = server.FasterGRBC.create(g_id,'',[],1)
    fgrbc_alg_id_arr = server.FasterGRBC.create(g_id,'',[],2)
    grbc_alg_id = server.GRBC.create(g_id,'')
    
    #rat_grbc_alg_id = server.RationalGRBC.create(g_id,'')    
    #rat_fgrbc_alg_id_arr = server.RationalFasterGRBC.create(g_id,'',[])
    
    
    #########################################################################
    # GBC computation
    for _ki in range(min(kr,int((n-ks)/ki))):
        k = ks + _ki*ki
        for j in range (rg):
            vertices = random.sample(range(n),k+1)    
            ####################################################
            # GRBC
            T = time.time()
            GB = server.GRBC.getBetweenness(grbc_alg_id,vertices)
            T = time.time() - T
            #memory = server.Server.getMemoryConsumption()
            memory=0
            sys.stdout.write("%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"GRBC",T,memory,k,GB))
            resultf.write(   "%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"GRBC",T,memory,k,GB))             
             
            ####################################################
            # FasterGRBC
            T = time.time()
            GB = server.FasterGRBC.getBetweenness(fgrbc_alg_id_arr,vertices)
            T = time.time() - T
            #memory = server.Server.getMemoryConsumption()
            memory=0
            sys.stdout.write("%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"FGRBC",T,memory,k,GB))
            resultf.write(   "%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"FGRBC",T,memory,k,GB))
            
            ####################################################
            # RationalGRBC
            #T = time.time()
            #GB = server.RationalGRBC.getBetweenness(rat_grbc_alg_id,vertices)
            #T = time.time() - T
            #memory = server.Server.getMemoryConsumption()
          #  memory=0
            #sys.stdout.write("%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"RGRBC",T,memory,k,GB))
            #resultf.write(   "%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"RGRBC",T,memory,k,GB))             
             
            ####################################################
            # RationalFasterGRBC
            #T = time.time()
            #GB = server.RationalFasterGRBC.getBetweenness(rat_fgrbc_alg_id_arr,vertices)
            #T = time.time() - T
            #memory = server.Server.getMemoryConsumption()
         #   memory=0
            #sys.stdout.write("%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"RFGRBC",T,memory,k,GB))
            #resultf.write(   "%d\t%d\t%0.2f\t%s\t%0.3f\t%d\t%d\t%0.9f\n"%(G.__id,n,d,"RFGRBC",T,memory,k,GB))
    
 
    server.FasterGRBC.destroy (fgrbc_alg_id_arr);
    server.GRBC.destroy(grbc_alg_id);
    #server.RationalFasterGRBC.destroy (rat_fgrbc_alg_id_arr);
    #server.RationalGRBC.destroy(rat_grbc_alg_id);  
    server.Network.destroy(g_id);

            
            

resultf.close    

                        



        
      

