import numpy as np
import scipy.misc

class SparkImageInterpolator:
    image = None
    bounds = None
    scaleR = 0
    scaleC = 0


    def __init__(self, image, bounds, originalResolution = False):

        if originalResolution is False:
            image = scipy.misc.imresize(image, bounds+1) / 255

        self.image = image
        self.bounds = bounds
        self.scaleR = (self.image.shape[0]-1)/(bounds[0])
        self.scaleC = (self.image.shape[1]-1)/(bounds[1])

    def getInterpolatedImage(self, mappingR, mappingC, image=None):
        if image is None:
            image = self.image

        mappingR = self.scaleR * mappingR
        mappingC = self.scaleC * mappingC

        T = np.floor(mappingR).astype(int)
        L = np.floor(mappingC).astype(int)
        R = L + 1
        B = T + 1
        R = R.clip(0, image.shape[0]-1)
        B = B.clip(0, image.shape[1]-1)

        wtTL = (B - mappingR) * (R - mappingC)
        wtTR = (B - mappingR) * (mappingC - L)
        wtBR = (mappingR - T) * (mappingC - L)
        wtBL = (mappingR - T) * (R - mappingC)


        imgTL =  image[T, L]
        imgTR =  image[T, R]
        imgBR =  image[B, R]
        imgBL =  image[B, L]

        interpImg = imgTL * wtTL[:, :, None] + imgTR * wtTR[:, :, None] + imgBR * wtBR[:, :, None] + imgBL * wtBL[:, :, None]
        return interpImg
