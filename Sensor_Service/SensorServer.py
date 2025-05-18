import cherrypy
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Util.PathUtils import PathUtils
from Util.FileUtils import FileUtils
from Sensor import Sensor
import threading
import time

class SensorServer:
    
    def __init__(self):
        #basic settings for the server
        cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080
    })
        self.app_config = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd())
        }
    }
        #register all sensors for servers
        self.sensorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"cataLog.json"))["sensor_list"]
        #store registered sensors in the List for dynamic to adjust the running sensors 
        self.registered_sensors = []
        #iterate the sensor list
        for sensor in self.sensorList:
            sensorObject = Sensor(sensor["deviceID"], sensor["deviceType"], sensor["deviceLocation"], 
                                sensor["topic"], sensor["unit"], sensor["info_frequency"], sensor["status"])
            self.registered_sensors.append(sensorObject)

        #update sensor status (control the sensor published to the MQTT broker)
        for sensor in self.registered_sensors:
            sensor.start()
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def GET(self):
        return self.sensorList
    
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        return "SensorServer shut down Successfully!"
    

if __name__ == '__main__':

    Server = SensorServer()

    cherrypy.tree.mount(Server, '/', Server.app_config)
    cherrypy.engine.start()
    cherrypy.engine.block()
