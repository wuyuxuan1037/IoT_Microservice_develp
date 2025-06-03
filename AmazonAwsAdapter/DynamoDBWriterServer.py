import json
from decimal import Decimal
import time

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from Util.Utility import Log
from MQTT.MyMQTT import MyMQTT
from AmazonAwsAdapter.DynamoDBWriter import DynamoDBWriter
from Util import CORS

import logging
Log.setup_loggers('DB_writerServer')
logger = logging.getLogger('DB_writerServer')

class DynamoDBWriterServer:
    
    def __init__(self, client_id, topic):
        self.client = MyMQTT(client_id, self)
        self.client.start()
        self.client.mySubscribe(topic)
        self.writer = DynamoDBWriter()

    def notify(self, topic, payload, qos=None, retain=None):
        try:
            data = json.loads(payload.decode())
            value = data['e'][0]['v']
            deviceType = data['e'][0]['n']
            unit = data['e'][0]['u']
            # 从 bn 字段提取 deviceID
            bn = data.get('bn', '')
            deviceID = bn.split('/')[-1] if bn else ''
            deviceLocation = '/'.join(bn.split('/')[1:-2]) if bn else ''
            self.writer.write_sensor_data(
                deviceID=deviceID,
                deviceType=deviceType,
                deviceLocation=deviceLocation,
                value=Decimal(str(value)),
                unit=unit,
                topic=topic
            )
            logger.info(f"Written to DynamoDB: {data}")

        except Exception as e:
            logger.exception(f"Error:Written to DynamoDB. Processing message: {e}")


if __name__ == "__main__":
    client_id = "DynamoDBWriter"
    topic = "PoliTO_IotSmartFarm/Lingotto/#"
    server = DynamoDBWriterServer(client_id, topic)
    while True:
        time.sleep(1)