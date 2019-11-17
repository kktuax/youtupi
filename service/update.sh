#!/bin/bash

INSTALL_SCRIPT='https://raw.githubusercontent.com/kktuax/youtupi/master/service/install.sh'
YOUTUPI_HOME=/home/pi/youtupi
YOUTUPI_USER=pi

systemctl stop youtupi

apt-get update
curl -s $INSTALL_SCRIPT | grep 'apt-get install -y' | awk '{split($0,a," -y "); print a[2]}' | apt-get install -y

DEPS=$(curl -s $INSTALL_SCRIPT | grep 'pip install' | awk '{split($0,a," install "); print a[2]}')
pip install -I $DEPS
pip install --upgrade youtube_dl

cd $YOUTUPI_HOME
git pull
git submodule update
chown -R $YOUTUPI_USER:$YOUTUPI_USER $YOUTUPI_HOME

systemctl start youtupi
