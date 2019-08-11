


class Clock:
    currentTime = 0

    def __init__(self):
        self.currentTime = 0

    def update(self,time):
        global currentTime
        currentTime= time

    def read(self):
        return currentTime