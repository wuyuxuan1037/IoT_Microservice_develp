import cherrypy

class HttpAPI:
    
    @cherrypy.expose
    def index(self):
        return open('html/index.html', encoding="UTF-8")