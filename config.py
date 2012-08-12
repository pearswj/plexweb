import cherrypy
import os

prog_dir = os.getcwd()
data_root = os.path.join(prog_dir, 'static')

# Config
conf = {
    'global':
    {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8082,
    },
    
    '/':
    {
            'tools.staticdir.root': data_root,
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8',
    },
    '/images':
    {
            'tools.staticdir.on':  True,
            'tools.staticdir.dir': 'images'
    },
    #'/js':
    #{
    #        'tools.staticdir.on':  True,
    #        'tools.staticdir.dir': 'js'
    #},
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

server = "firefly"
player = "firefly"
webroot = "/plex"
