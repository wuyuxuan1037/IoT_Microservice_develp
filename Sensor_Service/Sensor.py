from mqtt_client.MyMQTT import MyMQTT
import datetime
import random
import time

class Sensor:
    
    def __init__(self, deviceID, deviceType, deviceLocation, topic, unit, info_frequency):
        self.deviceID = deviceID 
        self.deviceType = deviceType 
        self.deviceLocation = deviceLocation
        self.topic = topic
        self.unit = unit
        self.status = True
        self.info_frequency = info_frequency
        self.client = MyMQTT()
        self.client.start()
        self.msg = {
            'bn': f'{self.topic}',
            'e':[
                {
                    'n': f'{self.deviceType}',
                    'u': f'{self.unit}',
                    't': None,
                    'v': None
                }
            ]
        }
        
    def run(self):
        while True:
            if self.status :
                var = self.sensor_value()
                self.msg['e'][0]['v'] = var
                self.msg['e'][0]['t'] = time.time()
                self.client.myPublish(self.topic,self.msg)
                print(f'{self.topic} Current temperature is {self.msg['e'][0]['v']} {self.msg['e'][0]['u']} {datetime.datetime.fromtimestamp(self.msg['e'][0]['t']).strftime('%Y-%m-%d %H:%M:%S')}\n')
            time.sleep(self.info_frequency)   
            
    def sensor_value(self):
        return random.randint(10,40)
    
    #stop running when the user delete the device. 
    def stop_sensor(self):
        self.status = False