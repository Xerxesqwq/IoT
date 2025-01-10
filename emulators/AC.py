import paho.mqtt.client as mqtt
import config
import json
import time

class AC:
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
        self.client.run_loop()
        self.cnt = 0
        self.mode = 'auto'
        self.temperature = 25
        self.fan_speed = 'medium'
        self.swing = 'off'
        self.power = 'off'
        self.run_loop()
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")


    def run_loop(self):
        while True:
            self.client.loop()
            time.sleep(1)
            self.cnt += 1
            if self.cnt == 15:
                self.publish()
                self.cnt = 0
    
    def on_message(self, client, userdata, message):
        data = json.loads(message.payload.decode())
        # data may have the following data (but may not exist all at once):
        # mode: cool, heat, dry, fan_only, auto
        # temperature: 16-30
        # fan_speed: low, medium, high
        # swing: on, off
        # power: on, off
        new_mode = data.get('mode') if data.get('mode') else None
        new_temperature = data.get('temperature') if data.get('temperature') else None
        new_fan_speed = data.get('fan_speed') if data.get('fan_speed') else None
        new_swing = data.get('swing') if data.get('swing') else None
        new_power = data.get('power') if data.get('power') else None
        if new_mode is not None:
            self.set_mode(new_mode)
        if new_temperature is not None:
            self.set_temperature(new_temperature)
        if new_fan_speed is not None:
            self.set_fan_speed(new_fan_speed)
        if new_swing is not None:
            self.set_swing(new_swing)
        if new_power is not None:
            self.set_power(new_power)
        
    def publish(self):
        message = {
            "mode": self.mode,
            "temperature": self.temperature,
            "fan_speed": self.fan_speed,
            "swing": self.swing,
            "power": self.power
        }
        self.client.publish(self.pub_topic, message)
        
    def set_mode(self, mode):
        self.mode = mode
        print(f"Setting mode to {mode}")
    
    def set_temperature(self, temperature):
        self.temperature = temperature
        print(f"Setting temperature to {temperature}")
    
    def set_fan_speed(self, fan_speed):
        self.fan_speed = fan_speed
        print(f"Setting fan speed to {fan_speed}")
    
    def set_swing(self, swing):
        self.swing = swing
        print(f"Setting swing to {swing}")
    
    def set_power(self, power):
        self.power = power
        print(f"Setting power to {power}")
        