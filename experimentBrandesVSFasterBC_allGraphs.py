"""
experiment for testing speedup heuristics for BC computation
Time and memory consumption is measured for
1)  BC --- Brandes algorithm for BC
2)  BC(TM) --- BC with support for Traffic Matrices. For bipartite coauthorship networks only.
3)  BV+BC(TM) --- Remove Bridging Vertices (degree 2) that are not sources/targets before running BC
4)  SE+BC(TM) --- Unify Stracturally Equvalent vertices before running BC
5)  SE+BV+BC(TM)
6)  BV+SE+BC(TM)
7)  BCC+BC(TM) --- Partition the graph to Bi-Connetect Components and run BC for each component
8)  BCC(TM)+BC(TM) --- Partition the graph to Bi-Connetect Components and run BC for each component
9)  BV+BCC+BC(TM)
10) SE+BCC(TM)+BC(TM)
11) SE+BV+BCC(TM)+BC(TM)
12) BV+SE+BCC(TM)+BC(TM)

13) BCC+SE+BC(TM)
"""

from topology.graphBuilder import *
from topology.graph import GraphAsMatrix
import os
import time
from topology import representation
import sys
import random
from xmlrpclib import *
from topology.representation import getPajekRepr
import string
from networkx.generators.random_graphs import *
import csv
import ConfigParser as pyini

def withretry(f):
    def new_f(*args):
        time.sleep(0.05)
        try:
            return f(*args)
        except:
            time.sleep(10)
            return f(*args)
    return new_f


def has_option(ini,section,option):
   if ini.has_option(section,option):
      return True
   elif ini.has_option(pyini.DEFAULTSECT,option):
      return True
   elif ini.defaults().has_key(option):
      return True
   else:
      return False

def prompt_for_option(ini,section,option,prompt):
   if ini.has_option(section,option):
      value = eval(ini.get(section,option))
   elif ini.has_option(pyini.DEFAULTSECT,option):
      value = eval(ini.get(pyini.DEFAULTSECT,option))
   elif ini.defaults().has_key(option):
      value = eval(ini.defaults()[option])
   else:
      value = input(prompt)
   return value;

def prompt_for_raw_option(ini,section,option,prompt):
   if ini.has_option(section,option):
      value = ini.get(section,option)
   elif ini.has_option(pyini.DEFAULTSECT,option):
      value = ini.get(pyini.DEFAULTSECT,option)
   elif ini.defaults().has_key(option):
      value = ini.defaults()[option]
   else:
      value = raw_input(prompt)
   return value;

def get_option(ini,section,option,default):
   if ini.has_option(section,option):
      value = eval(ini.get(section,option))
   elif ini.has_option(pyini.DEFAULTSECT,option):
      value = eval(ini.get(pyini.DEFAULTSECT,option))
   elif ini.defaults().has_key(option):
      value = eval(ini.defaults()[option])
   else:
      value = default
   return value;


def prompt_for_arguments(f):
   argnames=[f.func_code.co_varnames[i] for i in range(f.func_code.co_argcount)]
   required_argcount = f.func_code.co_argcount - len(f.func_defaults)
   argvalues=[]
   for i in range(f.func_code.co_argcount):
      if i<required_argcount:
         argvalues.append(input("please enter \"" + argnames[i] + "\">"))
      else:
         value = raw_input("please enter \"" + argnames[i] + "\" (default value:" + repr(f.func_defaults[i-required_argcount]) +")>")
         if value=="":
            value = f.func_defaults[i-required_argcount]
         else:
            value = eval(value)
         argvalues.append(value)
   return argvalues

def prompt_for_argument_lists(f,ini,section):
   argnames=[f.func_name + "." + f.func_code.co_varnames[i] for i in range(f.func_code.co_argcount)]
   required_argcount = f.func_code.co_argcount - len(f.func_defaults)
   argvalues = []
   docdisplayed = False
   for i in range(f.func_code.co_argcount):
      if i<required_argcount:
         if (not docdisplayed) and (not has_option(ini,section,argnames[i])):
            docdisplayed=True
            print f.__doc__
         argvalues.append(prompt_for_option(ini,section,argnames[i],"please list the values of \"" + argnames[i] + ":"))
      else:
         if docdisplayed:
            value = prompt_for_raw_option(ini,section,argnames[i],"please list the values of \"" + argnames[i] + "\" (default [" + str(f.func_defaults[i-required_argcount]) + "]):")
            if value=="":
               value = [f.func_defaults[i-required_argcount]]
            else:
               value = eval(value)
            argvalues.append(value)
         else:
            argvalues.append(get_option(ini,section,argnames[i],[f.func_defaults[i-required_argcount]]))
   return argvalues


def network_generator(model,args_lists,repetitions):
   for args in args_lists:
      for i in range(repetitions):
         G = model(*args)
         G = GraphAsMatrix(G)
         yield model.func_name,representation.getPajekRepr(G,base=0),model.func_name,args


