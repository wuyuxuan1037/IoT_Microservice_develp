import telebot
from telebot import types # by telebot.types create keyboard
import requests
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from Util.Utility import Log
Log.setup_loggers('telebot')
logger = logging.getLogger('telebot')

# TeleBot: SmartAgrBot
class MyTelegramBot:

    def __init__(self, chatID=None):
        
        self.chatID = chatID
        self.API_KEY = '7312600355:AAHOD25LLkWUX-kWxsBbpSI7Zyk38bqOn6E'
        self.bot = telebot.TeleBot(self.API_KEY)
        self.add_sensor_data = {}  
        self._register_handlers()
        self.running = False
        self.bot_thread = None
        self.config = { 
            '/': {
                'tools.sessions.on': True,
                # 'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.CORS.on': True,
            }
    }

    def create_home_keyboard(self):
        """CREATE HOME KEYBOARD"""
        keyboard = types.InlineKeyboardMarkup(row_width=3) # <--- types.InlineKeyboardMarkup 3 maximum 内联键盘
        btn_status = types.InlineKeyboardButton(text="Environment Condition", callback_data="view_env_status") # <--- 使用 types.InlineKeyboardButton
        btn_control = types.InlineKeyboardButton(text="Device Control", callback_data="control_devices")
        # btn_logout = types.InlineKeyboardButton(text="Logout", callback_data="logout") # for logout
        
        # add buttons to keyboard layout
        keyboard.add(btn_status, btn_control)
        # keyboard.add(btn_logout) # logout as a single row
        return keyboard
    
    def on_device_keyboard(self):
        """SUBMENU ON DEVICE CONTROL"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        actuator_status = types.InlineKeyboardButton(text="Actuator List", callback_data="view_actuator_status")
        dev_sensorList = types.InlineKeyboardButton(text="Sensor List", callback_data="view_sensor_list") 
        add_sensor = types.InlineKeyboardButton(text='Add Sensor', callback_data="add_sensors")
        del_sensor = types.InlineKeyboardButton(text='Delete Sensor', callback_data="del_sensors")
        add_actuator = types.InlineKeyboardButton(text='Add Actuator', callback_data="add_actuators")
        del_actuator = types.InlineKeyboardButton(text='Delete Actuator', callback_data="del_actuators")
        set_threshold = types.InlineKeyboardButton(text='Set Threshold', callback_data="set_threshold")
        check_threshold = types.InlineKeyboardButton(text='Search Threshold', callback_data="check_threshold")
        dev_back = types.InlineKeyboardButton(text="Back", callback_data="dev_back")
        keyboard.add(actuator_status, dev_sensorList, add_sensor, del_sensor,add_actuator,del_actuator,set_threshold,check_threshold,dev_back)
        return keyboard

    def _handle_start_home(self, message):
            chat_id = message.chat.id
            keyboard = self.create_home_keyboard() # create keyboard
            self.bot.send_message(chat_id, "Main Menu - Please Select an Option:", 
                                  reply_markup=keyboard) # add keyboard
    
    # handle button click events in the call back  
    def _handle_callback_query(self, call):  
        
        try:
            # response to the callback
            self.bot.answer_callback_query(call.id) 
        except Exception as e:
            logger.info(f"answer_callback_query error: {e}")
            return 
    
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        callback_data = call.data

        # manipulate based on the callback 
        if callback_data == "view_env_status":
            status_text = self.get_status() 
            self.bot.send_message(chat_id, f"Current Environment Status:\n{status_text}")
        elif callback_data == "control_devices":
            device_keyboard = self.on_device_keyboard()
            self.bot.edit_message_text(chat_id=chat_id,
                                         message_id=message_id,
                                         text="Please select an option:", # device菜单文本
                                         reply_markup=device_keyboard) # 跳转至device菜单键盘
        elif callback_data == "view_actuator_status":
            actuator_list_text = self.get_actuator_list()
            self.bot.send_message(chat_id, f"Registered Actuators:\n{actuator_list_text}")

        elif callback_data == "view_sensor_list":
            sensor_list_text = self.get_sensor_list()
            self.bot.send_message(chat_id, f"Registered Sensors:\n{sensor_list_text}")

        elif callback_data == "add_sensors":
            self.add_sensor_start(chat_id)

        elif callback_data == "del_sensors":
            self.del_sensor_start(chat_id)
            
        elif callback_data == "add_actuators":
            self.add_actuator_start(chat_id)

        elif callback_data == "del_actuators":
            self.del_actuator_start(chat_id)
            
        elif callback_data == "set_threshold":
            self.set_threshold_start(chat_id)

        elif callback_data == "check_threshold":
            threshold_list_text = self.get_threshold_list()
            self.bot.send_message(chat_id, f"Threshold Value:\n{threshold_list_text}")
        
        elif callback_data == "dev_back":
            home_keyboard = self.create_home_keyboard() # create keyboard
            self.bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id, # 编辑的是当前这条带按钮的消息
                                        text="Main Menu - Please Select an Option:", # 换回主菜单的文本
                                        reply_markup=home_keyboard) # 

        # elif callback_data == "logout":
        #     self.bot.send_message(chat_id, "已退出 (功能待实现)")
            
        else:
            self.bot.send_message(chat_id, f"未知操作: {callback_data}")
    
    def _register_handlers(self):
        pass
    
    def get_threshold_list(self):
        try:
            url = "http://127.0.0.1:8082/controller/getControllerThreshold"
            response = requests.get(url)
            if response.status_code != 200:
                return "Can't get threshold list."
            threshold_list = response.json()
            if not threshold_list or not isinstance(threshold_list, list):
                return "No threshold registered."
            lines = []
            for s in threshold_list:
                line = f"Type: {s['deviceType']}\nMaximum: {s['thresholdMax']}\nMinimum: {s['thresholdMin']}\nUnit: {s.get('unit', '')}\n"
                lines.append(line)
            return "\n".join(lines)
        except Exception as e:
            return f"Failed to get threshold list: {e}"

    def get_status(self):
        
        try:
            url = "http://127.0.0.1:8082/controller/getControllerAverageValue2TeleBot"
            response = requests.get(url)
            if response.status_code != 200:
                return "Can't get sensor list."
            s = response.json()          
            return (
                    f"Time: {s.get('Time')}\n"
                    f"Lightness: {s.get('Lightness')}\n"
                    f"Soil Moisture: {s.get('Soil_Moisture')}\n"
                    f"Temperature: {s.get('Temperature')}\n"
                    f"CO2 Concentration: {s.get('CO2_Concentration')}"
                ) 
        except Exception as e:
            return f"Failed to get status: {e}"

    def get_sensor_list(self):
        try:
            url = "http://127.0.0.1:8081/sensor/getSensorDevice"
            response = requests.get(url)
            if response.status_code != 200:
                return "Can't get sensor list."
            sensors = response.json()
            if not sensors or not isinstance(sensors, list):
                return "No sensor registered."
            lines = []
            for s in sensors:
                line = f"ID: {s['deviceID']}\nType: {s['deviceType']}\nLocation: {s['deviceLocation']}\nUnit: {s.get('unit', '')}\nStatus: {'ON' if s.get('status', True) else 'OFF'}\n"
                lines.append(line)
            return "\n".join(lines)
        except Exception as e:
            return f"Failed to get sensor list: {e}"
    
    def get_actuator_list(self):
        try:
            url = "http://127.0.0.1:8083/actuator/getActuatorDevice"
            response = requests.get(url)
            if response.status_code != 200:
                return "Can't get sensor list."
            sensors = response.json()
            if not sensors or not isinstance(sensors, list):
                return "No sensor registered."
            lines = []
            for s in sensors:
                line = f"ID: {s['deviceID']}\nType: {s['deviceType']}\nLocation: {s['deviceLocation']}\nLast Status Update: {s.get('lastStatusUpdate')}\nStatus: {'ON' if s.get('status', True) else 'OFF'}\n"
                lines.append(line)
            return "\n".join(lines)
        except Exception as e:
            return f"Failed to get sensor list: {e}"
        
    def add_actuator_start(self, chat_id):
        self.add_sensor_data[chat_id] = {}
        self.bot.send_message(chat_id, "Please enter the actuator type (e.g. Cooler, Heater, Sunshade_Net, LED_Light, Drip_Irrigation_Pipe, Carbon_Dioxide_Generator, Exhaust_Fan):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_actuator_type)
        
    def add_actuator_type(self, message):
        chat_id = message.chat.id
        actuator_type = message.text.strip()
        if actuator_type not in ['Cooler', 'Heater', 'Sunshade_Net', 'LED_Light', 'Drip_Irrigation_Pipe', 'Carbon_Dioxide_Generator', 'Exhaust_Fan']:
            self.bot.send_message(chat_id, "❌ Wrong actuator type. Please try again.")
            return

        self.add_sensor_data[chat_id]['type'] = actuator_type
        self.bot.send_message(chat_id, "Please enter the actuator location (e.g. Lingotto/Area_A/Position_01):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_actuator_location)
        
    def add_actuator_location(self, message):
        chat_id = message.chat.id
        self.add_sensor_data[chat_id]['location'] = message.text.strip()
        # self.bot.send_message(chat_id, "Please enter the unit (e.g. Cel, %, ppm, lx):")
        self.bot.send_message(chat_id, "Thanks. Saving your actuator info...")
        self.add_actuator_end(chat_id)
        
    def add_actuator_end(self, chat_id):
        url = "http://127.0.0.1:8083/actuator/addActuatorDevice"
        data = self.add_sensor_data.get(chat_id, {})

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Actuator added successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to add actuator: {response.text}")
        except Exception as e:
            self.bot.send_message(chat_id, f"Failed to add actuator: {e}")

        del self.add_sensor_data[chat_id]

    def add_sensor_start(self, chat_id):
        self.add_sensor_data[chat_id] = {}
        self.bot.send_message(chat_id, "Please enter the sensor type (e.g. Temperature, Lightness, Soil_Moisture, CO2_Concentration):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_sensor_type)

    def add_sensor_type(self, message):
        chat_id = message.chat.id
        self.add_sensor_data[chat_id]['type'] = message.text.strip()
        if self.add_sensor_data[chat_id]['type'] not in ["Soil_Moisture","CO2_Concentration","Temperature","Lightness"]:
            self.bot.send_message(chat_id, "Wrong Sensor Type to Input!")
            return
        self.bot.send_message(chat_id, "Please enter the sensor location (e.g. Lingotto/Area_A/Position_01):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_sensor_location)

    def add_sensor_location(self, message):
        chat_id = message.chat.id
        self.add_sensor_data[chat_id]['location'] = message.text.strip()
        # self.bot.send_message(chat_id, "Please enter the unit (e.g. Cel, %, ppm, lx):")
        self.bot.send_message(chat_id, "Please enter the update frequency (integer, unit: seconds):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_sensor_frequency)

    def add_sensor_unit(self, message):
        chat_id = message.chat.id
        match(self.add_sensor_data[chat_id]['type']):
            case 'Temperature':
                self.add_sensor_data[chat_id]['unit'] = "Cel"
            case 'Lightness':
                self.add_sensor_data[chat_id]['unit'] = "lx"
            case 'Soil_Moisture':
                self.add_sensor_data[chat_id]['unit'] = "%"
            case 'CO2_Concentration':
                self.add_sensor_data[chat_id]['unit'] = "ppm"
            case _:
                self.bot.send_message(chat_id, "Wrong Type to match") 
        
        # 调用后端接口
        url = "http://127.0.0.1:8081/sensor/addSensorDevice"
        data = self.add_sensor_data[chat_id]
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Device added successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to add device: {response.text}")
        except Exception as e:
            self.bot.send_message(chat_id, f"Failed to add device: {e}")
        # 清理缓存
        del self.add_sensor_data[chat_id]

    def add_sensor_frequency(self, message):
        chat_id = message.chat.id
        try:
            freq = int(message.text.strip())
        except Exception:
            self.bot.send_message(chat_id, "The update frequency must be an integer, please re-enter:")
            self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_sensor_frequency)
            return
        self.add_sensor_data[chat_id]['updateFrequency'] = freq
        self.add_sensor_unit(message)

    def del_actuator_start(self, chat_id):
        self.bot.send_message(chat_id, "Please enter the device ID to delete:")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.del_actuator_confirm)
        
    def del_actuator_confirm(self, message):
        chat_id = message.chat.id
        user_input_id = message.text.strip()
        actuatorList = []
        try:
            url = "http://127.0.0.1:8083/actuator/getActuatorDevice"
            response = requests.get(url)
            if response.status_code != 200:
                self.bot.send_message(chat_id, "Can't Check Device ID.")
                return 
            sensors = response.json()
            if not sensors or not isinstance(sensors, list):
                self.bot.send_message(chat_id, "No any Device, Please add a new one.")
                return 
            actuatorList = [s.get("deviceID") for s in sensors]
        except Exception as e:
            self.bot.send_message(chat_id, f"Can't Check Device ID: {e}")
            return 
        
        if user_input_id not in actuatorList:
            self.bot.send_message(chat_id, "No such DeviceID. Please check carefully!")
            return 
        
        try:
            url = "http://127.0.0.1:8083/actuator/deleteActuatorDevice"  
            data = {"deviceID": user_input_id}
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Device deleted successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to delete device: {response.text}")
        except Exception as e:
                self.bot.send_message(chat_id, f"Failed to delete device: {e}")
    
    def del_sensor_start(self, chat_id):
        self.bot.send_message(chat_id, "Please enter the device ID to delete:")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.del_sensor_confirm)

    def del_sensor_confirm(self, message):
        chat_id = message.chat.id
        user_input_id = message.text.strip()
        sensorList = []
        try:
            url = "http://127.0.0.1:8081/sensor/getSensorDevice"
            response = requests.get(url)
            if response.status_code != 200:
                self.bot.send_message(chat_id, "Can't Check Device ID.")
                return 
            sensors = response.json()
            if not sensors or not isinstance(sensors, list):
                self.bot.send_message(chat_id, "No any Device, Please add a new one.")
                return 
            sensorList = [s.get("deviceID") for s in sensors]
        except Exception as e:
            self.bot.send_message(chat_id, f"Can't Check Device ID: {e}")
            return 
        
        if user_input_id not in sensorList:
            self.bot.send_message(chat_id, "No such DeviceID. Please check carefully!")
            return 
        
        try:
            url = "http://127.0.0.1:8081/sensor/deleteSensorDevice"  
            data = {"deviceID": user_input_id}
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Device deleted successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to delete device: {response.text}")
        except Exception as e:
                self.bot.send_message(chat_id, f"Failed to delete device: {e}")
                
    def set_threshold_start(self, chat_id):
        self.add_sensor_data[chat_id] = {}
        self.bot.send_message(chat_id, "Please enter the sensor type (e.g. Temperature, Lightness, Soil_Moisture, CO2_Concentration):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.set_thresholdMax)

    def set_thresholdMax(self, message):
        chat_id = message.chat.id
        self.add_sensor_data[chat_id]['deviceType'] = message.text.strip()
        if self.add_sensor_data[chat_id]['deviceType'] not in ["Soil_Moisture","CO2_Concentration","Temperature","Lightness"]:
            self.bot.send_message(chat_id, "Wrong Sensor Type to Input!")
            return
        self.bot.send_message(chat_id, "Please enter the maximum value (unit: s):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.set_thresholdMin)
        
    def set_thresholdMin(self, message):
        chat_id = message.chat.id
        self.add_sensor_data[chat_id]['thresholdMax'] = int(message.text.strip())
        self.bot.send_message(chat_id, "Please enter the minimum value (unit: s):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.submit_thresholdValue)
        
    def submit_thresholdValue(self, message):
        chat_id = message.chat.id
        self.add_sensor_data[chat_id]['thresholdMin'] = int(message.text.strip())
        self.bot.send_message(chat_id, "Thanks. Saving your threshold setting info...")
        self.set_threshold_end(chat_id)
        
    def set_threshold_end(self,chat_id):
        url = "http://127.0.0.1:8082/controller/updateControllerThreshold"
        data = self.add_sensor_data[chat_id]
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Threshold setting successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to set threshold: {response.text}")
        except Exception as e:
            self.bot.send_message(chat_id, f"Failed to set threshold: {e}")
        # 清理缓存
        del self.add_sensor_data[chat_id]

    def _register_handlers(self):
        
        #  将装饰器指向实例方法
        # 注意写法：先调用装饰器，再传入要装饰的方法
        self.bot.message_handler(commands=['start'])(self._handle_start_home)
        self.bot.callback_query_handler(func=lambda call: True)(self._handle_callback_query)
        
    def run(self):
        logger.info("Bot is running...")
        print('Service Starting...')
        self.bot.polling()
    
if __name__ == '__main__':

    MyTelegramBot().run()