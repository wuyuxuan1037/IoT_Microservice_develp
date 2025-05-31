import os
import cherrypy
import logging
from Sensor_Service.SensorServer import SensorServer
from Controller_Service.ControllerServer import ControllerServer
from TelegramBot_Service.TelebotServer import MyTelegramBot

#Create a global CORS
def CORS_tool():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
# Register a global CORS tool to allow cross-origin requests from any origin (*)
# Applied via decorator @cherrypy.tools.CORS() or via config: 'tools.CORS.on': True
cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS_tool)

class App:
    
    def __init__(self):
        
        #run logger
        self.setup_loggers()
        
        self.config_staticdir = {
            '/': {
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.CORS.on': True,
            }
    }   
        self.config_noStaticdir = {
            '/': {
                'tools.CORS.on': True,
            }
    } 
        #initiate the server object
        self.sensor_server = SensorServer()
        self.controller_server = ControllerServer()
        self.telegramBot_server = MyTelegramBot()
        
        #mount the resource of the severs
        cherrypy.tree.mount(self, '/', self.config_noStaticdir)
        cherrypy.tree.mount(self.sensor_server, '/sensor', self.config_noStaticdir)
        cherrypy.tree.mount(self.controller_server, '/controller', self.config_noStaticdir)

        #set the ip and port
        cherrypy.config.update({
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8080,
            'tools.sessions.on': False,
        })

        #start the servers
        self.telegramBot_server.run()
        cherrypy.engine.start()
        cherrypy.engine.block()
        
    #exit the server by using URL
    @cherrypy.expose
    def shutdown(self):
        if hasattr(self, 'telegramBot_server'):
            self.telegramBot_server.stop()
        cherrypy.engine.exit()
        return "Server shut down Successfully!"
    
    @cherrypy.expose
    def OPTIONS(self, *args, **kwargs):
        CORS_tool()
        return ""
    
    def setup_loggers(self):
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        def setup_logger(name, filename):
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)

            if logger.hasHandlers():
                logger.handlers.clear()

            handler = logging.FileHandler(filename, mode='w')
            handler.setFormatter(log_formatter)
            logger.addHandler(handler)

        # Configure the log for different modules
        setup_logger('mqtt', 'logs/mqtt.log')
        setup_logger('sensor', 'logs/sensor.log')
        setup_logger('controller', 'logs/controller.log')
        setup_logger('telebot', 'logs/telebot.log')
    


