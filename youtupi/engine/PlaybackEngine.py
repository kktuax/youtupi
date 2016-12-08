from abc import ABCMeta, abstractmethod

'''
@author: Max
'''
class PlaybackEngine(object):

    __metaclass__ = ABCMeta

    '''
    Base class for video playback engines
    '''

    @abstractmethod
    def play(self, video):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def togglePause(self):
        pass

    @abstractmethod
    def setPosition(self, seconds):
        pass

    @abstractmethod
    def getPosition(self):
        pass

    @abstractmethod
    def getDuration(self):
        pass

    @abstractmethod
    def isPlaying(self):
        pass

    @abstractmethod
    def volumeUp(self):
        pass

    @abstractmethod
    def volumeDown(self):
        pass

    @abstractmethod
    def seekBackSmall(self):
        pass

    @abstractmethod
    def seekForwardSmall(self):
        pass

    @abstractmethod
    def seekBackLarge(self):
        pass

    @abstractmethod
    def seekForwardLarge(self):
        pass

    @abstractmethod
    def prevAudioTrack(self):
        pass

    @abstractmethod
    def nextAudioTrack(self):
        pass

    @abstractmethod
    def getBaseVolume(self):
        pass

    @abstractmethod
    def setBaseVolume(self, vol):
        pass
