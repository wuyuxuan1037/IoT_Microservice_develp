import math
import time
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
logger = logging.getLogger('controller')

class ControllerServer:
    
    def __init__(self):

        #register all controllers for servers
        self.controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["controller_list"]
        #store registered controllers in the List for dynamic to adjust the running sensors 
        self.registered_controllers = []
        #iterate the controller list
        for controller in self.controllerList:
            controllerObject = Controller(controller["deviceType"], controller["subscribeTopic"], 
                                            controller["thresholdMax"], controller["thresholdMin"],controller["unit"])
            self.registered_controllers.append(controllerObject)
            
        self.dashboardData = []
        
    #show all controllers form the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerThreshold(self):
        controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["controller_list"]
        return controllerList
    
    #update the MAX and MIN of threshold
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def updateControllerThreshold(self):

        #obtain the parameter from the front # end 
        deviceType = cherrypy.request.json.get("deviceType")
        thresholdMax = cherrypy.request.json.get("thresholdMax")
        thresholdMin = cherrypy.request.json.get('thresholdMin')
        
        #iterating the self.registered_controllers to change the value of the device
        for controller in self.registered_controllers:
            if controller.deviceType == deviceType:
                controller.thresholdMax = thresholdMax
                controller.thresholdMin = thresholdMin
                logger.info(f'{controller.deviceType} - {controller.thresholdMax} - {controller.thresholdMin}')
                break
                
        #update the controllers status of the cataLog
        controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
        for controller in controllerList["controller_list"]:
            if controller['deviceType'] == deviceType:
                controller['thresholdMax'] = thresholdMax
                controller['thresholdMin'] = thresholdMin
                break    
        
        #save the file
        with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
            json.dump(controllerList, f, indent=4) 
            
        return { "status": "success", "message": "Threshold modified successfully." }
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerAverageValue(self):
        dict = {}
        dict["time"] = math.floor(time.time()*1000)
        for controller in self.registered_controllers:
            dict[f"{controller.deviceType}"] = math.floor(controller.averageValue)
        self.dashboardData.append(dict)
        return self.dashboardData
    
    @cherrypy.expose
    def shutdown(self):
        logger.info('Controller server is closed successfully')
        cherrypy.engine.exit()
        return "Controller server is closed successfully"
    
if __name__ == '__main__':
    
    Log.setup_loggers('controller')
    
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8082,
        'tools.sessions.on': False
    })
    
    config = {
            '/': {
                'tools.CORS.on': True,
            }
    }
    
    cherrypy.quickstart(ControllerServer(), '/controller', config)