import logging
import cherrypy
import json
import os,sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from Util.Utility import PathUtils, FileUtils, Utility, Log
from Util import CORS
from Sensor.Sensor import Sensor
logger = logging.getLogger('sensor')

class SensorServer:
    
    def __init__(self):  
        #register all sensors for servers
        self.sensorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["sensor_list"]
        #store registered sensors in the List for dynamic to adjust the running sensors 
        self.registered_sensors = []
        #iterate the sensor list
        for sensor in self.sensorList:
            sensorObject = Sensor(sensor["deviceID"], sensor["deviceType"], sensor["deviceLocation"], sensor["topic"], sensor["unit"], sensor["info_frequency"], sensor["status"])
            self.registered_sensors.append(sensorObject)

        #update sensor status (control the sensor published to the MQTT broker)
        for sensor in self.registered_sensors:
            sensor.start()
    
    #show all sensors from the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getSensorDevice(self):
        sensorsList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["sensor_list"]
        return sensorsList
    
    #add a new sensor device
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def addSensorDevice(self):
    
        #allocate the ID to the new device
        deviceID = Utility.generate_device_id()
        
        #obtain the parameter from the front-end page
        deviceType = cherrypy.request.json.get("type")
        deviceLocation = cherrypy.request.json.get("location")
        topic = f"PoliTO_IotSmartFarm/{deviceLocation}/{deviceType}/{deviceID}"
        unit = cherrypy.request.json.get("unit")
        info_frequency = cherrypy.request.json.get("updateFrequency")
        status = True
        
        #initiate the sensor to the registered Sensor
        newDeviceObject = Sensor(deviceID, deviceType, deviceLocation, topic, unit, info_frequency, status)
        self.registered_sensors.append(newDeviceObject)
        newDeviceObject.start()
        
        #loading configuration file
        new_config = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        
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
        
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=4)
        
        return { "status": "success", "message": "Device added successfully." }
    
    #delete a existed sensor device
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def deleteSensorDevice(self):

        #obtain the ID that need to be deleted
        deviceID = cherrypy.request.json.get('deviceID')
        #delete the sensor from the registeredList and stop running
        for sensor in self.registered_sensors:
            if sensor.deviceID == deviceID:
                sensor.stop()
                self.registered_sensors.remove(sensor)
                break
            
        #delete the sensor from the configuration
        sensorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        for sensor in sensorList["sensor_list"]:
            if sensor['deviceID'] == deviceID:
                sensorList["sensor_list"].remove(sensor)
                break
            
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(sensorList, f, indent=4)        
        
        return { "status": "success", "message": "Device deleted successfully." }
    
    #update the status of the sensor
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def updateSensorStatus(self):
        
        #obtain the parameter from the front # end 
        deviceList = cherrypy.request.json.get('device_ids')
        targetStatus = cherrypy.request.json.get('target_status')
        
        #update the device in the registeredList
        for deviceID in deviceList:
            for sensor in self.registered_sensors:
                if deviceID == sensor.deviceID:
                    if targetStatus:
                        sensor.status=True
                        sensor.start()
                    else:
                        sensor.stop()
                    break
                
        #update the sensors status of the cataLog
        sensorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        for deviceID in deviceList:
            for sensor in sensorList["sensor_list"]:
                if sensor['deviceID'] == deviceID:
                    sensor['status'] = targetStatus
                    break
                
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(sensorList, f, indent=4) 
        
        return { "status": "success", "message": "Status updated successfully." }

    @cherrypy.expose
    def shutdown(self):
        logger.info('Sensor server is closed successfully')
        cherrypy.engine.exit()
        return 'Sensor server is closed successfully'
    
if __name__ == '__main__':
    
    Log.setup_loggers('sensor')
    
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8081,
        'tools.sessions.on': False
    })
    
    config = {
            '/': {
                'tools.CORS.on': True,
            }
    }
    
    cherrypy.quickstart(SensorServer(), '/sensor', config)