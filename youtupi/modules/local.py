#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
from os.path import expanduser
import heapq
import datetime
import json
import web
from youtupi.util import config		

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
		local_videos = list()
		folders = config.conf.get('local-folders', ['~'])
		print 'Searching in folders: ' + ', '.join(folders)
		for folder in folders:
			for local_video_file in find_newest_files(expanduser(folder)):
				date = datetime.date.fromtimestamp(os.path.getmtime(local_video_file)).isoformat()
				name = os.path.basename(local_video_file)
				local_video = {'id': local_video_file, 'description': date, 'title': name, 'type': 'local'}
				local_videos.append(local_video)
		return json.dumps(local_videos, indent=4)

urls = ("", "local")
module_local = web.application(urls, locals())
