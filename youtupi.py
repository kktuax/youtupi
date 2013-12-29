#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json
from StringIO import StringIO
from youtupi.modules.local import module_local
from youtupi.modules.youtube import module_youtube
from youtupi.playlist import removeVideo, playNextVideo, playVideo, addVideo, controlPlayer, playList

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
		'/local', module_local,
		'/youtube', module_youtube,
		'/', 'index'
	)
	app = web.application(urls, globals())
	app.run()
