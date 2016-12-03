YouTuPi
=======

YouTuPi lets you play local and [YouTube](http://www.youtube.com/) videos in your
[Raspberry Pi](http://www.raspberrypi.org/) using a (mobile) web interface. It
provides a web UI for [Omxplayer](https://github.com/huceke/omxplayer) (the
[raspbian](http://www.raspbian.org/) media player). It has three modules:

 * Local file search and browse for available media in the filesystem
 * Youtube support thanks to [pafy](https://github.com/np1/pafy)
 * Paste video URL from anywhere

Screenshots
-----------

![Player View](https://cloud.githubusercontent.com/assets/2767109/18413068/799c9754-779e-11e6-8b27-5141d20c0071.png)
![Search Youtube](https://cloud.githubusercontent.com/assets/2767109/18413069/7e71871c-779e-11e6-9eb2-79928385b35d.png)
![Search Local Files](https://cloud.githubusercontent.com/assets/2767109/18413070/84eda3e6-779e-11e6-904e-2ad9b17f24b9.png)
![Settings View](https://cloud.githubusercontent.com/assets/2767109/18413065/6cc8f004-779e-11e6-8c7b-0dcab3ac3df9.png)


Manual installation
-------------------

1. Install dependencies:

    ```bash
    sudo apt-get update
    sudo apt-get install omxplayer python-pip python-magic python-dbus git
    sudo pip install web.py beautifulsoup4 youtube_dl betterprint
    ```

2. Clone repository:

    ```bash
    YOUTUPI_HOME=/home/pi/youtupi
    git clone git://github.com/kktuax/youtupi.git $YOUTUPI_HOME
    cd $YOUTUPI_HOME
    cp youtupi.conf.example youtupi.conf
    git submodule init
    git submodule update
    ```

3. Register service:

    ```bash
    sudo cp $YOUTUPI_HOME/service/youtupi /etc/init.d/
    sudo update-rc.d youtupi defaults
    ```

Note: If you want to run youtupi under a different user than `pi` or from a different directory, you'll need to modify `/etc/init.d/youtupi` before starting it.


Scripted installation
---------------------

    cd ~
    curl https://raw.githubusercontent.com/kktuax/youtupi/master/service/install.sh -o youtupi-install.sh
    cat youtupi-install.sh         # well, you need to check whether this shell script from the net is clean.
    chmod +x youtupi-install.sh
    sudo ./youtupi-install.sh

Note: If you want to run youtupi under a different user than `pi` or from a different directory than `/home/pi/youtupi/`, you'll need to modify `youtupi-install.sh` after downloading and `/etc/init.d/youtupi` after installing.

Use YouTuPi
-----------

 * Start youtupi

    ```
    sudo /etc/init.d/youtupi start
    ```

 * Grab your Tablet/Phone/PC and go to: http://192.168.1.2:8080 (replace 192.168.1.2 with your Raspberry Pi address).
 * Enjoy!

Debug YouTuPi
-------------

 * Don't start the service (or stop it), then cd into `/home/pi/youtupi` and run it from the command line:

    ```
    sudo /etc/init.d/youtupi stop
    cd /home/pi/youtupi
    python youtupi.py
    ```

 * Grab your Tablet/Phone/PC and go to: http://192.168.1.2:8080 (replace 192.168.1.2 with your Raspberry Pi address).

This'll give you all the debug messages on the command line. Add more by adding print/pprint statements to the code.


# Configuration file

You can customize the download folder and some other parameters in the JSON configuration file

    nano ~/youtupi/youtupi.conf

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

Still no luck? Raise [an issue](https://github.com/kktuax/youtupi/issues/new)
