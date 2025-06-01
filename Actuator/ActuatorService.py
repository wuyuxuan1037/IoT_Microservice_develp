import cherrypy
import json
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from Util.Utility import PathUtils, FileUtils, Utility, Log
from Util import CORS
from Controller.Controller import Controller

import logging
logger = logging.getLogger('actuator')

class ActuatorServer:
    
    def __init__(self):

        pass
    
    @cherrypy.expose
    def shutdown(self):
        logger.info('Actuator server is closed successfully')
        cherrypy.engine.exit()
    
if __name__ == '__main__':
    
    Log.setup_loggers('actuator')
    
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8083,
        'tools.sessions.on': False
    })
    
    config = {
            '/': {
                'tools.CORS.on': True,
            }
    }
    
    cherrypy.quickstart(ActuatorServer(), '/actuator', config)