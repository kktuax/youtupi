from youtupi.engine.OMXPlayerEngine import OMXPlayerEngine
from youtupi.engine.VlcEngine import VlcEngine
from youtupi.engine.MockEngine import MockEngine
from youtupi.util import config

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def createEngine():
    baseVolume = config.conf.get('base-volume', 0)
    engine = None
    if which("omxplayer"):
        print 'Using OMX Player engine'
        engine = OMXPlayerEngine()
    elif which("vlc"):
        print 'Using VLC engine'
        engine = VlcEngine()
    else:
        print 'No player detected, using mock player engine'
        engine = MockEngine()
    engine.setBaseVolume(baseVolume)
    return engine

engine = createEngine()
