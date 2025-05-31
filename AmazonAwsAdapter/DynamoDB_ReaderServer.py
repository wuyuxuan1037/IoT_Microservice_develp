import cherrypy
from DynamoDB_Reader import DynamoDBReader
import json
import decimal

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
            return {"error": "deviceID is required"}
        data = self.reader.get_latest_data(deviceID)
        if data:
            return convert_decimal(data)
        else:
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
            print(f"Error in getAllLatestData: {str(e)}")  # 添加服务器端日志
            return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 5002,
        # 添加 CORS 支持
        'tools.CORS.on': True
    })
    
    # 配置 CORS
    def CORS():
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)
    cherrypy.quickstart(DynamoDBReaderServer())