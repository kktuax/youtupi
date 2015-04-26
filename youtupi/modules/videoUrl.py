import threading
from youtupi.modules import kat, local, youtube
        
videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:        
        if not video.url:
            url = local.getUrl(video.data)
            if not url:
                url = youtube.getUrl(video.data)
            if not url:
                url = kat.getUrl(video.data)
            video.url = url
            
closeVideoLock = threading.RLock()

def closeVideo(video):
    with closeVideoLock:
        if(video.data['type'] == "kat"):
            kat.closeVideo(video)