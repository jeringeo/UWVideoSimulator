import threading
import time
import datetime
import numpy as np


def getNrActiveJobs(jobs):
    nrActive = 0

    for job in jobs:
        if job.is_alive():
            nrActive+=1
    return nrActive


def scheduleJobs(jobs, maxThreads):

    waitList = list(jobs)
    nrActiveJobs = 0

    while True:

        nrSlots = min(maxThreads - nrActiveJobs,len(waitList))

        for p in range(nrSlots):
            waitList[0].start()
            print(datetime.datetime.now().time().strftime("%H:%M:%S"), ' Scheduled ', waitList[0].name)
            waitList.pop(0)

        nrActiveJobs = getNrActiveJobs(jobs)
        if(nrActiveJobs is 0):
            break




