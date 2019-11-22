#!/bin/bash

YOUTUPI_HOME=/home/pi/youtupi
YOUTUPI_USER=pi

if [ -d "$YOUTUPI_HOME" ]; then
	rm -rf $YOUTUPI_HOME
fi

apt-get update && apt-get install -y libpcre3 fonts-freefont-ttf omxplayer python-pip python-magic python-dbus python-lxml git 
pip install web.py beautifulsoup4 youtube_dl betterprint
git clone git://github.com/kktuax/youtupi.git $YOUTUPI_HOME
cd $YOUTUPI_HOME
git submodule init
git submodule update
cp youtupi.conf.example youtupi.conf
chown -R $YOUTUPI_USER:$YOUTUPI_USER $YOUTUPI_HOME

cp $YOUTUPI_HOME/service/youtupi.service /etc/systemd/system/
cp $YOUTUPI_HOME/service/youtupi-update.service /etc/systemd/system/
cp $YOUTUPI_HOME/service/youtupi-update.timer /etc/systemd/system/
systemctl enable youtupi
systemctl start youtupi
systemctl enable youtupi-update.timer
systemctl start youtupi-update.timer
