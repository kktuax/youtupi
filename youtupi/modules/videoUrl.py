import threading
from youtupi.modules import local, youtube, url
        
videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:        
        if not video.url:
            return_url = local.getUrl(video.data)
            if not return_url and video.data['type'] == "url":
                return_url = url.getUrl(video.data)
            if not return_url:
                return_url = youtube.getUrl(video.data)
            video.url = return_url