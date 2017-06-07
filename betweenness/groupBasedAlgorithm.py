import copy 
from dataWorkshop import DataWorkshop

class GroupBasedAlgorithm(DataWorkshop):
        """
        The only information held by the Set is the information about the
        Set itself (in addition to common DataWorkshop).
        From this info we are able to calculate Set's GBC.
        """
        def createEmptySet(self, overheadModifier=1):
            """ create empty represention of set of vertices.
            The object returned is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.

            In later versions it is expected to have all set's
            functionality and actualy extend set()
            """
            return self.Set(self,overheadModifier)
        
        class Set:
            """
            Object of this class is NOT instance of set!
            However it supports methods add() and remove()
            from python set interface.

            In later versions it is expected to have all set's
            functionality and actualy extend Set class
            """
            class SubSet:
                def __init__(self):
                    self.path = []
                    self.delta = 1.0
                def __repr__(self):
                    return "<" + repr(self.path) + ", delta=" + repr(self.delta) + ">"
                def __getitem__(self,index):
                    return self.path[index]
                

            def __init__(self, GBAlg, overheadModifier):
                from opus7.avlTree import AVLTree
                self._alg = GBAlg
                self._members = set([])
                self._subsets = set([self.SubSet()])
                #self._subsets.add(self.SubSet())
                self._GB = 0
                self._OV = 0
                self._valid = True
                self._OVModifier = overheadModifier

            def __repr__(self):
                self.getGB()
                return "GroupBetweenness" + "<" + repr(self._members) + ",%.2f,%.2f"%(self._GB,self._OV)+">"
            def __str__(self):
                return self.__repr__()
            def __iter__(self):
                return self._members.__iter__()
            def __getitem__(self,index):
                return self._members[index]
            def __len__(self):
                return len(self._members)
            def getGB(self):
                if self._valid:
                    return self._GB - self._OV * self._OVModifier
                else:
                    self.calculateGB()
                    self.calculateOverhead()
                    self._valid = True
                    return self.getGB()
            def getMembers(self):
                return self._members
            def add(self,v):
                """
                (Set, int) -> None
                """
                if v not in self._members:
                    self._valid = False
                    v_subsets = set([])
                    d = self._alg.getDistanceMatrix()
                    for s in self._subsets:
                        ns = copy.deepcopy(s)
                        k = len(ns.path)-1
                        
                        if len(ns.path) == 0:
                            ns.delta = 1.0
                            ns.path = [v]
                            v_subsets.add(ns)
                        elif d[v][ns[0]]+d[ns[0]][ns[k]]==d[v][ns[k]] :
                            ns.delta *= self._alg.getDelta(v,ns[0],ns[k])
                            ns.path[0:0] = [v]
                            v_subsets.add(ns)
                        elif d[ns[0]][v]==d[ns[0]][ns[k]]+d[ns[k]][v] :
                            ns.delta *= self._alg.getDelta(ns[0],ns[k],v)
                            ns.path[k+1:k+1] = [v]
                            v_subsets.add(ns)
                        else:
                            for i in range(k):
                                if d[ns[i]][ns[i+1]] == d[ns[i]][v] + d[v][ns[i+1]] :
                                    ns.delta *= self._alg.getDelta(ns[i],v,ns[i+1])
                                    ns.path[i+1:i+1] = [v]
                                    v_subsets.add(ns)
                                    break

                    #self._subsets.update(v_subsets)
                    self._subsets |= v_subsets
                    self._members.add(v)
                
            def remove(self,v):
                """
                (int) -> None
                """
                if v in self._members:
                    self._valid = False
                    v_subsets = set([])
                    for s in self._subsets:                    
                        if v in s.path:
                            v_subsets.add(s)
                    #self._subsets.intersection_update(v_subsets)
                    self._subsets -= v_subsets
                    self._members.remove(v)
                
            def calculateGB(self):
                GB = 0
                for s in self._subsets:
                    k = len(s.path) - 1 
                    if k==-1: ##len(s.path)==0
                        pb = 0
                    elif k==0: ##len(s.path)==1
                        pb = self._alg.getB(s[0])
                    else: ##len(s.path)>1
                        pb = self._alg.getPairBetweenness(s[0],s[k]) * s.delta
                    sign = ((k+1)%2)*2 - 1 #odd->pos even->neg
                    #print pb, "\t", s.path
                    GB += sign * pb
                self._GB=GB
                return GB
            
            def calculateOverhead(self):
                totalOverhead = 0
                for s in self._subsets:
                    k = len(s.path)-1
                    sOverhead = 0
                    doubleOverhead = 0
                    if k>=0 :
                        for u in self._members - set(s.path):
                            sOverhead += s.delta * self._alg.getDelta(u,s[0],s[k]) * self._alg.getDelta(u,s[k])                            
                            sOverhead += s.delta * self._alg.getDelta(u,s[k],s[0]) * self._alg.getDelta(u,s[0])
                            for v in self._members - set(s.path):
                                doubleOverhead += s.delta * self._alg.getDelta(u,s[0],s[k]) * self._alg.getDelta(u,s[k],v)
                    if k==0 :
                        sOverhead /= 2
                        doubleOverhead /= 2
                    sign = ((k+1)%2)*2 - 1 #odd->pos even->neg
                    totalOverhead += sign * (sOverhead - doubleOverhead)
                    #print sOverhead-doubleOverhead, "\t", s.path
                self._OV = totalOverhead
                return totalOverhead
