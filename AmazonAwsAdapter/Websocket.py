from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from DynamoDB_Reader import DynamoDBReader
import os

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = DynamoDBReader('IoTSensorData')

CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cataLog.json")

def getLatestData(sensor_type):
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    device_ids = [sensor['deviceID'] for sensor in config['sensor_list'] if sensor['deviceType'] == sensor_type]
    values = []
    for device_id in device_ids:
        data = reader.get_latest_data(device_id)
        if data and 'value' in data:
            values.append(float(data['value']))
    return values

@app.websocket("/ws/sensor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "Temperature": getLatestData("Temperature"),
            "Soil_Moisture": getLatestData("Soil_Moisture"),
            "Lightness": getLatestData("Lightness"),
            "CO2_Concentration": getLatestData("CO2_Concentration")
        }
        await websocket.send_text(json.dumps(data))
        await asyncio.sleep(2)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/thresholds")
def get_thresholds():
    # 你可以根据实际需求返回阈值
    return {
        "temperature": 28,
        "moisture": 45,
        "lightness": 350,
        "co2_concentration": 600
    }
