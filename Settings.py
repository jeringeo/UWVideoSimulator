
import os
import  sys



import uuid
import numpy as np
import os
import datetime


coustics = False
resolution = 1

randomFrames = False

nrFrames = 101
fps = 50

waterDepth = 25
nrWaves = 2
maxMovObjs = 0

movingObjectImg = 'MovingObjectPatterns/3.jpg'

sceneSize = np.array([512,512], dtype=int)

convertToMP4 = False
#GT points
boundaryClearance = 32
nrTrajectories = 128

def getRecordingTime():
    return int(nrFrames/fps)

