from .Database import DatabaseManager

class Query:
    def __init__(self):
        self.db = DatabaseManager(sync_mode=True)
    
    def query(self, user_id, device_name):
        device_id = self.db.get_device_id(user_id, device_name)
        