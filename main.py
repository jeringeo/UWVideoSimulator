import Settings

import numpy as np
import cv2 as opencv
import SparkTimer
import  os

from UWSceneImager import UWSceneImager
import shutil
import uuid
from multiprocessing import Process, Lock
import random
from VideoGenerator import VideoGenerator
from SparkScheduler import scheduleJobs

seed = 127
workingDir = None
metadataFol = None
maxthreads = 4
# random.seed(seed)
# np.random.seed(seed)

# flags
def getSessionID():
    sessionID = str(uuid.uuid4()).split('-')[0]
    return sessionID


inputLoc = 'Synthetic'
outputDir = '../Videos'


def createSession():
    global workingDir, metadataFol
    sessionID = getSessionID()
    workingDir = os.path.join(outputDir, sessionID)
    workingDir = workingDir.replace(" ", "")
    os.mkdir(workingDir)
    metadataFol = os.path.join(workingDir, 'metadata')
    os.mkdir(metadataFol)
    print('Session ', sessionID, ' Created')
    SparkTimer.startClock()


if __name__ == "__main__":

    createSession()

    generators = []

    if (os.path.isfile(inputLoc)):
        videoGen = VideoGenerator(inputLoc, workingDir, metadataFol)
        generators.append(videoGen)
    else:
        if(os.path.isdir(inputLoc)):
            counter = 0
            for file in os.listdir(inputLoc):
                if file.endswith(tuple([".jpg", ".png"])):
                    fileName = os.path.join(inputLoc,file)
                    videoGen = VideoGenerator(fileName, workingDir, metadataFol)
                    generators.append(videoGen)
                    counter+=1

    scheduleJobs(generators, maxthreads)

    SparkTimer.printElapsedTime('Completed')
