import web, json
from StringIO import StringIO
from youtupi.playlist import removeVideo, addVideos, playList

class playlist:
	def GET(self):
		playlistVideos = list()
		for video in playList():
			playlistVideos.append(video.data)
		return json.dumps(playlistVideos, indent=4)

	def POST(self):
	        d = web.data()
	        s = StringIO(d)
	        print d
		data = json.load(s)
		addVideos(data)
		web.seeother('playlist')

	def DELETE(self):
		data = json.load(StringIO(web.data()))
		removeVideo(data['id'])
		web.seeother('playlist')

urls = (
	'', 'playlist',
)

module_playlist = web.application(urls, locals())
