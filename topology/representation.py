from edgeInfo import EdgeInfo
from vertexInfo import VertexInfo
import re
import string
from topology.graph import GraphAsMatrix
from graphBuilder import TopologyModel
import copy


colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]

################################################################
##  CAIDA AS links and relations
################################################################
def CAIDASVertexInfoGenerator(lines,ASNumbers,linkTypes):
    for line in lines:
        vInfo = VertexInfo()

#        i = int(vInfo_m.group('index'))
#        vInfo.setLabel(vInfo_m.group('label'))
#        vInfo.setX(float(vInfo_m.group('x')))
#        vInfo.setY(float(vInfo_m.group('y')))
#        vInfo.setZ(float(vInfo_m.group('z')))
#        for vProp_m in vProp_re.finditer(line,vInfo_m.end()):
#            if(vProp_m.group("unknown")):
#                vInfo.setProperty(vProp_m.group(1),UnknownValue(vProp_m.group(2)))
#            else:
#                vInfo.setProperty(vProp_m.group(1),eval(vProp_m.group(2)))
#        yield vInfo

def CAIDASEdgeInfoGenerator(lines):
    eInfo_re = re.compile("^\s*(?P<source>\d+)\s+(?P<dest>\d+)\s+(?P<width>\d*\.?\d*)\s*")
    eProp_re = re.compile("(\w+)\s+((?P<list>[\[].*?[\]])|(?P<float>\d*\.\d+)|(?P<int>\d+)|(?P<string>'\w*')|(?P<unknown>\w*))")
    for line in lines:
        eInfo = EdgeInfo()
        eInfo_m = eInfo_re.match(line)
        eInfo.setBandwidth(float(eInfo_m.group("width")))
        for eProp_m in eProp_re.finditer(line,eInfo_m.end()):
            if(eProp_m.group("unknown")):
                eInfo.setProperty(eProp_m.group(1),UnknownValue(eProp_m.group(2)))
            else:
                eInfo.setProperty(eProp_m.group(1),eval(eProp_m.group(2)))
        yield eInfo

#def CAIDASEdgeInfoGenerator(lines):
#    eInfo_re = re.compile("^\s*(?P<source>\d+)\s+(?P<dest>\d+)\s+(?P<width>\d*\.?\d*)\s*")
#    eProp_re = re.compile("(\w+)\s+((?P<list>[\[].*?[\]])|(?P<float>\d*\.\d+)|(?P<int>\d+)|(?P<string>'\w*')|(?P<unknown>\w*))")
#    for line in lines:
#        eInfo = EdgeInfo()
#        eInfo_m = eInfo_re.match(line)
#        eInfo.setBandwidth(float(eInfo_m.group("width")))
#        for eProp_m in eProp_re.finditer(line,eInfo_m.end()):
#            if(eProp_m.group("unknown")):
#                eInfo.setProperty(eProp_m.group(1),UnknownValue(eProp_m.group(2)))
#            else:
#                eInfo.setProperty(eProp_m.group(1),eval(eProp_m.group(2)))
#        yield eInfo

def loadCAIDASGraph(data,G=None):
    ## commented out, not clear what linkTypes is used for.
    #linkTypes = {-1:'customer-to-provider',0:peer-to-peer,1:'provider-to-customer',2:'sibling-to-sibling'}

    lines = data.splitlines()

    n=0;
    nodes = {}

    if(G==None):
        G = GraphAsMatrix(directed = True)

    for line in lines:
        assert isinstance(line,str)
        tokens = line.split()
        for token in tokens[0:2]:
            if not(nodes.has_key(token)):
                nodes[token]=n
                n+=1
        G.addVertex(nodes[tokens[0]])
        G.addVertex(nodes[tokens[1]])
        if tokens[2] == 1:
            G.addEdge(nodes[tokens[0]],nodes[tokens[1]])
        elif tokens[2] == -1:
            G.addEdge(nodes[tokens[1]],nodes[tokens[0]])
        else:
            G.addEdge(nodes[tokens[0]],nodes[tokens[1]])
            G.addEdge(nodes[tokens[1]],nodes[tokens[0]])


    ## not needed
    #model = TopologyModel(G)



    #model.setEdgeInfoGenerator(pajekEdgeInfoGenerator(lines[n+2:]).next)

    ## commented out - not working
    #for line in lines:
    #    tokens = line.split()
    #    for token in tokens[0:2]:
    #        G.addEdge(int(e_m.group("source"))-1,int(e_m.group("dest"))-1)

    return G

