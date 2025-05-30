import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from MQTT.MyMQTT import MyMQTT
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
        super().__init__()
        self.mqttStart()
        
    
    def run(self):
        pass
    
    def on_connect (self, paho_mqtt, userdata,flag, rc):
        pass