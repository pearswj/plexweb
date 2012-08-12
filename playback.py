import cherrypy
import urllib2
import config
from utils import getCurrentURL, redirect

class Playback:

    @cherrypy.expose
    def default(self, command=None, **kwargs):
        if command == None:
            return "Something's gone wrong..."
        else:
            if kwargs.get('player') != None:
                player = kwargs.get('player')
            else:
                player = config.player

            # create command url
            port = "32400"
            serverURL = "http://" + config.server + ":" + port
            commandURL = serverURL + "/system/players/" + player + "/playback/" + command

            # call command url
            urllib2.urlopen(commandURL)
            
            # redirect to previous page
            if kwargs.get('player') == None: # allows for standalone usage
                redirect(getCurrentURL())

