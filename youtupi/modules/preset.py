#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json, urllib, hashlib, os
from youtupi.util import config

class list:

	def GET(self):
		presets = []
		for presetUrl in config.conf.get('presets', []):
			m = hashlib.md5()
			m.update(presetUrl)
			preset = {'id': m.hexdigest(), 'description': presetUrl, 'title': os.path.basename(presetUrl), 'type': 'search', 'operations' : []}
			presets.append(preset)
		return json.dumps(presets, indent=4)

class load:

	def GET(self, presetId):
		print "searching for preset " + presetId
		data = []
		for presetUrl in config.conf.get('presets', []):
			m = hashlib.md5()
			m.update(presetUrl)
			if presetId == m.hexdigest():
				response = urllib.urlopen(presetUrl)
				data = json.loads(response.read())
				break
		return json.dumps(data, indent=4)

urls = (
	'', 'list',
	'/(.*)', 'load',
)

module_preset = web.application(urls, locals())
