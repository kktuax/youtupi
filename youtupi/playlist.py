import os, signal, subprocess, threading, time
from youtupi.video import Video
from youtupi.modules import local, youtube

player = None
videos = list()

def playingVideo():
    if isProcessRunning(player):
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
            if len(videos) == 1:
                stopPlayer()
            else:
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

def stopPlayer():
    global player
    if isProcessRunning(player):
        os.killpg(player.pid, signal.SIGTERM)
        player = None

def playNextVideo():
    viewedVideos = filter(lambda video:video.played==False, videos)
    nextVideo = viewedVideos[:1]
    if nextVideo:
        playVideo(nextVideo[0].vid)

def addVideo(data):
    video = Video(data['id'], data)
    videos.append(video)

lock = threading.RLock()

def playVideo(videoId):
    with lock:
        stopPlayer()
        svideo = findVideoInPlaylist(videoId)
        if svideo:
            if svideo != videos[0]:
                videos.remove(svideo)
                videos.insert(0, svideo)
                removeOldVideosFromPlaylist()
            if not svideo.url:
                prepareVideo(svideo)
            playerArgs = ["omxplayer", "-o", "hdmi"]
            if svideo.url.startswith("http"):
                playerArgs.append("--live")
            playerArgs.append(svideo.url)
            print "Running player: " + " ".join(playerArgs)
            global player
            player = subprocess.Popen(playerArgs, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
            while not isProcessRunning(player):
                time.sleep(1)
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
        if not isProcessRunning(player):
            playNextVideo()
        for nvideo in videos[:2]:
            prepareVideo(nvideo)
    threading.Timer(1, autoPlay).start()
    
def isProcessRunning(process):
    if process:
        if process.poll() == None:
            return True
    return False

def controlPlayer(action):
    global player
    if action == "stop":
        stopPlayer()
        global videos
        videos = list()
    if action == "pause":
        player.stdin.write("p")
    if action == "volup":
        player.stdin.write("+")
    if action == "voldown":
        player.stdin.write("-")
    if action == "forward":
        player.stdin.write("\x1B[C")
    if action == "backward":
        player.stdin.write("\x1B[D")

autoPlay()