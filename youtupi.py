#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json
from StringIO import StringIO
from youtupi.modules.local import module_local
from youtupi.modules.youtube import module_youtube
from youtupi.playlist import prepareVideo, findVideoInPlaylist, removeVideo, playNextVideo, playVideo, addVideo, resetPlaylist, playList
from youtupi.engine.PlaybackEngineFactory import engine

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
		if action == "play":
			data = json.load(StringIO(web.data()))
			video = findVideoInPlaylist(data['id'])
			if video:
				prepareVideo(video)
				playVideo(data['id'])
		if action == "position":
			data = json.load(StringIO(web.data()))
			engine.setPosition(int(data['seconds']))
		web.seeother('/playlist')

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
	app = web.application(urls, globals())
	app.run()
