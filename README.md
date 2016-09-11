YouTuPi
=======

YouTuPi lets you play local and [YouTube](http://www.youtube.com/) videos in your 
[Raspberry Pi](http://www.raspberrypi.org/) using a (mobile) web interface. It 
provides a web UI for [Omxplayer](https://github.com/huceke/omxplayer) (the 
[raspbian](http://www.raspbian.org/) media player). It has three modules:

 * Local file search and browse for available media in the filesystem
 * Youtube support thanks to [pafy](https://github.com/np1/pafy) 
 * Paste video URL from anywhere

This is an augmented fork of [kktuax' YouTuPi web app](https://github.com/kktuax/youtupi). 
We're cherrypicking each other's commits from time to time :)

Differences to kktuax' original:
 * Slight UI changes:
   * Player View does not hide in a submenu.
   * Tabs are fixed on top of screen and do not scroll out of view.
 * MPD autopause while playing video.
 * Does find .ogm files in local searches.
 * Is able to browse the folder structure.
 * Can submit arbitrary pasted video URLs to omxplayer.
 * REST interface prepared for third-party clients.
   * Minimal information needed, Youtube ID suffices.
   * Youtube Playlist IDs are also possible.
 * Errors like "This video is not available in your country" are displayed in playlist view.

Screenshots
-----------

![Player View](https://cloud.githubusercontent.com/assets/2767109/18413068/799c9754-779e-11e6-8b27-5141d20c0071.png)
![Search Youtube](https://cloud.githubusercontent.com/assets/2767109/18413069/7e71871c-779e-11e6-9eb2-79928385b35d.png)
![Search Local Files](https://cloud.githubusercontent.com/assets/2767109/18413070/84eda3e6-779e-11e6-904e-2ad9b17f24b9.png)
![Settings View](https://cloud.githubusercontent.com/assets/2767109/18413065/6cc8f004-779e-11e6-8c7b-0dcab3ac3df9.png)


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
