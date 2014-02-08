#!/bin/bash

YOUTUPI_HOME=/home/pi/youtupi
YOUTUPI_USER=pi

curl https://yt-dl.org/latest/youtube-dl -o /usr/local/bin/youtube-dl
apt-get install omxplayer python-pip python-magic git
pip install web.py beautifulsoup4
git clone git://github.com/kktuax/youtupi.git $YOUTUPI_HOME
cd $YOUTUPI_HOME
git submodule init
git submodule update
chown -R $YOUTUPI_USER:$YOUTUPI_USER $YOUTUPI_HOME
cp $YOUTUPI_HOME/service/youtupi /etc/init.d/
update-rc.d youtupi defaults
/etc/init.d/youtupi start
