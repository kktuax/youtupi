import subprocess, re, string, sys, web, json
import os.path
from StringIO import StringIO
from os.path import expanduser
from pafy import pafy
from youtupi.video import Video
from youtupi.util import config, downloader, ensure_dir

def getUrl(data):
	if(data['type'] == "youtube"):
		print 'Locating URL for: ' + data['id']
		try:
			video = pafy.new(data['id'])
			if data['format'] == "audio":
				bestaudio = video.getbestaudio(preftype="m4a")
				return bestaudio.url
			best = video.getbest(preftype="mp4")
			if data['format'] == "high":
				return best.url
			for stream in video.streams:
				if stream is not best:
					if stream.extension == 'mp4':
						return stream.url
			return best.url
		except:
			print "Error fetching video URL"
	return None

class youtube_dl:
    
    def POST(self):
		data = json.load(StringIO(web.data()))
		video = pafy.new(data['id'])
		dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
		ensure_dir(dfolder)
		dfile = os.path.join(dfolder, video.title + ".mp4")
		best = video.getbest(preftype="mp4")
		best.download(filepath=dfile)

urls = ("-download", "youtube_dl")
module_youtube = web.application(urls, locals())
