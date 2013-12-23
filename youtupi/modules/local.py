#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
from os.path import expanduser
from StringIO import StringIO
import heapq
import datetime
import json
import web
from youtupi.playlist import findVideoInPlaylist
from youtupi.video import createVideo
from youtupi.util import config, ensure_dir		

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

class local:
	
	def GET(self):
		user_data = web.input()
		search = user_data.search
		local_videos = list()
		folders = config.conf.get('local-folders', ['~'])
		print 'Searching "' + search + '" in folders: ' + ', '.join(folders)
		for folder in folders:
			for local_video_file in find_files(expanduser(folder), search=search):
				date = datetime.date.fromtimestamp(os.path.getmtime(local_video_file)).isoformat()
				name = os.path.basename(local_video_file)
				local_video = {'id': local_video_file, 'description': date, 'title': name, 'type': 'local'}
				local_videos.append(local_video)
		return json.dumps(local_videos, indent=4)

def downloadSubtitle(video):
	dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
	ensure_dir(dfolder)
	from periscope.periscope import Periscope
	p = Periscope(dfolder)
	p.downloadSubtitle(video.url, p.get_preferedLanguages())

class subtitle_dl:
	def POST(self, action):
		data = json.load(StringIO(web.data()))
		video = findVideoInPlaylist(data['id'])
		if(video == None):
			video = createVideo(data)
		downloadSubtitle(video)

urls = (
	"", "local",
	'/subtitle-dl', "subtitle_dl"
)

module_local = web.application(urls, locals())
