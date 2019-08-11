from scipy.interpolate import interp1d, RectBivariateSpline as twoDInterp
import numpy as np
import random
import math
from Clock import Clock
import cv2 as opencv
import Settings
from SparkImageInterpolator import SparkImageInterpolator

class RandomPath:

    Rt = None
    Ct = None
    VMin, VMax = 5,50

    def __init__(self, motionBounds, clearance, duration):

        self.VMax = math.sqrt(motionBounds[0]**2 + motionBounds[1]**2)/duration
        support = 2
        rows, rTime = self.getBounded1DPath(clearance, motionBounds[0] - clearance, support, duration)
        cols, cTime = self.getBounded1DPath(clearance, motionBounds[1] - clearance, support, duration)
        self.Rt = interp1d(rTime,rows, kind='linear')
        self.Ct = interp1d(cTime,cols, kind='linear')

    def getBounded1DPath(self,lower,upper, support, duration):

        path = np.random.uniform(lower,upper,support)
        dists = np.cumsum(np.abs(path[1:] - path[0:-1]))
        time  = np.append([0],duration * dists/dists[-1])

        return path, time

    def getLocation(self,time):

        r = int(self.Rt(time))
        c = int(self.Ct(time))

        return r,c


class MovingObject:
    clock = None
    path = None
    length = 0
    checkLen = 0
    img = None
    centreR, centreC = 0,0
    mask = None



    def __init__(self, length, motionBounds, margin, duration, clock):
        self.clock = clock
        self.path = RandomPath(motionBounds, margin, duration)
        self.length = 2*(length//2)
        #self.setCheckerBoardAppearence()
        self.setAppearenceFromImg(Settings.movingObjectImg)
        self.setMask(length)

    def setCheckerBoardAppearence(self):
        img = np.zeros((self.length, self.length, 3))

        X = np.array(range(self.length))
        Y = np.array(range(self.length))
        C, R = np.meshgrid(X, Y)
        self.checkLen = self.length//2

        C = C//self.checkLen
        R = R//self.checkLen

        whites = (C%2)==(R%2)
        img[whites,:] = 255

        self.img = img

    def setAppearenceFromImg(self, imgFile):
        img = opencv.imread(imgFile)
        img = opencv.resize(img,(self.length,self.length))
        self.img = img/255

    def setMask(self,len):
        rad = len//2
        axis = np.arange(0,len)-rad
        x,y = np.meshgrid(axis,axis)

        self.mask = (x**2 + y**2)<rad**2


    def getAppearance(self):
        return self.img, self.mask

    def getBounds(self):
        time = self.clock.read()
        centreR, centreC = self.path.getLocation(time)
        rT = centreR - self.length/2
        rB = centreR + self.length/2

        cL = centreC - self.length/2
        cR = centreC + self.length/2

        return int(rT), int(cL), int(rB), int(cR)


class Scene:
    clock = None
    randomPath = None

    bgScene = None


    def __init__(self, image, clock):
        self.clock = clock
        nrMovObjs = Settings.maxMovObjs
        motionTime = Settings.getRecordingTime()
        objLen = 50
        self.updateBackgroundScene(image/255, Settings.sceneSize-1)
        self.movingObjects = [MovingObject(objLen,image.shape,objLen+5, motionTime, self.clock) for _ in range(nrMovObjs)]

    def updateBackgroundScene(self, bgImg, outShape):
        self.bgScene = SparkImageInterpolator(bgImg, outShape, originalResolution = False)

    def paintObject(self, MovingObj, scene):
        rT, cL, rB, cR = MovingObj.getBounds()
        paintReg = scene[rT:rB,cL:cR,:]

        movImg, mask = MovingObj.getAppearance()
        paintReg[mask] = movImg[mask]
        scene[rT:rB, cL:cR, :] = paintReg


    def imagePoints(self, mapR, mapC):
        image = self.bgScene.image.copy()       

        for object in self.movingObjects:
            self.paintObject(object, image)
        
        image = self.bgScene.getInterpolatedImage(mapR, mapC, image)
        return image









        
