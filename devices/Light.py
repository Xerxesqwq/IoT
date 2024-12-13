import devices.device as device

class Light(device.Device):
    def __init__(self, name, device_id, user_id):
        super().__init__(name, 'light', device_id, user_id)
        self.status = 'OFF'
        self.client.publish(self.pub_topic, self.status)
        
    def toggle(self):
        if self.status == 'OFF':
            self.status = 'ON'
        else:
            self.status = 'OFF'
        
    def get_status(self):
        return self.status
    
    def publish_status(self):
        self.client.publish(self.pub_topic, self.status)
    
    def on_message(self, client, userdata, message):
        if message.topic == self.sub_topic:
            self.toggle()
            self.publish_status()
            print(f"Light status changed to {self.status}")
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        self.client.subscribe(self.sub_topic)
        self.publish_status()
    
    def __str__(self):
        return f"Light {self.name} is {self.status}"
    