def stored_graphs(graphnameprefix,path_to_graph_files):
   graphFiles = os.listdir(path_to_graph_files)
   graphFiles = filter(lambda x:x.startswith(graphnameprefix),graphFiles)
   for f in graphFiles:
      yield f,"",graphnameprefix,f
   pass

def empty_generator():
   if False:
      yield None
   pass


def cp(l):return reduce(lambda x,y:[l+[e] for e in y for l in x],[[[]]]+l)








#####################################################################
## START


ini=pyini.ConfigParser()

hasini = False
if len(sys.argv)>=2:
   if len(sys.argv[1])>0:
      hasini=True
      ini.read(sys.argv[1])


sections = ini.sections()
if len(sections)==0:
   sections = [pyini.DEFAULTSECT]
for section in sections:

   is_from_file = prompt_for_option(ini,section,"is_from_file","Use exiting network files [0 - no,  1 - yes]?")


   net_gen = empty_generator()

   if is_from_file:
      graph_name_prefix = prompt_for_raw_option(ini,section,"graph_name_prefix","Enter network name prefix (not a path):")
      path_to_graph_files = prompt_for_raw_option(ini,section,"path_to_graph_files","Please enter correct path")
      net_gen = stored_graphs(graph_name_prefix,path_to_graph_files)
   else:
      models = [random_powerlaw_tree,
                barabasi_albert_graph,
                powerlaw_cluster_graph,
                gnp_random_graph,
                gnm_random_graph,
                watts_strogatz_graph,
                newman_watts_strogatz_graph,
                random_regular_graph,
                random_lobster,
                random_shell_graph,
                ]
      modelnames = [f.func_name for f in models]
      model = prompt_for_option(ini,section,"model","Please enter graph model " + str(modelnames) + "\n>")
      model_arg_lists = prompt_for_argument_lists(model,ini,section)
      model_arg_lists = cp(model_arg_lists)

      net_r = prompt_for_option(ini,section,"network_repeats","Number of networks for each argument set:")
      net_gen = network_generator(model,model_arg_lists,net_r)

   serveruri = get_option(ini,section,"xmlrpc_server_uri","http://localhost:8080/")
   server=ServerProxy(serveruri)



   fieldnames = "graphID", "n", "m", "d", "model", "modelArgs", "alg", "time", "memory", "numberOfComponents", "numberOfComponentLinks", "avgComponentNodes", "avgComponentLinks", "maxComponentLinks", "maxComponentNodes", "theoreticRT",
   resultfileprefix=get_option(ini,section,"output_file_prefix",str(section))
   resultf = csv.DictWriter(file("experiment_result/"+resultfileprefix + "_%d.csv"%time.time(),"w"),fieldnames,"excel")
   resultf.writerow(dict(zip(fieldnames,fieldnames)))

   stdout = csv.DictWriter(sys.stdout,fieldnames,"excel-tab")
   stdout.writerow(dict(zip(fieldnames,fieldnames)))


   stats = {}

   for netFile, netContent, model, modelArgs in net_gen:
      stats["graphID"] = time.time()
      stats["model"] = model
      stats["modelArgs"] = modelArgs

      n_id = server.Network.importNetwork(netFile, netContent)

      if n_id != -1:

         n = server.Network.getNumberOfVertices(n_id);
         m = server.Network.getNumberOfEdges(n_id);

         if n>0:
            d = 2.0*m/n
            stats["n"] = n
            stats["m"] = m
            stats["d"] = d


            #################################################################
            ## 1)  BC --- Brandes algorithm for BC
            T = time.time()
            a_id = withretry(server.Brandes.create)(n_id)
            T = time.time() - T
            #bc_result = sorted(list(withretry(server.Brandes.getBetweenness)(a_id)))
            stats["alg"] = "BC"
            stats["time"] = T
            stats["memory"] = withretry(server.Server.getMemoryConsumption)()
            stats["numberOfComponents"] = ""
            stats["numberOfComponentLinks"] = ""
            stats["avgComponentNodes"] = ""
            stats["avgComponentLinks"] = ""
            stats["maxComponentNodes"] = ""
            stats["maxComponentLinks"] = ""
            stats["theoreticRT"] = n * m
            resultf.writerow(stats)
            stdout.writerow(stats)

            withretry(server.Brandes.destroy)(a_id)
            #print bc_result



            #################################################################
            ## 7)  UEBCC+BC(TM) --- Partition the graph to Bi-Connetect Components and run BC for each component
            ## uses EAGER BCC algorithm with default BCCalculator
            T = time.time()
            a_id = withretry(server.BCC.create)(n_id)
            T = time.time() - T
            #bc_result = sorted(list(withretry(server.BCC.getBetweenness)(a_id)))

            bccnet_ids = server.BCC.createNetworksFromComponents(a_id)
            bccvertexcounts = []
            bccedgecounts = []
            theoreticRT = 0
            for bccnet_id in bccnet_ids:
               ni = withretry(server.Network.getNumberOfVertices)(bccnet_id)
               mi = withretry(server.Network.getNumberOfEdges)(bccnet_id)
               bccvertexcounts.append(ni)
               bccedgecounts.append(mi)
               theoreticRT+=ni*mi

            stats["alg"] = "BCCBC"
            stats["time"] = T
            stats["memory"] = withretry(server.Server.getMemoryConsumption)()
            stats["numberOfComponents"] = len(bccvertexcounts)
            stats["numberOfComponentLinks"] = len(bccvertexcounts)-1 ##component tree is a tree
            stats["avgComponentNodes"] = 1.0 * sum(bccvertexcounts) / len(bccvertexcounts)
            stats["avgComponentLinks"] = 1.0 * sum(bccedgecounts) / len(bccedgecounts)
            stats["maxComponentNodes"] = max(bccvertexcounts)
            stats["maxComponentLinks"] = max(bccedgecounts)
            stats["theoreticRT"] = theoreticRT
            resultf.writerow(stats)
            stdout.writerow(stats)

            withretry(server.BCC.destroy)(a_id)

            for bccnet_id in bccnet_ids:
               withretry(server.Network.destroy)(bccnet_id)
            #print bc_result



            ##################################################################
            ### 4)  SE+BC(TM) --- Unify Stracturally Equvalent vertices before running BC
            TSE = time.time()
            algSE_id = server.SE.create(n_id)
            utm_id = server.SE.createUnifiedCW(algSE_id)
            unet_id = server.SE.createUnifiedNetwork(algSE_id)
            TSE = time.time() - TSE

            TBC = time.time()
            algBC_id   = server.Brandes.create(unet_id,utm_id)
            TBC = time.time() - TBC

            #unifiedBC = server.Brandes.getBetweenness(algBC_id)
            #bc_result = range(G.getNumberOfVertices())
            #for i in range(len(equivClasses)):
               #for v in equivClasses[i]:
                  #bc_result[v] = unifiedBC[i]/len(equivClasses[i])
            #bc_result=sorted(list(bc_result))
            equivClasses = server.SE.getEquivalenceClasses(algSE_id)

            stats["alg"] = "SEBC"
            stats["time"] = TSE + TBC
            stats["memory"] = withretry(server.Server.getMemoryConsumption)()
            stats["numberOfComponents"] = server.Network.getNumberOfVertices(unet_id);
            stats["numberOfComponentLinks"] = server.Network.getNumberOfEdges(unet_id);
            stats["avgComponentNodes"] = 1.0 * n / len(equivClasses)
            stats["avgComponentLinks"] = 0
            stats["maxComponentNodes"] = max([len(ec) for ec in equivClasses])
            stats["maxComponentLinks"] = 0
            stats["theoreticRT"] = stats["numberOfComponents"] * stats["numberOfComponentLinks"]
            resultf.writerow(stats)
            stdout.writerow(stats)

            server.Brandes.destroy(algBC_id)
            ##unified network, tm, and se algorithm are destroyed in the next section

            #print bc_result

            #################################################################
            ## 10)  SE+UEBCC+BC(TM) --- Unify structurally equivalent vertices first.
            ## Then partition the unified graph to Bi-Connetect Components and run BC for each component
            ## uses EAGER BCC algorithm with default BCCalculator
            TBC = time.time()
            a_id = server.BCC.createFromSE(unet_id,utm_id)
            TBC = time.time() - TBC
            #bc_result = sorted(list(withretry(server.BCC.getBetweenness)(a_id)))

            bccnet_ids = server.BCC.createNetworksFromComponents(a_id)
            bccvertexcounts = []
            bccedgecounts = []
            theoreticRT = 0
            for bccnet_id in bccnet_ids:
               ni = withretry(server.Network.getNumberOfVertices)(bccnet_id)
               mi = withretry(server.Network.getNumberOfEdges)(bccnet_id)
               bccvertexcounts.append(ni)
               bccedgecounts.append(mi)
               theoreticRT+=ni*mi

            stats["alg"] = "SEBCCBC"
            stats["time"] = TSE+TBC
            stats["memory"] = withretry(server.Server.getMemoryConsumption)()
            stats["numberOfComponents"] = len(bccvertexcounts)
            stats["numberOfComponentLinks"] = len(bccvertexcounts)-1 ##component tree is a tree
            stats["avgComponentNodes"] = 1.0 * sum(bccvertexcounts) / len(bccvertexcounts)
            stats["avgComponentLinks"] = 1.0 * sum(bccedgecounts) / len(bccedgecounts)
            stats["maxComponentNodes"] = max(bccvertexcounts)
            stats["maxComponentLinks"] = max(bccedgecounts)
            stats["theoreticRT"] = theoreticRT
            resultf.writerow(stats)
            stdout.writerow(stats)

            withretry(server.BCC.destroy)(a_id)
            for bccnet_id in bccnet_ids:
               withretry(server.Network.destroy)(bccnet_id)

            server.SE.destroy(algSE_id)
            server.Network.destroy(unet_id)
            server.TM.destroy(utm_id)

            #print bc_result

         withretry(server.Network.destroy)(n_id)

