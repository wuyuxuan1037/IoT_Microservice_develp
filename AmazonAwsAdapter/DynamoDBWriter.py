import json
import boto3
from botocore.exceptions import ClientError
import logging
import time

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Util.Utility import Log

import logging
Log.setup_loggers('DB_writer')
logger = logging.getLogger('DB_writer')

class DynamoDBWriter:
    def __init__(self, table_name='IoTSensorData', region_name='eu-north-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.logger = logging.getLogger("DynamoDBWriter")

    def write_sensor_data(self, deviceID, deviceType, deviceLocation, value, unit, topic, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
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
            self.logger.info(f"Data written to DynamoDB: {item}")
            return True
        except ClientError as e:
            self.logger.error(f"Failed to write to DynamoDB: {e}")
            return False
