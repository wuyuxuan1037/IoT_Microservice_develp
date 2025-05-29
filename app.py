import cherrypy
from Sensor_Service.SensorServer import SensorServer
from Controller_Service.ControllerServer import ControllerServer

class App:
    
    def __init__(self):
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
    


