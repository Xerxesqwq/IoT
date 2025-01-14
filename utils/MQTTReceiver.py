from .Database import DatabaseManager
import config
import paho.mqtt.client as mqtt
from datetime import datetime

class MQTTReceiver:
    def __init__(self):
        self.client = mqtt.Client()
        self.broker = config.MQTT_BROKER
        self.port = config.MQTT_PORT
        self.topic = "devices/public/#"
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connect()
        # use async to improve performance
        self.db = DatabaseManager(sync_mode=True)
        print("MQTTReceiver initialized")
    
    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.subscribe(self.topic)
        #self.client.loop_forever()
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
    
    def on_message(self, client, userdata, message):
        print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")
        payload = message.payload.decode()
        # topic: devices/public/{client_id}, client_id is device_id
        topic = message.topic.split("/")
        client_id = topic[-1]
        self.db.log_event(client_id, payload, datetime.now())
