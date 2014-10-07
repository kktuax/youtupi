#!/bin/bash

YOUTUPI_HOME=/home/pi/youtupi
YOUTUPI_USER=pi

cd $YOUTUPI_HOME
git pull
git submodule -q foreach git pull -q origin master
chown -R $YOUTUPI_USER:$YOUTUPI_USER $YOUTUPI_HOME
