# pip install boto3
import boto3
from boto3.dynamodb.conditions import Key


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
                # print(response) # for debug
                return items[0]
            else:
                return None
        except Exception as e:
            print(f"Failed to get latest data: {e}")
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
        print(data)

    def get_history_data(self, deviceID, limit=10):
        try:
            response = self.table.query(
                KeyConditionExpression=Key('deviceID').eq(deviceID),
                ScanIndexForward=False,  # 最新的在前面
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Failed to get history data: {e}")
            return []

# if __name__ == "__main__":
#     reader = DynamoDBReader('IoTSensorData')
#     reader.print_latest_data('c3d47900')