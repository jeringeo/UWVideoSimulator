import SparkHashing
import Settings
import os
import numpy as np
import cv2 as opencv
from UWSceneImager import UWSceneImager
from multiprocessing import Process
import SparkPointFeatureUtility
import subprocess

exitFlag = 0

class VideoGenerator(Process):
    sceneImager = None
    workingDir = None
    metadataFol = None
    tag = None

    def __init__(self, imageFilePath, saveLoc, metadataFol):
       Process.__init__(self)
       bgImg = opencv.imread(imageFilePath)
       self.sceneImager = UWSceneImager(bgImg)
       self.workingDir = saveLoc
       self.tag = imageFilePath.split('/')[-1].split('.')[0]
       self.metadataFol = os.path.join(metadataFol,self.tag)
       os.mkdir(self.metadataFol)

       self.name = self.tag


    def getTrackPoints(self, nrPts, clearance):
        image, _, _ = self.sceneImager.getUWImageAt(0)
        rows, cols = image.shape[0], image.shape[1]
        keyPts = SparkPointFeatureUtility.getSurfKeyPts(np.array(image * 255, dtype='uint8'))
        keyPts = np.array([(int(keyPts[i].pt[1]), int(keyPts[i].pt[0])) for i in range(len(keyPts))])
        keyPts = np.round(keyPts)

        validR = (keyPts[:, 0] >  clearance) & (rows - keyPts[:, 0] > clearance)
        validC = (keyPts[:, 1] >  clearance) & (rows - keyPts[:, 1] > clearance)
        validPts = validR & validC

        keyPts = keyPts[validPts, :]
        keyPts = keyPts[0:nrPts, :]
        return keyPts

    def getCurrentLoc(self, mapR, mapC, loc):
        dists = (mapR - loc[0]) ** 2 + (mapC - loc[1]) ** 2
        r, c = np.unravel_index(dists.argmin(), dists.shape)
        return np.array([r, c]).astype(int)

    def run(self):
        self.generateVideos()


    def generateVideos(self):

        nrFrames = Settings.nrFrames
        fps = Settings.fps
        outFile = os.path.join(self.workingDir, self.tag + '.avi')

        np.save(os.path.join(self.metadataFol, 'waveParameters'), self.sceneImager.getWaveParameters())

        frameSize = Settings.sceneSize
        mapping = np.zeros((frameSize[0], frameSize[1], 2, nrFrames),dtype='int16')

        fourcc = opencv.VideoWriter_fourcc(*'MJPG')

        videoWriter = opencv.VideoWriter(outFile, fourcc, fps, (frameSize[1], frameSize[0]))

        for frameIdx in range(nrFrames):
            distScene, mapR, mapC = self.sceneImager.getUWImageAt(frameIdx / fps)
            mapping[:, :,0, frameIdx], mapping[:, :,1, frameIdx] = np.round(mapR), np.round(mapC)
            videoWriter.write((255 * distScene).astype('uint8'))

            if Settings.randomFrames:
                self.sceneImager.reset()

        videoWriter.release()

        np.save(os.path.join(self.metadataFol, 'mapping'), mapping)

        if(Settings.convertToMP4 is True):
            mp4Name = outFile.split('.')[0] + '.mp4'
            cmd = 'ffmpeg -i ' + outFile + ' ' + mp4Name
            os.system(cmd)
            os.remove(outFile)
