import logging
import uuid
import json
import os
# from cherrypy._cpdispatch import MethodDispatcher

class Utility:
        
    @staticmethod
    def generate_device_id():
        return uuid.uuid4().hex[:8]
    

class FileUtils:
    
    @staticmethod
    def load_config(filepath: str) -> dict:
        
        with open(filepath, 'r', encoding='utf-8') as f:
            config_str = f.read()
        
        config = json.loads(config_str)
        
        # # replace placeholder
        # if "api_config" in config:
        #     config["api_config"]["/"]["request.dispatch"] = MethodDispatcher()
        
        # if "root_config" in config:
        #     config["root_config"]["/"]["tools.staticdir.root"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return config
    
    @staticmethod
    def random_uuid_create() -> str:
        client_ID = str(uuid.uuid4().hex[:18])
        return client_ID

class PathUtils:
    
    def project_path() -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
class Log:
    
    @staticmethod
    def setup_loggers(name):
        #information format
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        def setup_logger(name, filename):
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)

            if logger.hasHandlers():
                logger.handlers.clear()

            handler = logging.FileHandler(filename, mode='a')
            handler.setFormatter(log_formatter)
            logger.addHandler(handler)

        # Configure the log for different modules
        setup_logger(name, f'logs/{name}.log')