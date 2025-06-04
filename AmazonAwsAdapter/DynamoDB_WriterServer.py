from decimal import Decimal
import json
import boto3
from botocore.exceptions import ClientError
import logging
import time

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Util.Utility import Log, FileUtils,PathUtils
from MQTT.MyMQTT import MyMQTT

import logging
Log.setup_loggers('DB_writerServer')
logger = logging.getLogger('DB_writerServer')

# from dotenv import load_dotenv
# import os

# load_dotenv()

# aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

class DynamoDBWriter(MyMQTT):
    def __init__(self, table_name='IoTSensorData', region_name='eu-north-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name,
                                        aws_access_key_id= 'AKIA4OEY2SAUY4JKU3GD',
                                        aws_secret_access_key= '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'
                                    )
        self.table = self.dynamodb.Table(table_name)
        self.clientMqtt = super().__init__(FileUtils.random_uuid_create())
        super().start()
        self._paho_mqtt.on_message = self.on_message
        self._paho_mqtt.on_connect = self.on_connect
        super().mySubscribe(FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["DynamoDB_SubscribeTopic"][0])
        super().mySubscribe(FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))["DynamoDB_SubscribeTopic"][1])
        
    def on_message(self, paho_mqtt, userdata, msg):
        try:
            data = json.loads(msg.payload.decode('utf-8'))
            deviceType = data['e'][0]['n']
            unit = data['e'][0]['u']
            value = data['e'][0]['v'] if isinstance(data['e'][0]['v'], bool) else Decimal(str(data['e'][0]['v']))
            time = data['e'][0]['t']
            topic = data.get('bn', '')
            deviceID = topic.split('/')[5] if len(topic.split('/')) == 6 else topic.split('/')[7]
            deviceLocation = '/'.join(topic.split('/')[1:-2]) if len(topic.split('/')) == 6 else '/'.join(topic.split('/')[1:-5])
            self.write_sensor_data(
                deviceID=deviceID,
                deviceType=deviceType,
                deviceLocation=deviceLocation,
                value=value,
                unit=unit,
                topic=topic,
                timestamp = Decimal(int(time))
            )
            logger.info(f"Written to DynamoDB: {data}")

        except Exception as e:
            logger.exception(f"Error:Written to DynamoDB. Processing message: {e}")

    def write_sensor_data(self, deviceID, deviceType, deviceLocation, value, unit, topic, timestamp=None):
        item = {
            'deviceID': deviceID,
            'timestamp': timestamp,
            'deviceType': deviceType,
            'deviceLocation': deviceLocation,
            'value': value,
            'unit': unit,
            'topic': topic
        }
        try:
            self.table.put_item(Item=item)
            logger.info(f"Data written to DynamoDB: {item}")
            return True
        except ClientError as e:
            logger.error(f"Failed to write to DynamoDB: {e}")
            return False
        
    def on_connect (self, paho_mqtt, userdata,flag, rc):
        logger.info(f'DynamoDBWriter: Connected to {self.broker} with result code: {rc} ')
        

    
if __name__ == "__main__":
    
    writer = DynamoDBWriter()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        writer.stop()