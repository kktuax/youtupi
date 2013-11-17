import urllib2
import os

def download(url, destination):
    tdestination = destination + ".part"
    with open(tdestination, 'w') as f:
        try:
            f.write(urllib2.urlopen(url).read())
            f.close()
            os.rename(tdestination, destination)
        except urllib2.HTTPError:
            raise RuntimeError('Error getting URL.')
