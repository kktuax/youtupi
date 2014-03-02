import subprocess, re, string, sys, web, json
import os.path
from StringIO import StringIO
from os.path import expanduser
from youtupi.video import Video
from youtupi.util import config, downloader, ensure_dir

def getUrl(data):
    if(data['type'] == "youtube"):
        print 'Locating URL for: ' + data['id']
        formats = getYoutubeFormats(data['id'])
        if data['format'] == "high":
            formats = formats[::-1]
        for eformat in formats:
            try:
                return getYoutubeUrl(data['id'], eformat)
            except RuntimeError:
                print 'Unable to fetch valid URL in format: ' + eformat
    return None

def getYoutubeFormats(video):
    url = "http://www.youtube.com/watch?v=" + video
    args = ['youtube-dl', '-F', url]
    yt_dl = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (response, err) = yt_dl.communicate()
    if yt_dl.returncode != 0:
        sys.stderr.write(err)
        raise RuntimeError('Error getting format list.')
    else:
        formats = []
        formatsRegexp = re.compile("(\d+)\s{2,}([\d\w]+)\s{2,}(.+)\s{2,}(.+)")
        responseLines = string.split(response.decode('UTF-8').strip(), '\n')
        for line in responseLines:
            formatResponse = formatsRegexp.search(line)
            if formatResponse and "mp4" in formatResponse.group(2) and not "DASH" in formatResponse.group(4):
                formats.append(formatResponse.group(1))
        return formats

def getYoutubeUrl(video, vformat = None):
    url = "http://www.youtube.com/watch?v=" + video
    if not vformat: 
        args = ['youtube-dl', '-g', url]
    else:
        args = ['youtube-dl', '-f', vformat, '-g', url]
    yt_dl = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (url, err) = yt_dl.communicate()
    if yt_dl.returncode != 0:
        sys.stderr.write(err)
        raise RuntimeError('Error getting URL.')
    else:
        rurl = url.decode('UTF-8').strip()
        if not isValidUrl(rurl):
            raise RuntimeError('Invalid URL.')
        return rurl

def isValidUrl(url):
    args = ['omxplayer', '-i', url]
    opi = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (exitm, out) = opi.communicate()
    if out:
        return True
    return False

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
