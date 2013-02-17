#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, signal, sys, subprocess, threading
import web
import json
from StringIO import StringIO

player = None
videos = list()
lock = threading.RLock()

class Video:
	def __init__(self, vid, data, url):
		self.vid = vid
		self.data = data
		self.url = url
		self.played = False

def addVideo(data):
	if(data['type'] == "youtube"):
		if(data['format'] == "default"):
			url = getYoutubeUrl(data['id'])
		else:
			url = getYoutubeUrl(data['id'], data['format'])
		video = Video(data['id'], data, url)
		videos.append(video)

def removeOldVideosFromPlaylist():
	viewedVideos = filter(lambda video:video.played==True, videos)
	if isProcessRunning(player):
		oldVideos = viewedVideos[1:]
	else:
		oldVideos = viewedVideos
	for vv in oldVideos:
		videos.remove(vv)

def removeVideoFromPlaylist(vid):
	global videos
	videos = filter(lambda video:video.vid!=vid, videos)

def playNextVideo():
	with lock:
		global player
		if isProcessRunning(player):
			os.killpg(player.pid, signal.SIGTERM)
		for video in videos:
			if not video.played:
				player = subprocess.Popen(['omxplayer', '-ohdmi', video.url], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
				video.played = True
				break

def autoPlay():
	removeOldVideosFromPlaylist()
	if (not isProcessRunning(player)) and (len(videos) > 0):
		playNextVideo()

def isProcessRunning(process):
	if process:
		if process.poll() == None:
			return True
	return False

def getYoutubeUrl(video, vformat = None):
	url = "http://www.youtube.com/watch?v=" + video
	if not vformat: 
		args = ['youtube-dl', '-g', url]
	else:
		args = ['youtube-dl', '-f', vformat, '-g', url]
	yt_dl = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	(url, err) = yt_dl.communicate()
	if yt_dl.returncode != 0:
		if vformat != None:
			return getYoutubeUrl(video, None)
		else:
			sys.stderr.write(err)
			raise RuntimeError('Error getting URL.')
	else:
		return url.decode('UTF-8').strip()

class redirect:
	def GET(self, path):
		web.seeother('/' + path)

class index:
	def GET(self):
		web.seeother('/static/youtupi.html')

class playlist:
	def GET(self):
		autoPlay()
		playlistVideos = list()
		for video in videos:
			playlistVideos.append(video.data)
		
		return json.dumps(playlistVideos, indent=4)
	
	def POST(self):
		data = json.load(StringIO(web.data()))
		addVideo(data)
		web.seeother('/playlist')
		
	def DELETE(self):
		data = json.load(StringIO(web.data()))
		removeVideoFromPlaylist(data['id'])
		web.seeother('/playlist')

class control:
	
	def GET(self, action):
		if action == "play":
			playNextVideo()
		else:
			global player
			if isProcessRunning(player):
				if action == "stop":
					player.stdin.write("q")
					player = None
					global videos
					videos = list()
				if action == "pause":
					player.stdin.write("p")
				if action == "volup":
					player.stdin.write("+")
				if action == "voldown":
					player.stdin.write("-")
				if action == "forward":
					player.stdin.write("\x1B[C")
				if action == "backward":
					player.stdin.write("\x1B[D")
		web.seeother('/playlist')
		
	def POST(self, action):
		if action == "play":
			data = json.load(StringIO(web.data()))
			svideo = None
			for video in videos:
				if video.vid == data['id']:
					svideo = video
					break
			if svideo:
				videos.remove(svideo)
				svideo.played = False
				videos.insert(0, svideo)
				playNextVideo()
		web.seeother('/playlist')

if __name__ == "__main__":
	urls = (
		'/(.*)/', 'redirect',
		'/playlist', 'playlist',
		'/control/(.*)', 'control',
		'/', 'index'
	)
	app = web.application(urls, globals())
	app.run()
