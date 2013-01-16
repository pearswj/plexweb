'''
Plexweb class

the root class called when initialising cherrypy
'''
from Cheetah.Template import Template
from api.episode import Episode
from api.movie import Movie
from api.season import Season
from api.server import Server
from api.show import Show
from containers import Info, Directory
from xml.etree.ElementTree import ElementTree
import cherrypy
import os.path
import sys
import urllib2


class Interface(object):

    favicon_ico = None
    
    def __init__(self, webroot="", servername="localhost"):
        self.webroot = webroot
        self.servername = servername
        self.server = Server(servername, 32400)
        try:
            self.player = self.server.clients[0].name
        except IndexError:
            print "No plex clients found. Exiting..."
            sys.exit();

    # Redirect "/" to "/home"
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect(self.webroot + "/home")

    # Home: Display recently added media
    @cherrypy.expose
    def home(self):
        items =  self.server.library.recentlyAdded
        info = {'title':"Home", 'subtitle':"Recently Added", 'mixedParents':True}
        t = self.tmplt(items, info)
        return str(t)

    # Library: display media from library (specified by "key")
    @cherrypy.expose
    def library(self, key="/library"):
        if key.endswith('/'):
            raise cherrypy.HTTPRedirect(self.webroot + cherrypy.request.path_info + "?key=" + key[:-1])
        info, items = self.parseMedia(key)
        t = self.tmplt(items, info)
        return str(t)
    
    @cherrypy.expose
    def lib(self, *args):
        library = self.server.library
        o = library
        
        for arg in args:
            if isinstance(o, list) and o != library:
                try:
                    o = o[int(arg)]
                except (IndexError, ValueError) as e:
                    return e
            elif hasattr(o, '__call__'):
                try:
                    o = o(arg)
                except (AssertionError, ValueError) as e:
                    return e
            else:
                try:
                    o = getattr(o, arg)
                except AttributeError as e:
                    return e
        
        if isinstance(o, list):
#            l = []
#            for a in o:
#                l.append("%s\n" % str(vars(a)))
#            t = ''.join(l)
            t = self.tmplt(o) # template
            
        else:
            t = vars(o) # simple print
        return str(t)
    
    # Parse plex xml into container classes to be passed to Cheetah template
    def parseMedia(self, key):
        # TODO: Use self.server.query or self.server.library.mediaByType instead
        # open library url
        #library = "http://" + config.server + ":32400" + key
        xml = urllib2.urlopen("http://" + self.servername + ":32400" + key)
        
        # parse xml
        tree = ElementTree()
        tree.parse(xml)
        
        # store info from MediaContainer tag
        MediaContainer = tree.getroot()
        info = Info(MediaContainer)
        
        # store items from Directory/Video tags
        xmlItems = list(tree.iter())
        items = []
        for i in xmlItems:
            kind = i.get("type")
            
            if i.tag == "Directory":
                if key[:17] == "/library/sections": # Don't interpret sections as media items
                    items.append(Directory(i, prefix=key))
                else:
                    if kind == "season":
                        items.append(Season(i, self.server))
                    elif kind == "show":
                        items.append(Show(i, self.server))
                    elif kind == None:
                        items.append(Directory(i, prefix=key))
            if i.tag == "Video":
                if kind == "episode":
                    items.append(Episode(i, self.server))
                elif kind == "movie":
                    items.append(Movie(i, self.server))

        if key == "/library/recentlyAdded":
            info.title = "Recently Added"
        
        return info, items

    @cherrypy.expose
    def changePlayer(self, player):
        #self.player = self.server.clients[int(index)].name
        self.player = player
        print "Plex client changed: " + self.player
        
    def tmplt(self, media, info=Info()):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        t = Template(file=os.path.join(current_dir, 'templates/template.tmpl'))
        t.info = info
        t.media = media
        t.config = {"server":self.servername, "port":"32400", "player":self.player, "webroot":self.webroot}
        t.clients = self.server.clients
        #t.clients.append({"name":"test"})
        return t
