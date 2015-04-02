from youtupi.engine.PlaybackEngine import PlaybackEngine
import os, subprocess, dbus, time

SECONDS_FACTOR = 1000000
DBUS_RETRY_LIMIT = 50

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
	if not video.url:
		raise RuntimeError("Video URL not found")
        if self.isPlaying():
            self.stop()
        playerArgs = ["omxplayer", "-o", "both"]
        playerArgs.append(video.url)
        print "Running player: " + " ".join(playerArgs)
        self.player = subprocess.Popen(playerArgs, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
        
    def stop(self):
        self.tryToSendAction(dbus.Int32("15"))
        self.player = None
    
    def togglePause(self):
        self.tryToSendAction(dbus.Int32("16"))
    
    def setPosition(self, seconds):
        if self.isPlaying():
            try:
                self.controller().SetPosition(dbus.ObjectPath("/not/used"), dbus.Int64(seconds*SECONDS_FACTOR))
            except:
                print 'Unable to set position'
    
    def getPosition(self):
        if self.isProcessRunning():
            try:
                return int(self.props().Position())/SECONDS_FACTOR
            except:
                print 'Unable to determine position'
                return 0
        return None
    
    def getDuration(self):
        if self.isProcessRunning():
            try:
                return int(self.props().Duration())/SECONDS_FACTOR
            except:
                print 'Unable to determine duration'
        return None
    
    def volumeUp(self):
        self.tryToSendAction(dbus.Int32("18"))
    
    def volumeDown(self):
        self.tryToSendAction(dbus.Int32("17"))
    
    def isPlaying(self):
        if self.isProcessRunning():
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
    
    def tryToSendAction(self, action):
        if self.isProcessRunning():
            try:
                self.controller().Action(action)
            except:
                print 'Error connecting with player'
    
    def controller(self):
        retry=0
        while True:
            try:
                with open('/tmp/omxplayerdbus.pi', 'r+') as f:
                    omxplayerdbus = f.read().strip()
                bus = dbus.bus.BusConnection(omxplayerdbus)
                dbobject = bus.get_object('org.mpris.MediaPlayer2.omxplayer','/org/mpris/MediaPlayer2', introspect=False)
                return dbus.Interface(dbobject,'org.mpris.MediaPlayer2.Player')
            except:
                time.sleep(0.1)
                retry+=1
                if retry >= DBUS_RETRY_LIMIT:
                    raise RuntimeError('Error loading player dbus interface')
    
    def props(self):
        retry=0
        while True:
            try:
                with open('/tmp/omxplayerdbus.pi', 'r+') as f:
                    omxplayerdbus = f.read().strip()
                bus = dbus.bus.BusConnection(omxplayerdbus)
                dbobject = bus.get_object('org.mpris.MediaPlayer2.omxplayer','/org/mpris/MediaPlayer2', introspect=False)
                return dbus.Interface(dbobject,'org.freedesktop.DBus.Properties')
            except:
                time.sleep(0.1)
                retry+=1
                if retry >= DBUS_RETRY_LIMIT:
                    raise RuntimeError('Error loading player dbus interface')
    
            
    def isProcessRunning(self):
        if self.player:
            if self.player.poll() == None:
                return True
        return False
