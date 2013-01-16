"""
                                   - - - # Plexweb # - - - 

    Author: Will Pearson
    Github: pearswj

    A *simple* python webapp to control Plex Media Center via the HTTP API using Cherrpy, Cheetah and Javascript.
    
    See README.md for more info...

"""


from interface import Interface
import argparse
import cherrypy
import os.path


def main():

    parser = argparse.ArgumentParser(description='A *simple* python webapp to control Plex Media Center via the HTTP API using Cherrpy, Cheetah and Javascript.') 
    parser.add_argument('--server', default='localhost',
                        help='the address/hostname of the computer running plex media server')
    parser.add_argument('--webroot', default='')
    parser.add_argument('--port', type=int, default=8082,
                        help='the port on which to run plexweb')
    args = parser.parse_args()

    # Cherrypy Config
    data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    conf = {
        'global':
        {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': args.port,
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
    cherrypy.quickstart(Interface(args.webroot, args.server), args.webroot, conf) 


if __name__ == '__main__':
    main()
