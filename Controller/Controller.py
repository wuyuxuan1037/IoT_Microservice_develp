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

class Controller (MyMQTT):
    
    def __init__(self, deviceType, subscribeTopic, thresholdMax, thresholdMin, unit, infoFrequency=1):
        
        #attribution
        self.deviceType = deviceType
        self.subscribeTopic = subscribeTopic
        self.sensorTopic = ''
        self.publishTopic =''
        self.thresholdMax = thresholdMax
        self.thresholdMin = thresholdMin
        self.unit = unit
        self.averageValue = 0
        self.infoFrequency = infoFrequency
        self.clientMqtt = super().__init__(FileUtils.random_uuid_create())
        super().start()
        self._paho_mqtt.on_message = self.on_message
        self._paho_mqtt.on_connect = self.on_connect
        self.mySubscribe(self.subscribeTopic)   
        
    def run (self, deviceType):
        match deviceType:
            # case 'Temperature':
            #     # when average value is higher than MAX, turn on the Cooler
            #     if self.averageValue > self.thresholdMax:
            #         self.publish_data('/Cooler',True)
            #         self.publish_data('/Heater',False)
            #     # when average value is lower than MIN, turn on the Heater
            #     elif self.averageValue < self.thresholdMin:
            #         self.publish_data('/Cooler',False)
            #         self.publish_data('/Heater',True)
            #     else :
            #         self.publish_data('/Cooler',False)
            #         self.publish_data('/Heater',False)
            # case 'Soil_Moisture':  
            #     # when average value is higher than MAX, turn on the Drip_Irrigation_Pipe
            #     if self.averageValue > self.thresholdMax:
            #         self.publish_data('/Drip_Irrigation_Pipe',True)
            #     else:
            #         self.publish_data('/Drip_Irrigation_Pipe',False)
            # case 'Lightness':  
            #     # when average value is higher than MAX, turn on the Sunshade_Net
            #     if self.averageValue > self.thresholdMax:
            #         self.publish_data('/Sunshade_Net',True)
            #         self.publish_data('/LED_Light',False)
            #     # when average value is lower than MIN, turn on the LED_Light
            #     elif self.averageValue < self.thresholdMin:
            #         self.publish_data('/Sunshade_Net',False)
            #         self.publish_data('/LED_Light',True)
            #     else:
            #         self.publish_data('/Sunshade_Net',False)
            #         self.publish_data('/LED_Light',False)
            # case 'CO2_Concentration':  
            #     # when average value is higher than MAX, turn on the Exhaust_Fan
            #     if self.averageValue > self.thresholdMax:
            #         self.publish_data('/Exhaust_Fan',True)
            #         self.publish_data('/Carbon_Dioxide_Generator',False)
            #     # when average value is lower than MIN, turn on the Carbon_Dioxide_Generator
            #     elif self.averageValue < self.thresholdMin:
            #         self.publish_data('/Exhaust_Fan',False)
            #         self.publish_data('/Carbon_Dioxide_Generator',True)
            #     else:
            #         self.publish_data('/Exhaust_Fan',False)
            #         self.publish_data('/Carbon_Dioxide_Generator',False)
            case _:
                pass 
        logger.info(f'{self.deviceType} - {self.publishTopic} -')      

            
    #publish the data to the broker    
    def publish_data(self, actualPath, actuatorStatus):
        self.publishTopic = self.sensorTopic + actualPath
        msg = {
            'bn': f'{self.publishTopic}',
            'e':[
                {
                    'n': f'{self.deviceType}',
                    'u': f'{self.unit}',
                    't': time.time(),
                    'v': actuatorStatus
                }
            ]
        }
        self.myPublish(self.publishTopic,msg)
        logger.info(f'{self.publishTopic} - PUBLISH TO ACTUATOR - {self.averageValue} - {actuatorStatus} - {self.thresholdMax} - {self.thresholdMin}')
        
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
        logger.info(f'Controller:{self.clientID} Connected to {self.broker} with result code: {rc} ')
    