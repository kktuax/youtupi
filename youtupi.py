#!/usr/bin/env /usr/bin/python
# -*- coding: utf-8 -*-

import web
from youtupi.modules.local import module_local
from youtupi.modules.youtube import module_youtube
from youtupi.modules.url import module_url
from youtupi.modules.control import module_control
from youtupi.modules.playlist import module_playlist
from youtupi.modules.preset import module_preset
from youtupi.util import config

class redirect:
	def GET(self, path):
		web.seeother('/' + path)

class index:
	def GET(self):
		web.seeother('/static/index.html')

class MyApplication(web.application):
    def run(self, host='0.0.0.0', port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, (host, port))

if __name__ == "__main__":
	urls = (
		'/(.*)/', 'redirect',
		'/playlist', module_playlist,
		'/control', module_control,
		'/url', module_url,
		'/local', module_local,
		'/youtube', module_youtube,
		'/preset', module_preset,
		'/', 'index'
	)
	app = MyApplication(urls, globals())
	port = config.conf.get('port', 8080)
	host = config.conf.get('host', '0.0.0.0')
	app.run(host=host, port=port)
