import cherrypy
import json
import os
from Util.Utility import PathUtils
from Util.Utility import FileUtils
from Util.Utility import Utility
from Controller_Service.Controller import Controller

import logging
logger = logging.getLogger('controller')

class ControllerServer:
    
    def __init__(self):
        
        cherrypy.tools.CORS = cherrypy.Tool('before_handler', Utility.CORS)
        
        self.config = { 
            '/': {
                'tools.sessions.on': True,
                # 'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.CORS.on': True,
            }
    }
        #register all controllers for servers
        self.controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"config/cataLog.json"))["controller_list"]
        #store registered controllers in the List for dynamic to adjust the running sensors 
        self.registered_controllers = []
        #iterate the controller list
        for controller in self.controllerList:
            controllerObject = Controller(controller["deviceType"], controller["subscribeTopic"], 
                                            controller["thresholdMax"], controller["thresholdMin"],controller["unit"])
            self.registered_controllers.append(controllerObject)
        
    #show all controllers form the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerThreshold(self):
        controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"config/cataLog.json"))["controller_list"]
        return controllerList
    
    #update the MAX and MIN of threshold
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def updateControllerThreshold(self):
        # handle CORS pre-request
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.status = 200
            return ""
        
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
        controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"config/cataLog.json"))
        for controller in controllerList["controller_list"]:
            if controller['deviceType'] == deviceType:
                controller['thresholdMax'] = thresholdMax
                controller['thresholdMin'] = thresholdMin
                break    
        
        #save the file
        with open(os.path.join(PathUtils.project_path(),"config/cataLog.json"), 'w', encoding='utf-8') as f:
            json.dump(controllerList, f, indent=4) 
            
        return { "status": "success", "message": "Threshold modified successfully." }
    
    
    @cherrypy.expose
    def OPTIONS(self, *args, **kwargs):
        Utility.CORS()
        return ""
    