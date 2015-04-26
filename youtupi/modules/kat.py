#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json, re
from KickassAPI import Search
import os, signal, subprocess, time

procs = {}

def getUrl(data):
	if(data['type'] == "kat"):
		peerflixArgs = ["peerflix", "-r", data['id'], "-q"]
		print "Running peerflix: " + " ".join(peerflixArgs)
		process = subprocess.Popen(peerflixArgs, stdout = subprocess.PIPE, preexec_fn=os.setsid)
		time.sleep(1)
		procs[data['id']] = process
		while True:
			nextline = process.stdout.readline()
			if nextline == '' and process.poll() != None:
				break
			print "Process output: " + nextline
			if "http" in nextline:
				return re.search("(?P<url>https?://[^\s]+)", nextline).group("url")
			time.sleep(0.5)
	else:
		return None
	
def closeVideo(video):
	if(video.data['type'] == "kat"):
		if video.data['id'] in procs:
			pid = procs[video.data['id']].pid
			if check_pid(pid):
				print 'Closing peerflix: ' + video.data['id']
				os.killpg(pid, signal.SIGTERM)

def check_pid(pid):        
	""" Check For the existence of a unix pid. """
	try:
		os.kill(pid, 0)
	except OSError:
		return False
	else:
		return True

class search:
	
	def GET(self):
		user_data = web.input()
		search = user_data.search
		count = int(user_data.count)
		results = Search(search).list()
		kat_videos = list()
		for result in results:
			name = result.name
			desc = "Size: " + result.size + " (in " + result.files + " file/s), seeds: " + result.seed
			kat_video = {'id': result.magnet_link, 'description': desc, 'title': name, 'type': 'kat'}
			kat_videos.append(kat_video)
		return json.dumps(kat_videos[0:count], indent=4)

urls = (
	"-search", "search"
)

module_kat = web.application(urls, locals())
