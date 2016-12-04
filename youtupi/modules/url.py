#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json, codecs, magic
from youtupi.util import config, ensure_dir
import urlparse
import youtube_dl

def getUrl(data):
	if(data['type'] == "url"):
		return data['id']
	else:
		return None

def ydlInfo(video):
	vdata = {'id': video['url'], 'title': video['url'], 'description': '', 'type': 'url', 'operations' : []}
	if 'title' in video:
		vdata['title'] = video['title']
	if 'description' in video:
		vdata['description'] = video['description']
	if 'thumbnail' in video:
		vdata['thumbnail'] = video['thumbnail']
	return vdata

class search:

	def GET(self):
		user_data = web.input()
		search = user_data.search.strip()
		count = int(user_data.count)
		videos = list()
		if search:
			ydl = youtube_dl.YoutubeDL({'ignoreerrors': True})
			with ydl:
				result = ydl.extract_info(search, download=False)
				if 'entries' in result:
					for video in result['entries']:
						if 'url' in video:
							videos.append(ydlInfo(video))
				else:
					video = result
					if 'url' in video:
						videos.append(ydlInfo(video))
		return json.dumps(videos[0:count], indent=4)

urls = (
	"-search", "search",
)

module_url = web.application(urls, locals())
