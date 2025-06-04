import os, sys
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from MQTT.MyMQTT import MyMQTT
from Util.Utility import FileUtils
import random
import threading

import logging
logger = logging.getLogger('sensor')

class Sensor (MyMQTT):
    
    def __init__(self, deviceID, deviceType, deviceLocation, 
                topic, unit, info_frequency, status):
        
        #attribution
        self.deviceID = deviceID 
        self.deviceType = deviceType 
        self.deviceLocation = deviceLocation
        self.topic = topic
        self.unit = unit
        self.info_frequency = info_frequency
        self.status = status  #sign for the front-end
        self.update_thread = None #assign the value when calls start()
        self._stop_event = threading.Event()  #sign for threading
        self.clientMqtt = super().__init__(FileUtils.random_uuid_create())
        super().start()
        self._paho_mqtt.on_message = self.on_message
        self._paho_mqtt.on_connect = self.on_connect
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
    
    #As the functional body of the targeted threading
    def run(self):
        while not self._stop_event.is_set():
            try:
                self.publish_data()
            except Exception as e:
                logger.error(f"Error in publish_data: {e}")
            self._stop_event.wait(self.info_frequency)  
    
    #simulate the IOT sensor generate the data based on the different type of       
    def sensor_value(self,deviceType):
        if deviceType == 'Temperature':  
            # room temperature usually float between 15~35℃
            return round(random.uniform(15, 45), 1)
        elif deviceType == 'Soil_Moisture':  
            # 10%~80%
            return round(random.uniform(10, 80), 1)
        elif deviceType == 'Light_Intensity':  
            # 10~1000 lx
            return round(random.uniform(10, 1000), 0)
        elif deviceType == 'CO2_Concentration':  
            # interior 400~1000 ppm
            return round(random.uniform(400, 1000), 0)

    
    #stop running when the user delete or stop the device. 
    def stop(self):
        self._stop_event.set()
        self.status = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join()
            logger.info(f'{self.update_thread} threading CLOSED')
        else:
            logger.info("No alive thread to join.")
        
    #start running when the user resume the device. 
    def start(self):
        if (self.update_thread is None or not self.update_thread.is_alive()) and self.status:
            self._stop_event.clear()
            #set an threading attribution for the Sensor Class
            self.update_thread = threading.Thread(target=self.run,daemon=True)
            self.update_thread.start()
    
    #publish the data to the broker    
    def publish_data(self):
        var = self.sensor_value(self.deviceType)
        self.msg['e'][0]['v'] = var
        self.msg['e'][0]['t'] = time.time()
        self.myPublish(self.topic,self.msg)
        logger.info(f'{self.topic} - {self.deviceType} - {self.msg["e"][0]["v"]} {self.msg["e"][0]["u"]} - infoFre {self.info_frequency}')
    
    def on_message(self, paho_mqtt, userdata, msg):
        pass
    
    def on_connect (self, paho_mqtt, userdata,flag, rc):
        logger.info(f'Sensor:{self.clientID} Connected to {self.broker} with result code: {rc} ')