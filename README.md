YouTuPi
=======

YouTuPi lets you play local and [YouTube](http://www.youtube.com/) videos in your [Raspberry Pi](http://www.raspberrypi.org/) using a (mobile) web interface. It provides a web UI for [Omxplayer](https://github.com/huceke/omxplayer) (the [raspbian](http://www.raspbian.org/) media player). It has two modules:
 * Local for available media in the filesystem
 * Youtube support thanks to [pafy](https://github.com/np1/pafy) 

Installation
------------

    cd ~
    curl https://raw.githubusercontent.com/kktuax/youtupi/master/service/install.sh -o youtupi-install.sh
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
        "local-folders": [
            "~/Media", "~/Downloads"
        ],
        "download-folder": "~/Downloads"
    }


## Problems?

Try updating, or installing again a newer version

    sudo /etc/init.d/youtupi update

Still no luck? Raise [an issue](https://github.com/kktuax/youtupi/issues/new)
