import cherrypy
from config import webroot

currentURL = ['']

def setCurrentURL(*args, **kwargs):
    if kwargs.get('key') != None:
        currentURL[0] = cherrypy.request.path_info + "?key=" + kwargs.get('key')
    else:
        currentURL[0] = cherrypy.request.path_info

def getCurrentURL():
    return currentURL[0]

def redirect(abspath, *args, **kwargs):
    raise cherrypy.HTTPRedirect(webroot + abspath, *args, **kwargs)

