import os, json

def loadConfig():
    dname = os.path.abspath('.')
    print 'Reading config from: ' + dname
    fname = 'youtupi.conf'
    conf = {}
    if os.path.isfile(fname):
        conf = json.load(open(fname))
    return(conf)

conf = loadConfig()