"""
                                   - - - # Plexweb # - - - 

    Author: Will Pearson
    Github: pearswj

    A *simple* python webapp to control Plex Media Center via the HTTP API using Cherrpy, Cheetah and Javascript.
    
    See README.md for more info...

"""


import cherrypy
import urllib2
from xml.etree.ElementTree import ElementTree
import os.path


# ---------------------------------------------------- #
#                 Config & Start Cherrpy               #
# ---------------------------------------------------- #

# main function: configure and start cherrypy
def main():

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # General Config - EDIT ME!

    server = "firefly"  # the hostname/IP of the computer running Plex Media Server
    pmsport = "32400"   # the PMS port (default: 32400)
    player = "firefly"  # the hostname/IP of the computer running Plex Media Center
    webroot = "/plex"   # useful for reverse proxies
    port = 8082         # the port on which plexweb will run

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

    global config
    config = Config(server, pmsport, player, webroot)

    # Cherrypy Config
    data_root = os.path.join(current_dir, 'static')

    conf = {
        'global':
        {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': port,
        },
        
        '/':
        {
                'tools.staticdir.root': data_root,
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
        },
        '/js':
        {
                'tools.staticdir.on':  True,
                'tools.staticdir.dir': 'js'
        },
        '/css':
        {
                'tools.staticdir.on':  True,
                'tools.staticdir.dir': 'css'
        },
        '/favicon.ico':
        {
            'tools.staticfile.on': False,
            #'tools.staticfile.filename': '/static/favicon.ico'
        }
    }
    
    # Init Cherrypy
    cherrypy.quickstart(Plexweb(), config.webroot, conf) 


# Config class: hold config for use in templates
class Config(object):
    def __init__(self, server, port, player, webroot):
        self.server = server
        self.port = port
        self.player = player
        self.webroot = webroot


# ---------------------------------------------------- #
#                  Cheetah Template                    #
# ---------------------------------------------------- #

# Check for compiled cheetah template (templates/template.py)
cheetahCompiled = False
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.isfile(os.path.join(current_dir, 'templates/template.py')):
    from templates.template import template
    cheetahCompiled = True
else:
    from Cheetah.Template import Template
    print '''

    To speed things up, compile the cheetah template and restart plexweb!

    $ cd %s
    $ cheetah-compile --nobackup template.tmpl

    '''%(os.path.join(current_dir, 'templates/'))

# tmplt function: Populate and return template
def tmplt(info, media):
    if cheetahCompiled:
        t = template()
    else:
        t = Template(file=os.path.join(current_dir, 'templates/template.tmpl'))
    t.info = info
    t.media = media
    t.config = config
    return t


# ---------------------------------------------------- #
#                       Plexweb                        #
# ---------------------------------------------------- #

# Plexweb class: the root class called when initialising cherrypy
class Plexweb(object):

    favicon_ico = None

    # Redirect "/" to "/home"
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect(config.webroot + "/home")

    # Home: Display recently added media
    @cherrypy.expose
    def home(self):
        info, items = self.parseMedia("/library/recentlyAdded?query=c&X-Plex-Container-Start=0&X-Plex-Container-Size=20")
        info.title = "Home"
        info.subtitle = "Recently Added"
        t = tmplt(info, items)
        return str(t)

    # Library: display media from library (specified by "key")
    @cherrypy.expose
    def library(self, key="/library"):
        if key.endswith('/'):
            raise cherrypy.HTTPRedirect(config.webroot + cherrypy.request.path_info + "?key=" + key[:-1])
        info, items = self.parseMedia(key)
        t = tmplt(info, items)
        return str(t)
    
    # Parse plex xml into container classes to be passed to Cheetah template
    def parseMedia(self, key):
        # open library url
        library = "http://" + config.server + ":32400" + key
        xml = urllib2.urlopen("http://" + config.server + ":32400" + key)
        
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
                    item = Directory(i, prefix=key)
                    items.append(item)
                else:
                    if kind == "season":
                        item = Season(i)
                        items.append(item)
                    elif kind == "show":
                        item = Show(i)
                        items.append(item)
                    elif kind == None:
                        item = Directory(i, prefix=key)
                        items.append(item)
            if i.tag == "Video":
                if kind == "episode":
                    item = Episode(i)
                    items.append(item)
                elif kind == "movie":
                    item = Movie(i)
                    items.append(item)

        if key == "/library/recentlyAdded":
            info.title = "Recently Added"
        
        return info, items


# ---------------------------------------------------- #
#              Library Container Classes               #
# ---------------------------------------------------- #

# Info class: contains select keys from MediaContainer tag
class Info(object):
    def __init__(self, tag):
        self.title = tag.get("title1", default=False)
        self.subtitle = tag.get("title2", default=False)
        #self.thumb = tag.get("thumb").replace('=','%3D') # TODO: default plex image if thumb not found?
        self.mixedParents = tag.get("mixedParents", default=False)

# Directory class (and subclasses): contains select keys from various Directory and Video tags
class Directory(object):
    def __init__(self, tag, **kwargs):
        self.title = tag.get("title").encode('ascii', 'xmlcharrefreplace')
        key = tag.get("key")
        if not key.startswith("/") and kwargs.get('prefix') != None:
            self.key = kwargs.get('prefix').split("?",1)[0] + "/" + key
        else:
            self.key = key
        self.kind = "directory"
        
class Media(Directory):
    def __init__(self, tag):
        super(Media, self).__init__(tag)
        self.kind = tag.get("type")
        #self.thumb = tag.get("thumb").replace('=','%3D') # TODO: default plex image if thumb not found?
    
class Show(Media):
    def __init__(self, tag):
        super(Show, self).__init__(tag)
        self.year = tag.get("year")

class Season(Media):
    def __init__(self, tag):
        super(Season, self).__init__(tag)
        self.number = tag.get("index")
        self.numEpisodes = tag.get("leafCount")
        self.showTitle = tag.get("parentTitle")

class Episode(Media):
    def __init__(self, tag):
        super(Episode, self).__init__(tag)
        key = self.key
        self.key = key.split("?",1)[0] # strip any flags (such as "unwatched")
        self.number = tag.get("index")
        self.seasonNumber = tag.get("parentIndex")
        self.showTitle = tag.get("grandparentTitle")
    
class Movie(Media):
    def __init__(self, tag):
        super(Movie, self).__init__(tag)
        self.year = tag.get("year")



if __name__ == '__main__':
    main()
