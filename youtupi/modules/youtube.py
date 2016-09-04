import subprocess, re, string, sys, web, json, threading
import os.path
from StringIO import StringIO
from os.path import expanduser
from pafy import pafy
from youtupi.video import Video
from youtupi.util import config, downloader, ensure_dir

infoLock = threading.RLock()

def getUrl(data):
        with infoLock:
                if(data['type'] == "youtube"):
                        print 'Locating URL for: ' + data['id']
                        try:
                                video = None
                                if data.has_key('url'):
                                        return data['url']
                                else:
                                        video = pafy.new(data['id'])
                                        data.update(video._ydl_info)
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
                        except Exception as e:
                                print "Error fetching video URL ", e
                                return "error"
                return None
	
def resolveYoutubePlaylist(data):
        with infoLock:
                if data['type'] == "youtube":
                        print 'Loading playlist data for ' + data['id']
                        try:
                                playlist = pafy.get_playlist(data['id'])
                                for item in playlist['items']:
                                        data = dict(id=item['pafy'].playlist_meta['encrypted_id'], type='youtube', format='high')
                                        data.update(item['pafy'].playlist_meta)
                                        print "Found video in playlist: ", data['id']
                                        yield data
                        except Exception as e:
                                print "Error fetching youtube playlist ", e
                
	
def updateVideoData(data):
        with infoLock:
                if(data['type'] == "youtube"):
                        print 'Loading data for ' + data['id']
                        try:
                                video = pafy.new(data['id'])
                                data.update(video._ydl_info)
                                if data['format'] == "audio":
                                        bestaudio = video.getbestaudio(preftype="m4a")
                                        return bestaudio.url
                                best = video.getbest(preftype="mp4")
                                if data['format'] == "high":
                                        data['url'] = best.url
                                else:
                                        for stream in video.streams:
                                                if stream is not best:
                                                        if stream.extension == 'mp4':
                                                                data['url'] = stream.url
                                                                break
                                        else:
                                                data['url'] = best.url
                                print data
                        except Exception as e:
                                print "Error fetching video data ", e
                return data

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
