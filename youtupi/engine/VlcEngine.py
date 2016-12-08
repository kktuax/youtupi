from youtupi.engine.PlaybackEngine import PlaybackEngine
from vlc.generated import vlc

SECONDS_FACTOR = 1000

'''
@author: Max
'''
class VlcEngine(PlaybackEngine):

    '''
    VLC playback engine
    '''

    player = None
    baseVolume = None

    def __init__(self):
        pass

    def play(self, video):
        if not video.url:
            raise RuntimeError("Video URL not found")
        if self.isPlaying():
            self.stop()
        if not self.player:
            self.player = vlc.MediaPlayer(video.url)
        else:
            self.player.set_media(vlc.Instance().media_new(video.url))
        if self.baseVolume:
            linear = pow(10.0, self.baseVolume/20.0)
            self.player.audio_set_volume(int(100 * linear))
        self.player.play()

    def stop(self):
        if self.isPlaying():
            self.player.stop()
        self.player = None

    def togglePause(self):
        if self.player:
            self.player.pause()

    def setPosition(self, seconds):
        if self.isPlaying():
            self.player.set_time(SECONDS_FACTOR*seconds)

    def getPosition(self):
        if self.player:
            posmillis = self.player.get_time()
            if posmillis > 0:
                return posmillis/SECONDS_FACTOR
            return 0
        return None

    def getDuration(self):
        if self.player:
            durmillis = self.player.get_length()
            if durmillis > 0:
                return durmillis/SECONDS_FACTOR
        return None

    def setBaseVolume(self, vol):
        self.baseVolume = vol

    def getBaseVolume(self):
        return self.baseVolume

    def volumeUp(self):
        if self.player:
            curvol = self.player.audio_get_volume()
            self.player.audio_set_volume(min(100, curvol + 10))

    def volumeDown(self):
        if self.player:
            curvol = self.player.audio_get_volume()
            self.player.audio_set_volume(max(0, curvol - 10))

    def seekBackSmall(self):
        if self.player:
            self.setPosition(max(self.getPosition() - 30, 0))

    def seekForwardSmall(self):
        if self.player:
            self.setPosition(min(self.getPosition() + 30, self.getDuration()))

    def seekBackLarge(self):
        if self.player:
            self.setPosition(max(self.getPosition() - 600, 0))

    def seekForwardLarge(self):
        if self.player:
            self.setPosition(min(self.getPosition() + 600, self.getDuration()))

    def prevAudioTrack(self):
        if self.player:
            currentTrack = self.player.audio_get_track()
            self.player.audio_set_track(currentTrack - 1)

    def nextAudioTrack(self):
        if self.player:
            currentTrack = self.player.audio_get_track()
            self.player.audio_set_track(currentTrack + 1)

    def isPlaying(self):
        if self.player:
            pos = self.getPosition()
            dur = self.getDuration()
            if pos and dur:
                if pos < dur:
                    print 'Still playing (Position ' + str(pos) + ', duration ' + str(dur) + ")"
                    return self.player.is_playing() or ((dur - pos) > 1)
                else:
                    print 'Finished Playing'
            else:
                return True
        return False
