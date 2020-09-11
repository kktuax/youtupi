import threading
import os.path
from youtupi.modules import local, youtube, url
        
videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:
        if not video.subtitles and video.data['type'] == "local":
            path = os.path.splitext(video.vid)[0] + ".srt"
            if os.path.exists(path):
                video.subtitles = path
        if not video.url:
            return_url = local.getUrl(video.data)
            if not return_url and video.data['type'] == "url":
                return_url = url.getUrl(video.data)
            if not return_url:
                return_url = youtube.getUrl(video.data)
            video.url = return_url