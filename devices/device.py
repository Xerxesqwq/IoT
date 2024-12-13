# mqtt
import paho.mqtt.client as mqtt
import config

# Basic class for a device, need to be extended for different types of devices
class Device:
    def __init__(self, name, device_type, device_id, user_id):
        self.name = name
        self.device_type = device_type
        self.device_id = device_id
        self.user_id = user_id
        self.pub_topic = f"{self.user_id}/{self.device_id}/pub"
        self.sub_topic = f"{self.user_id}/{self.device_id}/sub"
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        self.client.subscribe(self.sub_topic)
        self.client.loop_start()