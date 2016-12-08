import web, threading, json
from StringIO import StringIO
from youtupi.engine.PlaybackEngineFactory import engine
from youtupi.playlist import findVideoInPlaylist, playNextVideo, playVideo, playlistPosition, resetPlaylist

engineLock = threading.RLock()

class control:

	def GET(self, action):
		with engineLock:
			if action == "play":
				playNextVideo()
			elif action == "stop":
				engine.stop()
				resetPlaylist()
			elif action == "pause":
				engine.togglePause()
			elif action == "volup":
				engine.volumeUp()
			elif action == "voldown":
				engine.volumeDown()
			elif action == "seekbacksmall":
				engine.seekBackSmall()
			elif action == "seekforwardsmall":
				engine.seekForwardSmall()
			elif action == "seekbacklarge":
				engine.seekBackLarge()
			elif action == "seekforwardlarge":
				engine.seekForwardLarge()
			elif action == "prevaudiotrack":
				engine.prevAudioTrack()
			elif action == "nextaudiotrack":
				engine.nextAudioTrack()

	def POST(self, action):
		with engineLock:
			data = json.load(StringIO(web.data()))
			if action == "volume":
				print "setting volume to " + data['volume']
				volume = int(data['volume'])
				engine.setBaseVolume(volume)
			if action == "play":
				video = findVideoInPlaylist(data['id'])
				if video:
					playVideo(data['id'])
			if action == "playNext":
				video = findVideoInPlaylist(data['id'])
				if video:
					playlistPosition(data['id'], 2)
			if action == "order":
				video = findVideoInPlaylist(data['id'])
				if video:
					playlistPosition(data['id'], data['order'])
			if action == "position":
				engine.setPosition(int(data['seconds']))

urls = (
	'/(.*)', 'control',
)

module_control = web.application(urls, locals())