################################################################
##  G r a p h v i z
################################################################

def getGraphvizRepr(graph,name="qwerty",group=set([]), importance=[]):
    rslt = "graph \"" + name +"\" { "
    rslt += """
    node [
        shape = circle
        width = 0.1
        height = 0.1
        color = black
        style = filled
        fillcolor = lightgray
    ]
    edge [style=bold]
"""
    for v in graph.getVertices():
        if (v in group) or (v.getNumber() in group):
            rslt += "    " + repr(v.getNumber()) + " [shape=doublecircle]\n"
        if len(importance)>0:
            rslt += "    " + repr(v.getNumber()) + " [label=\"%d\\n%.3f\"]\n"%(v.getNumber(),importance[v.getNumber()])

    for e in graph.getEdges():
        rslt += "    " + repr(e.getV0().getNumber()) + "--" + repr(e.getV1().getNumber()) + "\n"
    rslt += "}"
    return rslt

################################################################
##  P A J E K
################################################################

class UnknownValue(object):
    def __init__(self,s):
        self._s = s
    def __str__(self):
        return self._s
    def __repr__(self):
        return self._s

def getPajekVertexRepr(vertex, base = 1):
    hasInfo = False
    rslt = " " + repr(vertex.getNumber()+base)
    w = vertex.getWeight()
    if (w != None):
        if(isinstance(w,VertexInfo)):
            rslt+=" " + repr(w.getLabel()) + ""
            rslt+=" " + "%f"%w.getX() + ""
            rslt+=" " + "%f"%w.getY() + ""
            rslt+=" " + "%f"%w.getZ() + ""
            for k in w.properties:
                rslt+= " " + k + " " + repr(w.properties[k]) + ""
    else:
        rslt+= " '' 0.0 0.0 0.0 "
    return rslt
def getPajekEdgeRepr(edge, base = 1):
    rslt = " " + repr(edge.getV0().getNumber()+base) + " " + repr(edge.getV1().getNumber()+base)
    w = edge.getWeight()
    if (w != None):
        if(isinstance(w,dict)):
            rslt += " " + repr(w["bandwidth"]) + ""
            for key in w.keys():
                rslt += "\t" + key + " " + str(w[key]) + " "
    else:
        rslt+=" 1"
    return rslt

# assumes graph nodes are indexed sequentially starting with 0
def getPajekRepr(graph, base = 1):
    rslt = "*Vertices " + repr(graph.getNumberOfVertices()) + "\n"
    for v in graph.getVertices():
        rslt += getPajekVertexRepr(v,base) + "\n"
    rslt += "*Edges \n"
    for e in graph.getEdges():
        rslt += getPajekEdgeRepr(e,base) + "\n"
    return rslt

def exportPajekRepr(graph, file_name):
    ''' Export a graph to a file in pajek formatted file '''
    out_file = file(file_name,'w')
    out_file.write("*Vertices " + repr(graph.getNumberOfVertices()) + "\n")
    for v in graph.getVertices():
        out_file.write(getPajekVertexRepr(v) + "\n")
    out_file.write("*Edges \n")
    for e in graph.getEdges():
        out_file.write(getPajekEdgeRepr(e) + "\n")
    out_file.close()

