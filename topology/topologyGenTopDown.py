from topology.graphBuilder import *
from vertexInfo import VertexInfo
from edgeInfo import EdgeInfo
from topology.graph import GraphAsMatrix
import copy


class RouterLevelNSP(TopologyModel):
    def __init__(self,G):
        TopologyModel.__init__(self,G)
    
    def generateNSP(self,NSPName,
                    centralPoPCount,
                    regionalPoPCount,
                    lerCount,
                    customerCount,
                    vipCustomerCount,
                    pMuiltihomedCustomers,
                    pInterconnectedCustomers,
                    CoreBD=4,
                    EdgeBD=1,
                    AccessBD=1,
                    withGadgets=False):
    
        vinfo = VertexInfo()
        einfo = EdgeInfo()
        model1 = BAModel(self._G)
        model1.setVertexInfoGenerator(lambda: copy.deepcopy(vinfo))
        model1.setEdgeInfoGenerator(lambda: copy.deepcopy(einfo))
        model2 = LayeredModel(self._G)
        model2.setVertexInfoGenerator(lambda: copy.deepcopy(vinfo))
        model2.setEdgeInfoGenerator(lambda: copy.deepcopy(einfo))
        
        vinfo.setProperty("NSP",NSPName)
        if NSPName=='DT':
            vinfo.setProperty("AllowDeployment",True)
            einfo.setProperty("AllowDeployment",True)
        else:
            vinfo.setProperty("AllowDeployment",False)
            einfo.setProperty("AllowDeployment",False)            
    
        #inner core level LSR-1
        print "first core layer..."
        vinfo.setProperty("RC","core")
        vinfo.setProperty("Computers",0.0)
        vinfo.setLabel(NSPName)
        einfo.setBandwidth(CoreBD)
        if withGadgets:
            einfo.setProperty("c","Maroon")
        lsr1Routers = model1.generateClique(3)
        for i in range(3,centralPoPCount):
            lsr1Routers.append(model1.generateVertex())
        #lsr1Routers = map(lambda x: x.getNumber(),G.getVertices())
    
    
        #outer core level LSR-2
        print "second core layer..."
        if withGadgets:
            einfo.setProperty("c","RedOrange")
        lsr2Routers = model2.duplicateLayerWithSourceLinkOnly(lsr1Routers)
    
        #outer core level LSR-3
        print "third core layer..."
        if withGadgets:
            einfo.setProperty("c","Orange")
        lsr3Routers = set(model2.duplicateLayerWithSourceLinkOnly(lsr2Routers))
        lsr3Routers |= set(model2.addLayerWithUniformConnectivity(lsr2Routers,regionalPoPCount,lambda:1))
        lsr3Routers = list(lsr3Routers)
    
    
        #edge interface level LER
        print "edge layer..."
        vinfo.setProperty("RC","edge")
        vinfo.setProperty("Computers",0.0)
        vinfo.setLabel(NSPName)
        einfo.setBandwidth(EdgeBD)
        if withGadgets:
            einfo.setProperty("c","OliveGreen")
        lerRouters = model2.addLayerWithUniformConnectivity(lsr3Routers,lerCount,lambda:1)
    
    
        #customer lever
        print "access layer..."
        vinfo.setProperty("RC","access")
        vinfo.setProperty("Computers",1.0)
        vinfo.setLabel(NSPName)
        einfo.setBandwidth(AccessBD)
        if withGadgets:
            einfo.setProperty("c","Green")
        #customerInterface = random.sample(lerRouters,len(lerRouters)/4)
        customerInterface = lerRouters
        customerRouters = model2.addLayerWithUniformConnectivity(lerRouters,customerCount,lambda:1)
        vipRouters = model2.addLayerWithUniformConnectivity(lsr2Routers,vipCustomerCount,lambda:1)
    
    
        #duplicate core for fault tollerance
        print "fault tollerance..."
        vinfo.setProperty("RC","core")
        vinfo.setProperty("Computers",0.0)
        vinfo.setLabel(NSPName)
        einfo.setBandwidth(CoreBD)
        if withGadgets:
            einfo.setProperty("c","Gray30")
        lsr1Routers+=model2.duplicateLayerWithHighInterconnection(lsr1Routers)
        lsr2Routers+=model2.duplicateLayerWithHighInterconnection(lsr2Routers)
        lsr3Routers+=model2.duplicateLayerWithHighInterconnection(lsr3Routers)
    
    
        #extra customer connectivity
        customers = vipRouters+customerRouters
        
        #inter customer
        print "extra connectivity..."
        einfo.setBandwidth(AccessBD)
        if withGadgets:
            einfo.setProperty("c","Blue")
        model2.generateRandomLinks(customers,customers,len(customers)*pMuiltihomedCustomers)
        #multihome customer 
        print "multi homed stubs..."
        einfo.setBandwidth(AccessBD)
        if withGadgets:
            einfo.setProperty("c","Green")
        model2.generateRandomLinks(customers,lerRouters+lsr2Routers,len(customers)*pInterconnectedCustomers)
        
        return (lsr1Routers,lsr2Routers,lsr3Routers,lerRouters,vipRouters,customerRouters)




def CreateRouterLevelNSPTopology(NSPName,
                    centralPoPCount,
                    regionalPoPCount,
                    lerCount,
                    customerCount,
                    vipCustomerCount,
                    pMuiltihomedCustomers,
                    pInterconnectedCustomers,
                    CoreBD=4,
                    EdgeBD=1,
                    AccessBD=1,
                    withGadgets=False):
    G = GraphAsMatrix(centralPoPCount*6+regionalPoPCount*2+lerCount+customerCount+vipCustomerCount)
    model = RouterLevelNSP(G)
    model.generateNSP(NSPName, centralPoPCount, regionalPoPCount, lerCount, customerCount, vipCustomerCount, pMuiltihomedCustomers, pInterconnectedCustomers, CoreBD, EdgeBD, AccessBD, withGadgets)
    return G
    

