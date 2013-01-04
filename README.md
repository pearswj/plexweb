# Plexweb

A *simple* python webapp to control Plex Media Center via the HTTP API using Cherrpy, Cheetah and Javascript. Allows control over the playback of media beyond the _start playing this media on that client_ functionality of Plex/Web.

Only handles TV Shows and Movies -- feel free to expand it!

Tested on Linux and Mac OSX.
    
## Usage:

    $ python2 /path/to/plexweb.py

(And open 'http://[hostname/IP]:8082[webroot]' in your browser)

## Hotkeys:

* `h`     - home
* `l`     - library
* `space` - play/pause
* `x`     - stop
* `right` - step forward
* `left`  - step back
* `Alt + right` - big step forward
* `Alt + left`  - big step back
* `up`    - volume up
* `down`  - volume down
* `u`     - toggle between 'all' and 'unwatched' views

## To Do:

* implement megawubs/plex-api-wrapper
* use api to get client list and implement as dropdown
* set config.server to localhost by default and add commandline argument
* optional: add commandline arg for plexweb port and webroot
* optional: refine keyboard shortcuts and display when `?` is pressed
