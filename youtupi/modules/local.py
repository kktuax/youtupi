#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
from os.path import expanduser
from StringIO import StringIO
import heapq, datetime, web, json, codecs, magic
from youtupi.util import config, ensure_dir
from periscope.periscope import Periscope

def getUrl(data):
	if(data['type'] == "local"):
		return data['id']
	else:
		return None

def find_files(rootfolder=expanduser("~"), search="", count=20, extension=(".avi", ".mp4", ".mp3", ".mkv", ".ogm", ".mov", ".MOV")):
	if not search:
		return find_newest_files(rootfolder, count=count, extension=extension)
	files = set()
	for dirname, dirnames, filenames in os.walk(rootfolder, followlinks=True):
		for filename in filenames:
			if filename.endswith(extension):
				if isFileInKeyWords(filename, search):
					files.add(os.path.join(dirname, filename))
	return sorted(files)[0:count]

def find_files_and_folders(rootfolder, path, extension=(".avi", ".mp4", ".mp3", ".mkv", ".ogm", ".mov", ".MOV")):
	while path.startswith("/"):
		path = path[1:]
	folder = os.path.join(rootfolder, path)
	dirs = set()
	files = set()
	for item, f in [ (os.path.join(folder,f),f) for f in os.listdir(folder) ]:
		if os.path.isdir(item):
			if not f.startswith('.'):
				dirs.add(f)
		elif os.path.isfile(item):
			if item.endswith(extension):
				files.add(os.path.join(item))
	return sorted(dirs), sorted(files)

def find_newest_files(rootfolder=expanduser("~"), count=20, extension=(".avi", ".mp4", ".mkv", ".ogm", ".mov", ".MOV")):
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
		extensions = config.conf.get('local-search-extensions', [".avi", ".mp4", ".mp3", ".ogg", ".mkv", ".flv"])
		print 'Searching "' + search + '" in folders: ' + ', '.join(folders)
		for folder in folders:
			for local_video_file in find_files(expanduser(folder), search=search, count=count, extension=tuple(extensions)):
				date = datetime.date.fromtimestamp(os.path.getmtime(local_video_file)).isoformat()
				name = os.path.basename(local_video_file)
				subtitleOperation = {'name': 'subtitle', 'text': 'Subtitles', 'successMessage': 'Subtitle downloaded'};
				deleteOperation = {'name': 'delete', 'text': 'Delete', 'successMessage': 'File deleted'};
				local_video = {'id': local_video_file, 'description': date, 'title': name, 'type': 'local', 'operations' : [subtitleOperation, deleteOperation]}
				local_videos.append(local_video)
		return json.dumps(local_videos[0:count], indent=4)

class browse:

	def GET(self):
		user_data = web.input()
		search = user_data.search.strip()
		count = int(user_data.count)
		extensions = config.conf.get('local-search-extensions', [".avi", ".mp4", ".mp3", ".ogg", ".mkv", ".flv"])
		local_dirs = list()
		local_videos = list()
		rootfolders = config.conf.get('local-folders', ['~'])
		print 'Browsing "' + search + '" in folders: ' + ', '.join(rootfolders)
		for rootfolder in rootfolders:
			rootfoldername = os.path.basename(rootfolder)
			if search == "" or search == "/":
				name = rootfoldername
				local_browse_folder = {'id': "/%s" % rootfoldername, 'description': "", 'title': name, 'type': 'search', 'engine' : 'local-dir', 'operations' : []}
				local_dirs.append(local_browse_folder)
			elif search.startswith("/%s" % rootfoldername):
				local_dirs.append({'id': os.path.dirname(search), 'description': "Go back", 'title': "..", 'type': 'search', 'engine' : 'local-dir', 'operations' : []})
				prefix = search[(len(rootfoldername)+1):]
				dirs, files = find_files_and_folders(expanduser(rootfolder), prefix, extension=tuple(extensions))
				for local_dir in dirs:
					name = os.path.basename(local_dir)
					local_browse_folder = {'id': os.path.join(search,local_dir), 'description': "Folder", 'title': name, 'type': 'search', 'engine' : 'local-dir', 'operations' : []}
					local_dirs.append(local_browse_folder)
				for local_video_file in files:
					date = datetime.date.fromtimestamp(os.path.getmtime(local_video_file)).isoformat()
					name = os.path.basename(local_video_file)
					subtitleOperation = {'name': 'subtitle', 'text': 'Subtitles', 'successMessage': 'Subtitle downloaded'};
					deleteOperation = {'name': 'delete', 'text': 'Delete', 'successMessage': 'File deleted'};
					local_video = {'id': local_video_file, 'description': date, 'title': name, 'type': 'local', 'operations' : [subtitleOperation, deleteOperation]}
					local_videos.append(local_video)
		return json.dumps(local_dirs + local_videos, indent=4)

def downloadSubtitle(video):
	dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
	ensure_dir.ensure_dir(dfolder)
	p = Periscope(dfolder)
	p.downloadSubtitle(video.vid, p.get_preferedLanguages())
	toUtf8File(os.path.splitext(video.vid)[0] + ".srt")

def toUtf8File(srtFile):
	if os.path.isfile(srtFile):
		blob = open(srtFile, "r").read()
		m = magic.open(magic.MAGIC_MIME_ENCODING)
		m.load()
		file_encoding = m.buffer(blob)
		if file_encoding != 'utf-8':
			base = os.path.splitext(srtFile)[0]
			extension = os.path.splitext(srtFile)[1]
			srtFileTmp = base + "-tmp." + extension
			os.rename(srtFile, srtFileTmp)
			file_stream = codecs.open(srtFileTmp, 'r', file_encoding)
			file_output = codecs.open(srtFile, 'w', 'utf-8')
			for l in file_stream:
				file_output.write(l)
			file_stream.close()
			file_output.close()
			os.remove(srtFileTmp)

class subtitle_dl:
	def POST(self):
		data = json.load(StringIO(web.data()))
		from youtupi.playlist import findVideoInPlaylist
		video = findVideoInPlaylist(data['id'])
		if video:
			downloadSubtitle(video)

class delete:
	def POST(self):
		data = json.load(StringIO(web.data()))
		from youtupi.playlist import removeVideo
		removeVideo(data['id'])
		if os.path.isfile(data['id']):
			os.remove(data['id'])

urls = (
	"-search", "search",
	"-browse", "browse",
	'-subtitle', "subtitle_dl",
	'-delete', "delete"
)

module_local = web.application(urls, locals())
