#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json
from StringIO import StringIO
from youtupi.video import createVideo
from youtupi.modules import local, youtube
from youtupi.playlist import autoPlay, removeVideo, playNextVideo, playVideo, addVideo, controlPlayer, playList

class redirect:
	def GET(self, path):
		web.seeother('/' + path)

class index:
	def GET(self):
		web.seeother('/static/index.html')

class playlist:
	def GET(self):
		autoPlay()
		playlistVideos = list()
		for video in playList():
			playlistVideos.append(video.data)
		return json.dumps(playlistVideos, indent=4)
	
	def POST(self):
		data = json.load(StringIO(web.data()))
		video = createVideo(data)
		addVideo(video)
		web.seeother('/playlist')
		
	def DELETE(self):
		data = json.load(StringIO(web.data()))
		removeVideo(data['id'])
		web.seeother('/playlist')

class control:
	
	def GET(self, action):
		if action == "play":
			playNextVideo()
		else:			
			controlPlayer(action)
		web.seeother('/playlist')
		
	def POST(self, action):
		if action == "play":
			data = json.load(StringIO(web.data()))
			playVideo(data['id'])
		web.seeother('/playlist')

if __name__ == "__main__":
	urls = (
		'/(.*)/', 'redirect',
		'/playlist', 'playlist',
		'/video/(.*)', 'video',
		'/control/(.*)', 'control',
		'/local', local.module_local,
		'/youtube-dl', youtube.module_youtube,
		'/', 'index'
	)
	app = web.application(urls, globals())
	app.run()
