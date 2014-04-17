import threading, time
from youtupi.video import Video
from youtupi.modules import local, youtube
from youtupi.engine.PlaybackEngineFactory import engine

TIMEOUT = 60

videos = list()

def resetPlaylist():
    global videos
    videos = list()
            
def playingVideo():
    if engine.isPlaying():
        viewedVideos = filter(lambda video:video.played==True, videos)
        lastPlayedVideo = viewedVideos[-1:]
        if lastPlayedVideo:
            return lastPlayedVideo[0]
    return None

def removeOldVideosFromPlaylist():
    viewedVideos = filter(lambda video:video.played==True, videos)
    currentVideo = playingVideo()
    for vv in viewedVideos:
        if vv != currentVideo:
            videos.remove(vv)

def removeVideo(videoId):
    video = findVideoInPlaylist(videoId)
    if video:
        if video == playingVideo():
            playNextVideo()
        videos.remove(video)

def playList():
    return videos

def findVideoInPlaylist(vid):
    fvideos = filter(lambda video:video.vid==vid, videos)
    if fvideos:
        return fvideos[0]
    else:
        return None

def playNextVideo():
    viewedVideos = filter(lambda video:video.played==False, videos)
    nextVideo = viewedVideos[:1]
    if nextVideo:
        try:
            playVideo(nextVideo[0].vid)
        except RuntimeError:
            print 'Error playing video'
            removeVideo(nextVideo[0].vid)
    else:
        engine.stop()

def addVideo(data):
    video = Video(data['id'], data)
    videos.append(video)

lock = threading.RLock()

def playVideo(videoId):
    with lock:
        svideo = findVideoInPlaylist(videoId)
        if svideo:
            if svideo != videos[0]:
                videos.remove(svideo)
                videos.insert(0, svideo)
                removeOldVideosFromPlaylist()
            cont = 0
            while not svideo.url:
                time.sleep(1)
                cont = cont + 1
                if cont > TIMEOUT:
                    raise RuntimeError('Error playing video: video not prepared')
            engine.play(svideo)
            svideo.played = True

videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:        
        if not video.url:
            url = local.getUrl(video.data)
            if not url:
                url = youtube.getUrl(video.data)
            video.url = url

def autoPlay():
    removeOldVideosFromPlaylist()
    if videos:
        for nvideo in videos[:1]:
            prepareVideo(nvideo)
        if not engine.isPlaying():
            playNextVideo()
        else:
            svideo = playingVideo()
            if svideo:
                position = engine.getPosition()
                if position:
                    svideo.data["position"] = position
                duration = engine.getDuration()
                if duration:
                    svideo.data["duration"] = duration
        for nvideo in videos[:3]:
            prepareVideo(nvideo)
    threading.Timer(1, autoPlay).start()

autoPlay()
