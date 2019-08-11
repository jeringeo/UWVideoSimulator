import time
startTime = 0

def startClock(tag=None):
    global startTime
    if(tag!=None): print(tag)
    startTime = time.time()

def getElapsedTime(precision = 0):
	return round((time.time()-startTime), precision)

def getElapsedTimeStr(precision=0):
	time = int(getElapsedTime(precision))
	timeStr = "{:02d}:{:02d}:{:02d}".format(time//3600,(time%3600)//60,time%60)
	return timeStr

def printElapsedTime(tag = None):
    if(tag==None): tag =''
    print(tag,' ',getElapsedTime())

#add a function which gives cumulative time for a key, so that it can act as a profiler: