import cherrypy
import json
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Util.Utility import PathUtils
from Util.Utility import FileUtils
from Util.Utility import Utility
from Controller_Service.Controller import Controller

class ControllerServer:
    
    def __init__(self):
        
        cherrypy.tools.CORS = cherrypy.Tool('before_handler', Utility.CORS)
        
        self.config = { 
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.CORS.on': True,
            }
    }
        #register all controllers for servers
        self.controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"cataLog.json"))["controller_list"]
        #store registered controllers in the List for dynamic to adjust the running sensors 
        self.registered_controllers = []
        #iterate the controller list
        for controller in self.controllerList:
            controllerObject = Controller(controller["deviceType"], controller["subscribeTopic"], 
                                            controller["thresholdMax"], controller["thresholdMin"])
            self.registered_controllers.append(controllerObject)

        # #update controller status (control the sensor published to the MQTT broker)
        # for sensor in self.registered_sensors:
        #     sensor.start()
        
    #show all controllers form the configuration     
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getControllerThreshold(self):
        controllerList = FileUtils.load_config(os.path.join(PathUtils.project_path(),"cataLog.json"))["controller_list"]
        return controllerList
    
    @cherrypy.expose
    def OPTIONS(self, *args, **kwargs):
        Utility.CORS()
        return ""
    