def pajekVertexInfoGenerator(lines):
    vInfo_re = re.compile("^\s*(?P<index>\d+)\s+['\"](?P<label>.*?)['\"]\s+(?P<x>\d+\.?\d*)\s+(?P<y>\d+\.?\d*)\s+(?P<z>\d+\.?\d*)")
    vProp_re = re.compile("(\w+)\s+((?P<list>[\[].*?[\]])|(?P<float>\d*\.\d+)|(?P<int>\d+)|(?P<string>'[^']*')|(?P<unknown>\w*))")
    vInfo = VertexInfo()
    for line in lines:
        vInfo_m = vInfo_re.match(line)
        if vInfo_m:
            i = int(vInfo_m.group('index'))
            vInfo.setLabel(vInfo_m.group('label'))
            vInfo.setX(float(vInfo_m.group('x')))
            vInfo.setY(float(vInfo_m.group('y')))
            vInfo.setZ(float(vInfo_m.group('z')))
            for vProp_m in vProp_re.finditer(line,vInfo_m.end()):
                if(vProp_m.group("unknown")):
                    vInfo.setProperty(vProp_m.group(1),UnknownValue(vProp_m.group(2)))
                else:
                    vInfo.setProperty(vProp_m.group(1),eval(vProp_m.group(2)))
        yield copy.deepcopy(vInfo)

def pajekEdgeInfoGenerator(lines):
    eInfo_re = re.compile("^\s*(?P<source>\d+)\s+(?P<dest>\d+)\s+(?P<width>\d*\.?\d*)\s*")
    eProp_re = re.compile("(\w+)\s+((?P<list>[\[].*?[\]])|(?P<float>\d*\.\d+)|(?P<int>\d+)|(?P<string>'[^']*')|(?P<unknown>\w*))")
    eInfo = EdgeInfo()
    for line in lines:
        eInfo_m = eInfo_re.match(line)
        if eInfo_m:
            width_str = eInfo_m.group("width")
            if len(width_str.strip())>0: # If width was set, put 1
                eInfo.setBandwidth(float(eInfo_m.group("width")))
            else:
                eInfo.setBandwidth(float(1)) # If width was set, put 1
            for eProp_m in eProp_re.finditer(line,eInfo_m.end()):
                if(eProp_m.group("unknown")):
                    eInfo.setProperty(eProp_m.group(1),UnknownValue(eProp_m.group(2)))
                else:
                    eInfo.setProperty(eProp_m.group(1),eval(eProp_m.group(2)))
        yield copy.deepcopy(eInfo)

def loadPajekGraph(data,G=None,base = 1):
    lines = data.splitlines()
    return loadPajekGraphFromLines(lines, G, base)

def loadPajekGraphFromLines(lines,G=None, base = 1):
    ''' Load a graph from a pajek formatted lines '''
    n = int(re.match("^\*Vertices\s+(\d+)",lines[0]).group(1))

    if(G==None):
        G = GraphAsMatrix()
    model = TopologyModel(G)

    model.setVertexInfoGenerator(pajekVertexInfoGenerator(lines[1:n+1]).next)
    for i in range(base,n+base,1):
        model.addVertex(i)

    assert lines[n+1].strip()=="*Edges"

    model.setEdgeInfoGenerator(pajekEdgeInfoGenerator(lines[n+2:]).next)
    e_re = re.compile("^\s*(?P<source>\d+)\s+(?P<dest>\d+)(\s+(?P<width>\d*\.?\d*))?")

    l=lines[n+2:]
    for line in l:
        e_m = e_re.match(line)
        u = int(e_m.group("source"))-base
        v = int(e_m.group("dest"))-base
        model.addEdge(u,v)

    return G



def importPajekRepr(file_name):
    ''' Import a graph from a pajek formatted file '''
    in_file = file(file_name,'r')
    G = loadPajekGraphFromLines(in_file.readlines())
    in_file.close()
    return G

graphviz = getGraphvizRepr
pajek = getPajekRepr

if(__name__=="__main__"):
    data = file("defaultnet.txt","r").readinto()
    G = loadPajekGraph(data)

