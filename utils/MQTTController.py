import paho.mqtt.client as mqtt
import config

class MQTTController:
    def __init__(self, topic = "devices/#"):
        self.client = mqtt.Client()
        self.broker = config.MQTT_BROKER
        self.port = config.MQTT_PORT
        self.topic = topic
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connect()

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        # self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def on_message(self, client, userdata, message):
        print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

    def publish(self, device_id, message):
        topic = f"devices/control/{device_id}"
        if self.client.publish(topic, message).rc == 0:
            print(f"Published message '{message}' to topic '{topic}'")
        else:
            print(f"Failed to publish message '{message}' to topic '{topic}'")