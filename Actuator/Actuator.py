import json
import time

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from MQTT.MyMQTT import MyMQTT
from Util.Utility import FileUtils

import logging
logger = logging.getLogger('controller')

class Actuator (MyMQTT):
    
    def __init__(self,deviceID, deviceType, deviceLocation, topic, lastStatusUpdate, status):
        
        #attribution
        self.deviceID = deviceID 
        self.deviceType = deviceType
        self.deviceLocation = deviceLocation
        self.topic = topic
        self.lastStatusUpdate = lastStatusUpdate
        self.status = status
        self.clientMqtt = super().__init__(FileUtils.random_uuid_create())
        super().start()
        self._paho_mqtt.on_message = self.on_message
        self._paho_mqtt.on_connect = self.on_connect
        self.mySubscribe(self.topic)   
    
        
    #callback function to receive data periodically    
    def on_message(self, paho_mqtt, userdata, msg):
        # if self.deviceType in msg.topic :
        # handle the message
            payload = msg.payload.decode('utf-8')  # decode the received message
            logger.info(f"Received message on topic {msg.topic}: {payload}")
            currentValue = json.loads(payload)['e'][0]['v']
            self.sensorTopic = msg.topic
            if self.averageValue == 0 :
                self.averageValue = currentValue
            else:
                self.averageValue = (currentValue + self.averageValue) / 2
            logger.info(f'{self.deviceType} - average value - {self.averageValue}')
            self.run(self.deviceType)

    def on_connect (self, paho_mqtt, userdata,flag, rc):
        logger.info(f'Actuator:{self.clientID} Connected to {self.broker} with result code: {rc} ')
    