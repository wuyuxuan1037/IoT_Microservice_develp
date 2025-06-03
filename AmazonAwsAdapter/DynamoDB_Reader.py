# pip install boto3
import boto3
from boto3.dynamodb.conditions import Key

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Util.Utility import Log

import logging
Log.setup_loggers('DB_reader')
logger = logging.getLogger('DB_reader')


class DynamoDBReader:
    def __init__(self, table_name='IoTSensorData'):
        self.dynamodb = boto3.resource('dynamodb',
                                        region_name='eu-north-1',
                                        aws_access_key_id='AKIA4OEY2SAU5ZZZGZLT',
                                        aws_secret_access_key='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')
        self.table = self.dynamodb.Table(table_name)

    def get_latest_data(self, deviceID):
        try:
            response = self.table.query(
                KeyConditionExpression=Key('deviceID').eq(deviceID),
                ScanIndexForward=False,
                Limit=1
            )
            items = response.get('Items', [])
            if items:
                logger.debug(response)
                return items[0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get latest data: {e}")
            return None

    def get_latest_data_str(self, deviceID):
        data = self.get_latest_data(deviceID)
        if data:
            ts = data.get('timestamp')
            location = data.get('deviceLocation')
            deviceType = data.get('deviceType')
            value = data.get('value')
            unit = data.get('unit')
            topic = data.get('topic')
            return f"Device: {deviceID}\nTime: {ts}\nLocation: {location}\nType: {deviceType}\nValue: {value} {unit}\nTopic: {topic}"
            
        else:
            return f"Device {deviceID} has no data"
# check the data
    def print_latest_data(self, deviceID):
        data = self.get_latest_data_str(deviceID)
        logger.info(data)

    def get_history_data(self, deviceID, limit=10):
        try:
            response = self.table.query(
                KeyConditionExpression=Key('deviceID').eq(deviceID),
                ScanIndexForward=False,  # 最新的在前面
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            logger.exception(f"Failed to get history data: {e}")
            return []
# 新增获取所有类型历史数据
    def get_all_history_data(self, limit=500):
        
        try:
            response = self.table.scan(Limit=limit)
            return response.get('Items', [])
        except Exception as e:
            logger.exception(f"Failed to scan all history data: {e}")
            return []