from __future__ import division
import cv2 as opencv



def getSiftFeatures(img):
    getSiftFeatures.siftUtility = opencv.SIFT()
    keyPts,des = getSiftFeatures.siftUtility.detectAndCompute(img, None)
    return keyPts,des

def getSurfFeatures(img):
    getSurfFeatures.surfUtility = opencv.xfeatures2d.SURF_create()
    keyPts, des = getSurfFeatures.surfUtility.detectAndCompute(img, None)
    return keyPts, des

def getSurfKeyPts(img):
    getSurfFeatures.surfUtility = opencv.xfeatures2d.SURF_create()
    keyPts = getSurfFeatures.surfUtility.detect(img, None)
    return keyPts