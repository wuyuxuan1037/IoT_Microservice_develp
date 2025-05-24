import cherrypy
import uuid

class Utility:
    
    @staticmethod
    def CORS():
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        
    @staticmethod
    def generate_device_id():
        return uuid.uuid4().hex[:8]
    
