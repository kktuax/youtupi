#!/bin/bash

YOUTUPI_HOME=/home/pi/youtupi
YOUTUPI_USER=pi

pip install --upgrade youtube_dl
cd $YOUTUPI_HOME
git pull
git submodule update
chown -R $YOUTUPI_USER:$YOUTUPI_USER $YOUTUPI_HOME
