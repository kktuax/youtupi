import threading
from os.path import expanduser, join
from babelfish import Language
from guessit import guess_video_info
from subliminal import download_best_subtitles
from subliminal.subtitle import get_subtitle_path
from subliminal.video import Video

from youtupi.util import config, ensure_dir
from youtupi.modules import kat, local, youtube
        
videoUrlLock = threading.RLock()

def prepareVideo(video):
    with videoUrlLock:
        kat.prepareVideo(video)
        youtube.prepareVideo(video)
        local.prepareVideo(video)
        prepareSubs(video)
            
def prepareSubs(video):
    if(video.data['type'] != "youtube") and video.data['subs']:
        dfolder = expanduser(config.conf.get('download-folder', "~/Downloads"))
        ensure_dir.ensure_dir(dfolder)
        filepath = join(dfolder, video.data['title'] + ".mp4")
        guess = guess_video_info(filepath, info=['filename'])
        subvideo = Video.fromguess(filepath, guess)
        subtitle = None
        try:
            subtitle = download_best_subtitles([subvideo], {Language(video.data['subs'])}, single=True)
        except Exception,e:
            print "Error finding subtitles: " + str(e)
        if subtitle is not None and len(subtitle):
            subtitle = get_subtitle_path(join(dfolder, subvideo.name))
        video.subs = subtitle

closeVideoLock = threading.RLock()

def closeVideo(video):
    with closeVideoLock:
        if(video.data['type'] == "kat"):
            kat.closeVideo(video)