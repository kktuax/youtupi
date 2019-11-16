#!/usr/bin/python
# -*- coding: utf-8 -*-

import web, json, urllib, hashlib, os
from youtupi.util import config

def presetFactory(data):
	if isinstance(data, dict):
		if data.get('type', '') == "peerflix-server":
			return PeerflixServerPreset(data.get('url', ''))
		if data.get('type', '') == "TV-Online-TDT-Spain":
			return TvOnlineTDTSpainPreset(data.get('url', ''))
	return Preset(data)

class Preset(object):

	url = ''

	def __init__(self, url):
		self.url = url

	def id(self):
		m = hashlib.md5()
		m.update(self.url)
		return m.hexdigest()

	def description(self):
		return self.url

	def title(self):
		return os.path.basename(self.url)

	def fetch(self):
		response = urllib.urlopen(self.url)
		content = json.loads(response.read())
		return content

class PeerflixServerPreset(Preset):
	def fetch(self):
		response = urllib.urlopen(self.url + '/torrents')
		content = []
		torrents = json.loads(response.read())
		for torrent in torrents:
			for torrentFile in torrent.get('files', []):
				content.append({'type': 'url', 'id': self.url + torrentFile.get('link', ''), 'title': torrentFile.get('name', '')})
		return content

class TvOnlineTDTSpainPreset(Preset):
	def fetch(self):
		response = urllib.urlopen(self.url)
		content = []
		channels = json.loads(response.read())
		for channel in channels:
			if channel.get('enabled', False):
				content.append({'type': 'url', 'id': channel.get('link_m3u8', ''), 'title': channel.get('name', '')})
		return content

class list:

	def GET(self):
		presets = []
		for presetData in config.conf.get('presets', []):
			preset = presetFactory(presetData)
			presets.append({'id': preset.id(), 'description': preset.description(), 'title': preset.title(), 'type': 'search', 'operations' : []})
		return json.dumps(presets, indent=4)

class load:

	def GET(self, presetId):
		print "searching for preset " + presetId
		data = []
		for presetData in config.conf.get('presets', []):
			preset = presetFactory(presetData)
			if presetId == preset.id():
				data = preset.fetch()
				break
		return json.dumps(data, indent=4)

urls = (
	'', 'list',
	'/(.*)', 'load',
)

module_preset = web.application(urls, locals())
