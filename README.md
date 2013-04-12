YouTuPi
=======

YouTube (mobile) web frontend for your Raspberry Pi
---------------------------------------------------

YouTuPi lets you play [YouTube](http://www.youtube.com/) videos in your [Raspberry Pi](http://www.raspberrypi.org/) using a (mobile) web interface. 

Video search is performed in the client using the YouTube Data API. Videos are added to a playlist with the usual options: next/pause/resume/stop. The video URL is retrieved using [youtube-dl](http://rg3.github.com/youtube-dl/) and the actual playback happens in the [Omxplayer](https://github.com/huceke/omxplayer).

Technologies used
-----------------

 * [web.py](http://webpy.org/) as HTTP server 
 * [youtube-dl](http://rg3.github.com/youtube-dl/) for youtube support  
 * [Omxplayer](https://github.com/huceke/omxplayer) as video player
 * [JQuery mobile](http://jquerymobile.com) UI frontend

How-To
----------

# Install the dependencies

    sudo apt-get install omxplayer python-pip
    sudo pip install web.py

# Get the last version of master branch

    cd ~
    wget https://github.com/kktuax/youtupi/archive/master.zip
    unzip master.zip

Use YouTuPi
-----------

# Launch YouTuPi server

    cd ~/youtupi-master
    nohup python youtupi.py >/dev/null 2>&1 &

 * Grab your Tablet/Phone/PC and go to: http://192.168.1.2:8080 (replace 192.168.1.2 with your Raspberry Pi address).
 * Enjoy!
