import time
import cherrypy
import telebot
from telebot import types # by telebot.types create keyboard
import requests
import threading

import logging
logger = logging.getLogger('telebot')

# TeleBot: SmartAgrBot
class MyTelegramBot:

    def __init__(self, chatID=None):
        
        self.chatID = chatID
        self.API_KEY = '7312600355:AAHOD25LLkWUX-kWxsBbpSI7Zyk38bqOn6E'
        self.bot = telebot.TeleBot(self.API_KEY)
        self.add_device_data = {}  # 用于暂存用户输入
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
    
    @cherrypy.expose
    def index(self):
        return "Telegram bot is running."

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
        dev_sensorlist = types.InlineKeyboardButton(text="Sensor List", callback_data="view_sensor_list") 
        add_dev = types.InlineKeyboardButton(text='Add Device', callback_data="add_devices")
        del_dev = types.InlineKeyboardButton(text='Delete Device', callback_data="del_devices")
        dev_back = types.InlineKeyboardButton(text="Back", callback_data="dev_back")
        keyboard.add(actuator_status, dev_sensorlist, add_dev, del_dev)
        keyboard.add(dev_back)
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
            print(f"answer_callback_query error: {e}")
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
            # 待实现
            self.bot.send_message(chat_id, f"Registered Actuators:\n{actuator_list_text}")

        elif callback_data == "view_sensor_list":
            sensor_list_text = self.get_sensor_list()
            self.bot.send_message(chat_id, f"Registered Sensors:\n{sensor_list_text}")

        elif callback_data == "add_devices":
            self.add_device_start(chat_id)

        elif callback_data == "del_devices":
            self.del_device_start(chat_id)

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

    def get_status(self):
        
        try:
            # 1. 获取所有注册的传感器信息
            sensor_url = "http://127.0.0.1:8080/sensor/getSensorDevice"
            sensor_resp = requests.get(sensor_url)
            if sensor_resp.status_code != 200:
                return "Can't get sensor list."
            sensors = sensor_resp.json()
            if not sensors:
                return "No sensor registered."

            # 2. 获取所有 deviceID 的最新数据（一次性批量获取）
            data_url = "http://127.0.0.1:5002/getAllLatestData"
            data_resp = requests.get(data_url)
            if data_resp.status_code != 200:
                return "Can't get latest data."
            all_data = data_resp.json().get("data", {})

            # 3. 组合信息
            status_lines = []
            for sensor in sensors:
                device_id = sensor['deviceID']
                latest = all_data.get(device_id)
                print(latest)
                if latest and isinstance(latest, dict):
                    value = latest.get('value', 'N/A')
                    unit = latest.get('unit', sensor.get('unit', ''))
                else:
                    value = 'N/A'
                    unit = sensor.get('unit', '')
                line = f"Position: {sensor['deviceLocation']}\n : {sensor['deviceType']}\nValue: {value} {unit}\n"
                status_lines.append(line)
            return "\n".join(status_lines)
        except Exception as e:
            return f"Failed to get status: {e}"

    def get_sensor_list(self):
        try:
            url = "http://127.0.0.1:8080/sensor/getSensorDevice"
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
        pass

    def add_device_start(self, chat_id):
        self.add_device_data[chat_id] = {}
        self.bot.send_message(chat_id, "Please enter the sensor type (e.g. Temperature, Lightness, Soil_Moisture, CO2_Concentration):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_device_type)

    def add_device_type(self, message):
        chat_id = message.chat.id
        self.add_device_data[chat_id]['type'] = message.text.strip()
        self.bot.send_message(chat_id, "Please enter the sensor location (e.g. Lingotto/Area_A/Position_01):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_device_location)

    def add_device_location(self, message):
        chat_id = message.chat.id
        self.add_device_data[chat_id]['location'] = message.text.strip()
        # self.bot.send_message(chat_id, "Please enter the unit (e.g. Cel, %, ppm, lx):")
        self.bot.send_message(chat_id, "Please enter the update frequency (integer, unit: seconds):")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_device_frequency)

    def add_device_unit(self, message):
        chat_id = message.chat.id
        match(self.add_device_data[chat_id]['type']):
            case 'Temperature':
                self.add_device_data[chat_id]['unit'] = "Cel"
            case 'Lightness':
                self.add_device_data[chat_id]['unit'] = "lx"
            case 'Soil_Moisture':
                self.add_device_data[chat_id]['unit'] = "%"
            case 'CO2_Concentration':
                self.add_device_data[chat_id]['unit'] = "ppm"
            case _:
                self.bot.send_message(chat_id, "Wrong Type to match") 
        
        # 调用后端接口
        url = "http://127.0.0.1:8080/sensor/addSensorDevice"
        data = self.add_device_data[chat_id]
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Device added successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to add device: {response.text}")
        except Exception as e:
            self.bot.send_message(chat_id, f"Failed to add device: {e}")
        # 清理缓存
        del self.add_device_data[chat_id]

    def add_device_frequency(self, message):
        chat_id = message.chat.id
        try:
            freq = int(message.text.strip())
        except Exception:
            self.bot.send_message(chat_id, "The update frequency must be an integer, please re-enter:")
            self.bot.register_next_step_handler_by_chat_id(chat_id, self.add_device_frequency)
            return
        self.add_device_data[chat_id]['updateFrequency'] = freq
        self.add_device_unit(message)

    def del_device_start(self, chat_id):
        self.bot.send_message(chat_id, "Please enter the device ID to delete:")
        self.bot.register_next_step_handler_by_chat_id(chat_id, self.del_device_confirm)

    def del_device_confirm(self, message):
        chat_id = message.chat.id
        device_id = message.text.strip()
        url = "http://127.0.0.1:8080/sensor/deleteSensorDevice"
        data = {"deviceID": device_id}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.bot.send_message(chat_id, "Device deleted successfully!")
            else:
                self.bot.send_message(chat_id, f"Failed to delete device: {response.text}")
        except Exception as e:
            self.bot.send_message(chat_id, f"Failed to delete device: {e}")

    
    def _register_handlers(self):
        
        #  将装饰器指向实例方法
        # 注意写法：先调用装饰器，再传入要装饰的方法
        self.bot.message_handler(commands=['start'])(self._handle_start_home)
        self.bot.callback_query_handler(func=lambda call: True)(self._handle_callback_query)
    
    def run(self):
        self.running = True
        self.bot_thread = threading.Thread(target=self._polling_loop)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
    def _polling_loop(self):
        while self.running:
            try:
                self.bot.polling(none_stop=True, interval=0)
            except Exception as e:
                logger.exception(f"Polling error: {e}")
    
    def stop(self):
        self.running = False
        self.bot.stop_polling()
        if self.bot_thread is not None:
            self.bot_thread.join()

    


