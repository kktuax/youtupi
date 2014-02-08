YouTuPi
=======

YouTube (mobile) web frontend for your Raspberry Pi
---------------------------------------------------

YouTuPi lets you play local and [YouTube](http://www.youtube.com/) videos in your [Raspberry Pi](http://www.raspberrypi.org/) using a (mobile) web interface. 

YouTuPi provides a web UI for [Omxplayer](https://github.com/huceke/omxplayer) (the [raspbian](http://www.raspbian.org/) media player). It has two modules:
 * Local for available media in the filesystem
 * Youtube support thanks to [youtube-dl](http://rg3.github.com/youtube-dl/) 

Installation
------------

    cd ~
    curl https://raw.github.com/kktuax/youtupi/master/service/install.sh -o youtupi-install.sh
    chmod +x youtupi-install.sh 
    sudo ./youtupi-install.sh

Use YouTuPi
-----------

 * Start youtupi
 
    sudo /etc/init.d/youtupi start

 * Grab your Tablet/Phone/PC and go to: http://192.168.1.2:8080 (replace 192.168.1.2 with your Raspberry Pi address).
 * Enjoy!

# Configuration file

You can customize the download folder and some other parameters in the JSON configuration file

    nano /home/pi/youtupi/youtupi.conf

    {
        "local-folders": [
                "~/Media",
                "~/Downloads"
        ],
        "download-folder": "~/Downloads"
    }


## Updating YouTuPi

Problems? Try updating...

    sudo /etc/init.d/youtupi update
