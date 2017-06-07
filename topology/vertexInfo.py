import random

class VertexInfo(object):

    def __init__(self,label='',properties={}):
        self.properties = properties
        self._label = label

    def setProperty(self,key,value):
        self.properties[key] = value

    def getProperty(self,key):
        return self.properties[key]

    def setLabel(self,label):
        self._label = label

    def getLabel(self):
        return self._label

    def setX(self,x):
        self._x = x
    def getX(self):
        if("_x" in dir(self)):
            return self._x
        else:
            return random.random()*0.999
    def setY(self,y):
        self._y = y
    def getY(self):
        if("_y" in dir(self)):
            return self._y
        else:
            return random.random()*0.999
    def setZ(self,z):
        self._z = z
    def getZ(self):
        if("_z" in dir(self)):
            return self._z
        else:
            return random.random()*0.999
