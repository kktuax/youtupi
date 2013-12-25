#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
from os.path import expanduser
from StringIO import StringIO
import heapq
import datetime
import json
import web
from youtupi.playlist import findVideoInPlaylist, removeVideo
from youtupi.video import createVideo
from youtupi.util import config, ensure_dir		
from periscope.periscope import Periscope
	
def find_files(rootfolder=expanduser("~"), search="", count=20, extension=(".avi", ".mp4", ".mkv")):
	if not search:
		return find_newest_files(rootfolder, count=count, extension=extension)
	files = set()
	for dirname, dirnames, filenames in os.walk(rootfolder, followlinks=True):
		for filename in filenames:
			if filename.endswith(extension):
				if isFileInKeyWords(filename, search):
					files.add(os.path.join(dirname, filename))
	return sorted(files)[0:count]

def find_newest_files(rootfolder=expanduser("~"), count=20, extension=(".avi", ".mp4", ".mkv")):
	return heapq.nlargest(count,
		(os.path.join(dirname, filename)
		for dirname, dirnames, filenames in os.walk(rootfolder, followlinks=True)
		for filename in filenames
		if filename.endswith(extension)),
		key=lambda fn: os.stat(fn).st_mtime)

def isFileInKeyWords(filename, search):
	words = search.split()
	for word in words:
		if word.lower() not in filename.lower():
			return False
	return True

class search:
	
	def GET(self):
		user_data = web.input()
		search = user_data.search
		count = int(user_data.count)
		local_videos = list()
		folders = config.conf.get('local-folders', ['~'])
		print 'Searching "' + search + '" in folders: ' + ', '.join(folders)
		for folder in folders:
			for local_video_file in find_files(expanduser(folder), search=search, count=count):
				date = datetime.date.fromtimestamp(os.path.getmtime(local_video_file)).isoformat()
				name = os.path.basename(local_video_file)
				subtitleOperation = {'name': 'subtitle', 'text': 'Subtitles', 'successMessage': 'Subtitle downloaded'};
				deleteOperation = {'name': 'delete', 'text': 'Delete', 'successMessage': 'File deleted'};
				local_video = {'id': local_video_file, 'description': date, 'title': name, 'type': 'local', 'operations' : [subtitleOperation, deleteOperation]}
				local_videos.append(local_video)
		return json.dumps(local_videos[0:count], indent=4)

def downloadSubtitle(video):
	dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
	ensure_dir.ensure_dir(dfolder)
	p = Periscope(dfolder)
	p.downloadSubtitle(video.url, p.get_preferedLanguages())

class subtitle_dl:
	def POST(self):
		data = json.load(StringIO(web.data()))
		video = findVideoInPlaylist(data['id'])
		if(video == None):
			video = createVideo(data)
		downloadSubtitle(video)

class delete:
	def POST(self):
		data = json.load(StringIO(web.data()))
		removeVideo(data['id'])
		if os.path.isfile(data['id']):
			os.remove(data['id'])

urls = (
	"-search", "search",
	'-subtitle', "subtitle_dl",
	'-delete', "delete"
)

module_local = web.application(urls, locals())
