from youtupi.engine.PlaybackEngine import PlaybackEngine
import os, signal, subprocess, dbus, time, textwrap, codecs, getpass
from betterprint import pprint

SECONDS_FACTOR = 1000000
DBUS_RETRY_LIMIT = 50
TITLE_DISPLAY_SRT = "/run/shm/youtupi.srt"

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
    baseVolume = 0

    def subtitleBlock(self, id, text):
        id = max(id, 1)
        r = "\n%d\n00:00:%02d,000 --> 00:00:%02d,000\n%s\n" % (id, (id-1)*5, id*5, "\n".join(textwrap.wrap(text, 42)[:3]))
        return r

    def prepareSubtitles(self, fname, video):
        try:
            id = 1
            with codecs.open(fname, 'w', 'utf-8') as f:
                if 'title' in video.data:
                    f.write(self.subtitleBlock(id, video.data['title']))
                    id += 1
                if 'description' in video.data:
                    f.write(self.subtitleBlock(id, video.data['description']))
                    id += 1
        except Exception as e:
            pprint(e)

    def play(self, video):
        if not video.url:
            raise RuntimeError("Video URL not found")
        if self.isPlaying():
            self.stop()
        volume = self.baseVolume * 100 # OMXPlayer requires factor 100 to dB input
        playerArgs = ["omxplayer", "-b", "-o", "both", "--vol", "%d" % volume ]
        if video.data:
            self.prepareSubtitles(TITLE_DISPLAY_SRT, video)
            playerArgs.extend(("--subtitles", TITLE_DISPLAY_SRT))
        playerArgs.append(video.url)
        print "Running player: " + " ".join(playerArgs)
        self.player = subprocess.Popen(playerArgs, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)

    def stop(self):
        if self.isProcessRunning():
            try:
                self.controller().Action(dbus.Int32("15"))
            except:
		print "Failed sending stop signal"
                os.killpg(self.player.pid, signal.SIGTERM)
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

    def setBaseVolume(self, vol):
        self.baseVolume = vol

    def getBaseVolume(self):
        return self.baseVolume

    def volumeUp(self):
        self.tryToSendAction(dbus.Int32("18"))

    def volumeDown(self):
        self.tryToSendAction(dbus.Int32("17"))

    def seekBackSmall(self):
        self.tryToSendAction(dbus.Int32("19"))

    def seekForwardSmall(self):
        self.tryToSendAction(dbus.Int32("20"))

    def seekBackLarge(self):
        self.tryToSendAction(dbus.Int32("21"))

    def seekForwardLarge(self):
        self.tryToSendAction(dbus.Int32("22"))

    def prevAudioTrack(self):
        self.tryToSendAction(dbus.Int32("6"))

    def nextAudioTrack(self):
        self.tryToSendAction(dbus.Int32("7"))

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
                with open('/tmp/omxplayerdbus.'+getpass.getuser(), 'r+') as f:
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
                with open('/tmp/omxplayerdbus.'+getpass.getuser(), 'r+') as f:
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
