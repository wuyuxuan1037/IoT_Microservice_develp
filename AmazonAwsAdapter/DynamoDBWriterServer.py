from MQTT.MyMQTT import MyMQTT
from DynamoDBWriter import DynamoDBWriter
import json
from decimal import Decimal
import time

class DynamoDBWriterServer:
    
    def __init__(self, client_id, topic):
        self.client = MyMQTT(client_id, self)
        self.client.start()
        time.sleep(1)
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
            print(f"Written to DynamoDB: {data}")
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    client_id = "DynamoDBWriter"
    topic = "TO_IotSmartFarm/#"
    server = DynamoDBWriterServer(client_id, topic)
    while True:
        time.sleep(1)