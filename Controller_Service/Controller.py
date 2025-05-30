import os, sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from MQTT.MyMQTT import MyMQTT
from Util.Utility import FileUtils

import logging
logger = logging.getLogger('controller')

class Controller (MyMQTT):
    
    def __init__(self, deviceType, subscribeTopic, thresholdMax, thresholdMin, infoFrequency=1):
        
        #attribution
        self.deviceType = deviceType
        self.subscribeTopic = subscribeTopic
        self.thresholdMax = thresholdMax
        self.thresholdMin = thresholdMin
        self.infoFrequency = infoFrequency
        super().__init__(FileUtils.random_uuid_create())
        self.mqttStart()
        self._paho_mqtt.on_message = self.on_message
        self.update_thread = None
        self._stop_event = threading.Event()
        self.threading = threading.Thread(target = self.run)
        
    
    def run(self):
        pass
    
    #start a threading for this controller 
    def start(self):
        if self.update_thread is None or not self._stop_event.is_alive():
            self._stop_event.clear()
            #set an threading attribution for this controller
            self.update_thread = threading.Thread(target=self.run,daemon=True)
            self.update_thread.start()
            #Subscribe the interesting topic
            self.mySubscribe(self.subscribeTopic)
            
    def on_message(self, paho_mqtt, userdata, msg):
        # logger.info(f"Received message on topic {self.deviceType}: {self.subscribeTopic}")
        if self.deviceType in msg.topic:
        # handle the message
            payload = msg.payload.decode('utf-8')  # decode the received message
            logger.info(f"Received message on topic {msg.topic}: {payload}")
