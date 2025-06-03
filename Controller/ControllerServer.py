from datetime import datetime
import math
import threading
import time
import cherrypy
import json
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from Util.Utility import PathUtils, FileUtils, Log
from Util import CORS
from Controller.Controller import Controller

import logging
Log.setup_loggers('controllerServer')
logger = logging.getLogger('controllerServer')

class ControllerServer:
    
    def __init__(self):

        #register all controllers for servers
        self.controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["controller_list"]
        #store registered controllers in the List for dynamic to adjust the running sensors 
        self.registered_controllers = []
        #iterate the controller list
        for controller in self.controllerList:
            controllerObject = Controller(controller["deviceType"], controller["subscribeTopic"], controller["thresholdMax"], controller["thresholdMin"],controller["unit"])
            self.registered_controllers.append(controllerObject)
            
        self.dashboardData = []
        self.threading = threading.Thread(target = self.run)
        self.threading.start()
        
    def run(self):
        while True:
            dict = {}
            dict["time"] = math.floor(time.time()*1000)
            for controller in self.registered_controllers:
                dict[f"{controller.deviceType}"] = math.floor(controller.averageValue)
            self.dashboardData.append(dict)
            time.sleep(5)
        
    #show all controllers form the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerThreshold(self):
        controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["controller_list"]
        logger.info(f"getControllerThreshold: [{controllerList}]")

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
        
        if deviceType not in ["Soil_Moisture","CO2_Concentration","Temperature","Lightness"]:
            return "Wrong Device Type!"
        
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
        
        logger.info(f"updateControllerThreshold: {deviceType} - {thresholdMax} - {thresholdMin}")
            
        return { "status": "success", "message": "Threshold modified successfully." }
    
    #This server for web dashboard
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerAverageValue(self):

        logger.info(f"getControllerAverageValue")
 
        return self.dashboardData
    
    #This server for environmental condition of the TeleBot
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerAverageValue2TeleBot(self):
        dict = {}
        dict["Time"] = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        for controller in self.registered_controllers:
            dict[f"{controller.deviceType}"] = f'{math.floor(controller.averageValue)}' + f' {controller.unit}'
            
        logger.info(f"getControllerAverageValue2TeleBot: {dict}")
        
        return dict
    
    @cherrypy.expose
    def shutdown(self):
        logger.info('Controller server is closed successfully')
        cherrypy.engine.exit()
        return "Controller server is closed successfully"
    
if __name__ == '__main__':
    
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