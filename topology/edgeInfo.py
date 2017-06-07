


class EdgeInfo(dict):
    def __init__(self, bandwidth=1, defaults={}):
        super(dict, self).__init__()
        self["bandwidth"]=bandwidth
        self.update(defaults)


    def setProperty(self,key,value):
        self[key] = value

    def getProperty(self,key):
        return self[key]

    def getBandwidth(self):
        return self["bandwidth"]

    def setBandwidth(self,value):
        self["bandwidth"] = value




