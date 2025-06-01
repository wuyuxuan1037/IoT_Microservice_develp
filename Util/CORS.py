import cherrypy

#Create a global CORS
def CORS_tool():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    if cherrypy.request.method == 'OPTIONS':
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        cherrypy.response.status = 200
        cherrypy.response.body = b''
        cherrypy.serving.request.handler = None
    
# Register a global CORS tool to allow cross-origin requests from any origin (*)
# Applied via decorator @cherrypy.tools.CORS() or via config: 'tools.CORS.on': True
cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS_tool)