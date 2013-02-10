YouTuPi
=======

YouTube (mobile) web frontend for your Raspberry Pi
---------------------------------------------------

YouTuPi lets you play [YouTube](http://www.youtube.com/) videos in your [http://www.raspberrypi.org/](Raspberry Pi) using a (mobile) web interface. 

YouTube video search uses the YouTube Data API. Videos are added to a playlist with the usual options (next/pause/resume/stop). The video URL is retrieved using [youtube-dl](http://rg3.github.com/youtube-dl/) and the actual playback happens in the [Omxplayer](https://github.com/huceke/omxplayer).

# Technologies used

 * [web.py](http://webpy.org/) as HTTP server 
 * [youtube-dl](http://rg3.github.com/youtube-dl/) for youtube support  
 * [Omxplayer](https://github.com/huceke/omxplayer) as video player
 * [JQuery mobile](http://jquerymobile.com) UI frontend

# Installing

## Dependencies

::
	sudo apt-get install omxplayer python-pip
	sudo pip install web.py
	sudo wget http://youtube-dl.org/downloads/2013.02.02/youtube-dl -O /usr/local/bin/youtube-dl
	sudo chmod a+x /usr/local/bin/youtube-dl

## Last version of master branch

::
	cd ~
	wget https://github.com/kktuax/youtupi/archive/master.zip
	unzip master.zip

# Using

 * Launch YouTuPi server

::
	cd ~/youtupi-master
	nohup python youtupi.py >/dev/null 2>&1 &

 * Grab your Tablet/Phone/PC and go to: http://192.168.1.2:8080 (replace 192.168.1.2 with your Raspberry Pi address). If you don't know your address you can check it out with ifconfig command.
 * Enjoy!
