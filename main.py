from app import App
import logging

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# configure the logger of the MQTT
mqtt_logger = logging.getLogger('mqtt')
mqtt_handler = logging.FileHandler('mqtt.log')
mqtt_handler.setFormatter(log_formatter)
mqtt_logger.addHandler(mqtt_handler)
mqtt_logger.setLevel(logging.DEBUG)
mqtt_logger.info("Mqtt started")
mqtt_logger.debug("Debugging mqtt value")
mqtt_logger.error("Something went wrong")

# configure the logger of the Sensor
sensor_logger = logging.getLogger('sensor')
sensor_handler = logging.FileHandler('sensor.log')
sensor_handler.setFormatter(log_formatter)
sensor_logger.addHandler(sensor_handler)
sensor_logger.setLevel(logging.DEBUG)
sensor_logger.info("Sensor started")
sensor_logger.debug("Debugging sensor value")
sensor_logger.error("Something went wrong")

# configure the logger of the Controller
controller_logger = logging.getLogger('controller')
controller_handler = logging.FileHandler('controller.log')
controller_handler.setFormatter(log_formatter)
controller_logger.addHandler(controller_handler)
controller_logger.setLevel(logging.DEBUG)
controller_logger.info("Controller started")
controller_logger.debug("Debugging controller value")
controller_logger.error("Something went wrong")

if __name__ == "__main__":
    App()