import threading
from youtupi.modules import kat, local, youtube
        
videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:
        kat.prepareVideo(video)
        youtube.prepareVideo(video)
        local.prepareVideo(video)
            
closeVideoLock = threading.RLock()

def closeVideo(video):
    with closeVideoLock:
        if(video.data['type'] == "kat"):
            kat.closeVideo(video)