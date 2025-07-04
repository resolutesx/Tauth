import os
import json
from kivy.storage.jsonstore import JsonStore

class StorageService:
    def __init__(self, user_data_dir):
        self.data_dir = user_data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.store_path = os.path.join(self.data_dir, "data.json")
        self.store = JsonStore(self.store_path)

    def load_keys(self):
        if self.store.exists('keys'):
            return self.store.get('keys')['data']
        return {}

    def save_keys(self, keys):
        self.store.put('keys', data=keys)
