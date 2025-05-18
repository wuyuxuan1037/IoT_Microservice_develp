# from mqtt_client.MyMQTT import MyMQTT
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from MQTT_Service.MyMQTT import MyMQTT
import datetime
import random
import time
import threading

class Sensor:
    
    def __init__(self, deviceID, deviceType, deviceLocation, topic, unit, info_frequency, status):
        #attribution
        self.deviceID = deviceID 
        self.deviceType = deviceType 
        self.deviceLocation = deviceLocation
        self.topic = topic
        self.unit = unit
        self.info_frequency = info_frequency
        self.status = status
        #set an threading attribution for the Sensor Class
        self.update_thread = threading.Thread(target=self.run,daemon=True)
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
        while self.status:
            self.publish_data()
            time.sleep(self.info_frequency)   
    
    #simulate the IOT sensor generate the data based on the different type of       
    def sensor_value(self):
        return random.randint(10,40)
    
    #stop running when the user delete or stop the device. 
    def stop(self):
        self.status = False
        self.update_thread.join()
        
    #start running when the user resume the device. 
    def start(self):
        if self.status:
            self.update_thread.start()
    
    #publish the data to the broker    
    def publish_data(self):
        var = self.sensor_value()
        self.msg['e'][0]['v'] = var
        self.msg['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic,self.msg)
        print(f'{self.topic} Current {self.deviceType} is {self.msg['e'][0]['v']} {self.msg['e'][0]['u']} {datetime.datetime.fromtimestamp(self.msg['e'][0]['t']).strftime('%Y-%m-%d %H:%M:%S')}\n')