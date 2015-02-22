from youtupi.engine.PlaybackEngine import PlaybackEngine
import os, subprocess, time, dbus

TIMEOUT = 60
DBUS_RETRY_LIMIT = 600
SECONDS_FACTOR = 1000000

'''
@author: Max
'''
class OMXPlayerEngine(PlaybackEngine):
    
    '''
    OMXPlayer playback engine using DBUS interface
    '''

    def __init__(self):
        pass

    player = None
        
    def play(self, video):
        if self.isPlaying():
            self.stop()
        playerArgs = ["omxplayer", "-o", "both"]
        playerArgs.append(video.url)
        print "Running player: " + " ".join(playerArgs)
        self.player = subprocess.Popen(playerArgs, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
        cont = 0
        while not self.isPlaying():
            time.sleep(1)
            cont = cont + 1
            if cont > TIMEOUT:
                raise RuntimeError('Error playing video')
    
    def stop(self):
        if self.isPlaying():
            self.tryToSendAction(dbus.Int32("15"))
            cont = 0
            while self.isPlaying():
                time.sleep(1)
                cont = cont + 1
                if cont > TIMEOUT:
                    print 'Unable to stop player'            
        self.player = None
    
    def togglePause(self):
        self.tryToSendAction(dbus.Int32("16"))
    
    def setPosition(self, seconds):
        try:
            if self.isPlaying():
                self.omxController().SetPosition(dbus.ObjectPath("/not/used"), dbus.Int64(seconds*SECONDS_FACTOR))
        except:
            print 'Unable to set position'
    
    def getPosition(self):
        try:
            if self.isPlaying():
                return int(self.omxProps().Position())/SECONDS_FACTOR
        except:
            print 'Unable to determine position'
        return None
    
    def getDuration(self):
        try:
            if self.isPlaying():
                return int(self.omxProps().Duration())/SECONDS_FACTOR
        except:
            print 'Unable to determine duration'
        return None
    
    def volumeUp(self):
        self.tryToSendAction(dbus.Int32("18"))
    
    def volumeDown(self):
        self.tryToSendAction(dbus.Int32("17"))
    
    def isPlaying(self):
        if self.player:
            if self.player.poll() == None:
                return True
        return False
    
    def omxProps(self):
        return self.omxIface('org.freedesktop.DBus.Properties')
    
    def omxController(self):
        return self.omxIface('org.mpris.MediaPlayer2.Player')
    
    def omxIface(self, ifaceName):
        retry=0
        while True:
            try:
                with open('/tmp/omxplayerdbus', 'r+') as f:
                    omxplayerdbus = f.read().strip()
                bus = dbus.bus.BusConnection(omxplayerdbus)
                dbobject = bus.get_object('org.mpris.MediaPlayer2.omxplayer','/org/mpris/MediaPlayer2', introspect=False)
                return dbus.Interface(dbobject,ifaceName)
            except:
                retry+=1
                if retry >= DBUS_RETRY_LIMIT:
                    raise RuntimeError('Error loading player dbus interface')
    
    def tryToSendAction(self, action):
        if self.isPlaying():
            try:
                self.omxController().Action(action)
            except:
                print 'Error connecting with player'
