from youtupi.engine.PlaybackEngine import PlaybackEngine
import os, signal, subprocess, time

SECONDS_SLEEP = 15

'''
@author: Max
'''
class MockEngine(PlaybackEngine):

    '''
    Mock engine for testing purposes
    '''

    player = None
    baseVolume = None

    def play(self, video):
        if self.isPlaying():
            self.stop()
        playerArgs = ["sleep", str(SECONDS_SLEEP)]
        print "Running player: " + " ".join(playerArgs)
        self.player = subprocess.Popen(playerArgs, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
        cont = 0
        while not self.isPlaying():
            time.sleep(1)
            cont = cont + 1

    def stop(self):
        print 'Stop requested'
        if self.isPlaying():
            os.killpg(self.player.pid, signal.SIGTERM)
        self.player = None

    def togglePause(self):
        print 'Toggle pause requested'

    def setPosition(self, seconds):
        print 'Requested position ' + str(seconds)

    def getPosition(self):
        return None

    def getDuration(self):
        if self.isPlaying():
            return SECONDS_SLEEP
        return None

    def setBaseVolume(self, vol):
        self.baseVolume = vol

    def getBaseVolume(self):
        return self.baseVolume

    def volumeUp(self):
        print 'Volume up requested'

    def volumeDown(self):
        print 'Volume down requested'

    def seekBackSmall(self):
        print 'seekBackSmall requested'

    def seekForwardSmall(self):
        print 'seekForwardSmall requested'

    def seekBackLarge(self):
        print 'seekBackLarge requested'

    def seekForwardLarge(self):
        print 'seekForwardLarge requested'

    def prevAudioTrack(self):
        print 'Previous Audio Track requested'

    def nextAudioTrack(self):
        print 'Next Audio Track requested'

    def isPlaying(self):
        if self.player:
            if self.player.poll() == None:
                return True
        return False
