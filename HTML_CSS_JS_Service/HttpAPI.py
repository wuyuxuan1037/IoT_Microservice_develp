import cherrypy
import os

class FrontendApp:
    @cherrypy.expose
    def index(self):
        return open('dist/index.html')

    @cherrypy.expose
    def default(self, *args, **kwargs):
        """return the request link is not the index.html（to support React Router）"""
        return open('dist/index.html')

config = {
    '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.abspath('dist'),
        'tools.staticdir.index': 'index.html',
    }
}

if __name__ == '__main__':
    cherrypy.quickstart(FrontendApp(), '/', config)