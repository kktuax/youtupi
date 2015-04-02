import threading
from youtupi.modules import local, youtube
        
videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:        
        if not video.url:
            url = local.getUrl(video.data)
            if not url:
                url = youtube.getUrl(video.data)
            video.url = url