import cherrypy
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from Util import CORS
from Util.Utility import Log
Log.setup_loggers('http')
logger = logging.getLogger('http')

class HttpServer:
    
    @cherrypy.expose
    def index(self):
        index_path = os.path.join(project_root, 'Http','dist', 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
        
    @cherrypy.expose
    def default(self, *args, **kwargs):
        index_path = os.path.join(project_root, 'Http','dist', 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
        
    @cherrypy.expose
    def shutdown(self):
        logger.info('Http server is closed successfully')
        cherrypy.engine.exit()
        

if __name__ == '__main__':
    
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
        'tools.sessions.on': False
    })
    
    config = {
            '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(project_root, 'Http','dist'),
                'tools.CORS.on': True
            }
    }
    
    cherrypy.quickstart(HttpServer(), '/', config)