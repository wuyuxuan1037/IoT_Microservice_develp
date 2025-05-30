import cherrypy
import logging
from Sensor_Service.SensorServer import SensorServer
from Controller_Service.ControllerServer import ControllerServer

class App:
    
    def __init__(self):
        
        #run logger
        self.setup_loggers()
        
        #create a resource link between the sensors and broker
        # self.mqtt_client = MyMQTT()
        # self.mqtt_client.mqttStart()
        
        #initiate the server object
        sensor_server = SensorServer()
        controller_server = ControllerServer()
        
        #add a path to stop the server by url
        cherrypy.tree.mount(self, '/', {
            '/': {
                    'tools.sessions.on': True,
                }
        })
        
        #mount the resource of the severs
        cherrypy.tree.mount(sensor_server, '/sensor', sensor_server.config)
        cherrypy.tree.mount(controller_server, '/controller', controller_server.config)

        cherrypy.config.update({
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8080,
            'tools.sessions.on': True,
        })

        cherrypy.engine.start()
        cherrypy.engine.block()
        
    #exit the server by using URL
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        return "Server shut down Successfully!"
    
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
        setup_logger('mqtt', 'mqtt.log')
        setup_logger('sensor', 'sensor.log')
        setup_logger('controller', 'controller.log')
    


