import scipy.signal
import numpy as np
import math
import random
from Clock import Clock
import Settings


class WaveGenerator:
    clock = None
    nrWaves = 0


    depth = 10


    resolution = 0
    X = None
    Y = None

    waveParameters = None

    def __init__(self,size, clock):
        self.clock = clock

        lengthX, lengthY = size[0], size[1]


        self.depth = Settings.waterDepth
        self.nrWaves = Settings.nrWaves


        self.setCoordinates(lengthX, lengthY)
        self.setWaveParameters(sample = 'random')


    def setCoordinates(self, lengthX, lengthY):
        X =  np.linspace(0,lengthX-1,lengthX)
        Y = -np.linspace(0,lengthY-1,lengthY)
        self.X,self.Y = np.meshgrid(X,Y)


    def normalizeAmplitudes(self, waveParameters):
        a = random.uniform(9,12)
        t = np.linspace(0,10000*math.pi,1000000)
        signal = 0

        for i in range(len(waveParameters)):
            wave = waveParameters[i]
            signal = signal + wave['amplitude']*np.sin((2*math.pi*wave['frequency'])*t + 2*math.pi*random.random())

        scale = (a/math.sqrt(2))/np.sqrt(np.mean(signal**2))

        for i in range(len(waveParameters)):
            waveParameters[i]['amplitude'] = waveParameters[i]['amplitude']*scale




    def setWaveParameters(self,sample = 'custom'):

        if(sample == 'custom'):
            wave1 = {'amplitude':18,'waveLen':200,'frequency':1,'theta': math.pi/3,'phi':0}
            waveParameters = [wave1]
        else:
            waveParameters = []
            if(sample=='random'):
                for i in range(self.nrWaves):
                    wave = self.getRandomWave()
                    waveParameters.append(wave)
                    #print(wave['amplitude'] , wave['theta'])
                self.normalizeAmplitudes(waveParameters)

            else:
                if(sample=='noisyUCW'):
                    pass



        self.waveParameters = waveParameters

    def getRandomWave(self):
        A = random.uniform(0,1)
        lam = random.uniform(125,200)
        frequency = random.uniform(2,3.5)
        dire = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        waveParameters = {'amplitude': A, 'waveLen': lam, 'frequency': frequency, 'theta': dire, 'phi': phi}
        return waveParameters


    def getSurfaceAndNormals(self):
        time = self.clock.read()
        surface = self.getSurface(time)
        normals = self.getSurfaceNormals(time)

        return surface, normals



    def getSurface(self,t):
        Z = 0
        for w in range(self.nrWaves):
            Z = Z + self.getWaveSurface(w,t)

        surface = self.depth + Z

        return surface


    def getWaveSurface(self, idx, t):
        X,Y = self.X,self.Y
        A, kx, ky, w, phi = self.getNthWaveParameters(idx)
        Z = A * np.sin(kx * X + ky *Y - w*t + phi)
        return Z

    def getSurfaceNormals(self,t):
        N = 0
        for n in range(self.nrWaves):
            N = N + self.getWaveSurfaceNormals(n,t)

        norm = np.linalg.norm(N,axis=2)
        N = np.divide(N,norm[:,:,None])

        return N


    def getWaveSurfaceNormals(self, idx, t):
        X, Y = self.X, self.Y
        A, kx, ky, w, phi = self.getNthWaveParameters(idx)

        N = -np.ones((X.shape[0], X.shape[1],3))

        N[:,:,0] = A * kx * np.cos(kx * X + ky*Y - w*t + phi)
        N[:,:,1] = A * ky * np.cos(kx * X + ky*Y - w*t + phi)

        return N

    def getNthWaveParameters(self, idx):

        waveParameters = self.waveParameters[idx]

        A = waveParameters['amplitude']
        lam = waveParameters['waveLen']
        theta = waveParameters['theta']
        kx,ky = (2 * math.pi/lam)* math.cos(theta), (2 * math.pi/lam)*math.sin(theta)
        phi = waveParameters['phi']
        w = 2*math.pi * waveParameters['frequency']

        return A,kx,ky,w,phi

    def getWaveParameters(self):
        return self.waveParameters.copy()



class UWDistorter:

    cameraHt = 0
    waveGenerator = None
    refIdx = 4/3

    def __init__(self, clock, cameraHt):

        self.cameraHt = cameraHt
        self.waveGenerator = WaveGenerator(Settings.sceneSize, clock)

    def getDistortions(self):
        surface, N = self.waveGenerator.getSurfaceAndNormals()
        I = self.getIncidentRays(surface)
        n = self.refIdx
        #vector eqn refration : n*r - i = -N(n*cos(r) - cos(i))
        cosI = np.sum(np.multiply(-N,I),axis=2)
        cosR = np.sqrt(1 - 1/(n**2) + np.power(cosI/n,2))

        R = n * (I + np.multiply(-N,(n * cosR - cosI)[:,:,None]))
        R = np.divide(R,(R[:,:,2])[:,:,None])

        distortionX = np.multiply(R[:,:,0] , surface)
        distortionY = np.multiply(R[:,:,1] , surface)

        return distortionX, distortionY

    def getCousticDist(self, distX, distY):
        filtSize = 7
        filt = np.ones((filtSize,filtSize))/(filtSize**2)
        meanX = scipy.signal.convolve2d(distX, filt, mode='same')
        meanY = scipy.signal.convolve2d(distY, filt, mode='same')
        
        diff = np.sqrt((distX-meanX)**2 + (distY-meanY)**2)
        diff[0:filtSize,:]=diff[512-filtSize:,:]= diff[:,0:filtSize]=diff[:,512-filtSize:]=0
        diff = (diff - np.min(diff))/(np.max(diff)-np.min(diff))
        diff = 1- diff
        return diff


    def getIncidentRays(self, surface = None):

        if(math.isinf(self.cameraHt)):
            gridSize = surface.shape
            iRays = np.zeros((gridSize[0], gridSize[1], 3))
            iRays[:,:,2] = -1
        else:
            iRays = None #implement perspective projection

        return iRays

    def reset(self):
        self.waveGenerator.setWaveParameters('random')

    def getWaveParameters(self):
        return self.waveGenerator.getWaveParameters()
