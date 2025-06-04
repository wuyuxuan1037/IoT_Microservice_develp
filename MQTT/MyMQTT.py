import paho.mqtt.client as PahoMQTT
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Util.Utility import PathUtils, Log
from Util.Utility import FileUtils
import json

import logging
Log.setup_loggers('mqtt')
logger = logging.getLogger('mqtt')

class MyMQTT:
    
    def __init__(self, client_id, notifier=None, 
                configfile = os.path.join(PathUtils.project_path(),'config','cataLog.json')):
        # obtain config file
        self.config = FileUtils.load_config(configfile)
        self.broker = self.config["mqtt"]["broker"]
        self.port = self.config["mqtt"]["port"]
        self.keepalive = self.config["mqtt"]["keepAlive"]
        self.clientID = client_id
        self.notifier = notifier
        self._topic = ""
        self._isSubscriber = False
        self._paho_mqtt = PahoMQTT.Client(client_id,True)  
        self._paho_mqtt.on_disconnect = self.on_disconnect
    
    def myPublish (self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2, retain = False)
        logger.info(f"Publish to {topic} - {msg}")

    def mySubscribe (self, topic,callback = None): 
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2) 
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
        logger.info(f"subscribed to {topic}")

    def start(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port, keepalive=self.keepalive)
        self._paho_mqtt.loop_start()
        
    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
            
    def stop (self):
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
    
    

