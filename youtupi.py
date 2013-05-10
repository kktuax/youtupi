#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, signal, sys, subprocess, threading, time
import os.path
from os.path import expanduser
import heapq
import datetime
import web
import json
import urllib2
from StringIO import StringIO

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
fname = 'youtupi.conf'
conf = {}
if os.path.isfile(fname):
	conf = json.load(open(fname))

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

def download(url, destination):
	with open(destination, 'w') as f:
		try:
			f.write(urllib2.urlopen(url).read())
			f.close()
		except urllib2.HTTPError:
			raise RuntimeError('Error getting URL.')

def ensure_dir(d):
	if not os.path.exists(d):
		os.makedirs(d)

def downloadVideo(video):
	dfolder = expanduser(conf.get('download-folder', "~/Downloads"))
	ensure_dir(dfolder)
	if video.data['type'] == "youtube":
		dfile = os.path.join(dfolder, video.data['title'] + ".mp4")
		download(video.url, dfile)
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

def find_newest_files(rootfolder=expanduser("~"), count=20, extension=(".avi", ".mp4", ".mkv")):
	return heapq.nlargest(count,
		(os.path.join(dirname, filename)
		for dirname, dirnames, filenames in os.walk(rootfolder, followlinks=True)
		for filename in filenames
		if filename.endswith(extension)),
		key=lambda fn: os.stat(fn).st_mtime)

def find_files(rootfolder=expanduser("~"), search="", extension=(".avi", ".mp4", ".mkv")):
	if not search:
		return find_newest_files(rootfolder, extension=extension)
	files = set()
	for dirname, dirnames, filenames in os.walk(rootfolder, followlinks=True):
		for filename in filenames:
			if filename.endswith(extension):
				if search.lower() in filename.lower():
					files.add(os.path.join(dirname, filename))
	return sorted(files)

class redirect:
	def GET(self, path):
		web.seeother('/' + path)

class index:
	def GET(self):
		web.seeother('/static/index.html')

class local:
	def GET(self):
		local_videos = list()
		folders = conf.get('local-folders', ['~'])
		for folder in folders:
			for local_video_file in find_newest_files(expanduser(folder)):
				date = datetime.date.fromtimestamp(os.path.getmtime(local_video_file)).isoformat()
				name = os.path.basename(local_video_file)
				local_video = {'id': local_video_file, 'description': date, 'title': name, 'type': 'local'}
				local_videos.append(local_video)
		return json.dumps(local_videos, indent=4)

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
		'/local', 'local',
		'/playlist', 'playlist',
		'/video/(.*)', 'video',
		'/control/(.*)', 'control',
		'/', 'index'
	)
	app = web.application(urls, globals())
	app.run()
