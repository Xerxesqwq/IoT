class Device:
    def __init__(self, name : str, device_type : str, \
        device_id : int, user_id : int):
        self.name = name
        self.device_type = device_type
        self.device_id = device_id
        self.user_id = user_id