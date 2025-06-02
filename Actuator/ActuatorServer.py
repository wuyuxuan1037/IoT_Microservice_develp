from datetime import datetime
import time
import cherrypy
import json
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from Util.Utility import PathUtils, FileUtils, Utility, Log
from Util import CORS
from Actuator.Actuator import Actuator

import logging
logger = logging.getLogger('actuator')

class ActuatorServer:
    
    def __init__(self):

        #register all actuators for servers
        self.actuatorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["actuator_list"]
        #store registered actuators in the List for dynamic to adjust the running actuators 
        self.registered_actuators = []
        #iterate the actuator list
        for actuator in self.actuatorList:
            actuatorObject = Actuator(actuator["deviceID"], actuator["deviceType"], actuator["deviceLocation"], 
                                actuator["topic"], actuator["lastStatusUpdate"], actuator["status"])
            self.registered_actuators.append(actuatorObject)
            
    #show all actuators from the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getActuatorDevice(self):
        actuatorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["actuator_list"]
        logger.info(f'Print the actuator lists.')
        return actuatorList
    
    #add a new actuator device
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def addActuatorDevice(self):
        
        logger.info('start to add a new actuator device.')
    
        #allocate the ID to the new device
        deviceID = Utility.generate_device_id()
        
        #obtain the parameter from the front-end page
        deviceType = cherrypy.request.json.get("type")
        deviceLocation = cherrypy.request.json.get("location")
        topic = f"PoliTO_IotSmartFarm/{deviceLocation}/+/+/{deviceType}"
        #obtain current time
        timestamp = time.time()
        #convert timestamp into time object
        dt = datetime.fromtimestamp(timestamp)
        #define the format  of the time to display
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        lastStatusUpdate = formatted_time
        status = True
        
        logger.info(f'CREATE - {deviceID} - {deviceType} - {topic}')
        
        #initiate the actuator to the registered actuator
        newDeviceObject = Actuator(deviceID, deviceType, deviceLocation, topic, lastStatusUpdate, status)
        self.registered_actuators.append(newDeviceObject)
        newDeviceObject.start()
        
        #loading configuration file
        new_config = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        
        #update the information of the cataLog
        newActuator = {
            "deviceID": deviceID,
            "deviceType": deviceType,
            "deviceLocation": deviceLocation,
            "topic": topic,
            "lastStatusUpdate": lastStatusUpdate,
            "status": status
        }
        
        new_config["actuator_list"].append(newActuator)
        
        logger.info(f'Successfully create [{deviceID}] - {deviceType} - {deviceLocation}.')
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=4)
        
        return { "status": "success", "message": "Device added successfully." }
    
    #update the status of the actuator
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def deleteActuatorDevice(self):

        #obtain the ID that need to be deleted
        deviceID = cherrypy.request.json.get('deviceID')
        logger.info(f'Start to delete - [{deviceID}] - actuator device.')
        #delete the actuator from the registeredList and stop running
        for actuator in self.registered_actuators:
            if actuator.deviceID == deviceID:
                actuator.stop()
                self.registered_actuators.remove(actuator)
                logger.info(f'Successfully to remove - [{deviceID}] - from registered_actuators.')
                break
            
        #delete the actuator from the configuration
        actuatorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        for actuator in actuatorList["actuator_list"]:
            if actuator['deviceID'] == deviceID:
                actuatorList["actuator_list"].remove(actuator)
                logger.info(f'Successfully to remove - [{deviceID}] - from configuration.')
                break
            
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(actuatorList, f, indent=4)        
        
        return { "status": "success", "message": "Device deleted successfully." }
    
    #update the status of the actuator
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def updateActuatorStatus(self):
        
        #obtain the parameter from the front # end 
        deviceList = cherrypy.request.json.get('device_ids')
        targetStatus = cherrypy.request.json.get('target_status')
        
        logger.info(f'Start to update [{deviceList}] to status [{targetStatus}]')
        #update the device in the registeredList
        for deviceID in deviceList:
            for actuator in self.registered_actuators:
                if deviceID == actuator.deviceID:
                    if targetStatus:
                        actuator.status=True
                        actuator.start()
                    else:
                        actuator.stop()
                    break
        logger.info(f'Change the registered_actuators [{deviceList}] to status [{targetStatus}]')
        #update the actuators status of the cataLog
        actuatorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        for deviceID in deviceList:
            for actuator in actuatorList["actuator_list"]:
                if actuator['deviceID'] == deviceID:
                    actuator['status'] = targetStatus
                    break
        
        logger.info(f'Change the configuration [{deviceList}] to status [{targetStatus}]')
                
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(actuatorList, f, indent=4) 
        
        return { "status": "success", "message": "Status updated successfully." }

    
    @cherrypy.expose
    def shutdown(self):
        logger.info('Actuator server is closed successfully')
        cherrypy.engine.exit()
        return "Actuator server is closed successfully"
    
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