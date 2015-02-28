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
    
    def __init__(self):
        pass
        
    def play(self, video):
        if self.isPlaying():
            self.stop()
        if not self.player:
            self.player = vlc.MediaPlayer(video.url)
        else:
            self.player.set_media(vlc.Instance().media_new(video.url))
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
    
    def volumeUp(self):
        if self.player:
            curvol = self.player.audio_get_volume()
            self.player.audio_set_volume(curvol + 5)
    
    def volumeDown(self):
        if self.player:
            curvol = self.player.audio_get_volume()
            self.player.audio_set_volume(curvol - 5)
    
    def isPlaying(self):
        if self.player:
            pos = self.getPosition()
            dur = self.getDuration()
            if pos and dur:
                if pos < dur:
                    print 'Still playing (Position ' + str(pos) + ', duration ' + str(dur) + ")"
                    return True
                else:
                    print 'Finished Playing'
            else:
                return True
        return False
