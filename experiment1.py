"""                          
experiment 1
compare the running time of the following algorithms on random groups:
1)ulrik
2)CCA
3)CCARP
"""
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
from betweenness.brandes import WeightedBetweenness


#Graph generation :
ns = input("Initial Number of vertices :")
#ns = 100
ni = input("Number of vertices increment:")
#ni = 20
nr = input("Repetitions:")
#nr = 1

#d = input("Graph density (>1)(recommended 1.2-1.5) :")
d = 1.3
#p = input("Connection preferance (>0)(recommended 1) :")
p = 1.4


#gm=input("Graph generation model [0:BA,1:Uniform]:")
gm=0
#r = input("Repetitions :")
r = 1


#dd = input("Delta (s,s,t) definition [1 or 0]:")
dd = 1

#Execution parameters :
#ks = input("Initial set size :")
ks = 3
#ki = input("Set size increment:")
ki = 3
#kr = input("Repetitions :")
kr = 1

#rr = input("Number of random sets:")
rr = 100


cover = 0.999

maxtime = 21600


SetAlgList=[]
#if (raw_input("Use StaticSet? [y/n]")=="y"):
#  SetAlgList.append((StaticSet,"S"))
#if (raw_input("Use DynamicSet? [y/n]")=="y"):
#  SetAlgList.append((DinamicSet,"D"))
#if (raw_input("Use OptimizedDinamicSet? [y/n]")=="y"):
SetAlgList.append((lambda x:OptimizedDinamicSet(x,range(n)),"O"))



resultf = file("traversal_results_%d.txt"%time.time(),"w")
print "Graph#   \tn\td\tSetSize\tAlg\tTime\tResult\tNodes\tLeafs"
resultf.write("Graph#\tn\td\tSetSize\tAlg\tTime\tResult\tNodes\tLeafs\n")
for i in range(nr):
  n = ns + i*ni
  for _r in range(r):

    models = [("BA",graphBuilder.createRandomBAGraph),("Uniform",graphBuilder.createRandomGraph)]
    #create random graph
    #G = graphBuilder.createRandomScalefreeGraph(GraphAsMatrix,n,d,p)
    T = time.time()
    G = models[gm][1](n,d)
    T = time.time() - T
    G.__id = time.time()
    sys.stdout.write("%d\t%d\t%0.2f\t \t%s\t%0.3f\t \t \n"%(G.__id,n,d,models[gm][0],T))
    resultf.write("%d\t%d\t%0.2f\t \t%s\t%0.3f\t \t \n"%(G.__id,n,d,models[gm][0],T))


    #some well known constants
    totalB = (n*(n-1))

    ##precomputation
    #T = time.time()
    #dw = DataWorkshop(G)
    #T = time.time() - T
    #sys.stdout.write("%d\t%d\t%0.2f\t \t%s\t%0.3f\t \t \n"%(G.__id,n,d,"Pre",T))
    #resultf.write("%d\t%d\t%0.2f\t \t%s\t%0.3f\t \t \n"%(G.__id,n,d,"Pre",T))

    #reduced precomputation
    T = time.time()
    rdw = DataWorkshop(G,delayPrecomputation=True)
    T = time.time() - T
    sys.stdout.write("%d\t%d\t%0.2f\t \t%s\t%0.3f\t \t \n"%(G.__id,n,d,"RPre",T))
    resultf.write("%d\t%d\t%0.2f\t \t%s\t%0.3f\t \t \n"%(G.__id,n,d,"RPre",T))


    for j in range(min(kr,int((n-ks)/ki))):
        k = ks + j*ki
        for l in range(rr):
        
          ##value 1 (ulrik)
          #T = time.time()
          #ulrik = WeightedUlrik(G)
          #T = time.time() - T
          #sys.stdout.write("%d\t%d\t%0.2f\t%d\t%s\t%0.3f\t%0.3f\t%d\n"%(G.__id,n,d,k,"Ulrik",T,0,1))
          #resultf.write("%d\t%d\t%0.2f\t%d\t%s\t%0.3f\t%0.3f\t%d\n"%(G.__id,n,d,k,"Ulrik",T,0,1))
  
          ##value 3 (cca)
          #T = time.time()
          #cset = StaticSet(dw,set(random.sample(range(n),k)))
          #GB = cset.getGB() / totalB
          #T = time.time() - T
          #sys.stdout.write("%d\t%d\t%0.2f\t%d\t%s\t%0.3f\t%0.3f\t%d\n"%(G.__id,n,d,k,"CCA",T,GB,1))
          #resultf.write("%d\t%d\t%0.2f\t%d\t%s\t%0.3f\t%0.3f\t%d\n"%(G.__id,n,d,k,"CCA",T,GB,1))

          #value 3 (ccarp)
          T = time.time()
          cset = StaticSet(rdw,set(random.sample(range(n),k)))
          GB = cset.getGB() / totalB
          T = time.time() - T
          sys.stdout.write("%d\t%d\t%0.2f\t%d\t%s\t%0.3f\t%0.3f\t%d\n"%(G.__id,n,d,k,"CCARP",T,GB,1))
          resultf.write("%d\t%d\t%0.2f\t%d\t%s\t%0.3f\t%0.3f\t%d\n"%(G.__id,n,d,k,"CCARP",T,GB,1))



