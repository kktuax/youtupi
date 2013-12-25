import os, signal, subprocess, threading, time

player = None
videos = list()
lock = threading.RLock()

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

def playList():
    return videos

def removeVideo(vid):
    video = findVideoInPlaylist(vid)
    if video:
        if video == playingVideo():
            if len(videos) == 1:
                stopPlayer()
            else:
                playNextVideo()
        global videos
        videos = filter(lambda video:video.vid!=vid, videos)
    
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

def addVideo(video):
    videos.append(video)

def playVideo(videoId):
    with lock:
        stopPlayer()
        svideo = findVideoInPlaylist(videoId)
        if svideo:
            if svideo != videos[0]:
                removeOldVideosFromPlaylist()
                videos.remove(svideo)
                videos.insert(0, svideo)
            global player
            player = subprocess.Popen(['omxplayer', '-ohdmi', svideo.url], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
            while not isProcessRunning(player):
                time.sleep(1)
            svideo.played = True

def autoPlay():
    threading.Timer(1, autoPlay).start()
    removeOldVideosFromPlaylist()
    if (not isProcessRunning(player)) and (len(videos) > 0):
        playNextVideo()
    
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