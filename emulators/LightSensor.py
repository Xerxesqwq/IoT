import paho.mqtt.client as mqtt
import config
import json
import time
import random

class LightSensor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.sub_topic = f"devices/control/{self.device_id}"
        self.pub_topic = f"devices/public/{self.device_id}"
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        self.client.subscribe(self.sub_topic)
        self.client.loop_forever()
        self.light = 100
        self.run_loop()
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
    
    def on_message(self, client, userdata, message):
        print('Received message')
    
    def publish(self):
        self.light = random.randint(0, 100)
        light_status = '好'
        if self.light < 67:
            light_status = '一般'
        if self.light < 33:
            light_status = '差'
        message = {
            'light': light_status
        }
        self.client.publish(self.pub_topic, json.dumps(message))
    
    def run_loop(self):
        while True:
            self.client.loop()
            time.sleep(20)