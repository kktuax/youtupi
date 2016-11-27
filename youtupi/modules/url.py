#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json, codecs, magic
from youtupi.util import config, ensure_dir
import urlparse

def getUrl(data):
	if(data['type'] == "url"):
		return data['id']
	else:
		return None

class search:

	def GET(self):
		user_data = web.input()
		search = user_data.search.strip()
		count = int(user_data.count)
		url = urlparse.urlparse(search)
		title = "%s: %s" % (url.netloc, url.path.rpartition('/')[2])
		videos = list()
		video = {'id': search, 'description': search, 'title': title, 'type': 'url', 'operations' : []}
		videos.append(video)
		return json.dumps(videos, indent=4)

urls = (
	"-search", "search",
)

module_url = web.application(urls, locals())
