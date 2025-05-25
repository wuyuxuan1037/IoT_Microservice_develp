# from mqtt_client.MyMQTT import MyMQTT
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from MQTT_Service.MyMQTT import MyMQTT
import random
import threading
import logging

logging.basicConfig(
    level=logging.DEBUG,  # DEBUG/INFO/WARNING/ERROR/CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    # filename='sensor.log'
)

class Sensor:
    
    def __init__(self, deviceID, deviceType, deviceLocation, topic, unit, info_frequency, status):
        
        #attribution
        self.deviceID = deviceID 
        self.deviceType = deviceType 
        self.deviceLocation = deviceLocation
        self.topic = topic
        self.unit = unit
        self.info_frequency = info_frequency
        self.status = status  #sign for the front-end
        self.client = MyMQTT()
        self.client.start()
        self.update_thread = None #assign the value when calls start()
        self._stop_event = threading.Event()  #sign for threading
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
            self.publish_data()
            self._stop_event.wait(timeout=self.info_frequency)  
    
    #simulate the IOT sensor generate the data based on the different type of       
    def sensor_value(self,deviceType):
        if deviceType == 'Temperature':  
            # room temperature usually float between 15~35℃
            return round(random.uniform(15, 35), 1)
        elif deviceType == 'Soil_Moisture':  
            # 10%~80%
            return round(random.uniform(10, 80), 1)
        elif deviceType == 'Lightness':  
            # 10~1000 lx
            return round(random.uniform(10, 1000), 0)
        elif deviceType == 'CO2_Concentration':  
            # interior 400~1000 ppm
            return round(random.uniform(400, 1000), 0)

    
    #stop running when the user delete or stop the device. 
    def stop(self):
        self._stop_event.set()
        self.status = False
        self.client.stop()
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=0)
        
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
        # self.msg['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic,self.msg)
        logging.info(f'{self.topic} - {self.deviceType} - {self.msg["e"][0]["v"]} {self.msg["e"][0]["u"]}')