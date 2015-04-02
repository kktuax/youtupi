import os, json

def initialize():
	dname = os.path.abspath('.')
	f = dname + '/pafy/__init__.py'
	if not os.path.exists(f):
		print 'Initializing pafy folder'
		open(f, 'w').close()
	f = dname + '/vlc/__init__.py'
	if not os.path.exists(f):
		print 'Initializing vlc folder'
		open(f, 'w').close()
		f = dname + '/vlc/generated/__init__.py'
		open(f, 'w').close()		

def loadConfig():
    dname = os.path.abspath('.')
    print 'Reading config from: ' + dname
    fname = 'youtupi.conf'
    conf = {}
    if os.path.isfile(fname):
        conf = json.load(open(fname))
    return(conf)

initialize()
conf = loadConfig()
