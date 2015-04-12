import numpy

class Colony():
    def __init__(self, mask, image, gsimage, gsrescoeff, geometry=None):
        self.mask = mask
        self.image = image
        self.gsimage = gsimage
        self.gsrescoeff = gsrescoeff
        self.geometry = geometry
        self.score = None
        
    def getScore(self):
        if self.score == None:
            self.score = self.calcScore()
        return self.score
        
    def getGeom(self):
        if self.geometry == None:
            return [-1, -1, 0]
        return self.geometry


    def calcScore(self):
        return self.maxDensity(5) # TODO not 5

    def gatherData(self, data):
        data.append(self.getScore())
        return data[-1]

    def integrate(self, x, y, r):
	
        w = self.gsimage.shape[0]
        h = self.gsimage.shape[1]
        
        s = 0.0
        n = 0
        r2 = r**2
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                currX = x + i
                currY = y + j
                if currX >= w or currX < 0 or currY >= h or currY < 0 or (i**2 + j**2) > r2:
                    continue
                else:
                    s += self.gsimage[currX][currY]
                    n += 1
        if n != 0:
            s /= n
        return s

    def maxDensity(self, r):

        retval = 255.0
        w = self.gsimage.shape[0]
        h = self.gsimage.shape[1]
        
        for i in range(-self.geometry[2], self.geometry[2]+1):
            for j in range(-self.geometry[2], self.geometry[2]+1):
                currX = self.geometry[0] + i
                currY = self.geometry[1] + j
                if currX >= w or currX < 0 or currY >= h or currY < 0:
                    continue
                else:
                    tmp = self.integrate(currX, currY, r)
                if(tmp < retval):
                    retval = tmp
        return retval
        
        
