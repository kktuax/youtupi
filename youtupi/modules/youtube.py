import subprocess, sys
from youtupi.video import Video 

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
