#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json, threading
from StringIO import StringIO
from youtupi.modules.local import module_local
from youtupi.modules.youtube import module_youtube
from youtupi.playlist import findVideoInPlaylist, removeVideo, playNextVideo, playVideo, addVideo, playlistPosition, resetPlaylist, playList
from youtupi.engine.PlaybackEngineFactory import engine
from youtupi.util import config

engineLock = threading.RLock()

class redirect:
	def GET(self, path):
		web.seeother('/' + path)

class index:
	def GET(self):
		web.seeother('/static/index.html')

class playlist:
	def GET(self):
		playlistVideos = list()
		for video in playList():
			playlistVideos.append(video.data)
		return json.dumps(playlistVideos, indent=4)
	
	def POST(self):
		data = json.load(StringIO(web.data()))
		addVideo(data)
		web.seeother('/playlist')
		
	def DELETE(self):
		data = json.load(StringIO(web.data()))
		removeVideo(data['id'])
		web.seeother('/playlist')

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
			web.seeother('/playlist')
		
	def POST(self, action):
		with engineLock:
			data = json.load(StringIO(web.data()))
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
			web.seeother('/playlist')

class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

if __name__ == "__main__":
	urls = (
		'/(.*)/', 'redirect',
		'/playlist', 'playlist',
		'/video/(.*)', 'video',
		'/control/(.*)', 'control',
		'/local', module_local,
		'/youtube', module_youtube,
		'/', 'index'
	)
	app = MyApplication(urls, globals())
	port = config.conf.get('port', 8080)
	app.run(port=port)
