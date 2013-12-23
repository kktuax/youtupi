import os, signal, subprocess, threading, time

player = None
videos = list()
lock = threading.RLock()

def removeOldVideosFromPlaylist():
    viewedVideos = filter(lambda video:video.played==True, videos)
    if isProcessRunning(player):
        oldVideos = viewedVideos[1:]
    else:
        oldVideos = viewedVideos
    for vv in oldVideos:
        videos.remove(vv)

def playList():
    return videos

def removeVideo(vid):
    global videos
    videos = filter(lambda video:video.vid!=vid, videos)
    
def findVideoInPlaylist(vid):
    fvideos = filter(lambda video:video.vid==vid, videos)
    if(len(fvideos)>0):
        return fvideos[0]
    else:
        return None

def playNextVideo():
    with lock:
        global player
        if isProcessRunning(player):
            os.killpg(player.pid, signal.SIGTERM)
            player = None
            removeOldVideosFromPlaylist()
        for video in videos:
            if not video.played:
                player = subprocess.Popen(['omxplayer', '-ohdmi', video.url], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
                while not isProcessRunning(player):
                    time.sleep(1)
                video.played = True
                break

def addVideo(video):
    videos.append(video)

def playVideo(videoId):
    svideo = None
    for video in videos:
        if video.vid == videoId:
            svideo = video
            break
    if svideo:
        videos.remove(svideo)
        svideo.played = False
        videos.insert(0, svideo)
        playNextVideo()

def autoPlay():
    removeOldVideosFromPlaylist()
    if (not isProcessRunning(player)) and (len(videos) > 0):
        playNextVideo()

def isProcessRunning(process):
    if process:
        if process.poll() == None:
            return True
    return False

def controlPlayer(action):
    if action == "stop":
        player.stdin.write("q")
        player = None
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