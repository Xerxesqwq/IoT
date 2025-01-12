from .MQTTController import MQTTController
from .Devices import Device
import json
from .Database import DatabaseManager

class Operation:
    LED_ON = 1
    LED_OFF = 2
    AIR_CONDITION_OPERATING = 3
    FAN_SPEED_UP = 5
    FAN_SPEED_DOWN = 6
    FAN_SET_SPEED = 7
    RING_ALARM_ON = 8
    RING_ALARM_OFF = 9
    PLAY_MUSIC = 10
    

class Controller:    
    def __init__(self):
        self.devices = {}
        self.controller = MQTTController()
        self.db = DatabaseManager(sync_mode=True)
    
    def find_device(self, user_id, device_name):
        device_id = self.db.get_device_id(user_id, device_name)
        return device_id
    
    def find_device_status(self, user_id, device_name):
        device_id = self.find_device(user_id, device_name)
        if device_id is None:
            return None
        return self.db.get_device_status(device_id)
    
    def device_control(self, user_id, device_name, operation, payload = None):
            """
            user_id: int, the user id
            device_name: str, the name of the device
            operation: int, the operation to be performed, refer to Operation class for more explicit
            payload: json format str, the payload to be sent to the device, if the operation requires a payload, default is None
            """
            device_id = self.find_device(user_id, device_name)
            if device_id == -1 or device_id is None:
                print('Device not found')
                return "Device not found"
            message = ""
            if operation == Operation.LED_ON:
                message = "ON"
            elif operation == Operation.LED_OFF:
                message = "OFF"
            elif operation == Operation.FAN_SPEED_UP:
                current_speed = self.find_device_status(user_id, device_name)
                current_speed = current_speed['status']
                if current_speed == "OFF":
                    message = "LV1"
                elif current_speed == "LV1":
                    message = "LV2"
                else:
                    message = "OFF"
            elif operation == Operation.FAN_SPEED_DOWN:
                current_speed = self.find_device_status(user_id, device_name)
                current_speed = current_speed['status']
                if current_speed == "LV1":
                    message = "OFF"
                elif current_speed == "LV2":
                    message = "LV1"
                else:
                    message = "OFF"
            elif operation == Operation.FAN_SET_SPEED:
                message = payload
            elif operation == Operation.RING_ALARM_ON:
                message = {"Operation": "ON"}
            elif operation == Operation.RING_ALARM_OFF:
                message = {"Operation": "OFF"}
            elif operation == Operation.PLAY_MUSIC:
                music = self.db.get_music(payload)
                tones = music['tones'].replace(',', ' ')
                durations = music['durations'].replace(',', ' ')
                cnt = len(tones.split(' '))
                #message = "123"
                message = {"tones": tones, "durations": durations, "len": cnt, "Operation": 'MUSIC'}
                message = json.dumps(message)
                print(message)
            elif operation == Operation.AIR_CONDITION_OPERATING:
                message = payload            
            self.controller.publish(device_id, message)

    def device_control_all(self, user_id, type, operation):
        device_name = self.db.get_user_devices_by_type(user_id, type)
        for each in device_name:
            self.device_control(user_id, each, operation)
    