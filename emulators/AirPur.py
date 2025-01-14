from paho.mqtt.client import Client
import config
import json
import time
import random

class AirPur:
    def __init__(self, device_id):
        self.device_id = device_id
        self.sub_topic = f"devices/control/{self.device_id}"
        self.pub_topic = f"devices/public/{self.device_id}"
        self.client = Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        self.client.subscribe(self.sub_topic)
        self.client.loop_forever()
        self.cnt = 0
        self.mode = 'auto'
        self.fan_speed = 'medium'
        self.power = 'off'
        self.filter = 100
        self.AQI = 100
        self.run_loop()
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
    
    def on_message(self, client, userdata, message):
        data = json.loads(message.payload.decode())
        new_mode = data.get('mode') if data.get('mode') else None
        new_fan_speed = data.get('fan_speed') if data.get('fan_speed') else None
        new_power = data.get('power') if data.get('power') else None
        if new_mode is not None:
            self.set_mode(new_mode)
        if new_fan_speed is not None:
            self.set_fan_speed(new_fan_speed)
        if new_power is not None:
            self.set_power(new_power)
    
    def publish(self):
        self.AQI = random.randint(0, 500)
        self.filter = random.randint(0, 100)
        message = {
            'mode': self.mode,
            'fan_speed': self.fan_speed,
            'power': self.power,
            'filter': self.filter,
            'AQI': self.AQI
        }
        self.client.publish(self.pub_topic, json.dumps(message))
    
    def set_mode(self, mode):
        self.mode = mode
        self.publish()
    
    def set_fan_speed(self, fan_speed):
        self.fan_speed = fan_speed
        self.publish()
    
    def set_power(self, power):
        self.power = power
        self.publish()
        
    def run_loop(self):
        while True:
            self.client.loop()
            time.sleep(1)
            self.cnt += 1
            if self.cnt == 20:
                self.publish()
                self.cnt = 0