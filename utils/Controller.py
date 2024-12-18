from .MQTTController import MQTTController
from .Devices import Device
import json
from .Database import DatabaseManager

class Operation:
    LED_ON = 1
    LED_OFF = 2
    AIR_CONDITIONER_ON = 3
    AIR_CONDITIONER_OFF = 4

class Controller:    
    def __init__(self):
        self.devices = {}
        self.controller = MQTTController()
        self.db = DatabaseManager(sync_mode=True)
    
    def find_device(self, user_id, device_name):
        device_id = self.db.get_device_id(user_id, device_name)
        return device_id
    
    def device_control(self, user_id, device_name, operation):
        # operation = 1 -> LED ON, 2 -> LED OFF...
        # message: json object
        device_id = self.find_device(user_id, device_name)
        if device_id == -1 or device_id is None:
            print('Device not found')
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

    
    def device_control_all(self, user_id, type, operation):
        device_name = self.db.get_user_devices_by_type(user_id, type)
        for each in device_name:
            self.device_control(user_id, each, operation)
    