"""
                                   - - - # Plexweb # - - - 

    Author: Will Pearson
    Github: pearswj

    A *simple* webinterface to control Plex Media Center using Cherrpy, Cheetah and Javascript
    Only handles TV Shows and Movies -- feel free to expand it!
    Tested on Linux and Mac OSX
    
    Usage:
    $ python2 /path/to/plexweb.py
    (And open 'http://[hostname/IP]:8082[webroot]' in your browser)

    Hotkeys:
    h     - home
    l     - library
    space - play/pause
    x     - stop
    right - step forward
    left  - step back

"""


import cherrypy
import urllib2
from xml.etree.ElementTree import ElementTree
import os.path


# ---------------------------------------------------- #
#                 Config & Start Cherrpy               #
# ---------------------------------------------------- #

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

# Populate and return template
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
#                       Library                        #
# ---------------------------------------------------- #

class Library:
    @cherrypy.expose
    def index(self):
        info, items = self.parseMedia("/library")
        t = tmplt(info, items)
        return str(t)
    
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
            kind = getAttrib(i, "type")
            
            if i.tag == "Directory":
                if key[:17] == "/library/sections":
                    item = Directory(i, key=key)
                    items.append(item)
                else:
                    if kind == "season":
                        item = Season(i)
                        items.append(item)
                    elif kind == "show":
                        item = Show(i)
                        items.append(item)
                    elif kind == "":
                        item = Directory(i, key=key)
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

    def getRecentlyAdded(self):
        info, items = self.parseMedia("/library/recentlyAdded?query=c&X-Plex-Container-Start=0&X-Plex-Container-Size=20")
        return info, items

    @cherrypy.expose
    def displayMedia(self, key=None):
        if key.endswith('/'):
            raise cherrypy.HTTPRedirect(config.webroot + cherrypy.request.path_info + "?key=" + key[:-1])
        info, items = self.parseMedia(key)
        t = tmplt(info, items)
        return str(t)

        
# function to get attribute "key" from item "tag"
def getAttrib(tag, key, false=""):
    try:
        attrib = tag.attrib[key]
    except:
        attrib = false
    return attrib

class Info(object):
    def __init__(self, tag):
        self.title = getAttrib(tag, "title1", false=False)
        self.subtitle = getAttrib(tag, "title2", false=False)
        #self.thumb = getAttrib(tag, "thumb").replace('=','%3D') # default plex image if thumb not found?
        self.mixedParents = getAttrib(tag, "mixedParents", false=False)

class Directory(object):
    def __init__(self, tag, **kwargs):
        self.title = getAttrib(tag, "title").encode('ascii', 'xmlcharrefreplace')
        key = getAttrib(tag, "key")
        if not key.startswith("/") and kwargs.get('key') != None:
            self.key = kwargs.get('key') + "/" + key
        else:
            self.key = key
        self.kind = "directory"
        
class Media(Directory):
    def __init__(self, tag):
        super(Media, self).__init__(tag)
        self.kind = getAttrib(tag, "type")
        self.thumb = getAttrib(tag, "thumb").replace('=','%3D') # default plex image if thumb not found?
    
class Show(Media):
    def __init__(self, tag):
        super(Show, self).__init__(tag)
        self.year = getAttrib(tag, "year")

class Season(Media):
    def __init__(self, tag):
        super(Season, self).__init__(tag)
        self.number = getAttrib(tag, "index")
        self.numEpisodes = getAttrib(tag, "leafCount")
        self.showTitle = getAttrib(tag, "parentTitle")

class Episode(Media):
    def __init__(self, tag):
        super(Episode, self).__init__(tag)
        key = self.key
        self.key = key.split("?",1)[0] # strip any flags (such as "unwatched")
        self.number = getAttrib(tag, "index")
        self.seasonNumber = getAttrib(tag, "parentIndex")
        self.showTitle = getAttrib(tag, "grandparentTitle")
    
class Movie(Media):
    def __init__(self, tag):
        super(Movie, self).__init__(tag)
        self.year = getAttrib(tag, "year")


# ---------------------------------------------------- #
#                       Plexweb                        #
# ---------------------------------------------------- #

class Plexweb(object):

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect(config.webroot + "/home")

    @cherrypy.expose
    def home(self):
        info, items = Library().getRecentlyAdded()
        info.title = "Recently Added"
        t = tmplt(info, items)
        return str(t)

    library = Library()
    favicon_ico = None


if __name__ == '__main__':
    main()
