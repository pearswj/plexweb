import cherrypy
import urllib2
from xml.etree.ElementTree import ElementTree
import library
from config import conf, webroot, server, player
import config
import playback
#import playback.playMedia as 
from templates.plex import plex
from templates.template import template
from utils import setCurrentURL, getCurrentURL, redirect


class Home(object):

    @cherrypy.expose
    def index(self):
        redirect("/home")

    @cherrypy.expose
    def home(self):
        info, items = library.Library().getRecentlyAdded()

        #for i in items:
            #print i.title + " -- " + str(i.kind)
            #print str(i)
         
        setCurrentURL()
        info.title = "Recently Added"
        t = template()
        #t.urlBase = "http://" + server + ":32400"
        t.info = info
        t.media = items
        return str(t)

    @cherrypy.expose
    def playMedia(self, key=None, server=config.server, player=config.player):
        if key == None:
            return "Something's gone wrong..."
        else:
            port = "32400"
            serverURL = "http://" + server + ":" + port
            playURL = serverURL + "/system/players/" + player + "/application/playMedia?key=" + key + "&path=" + serverURL + key
            
            # call command url
            urllib2.urlopen(playURL)
            
            # redirect to previous page
            redirect(getCurrentURL())

    library = library.Library()
    playback = playback.Playback()
    
    favicon_ico = None


if __name__ == '__main__':
    cherrypy.quickstart(Home(), webroot, conf) 

