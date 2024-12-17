import paho.mqtt.client as mqtt
import config

class Light:
    def __init__(self, device_id):
        #self.name = name
        self.device_id = device_id
        # self.user_id = user_id
        # self.pub_topic = f"{self.user_id}/{self.device_id}/pub"
        self.sub_topic = f"devices/control/{self.device_id}"
        self.pub_topic = f"devices/public/{self.device_id}"
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        self.client.subscribe(self.sub_topic)
        # self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def on_message(self, client, userdata, message):
        if message.payload.decode() == "ON":
            self.turn_on()
        elif message.payload.decode() == "OFF":
            self.turn_off()
        else:
            print("Invalid message")

    def publish(self, message):
        self.client.publish(self.pub_topic, message)
        
    def turn_on(self):
        print("Turning on the light")
    
    def turn_off(self):
        print("Turning off the light")
        