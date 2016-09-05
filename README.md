YouTuPi
=======

YouTuPi lets you play local and [YouTube](http://www.youtube.com/) videos in your [Raspberry Pi](http://www.raspberrypi.org/) using a (mobile) web interface. It provides a web UI for [Omxplayer](https://github.com/huceke/omxplayer) (the [raspbian](http://www.raspbian.org/) media player). It has two modules:
 * Local for available media in the filesystem
 * Youtube support thanks to [pafy](https://github.com/np1/pafy) 

This is an augmented fork of [kktuax' YouTuPi web app](https://github.com/kktuax/youtupi). We're cherrypicking each other's commits from time to time :)

Differences to kktuax' original:
 * Different UI.
   * Player View does not hide in a submenu.
   * Tabs are fixed on top of screen and do not scroll out of view.
 * MPD autopause while playing video.
 * Does find .ogm files in local searches.
 * REST interface prepared for third-party clients.
   * Minimal information needed, Youtube ID suffices.
   * Youtube Playlist IDs are also possible.
   * My girlfriend is writing an android app that allows sending a video or playlist from the youtube app's share menu to YouTuPi.
 * Errors like "This video is not available in your country" are displayed in playlist view.

Installation
------------

    cd ~
    curl https://raw.githubusercontent.com/orithena/youtupi/master/service/install.sh -o youtupi-install.sh
    cat youtupi-install.sh         # well, you need to check whether this shell script from the net is clean.
    chmod +x youtupi-install.sh 
    sudo ./youtupi-install.sh

Use YouTuPi
-----------

 * Start youtupi
 
    ```
    sudo /etc/init.d/youtupi start
    ```
    
 * Grab your Tablet/Phone/PC and go to: http://192.168.1.2:8080 (replace 192.168.1.2 with your Raspberry Pi address).
 * Enjoy!

# Configuration file

You can customize the download folder and some other parameters in the JSON configuration file

    nano /home/pi/youtupi/youtupi.conf

<!-- -->

    {
        "port": 8888,
        "local-folders": [
            "~/Media", "~/Downloads"
        ],
        "download-folder": "~/Downloads"
    }


## Problems?

Try updating, or installing again a newer version

    sudo /etc/init.d/youtupi update

Still no luck? Raise [an issue](https://github.com/orithena/youtupi/issues/new)
