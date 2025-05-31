import json
import boto3
from botocore.exceptions import ClientError
import logging
import time

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
