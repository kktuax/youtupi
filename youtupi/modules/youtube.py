import subprocess, sys, web, json
import os.path
from StringIO import StringIO
from os.path import expanduser
from youtupi.video import Video
from youtupi.util import config, downloader, ensure_dir

def getUrl(data):
    if(data['type'] == "youtube"):
        print 'Locating URL for: ' + data['id']
        if(data['format'] == "default"):
            return getYoutubeUrl(data['id'])
        else:
            return getYoutubeUrl(data['id'], data['format'])
    else:
        return None

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



class youtube_dl:
    
    def POST(self):
        from youtupi.playlist import findVideoInPlaylist, prepareVideo
        data = json.load(StringIO(web.data()))
        video = findVideoInPlaylist(data['id'])
        if video:
            dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
            ensure_dir.ensure_dir(dfolder)
            dfile = os.path.join(dfolder, video.data['title'] + ".mp4")
            if not video.url:
                prepareVideo(video)
            downloader.download(video.url, dfile)

urls = ("-download", "youtube_dl")
module_youtube = web.application(urls, locals())
