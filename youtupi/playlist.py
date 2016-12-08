import threading
from youtupi.video import Video
from youtupi.modules.videoUrl import prepareVideo
from youtupi.modules.youtube import updateVideoData, resolveYoutubePlaylist
from youtupi.engine.PlaybackEngineFactory import engine

videos = list()

def resetPlaylist():
    global videos
    videos = list()

def currentVideo():
    viewedVideos = filter(lambda video:video.played==True, videos)
    lastPlayedVideo = viewedVideos[-1:]
    if lastPlayedVideo:
        return lastPlayedVideo[0]
    return None

def removeOldVideosFromPlaylist():
    viewedVideos = filter(lambda video:video.played==True, videos)
    cv = currentVideo()
    for vv in viewedVideos:
        if vv != cv:
            videos.remove(vv)

def removeVideo(videoId):
    video = findVideoInPlaylist(videoId)
    if video:
        if video == currentVideo():
            playNextVideo()
    try:
        videos.remove(video)
    except ValueError:
        print "Video already deleted"

def playlistPosition(videoId, position):
    video = findVideoInPlaylist(videoId)
    if (len(videos) > 1) and video:
        isPlaying = None
        if video == currentVideo():
            isPlaying = True
    pos = int(position) - 1
    curPos = videos.index(video)
    if pos != curPos:
        print "Changing video " + videoId + " position to: " + str(pos) + " (was " + str(curPos) + ")"
        videos.remove(video)
        videos.insert(pos, video)
        if isPlaying:
            video.played=False
            playNextVideo()

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
        playVideo(nextVideo[0].vid)
        removeOldVideosFromPlaylist()
    else:
        engine.stop()
        resetPlaylist()

def updateData(data):
    data.update(updateVideoData(data))

def addYoutubePlaylist(data):
    for video in resolveYoutubePlaylist(data):
        addVideos(video)

def addVideos(data):
    if type(data) is list:
        for vData in data:
            addVideos(vData)
    elif data['type'] == "youtube" and len(data['id']) > 12:
        threading.Thread(target=addYoutubePlaylist, args=(data,)).start()
    else:
        if data['type'] == 'youtube' and not data.has_key('title'):
            threading.Thread(target=updateData, args=(data,)).start()
        video = Video(data['id'], data)
        videos.append(video)

def playVideo(videoId):
    svideo = findVideoInPlaylist(videoId)
    if svideo:
        print 'Requested video ' + videoId
        if svideo == currentVideo():
            engine.setPosition(0)
        else:
            svideo.played = True
            removeOldVideosFromPlaylist()
            if svideo != videos[0]:
                videos.remove(svideo)
                videos.insert(0, svideo)
            if not svideo.url:
                prepareVideo(svideo)
            try:
                engine.play(svideo)
            except RuntimeError:
                print 'Error playing video ' + videoId
                removeVideo(svideo.vid)

def autoPlay():
    removeOldVideosFromPlaylist()
    if videos:
        if not engine.isPlaying():
            playNextVideo()
        else:
            svideo = currentVideo()
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
