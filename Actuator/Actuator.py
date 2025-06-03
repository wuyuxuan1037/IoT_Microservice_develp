from datetime import datetime
import time
import json
import time
import telebot

import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from MQTT.MyMQTT import MyMQTT
from Util.Utility import FileUtils, PathUtils

import logging
logger = logging.getLogger('actuator')

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
        super().mySubscribe(self.topic)
        
        self.BOT_TOKEN = '7312600355:AAHOD25LLkWUX-kWxsBbpSI7Zyk38bqOn6E'
        self.CHAT_ID = '6565978127'
        self.bot = telebot.TeleBot(self.BOT_TOKEN)
    
        
    #callback function to receive data periodically    
    def on_message(self, paho_mqtt, userdata, msg):
        # sourcery skip: extract-method
        # handle the message
        payload = msg.payload.decode('utf-8')  # decode the received message
        logger.info(f"Received message on topic {msg.topic}: {payload}")
        if json.loads(payload)['e'][0]['v'] != self.status:
            old_status = self.status
            self.status = json.loads(payload)['e'][0]['v']
            #obtain current time
            timestamp = time.time()
            #convert timestamp into time object
            dt = datetime.fromtimestamp(timestamp)
            #define the format  of the time to display
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            self.lastStatusUpdate = formatted_time
            logger.info(f'{self.deviceType} - {self.deviceID} - {self.status} - {self.lastStatusUpdate}')

            #update the actuators status of the cataLog
            actuatorList = FileUtils.load_config(os.path.join(PathUtils.project_path(),'config','cataLog.json'))
            for actuator in actuatorList["actuator_list"]:
                if actuator['deviceID'] == self.deviceID:
                    actuator['status'] = self.status
                    actuator['lastStatusUpdate'] = self.lastStatusUpdate
                    break
                
            logger.info(f'[{self.lastStatusUpdate}] successfully change the status of [{self.deviceID}] from [{old_status}] into [{self.status}]')

            #save the file
            with open(os.path.join(PathUtils.project_path(),'config','cataLog.json'), 'w', encoding='utf-8') as f:
                json.dump(actuatorList, f, indent=4) 

            logger.info(f'[{self.lastStatusUpdate}] successfully WRITE the status of [{self.deviceID}] into [{self.status}]')
            

            #push information to my TeleBot
            message = (
                f'Actuator Status Changed :\n\n'
                f"DeviceID: {self.deviceID}\n"
                f"Device Type: {self.deviceType}\n"
                f"Time: {self.lastStatusUpdate}\n"
                f"Location: {self.deviceLocation}\n"
                f"Current Status: {'ON' if self.status else 'OFF'}\n"
            )
            try:
                self.bot.send_message(self.CHAT_ID, message)
                logger.info(f"Info has pushed into Telegram: {message}")
            except Exception as e:
                logger.error(f"Info has failed to push into Telegram: {e}")
        else:
            logger.info(f"Status of [{self.deviceID} - {self.deviceType}] doesn't need to change")
            
        
    def on_connect (self, paho_mqtt, userdata,flag, rc):
        logger.info(f'Actuator:{self.clientID} Connected to {self.broker} with result code: {rc} ')
    