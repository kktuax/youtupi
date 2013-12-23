import subprocess, sys, web, json
import os.path
from StringIO import StringIO
from os.path import expanduser
from youtupi.video import Video 
from youtupi.util import config, downloader, ensure_dir
from youtupi.playlist import findVideoInPlaylist

def createVideo(data):
    if(data['type'] == "youtube"):
        if(data['format'] == "default"):
            url = getYoutubeUrl(data['id'])
        else:
            url = getYoutubeUrl(data['id'], data['format'])
        return Video(data['id'], data, url)
    else:
        raise Exception("Unkown video type")

def getYoutubeUrl(video, vformat = None):
    url = "http://www.youtube.com/watch?v=" + video
    if not vformat: 
        args = ['youtube-dl', '-g', url]
    else:
        args = ['youtube-dl', '-f', vformat, '-g', url]
    yt_dl = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (url, err) = yt_dl.communicate()
    if yt_dl.returncode != 0:
        if vformat != None:
            return getYoutubeUrl(video, None)
        else:
            sys.stderr.write(err)
            raise RuntimeError('Error getting URL.')
    else:
        return url.decode('UTF-8').strip()

def downloadVideo(video):
    dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
    ensure_dir.ensure_dir(dfolder)
    dfile = os.path.join(dfolder, video.data['title'] + ".mp4")
    downloader.download(video.url, dfile)

class youtube_dl:
    
    def POST(self):
        data = json.load(StringIO(web.data()))
        video = findVideoInPlaylist(data['id'])
        if(video == None):
            video = createVideo(data)
        downloadVideo(video)

urls = ("-download", "youtube_dl")
module_youtube = web.application(urls, locals())
