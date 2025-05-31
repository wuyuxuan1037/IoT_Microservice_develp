import paho.mqtt.client as PahoMQTT
import os

from Util.Utility import PathUtils
from Util.Utility import FileUtils
import json

import logging
logger = logging.getLogger('mqtt')

class MyMQTT:
    
    def __init__(self, client_id, notifier=None, configfile = os.path.join(PathUtils.project_path(),"cataLog.json")):
        # obtain config file
        self.config = FileUtils.load_config(configfile)
        self.broker = self.config["mqtt"]["broker"]
        self.port = self.config["mqtt"]["port"]
        self.keepalive = self.config["mqtt"]["keepAlive"]
        self.clientID = client_id
        self.notifier = notifier
        self._topic = ""
        self._isSubscriber = False
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(client_id,True)  
        # register the callback
        # self._paho_mqtt.on_connect = self.on_connect
        # self._paho_mqtt.on_message = self.on_message
        self._paho_mqtt.on_disconnect = self.on_disconnect
        


    # def on_connect (self, paho_mqtt, userdata,flag, rc):
    #     logger.info(f'{self.clientID} Connected to {self.broker} with result code: {rc} ')

    # def on_message (self,paho_mqtt,userdata, msg):
        # A new message is received
        # logger.info(f"Received Message on {msg.topic}: {msg.payload.decode()}")
        # self.on_message(paho_mqtt,userdata, msg)
        # self.notifier.notify (msg.topic, msg.payload, msg.qos, msg.retain)
    
    def myPublish (self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2, retain = False)

    def mySubscribe (self, topic,callback = None): 
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2) 
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
        logger.info(f"subscribed to {topic}")

    def Start(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port, keepalive=self.keepalive)
        self._paho_mqtt.loop_start()
        
    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
            
    def Stop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        
    def on_disconnect(self, client, userdata, rc, properties=None):
        if rc != 0:
            logger.warning(f"Unexpected disconnection. rc={rc}")
        else:
            logger.warning("Disconnected normally.")

