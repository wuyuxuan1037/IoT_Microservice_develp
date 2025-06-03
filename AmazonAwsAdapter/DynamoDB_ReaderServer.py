import cherrypy
from DynamoDB_Reader import DynamoDBReader
import json
import decimal

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Util.Utility import Log
from Util import CORS

import logging
Log.setup_loggers('DB_readerServer')
logger = logging.getLogger('DB_readerServer')

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

class DynamoDBReaderServer:
    def __init__(self, table_name='IoTSensorData'):
        self.reader = DynamoDBReader(table_name)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getLatestData(self, deviceID=None):
        if not deviceID:
            logger.error("error: deviceID is required")
            return {"error": "deviceID is required"}
        data = self.reader.get_latest_data(deviceID)
        if data:
            return convert_decimal(data)
        else:
            logger.error (f"error: No data found for {deviceID}")
            return {"error": f"No data found for {deviceID}"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getHistoryData(self, deviceID=None, limit=100):
        if not deviceID:
            return {"error": "deviceID is required"}
        try:
            limit = int(limit)
        except Exception:
            limit = 10
        data = self.reader.get_history_data(deviceID, limit)
        if data:
            return convert_decimal(data)
        else:
            logger.error (f"error: No history data found for {deviceID}")
            return {"error": f"No history data found for {deviceID}"}
    

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getAllLatestData(self):
        # 返回数组格式，便于前端处理
        try:
            with open('cataLog.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            device_ids = [sensor['deviceID'] for sensor in config['sensor_list']]
            result = []
            for device_id in device_ids:
                data = self.reader.get_latest_data(device_id)
                if data:
                    result.append(data)
            return convert_decimal(result)
        except Exception as e:
            logger.exception(f"Error in getAllLatestData: {str(e)}")
            return {"status": "error", "message": str(e)}
        
        
# 获取所有类型历史数据
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getAllHistoryData(self, limit=500):

        data = self.reader.get_all_history_data(limit)
        if data:
            return convert_decimal(data)
        else:
            logger.error (f"error: No history data found")
            return {"error": "No history data found"}
        
    @cherrypy.expose
    def shutdown(self):
        logger.info('DBreader server is closed successfully')
        cherrypy.engine.exit()
        return 'DBreader server is closed successfully'

if __name__ == '__main__':
    
    cherrypy.config.update({
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 8084,
    'tools.sessions.on': False
    })
    
    config = {
            '/': {
                'tools.CORS.on': True,
            }
    }
    
    cherrypy.quickstart(DynamoDBReaderServer(), '/DBreader', config)