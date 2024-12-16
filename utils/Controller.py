from .MQTTController import MQTTController
from .Devices import Device
import json

class Operation:
    LED_ON = 1
    LED_OFF = 2
    AIR_CONDITIONER_ON = 3
    AIR_CONDITIONER_OFF = 4

class Controller:    
    def __init__(self):
        self.devices = {}
        self.controller = MQTTController()
        
    def add_device(self, device: Device):
        self.devices[device.device_id] = device
    
    def remove_device(self, device_id):
        del self.devices[device_id]
    
    def find_device(self, user_id, device_name):
        for device in self.devices.values():
            if device.user_id == user_id and device.name == device_name:
                return device.device_id
        return None
    
    def device_control(self, user_id, device_name, operation):
        # operation = 1 -> LED ON, 2 -> LED OFF...
        # message: json object
        device_id = self.find_device(user_id, device_name)
        if device_id is None:
            return "Device not found"
        message = ""
        if operation == Operation.LED_ON:
            message = "ON"
        elif operation == Operation.LED_OFF:
            message = "OFF"
        elif operation == Operation.AIR_CONDITIONER_ON:
            message = json.dumps({"air_conditioner": "ON", "temperature": 25})
        elif operation == Operation.AIR_CONDITIONER_OFF:
            message = json.dumps({"air_conditioner": "OFF"})
        
        self.controller.publish(device_id, message)        
    