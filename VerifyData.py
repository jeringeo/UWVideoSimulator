import numpy as np
import cv2 as opencv
import random
import os


def drawTracker(frame, pt):
    frame = opencv.drawMarker(frame.astype('uint8'), (pt[1], pt[0]),
                              (0,255,0), markerType=opencv.MARKER_CROSS,
                              markerSize=36, thickness=4)
    frame = opencv.circle(frame.astype('uint8'), (pt[1], pt[0]), 6,
                          (0,0,255), thickness=4)
    return frame




patchFol = '/home/jerin/WorkingDir/Patches/SmallWaves/trainingSet/Regressor-5bd67f31'
vidIdx = str(random.randint(0,16))
vid = np.load(patchFol+'/'+vidIdx+'_Patches'+'.npy')
locs = np.load(patchFol+'/'+vidIdx+'_locs'+'.npy')

patch = random.randint(0,31)

fol = os.path.join(patchFol,str(random.randint(0,16777216)))
print(fol)
os.mkdir(fol)

for i in range(16):
    img = np.zeros((64,64,3), dtype = 'uint8')
    img[:,:,0], img[:,:,1] , img[:,:,2] = vid[patch,i,0,:,:], vid[patch,i,1,:,:] , vid[patch,i,2,:,:]
    loc = locs[patch,i,:].astype(int) + 48
    print(loc)
    img = drawTracker(img,loc)
    opencv.imwrite(fol +'/'+str(i)+'.jpg',img)
    opencv.imshow('',img); opencv.waitKey(1)



