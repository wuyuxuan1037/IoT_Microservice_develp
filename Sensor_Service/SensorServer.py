import cherrypy
import json
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Util.PathUtils import PathUtils
from Util.FileUtils import FileUtils
from Util.Utility import Utility
from Sensor import Sensor

class SensorServer:
    
    def __init__(self):
        #basic settings for the server
        cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8081
    })
        
        #start the CORS service
        cherrypy.tools.CORS = cherrypy.Tool('before_handler', Utility.CORS)
        
        self.app_config = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.CORS.on': True
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
    
    #show all sensors form the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getSensorDevice(self):
        sensorsList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"cataLog.json"))["sensor_list"]
        return sensorsList
    
    #insert a new sensor's configuration to the cataLog.json
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def addSensorDevice(self):
        # handle CORS pre-request
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.status = 200
            return ""
        
        #allocate the ID to the new device
        deviceID = Utility.generate_device_id()
        
        #obtain the parameter from the front-end page
        deviceType = cherrypy.request.json.get("type")
        deviceLocation = cherrypy.request.json.get("location")
        topic = f"TO_IotSmartFarm/{deviceLocation}/temperature/{deviceID}"
        unit = cherrypy.request.json.get("unit")
        info_frequency = cherrypy.request.json.get("updateFrequency")
        status = True
        
        #initiate the sensor to the registered Sensor
        newDeviceObject = Sensor(deviceID, deviceType, deviceLocation, topic, unit, info_frequency, status)
        self.registered_sensors.append(newDeviceObject)
        newDeviceObject.start()
        
        #loading configuration file
        new_config = FileUtils.load_config(os.path.join(PathUtils.project_path(),"cataLog.json"))
        
        #update the information of the cataLog
        newSensor = {
            "deviceID": deviceID,
            "deviceType": deviceType,
            "deviceLocation": deviceLocation,
            "topic": topic,
            "unit": unit,
            "info_frequency": info_frequency,
            "status": status
        }
        
        new_config["sensor_list"].append(newSensor)
        
        #store the file
        with open(os.path.join(PathUtils.project_path(),"cataLog.json"), 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=4)
        
        return { "status": "success", "message": "Device added successfully." }
    
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        return "SensorServer shut down Successfully!"
    

    
    @cherrypy.expose
    def OPTIONS(self, *args, **kwargs):
        Utility.CORS()
        return ""
    

if __name__ == '__main__':

    Server = SensorServer()

    cherrypy.tree.mount(Server, '/', Server.app_config)
    cherrypy.engine.start()
    cherrypy.engine.block()
