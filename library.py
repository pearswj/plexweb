from urllib2 import urlopen
import cherrypy
from config import server, player
from templates.template import template
from xml.etree.ElementTree import ElementTree
import playback
from utils import setCurrentURL

class Library:

    @cherrypy.expose
    def index(self):
        info, items = self.parseMedia("/library")
        t = template()
        t.info = info
        t.media = items
        return str(t)
    
    def parseMedia(self, key):
        # open library url
        library = "http://" + server + ":32400" + key
        print library
        xml = urlopen("http://" + server + ":32400" + key)
        
        # parse xml
        tree = ElementTree()
        tree.parse(xml)
        
        # store info from MediaContainer tag
        MediaContainer = tree.getroot()
        info = Info()
        
        info.title = getAttrib(MediaContainer, "title1")
        info.subtitle = getAttrib(MediaContainer, "title2")
        info.thumb = getAttrib(MediaContainer, "thumb")
        
        # store info from Directory/Video tags
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
        
        return info, items

    @cherrypy.expose
    def displayMedia(self, key=None):
        info, items = self.parseMedia(key)
        setCurrentURL(key=key)
        t = template()
        t.info = info
        t.media = items
        return str(t)

    #@cherrypy.expose
    def getRecentlyAdded(self):
        info, items = self.parseMedia("/library/recentlyAdded?query=c&X-Plex-Container-Start=0&X-Plex-Container-Size=10")
        return info, items
        
# function to get attribute "key" from item "tag"
def getAttrib(tag, key):
    try:
        attrib = tag.attrib[key]
    except:
        attrib = ""
    return attrib

class Info:
    title = None
    subtitle = None
    thumb = None

class Directory(object):
    def __init__(self, tag, **kwargs):
        self.title = getAttrib(tag, "title").encode('ascii', 'xmlcharrefreplace')
        self.key = getAttrib(tag, "key")
        if self.key[0] != "/":
            if kwargs.get('key') != None:
                key = kwargs.get('key')
                if key[-1] != "/":
                    key += "/"
            else:
                key = ""
            self.key = key + self.key
        self.kind = "directory"
        
class Media(Directory):
    def __init__(self, tag):
        super(Media, self).__init__(tag)
        self.key = getAttrib(tag, "key")#.rsplit("/",2).pop(1)
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
        self.numChildren = getAttrib(tag, "leafCount")

class Episode(Media):
    def __init__(self, tag):
        super(Episode, self).__init__(tag)
        self.number = getAttrib(tag, "index")
        #self.season = getAttrib(tag, "season")
    
class Movie(Media):
    def __init__(self, tag):
        super(Movie, self).__init__(tag)
        self.year = getAttrib(tag, "year")
