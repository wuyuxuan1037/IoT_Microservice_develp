import paho.mqtt.client as PahoMQTT
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Util.Utility import PathUtils
from Util.Utility import FileUtils
import json

class MyMQTT:
    def __init__(self, client_id = FileUtils.random_uuid_create(), notifier=None, configfile = os.path.join(PathUtils.project_path(),"cataLog.json")):
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
        self._paho_mqtt.on_connect = self.on_connect
        self._paho_mqtt.on_message = self.on_message

    def on_connect (self, paho_mqtt, userdata,flag, rc):
        # print ("Connected to %s with result code: %d" % (self.broker, rc))
        pass

    def on_message (self,paho_mqtt,userdata, msg):
        # A new message is received
        # self.notifier.notify (msg.topic, msg.payload, msg.qos, msg.retain)
        pass

    def myPublish (self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)

    def mySubscribe (self, topic): 
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2) 
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
        print ("subscribed to %s" % (topic))

    def mqttStart(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()
        
    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
            
    def mqttStop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

