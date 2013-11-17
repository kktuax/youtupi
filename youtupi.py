#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal, sys, subprocess, threading, time
import os.path
from os.path import expanduser
import web
import json
from StringIO import StringIO
from youtupi.util import config, downloader
from youtupi.modules import local

player = None
videos = list()
lock = threading.RLock()

class Video:
	def __init__(self, vid, data, url):
		self.vid = vid
		self.data = data
		self.url = url
		self.played = False

def createVideo(data):
	url = data['id']
	if(data['type'] == "youtube"):
		if(data['format'] == "default"):
			url = getYoutubeUrl(data['id'])
		else:
			url = getYoutubeUrl(data['id'], data['format'])
	return Video(data['id'], data, url)

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
	
def findVideoInPlaylist(vid):
	fvideos = filter(lambda video:video.vid==vid, videos)
	if(len(fvideos)>0):
		return fvideos[0]
	else:
		return None

def playNextVideo():
	with lock:
		global player
		if isProcessRunning(player):
			os.killpg(player.pid, signal.SIGTERM)
			player = None
			removeOldVideosFromPlaylist()
		for video in videos:
			if not video.played:
				player = subprocess.Popen(['omxplayer', '-ohdmi', video.url], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
				while not isProcessRunning(player):
					time.sleep(1)
				video.played = True
				break

def ensure_dir(d):
	if not os.path.exists(d):
		os.makedirs(d)

def downloadVideo(video):
	dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
	ensure_dir(dfolder)
	if video.data['type'] == "youtube":
		dfile = os.path.join(dfolder, video.data['title'] + ".mp4")
		downloader.download(video.url, dfile)
	else:
		from periscope.periscope import Periscope
		p = Periscope(dfolder)
		p.downloadSubtitle(video.url, p.get_preferedLanguages())

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
		web.seeother('/static/index.html')

class playlist:
	def GET(self):
		autoPlay()
		playlistVideos = list()
		for video in videos:
			playlistVideos.append(video.data)
		
		return json.dumps(playlistVideos, indent=4)
	
	def POST(self):
		data = json.load(StringIO(web.data()))
		video = createVideo(data)
		videos.append(video)
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

class video:
	
	def POST(self, action):
		if action == "download":
			data = json.load(StringIO(web.data()))
			video = findVideoInPlaylist(data['id'])
			if(video == None):
				video = createVideo(data)
			downloadVideo(video)
		web.seeother('/playlist')


if __name__ == "__main__":
	urls = (
		'/(.*)/', 'redirect',
		'/playlist', 'playlist',
		'/video/(.*)', 'video',
		'/control/(.*)', 'control',
		'/local', local.module_local,
		'/', 'index'
	)
	app = web.application(urls, globals())
	app.run()
