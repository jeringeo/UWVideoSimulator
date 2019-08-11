import numpy as np
import math
from Clock import Clock
import SparkPointFeatureUtility
from UWDistorter import UWDistorter
from Scene import Scene
import Settings


class UWSceneImager:
    R = None
    C = None
    scene = None
    uwDistorter = None

    clock = None

    def __init__(self,bgImg):
        self.clock = Clock()
        self.scene = Scene(bgImg, self.clock)
        self.uwDistorter =  UWDistorter(self.clock, math.inf)
        self.setGrids(Settings.sceneSize)

    def setGrids(self, imSize):
        X = np.array(range(imSize[1]))
        Y = np.array(range(imSize[0]))
        self.C, self.R = np.meshgrid(X, Y)

    def getPixelMappings(self, distX, distY):
        mappingR = self.R - distY
        mappingC = self.C + distX

        maxR = self.R[-1][0]
        maxC = self.C[0][-1]

        mappingR[mappingR < 0] = - mappingR[mappingR < 0]
        mappingC[mappingC < 0] = - mappingC[mappingC < 0]
        mappingR[mappingR > maxR] = 2*maxR - mappingR[mappingR > maxR]
        mappingC[mappingC > maxC] = 2*maxC - mappingC[mappingC > maxC]

        return mappingR, mappingC

    def getUWImageAt(self,time, metaData = 'mapping'):

        self.clock.update(time)
        distX,distY = self.uwDistorter.getDistortions()

        #mappingR = np.clip(-(-self.R + distY), 0, self.R[-1][0]-1)
        #mappingC = np.clip(self.C + distX, 0, self.C[0][-1] - 1)

        mappingR, mappingC = self.getPixelMappings(distX, distY)
        uwScene = self.scene.imagePoints(mappingR, mappingC)

        if(Settings.coustics == True):
            coustics = self.uwDistorter.getCousticDist(distX, distY)
            uwScene = self.addCoustics(uwScene,coustics)

        if metaData is 'distortions':
            return uwScene, distX, distY
        else:
            return uwScene, mappingR, mappingC

    def addCoustics(self, img, coustics):
        sun = np.array([253, 184, 19])/255
        sun = np.array([1,1,1])
        co = np.zeros((512,512,3))
        co[:,:,0], co[:,:,1], co[:,:,2] = coustics/sun[0],coustics/sun[1],coustics/sun[2]


        base = img
        co = np.exp(-np.sqrt(1-co))
        co = co/co.min()
        img = base*co*.7
        img[img>1]=1
        #img = normalizeImg(img)
        return img

    def getWaveParameters(self):
        return self.uwDistorter.getWaveParameters()

    def reset(self):
        self.uwDistorter.reset()

def normalizeImg(img):
    img = (img - np.min(img))/(np.max(img)-np.min(img))
    return img