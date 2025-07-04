import pyotp
import json
from pathlib import Path
from app.utils.crypto_utils import encrypt_data, decrypt_data

class AuthService:
    def __init__(self, storage_service):
        self.storage = storage_service
        self.keys = self.storage.load_keys()
        self.totp_cache = {}

    def get_otp(self, name):
        if name not in self.totp_cache:
            secret = self.keys.get(name)
            if not secret:
                raise ValueError(f"No secret found for account: {name}")
            self.totp_cache[name] = pyotp.TOTP(secret)
        return self.totp_cache[name].now()

    def add_key(self, name, secret):
        if name in self.keys:
            raise ValueError("Account with this name already exists.")
        pyotp.TOTP(secret).now()  # Validate secret
        self.keys[name] = secret
        self.storage.save_keys(self.keys)
        if name in self.totp_cache:
            del self.totp_cache[name]

    def update_key(self, name, secret):
        if name not in self.keys:
            raise ValueError("Account not found.")
        pyotp.TOTP(secret).now()  # Validate secret
        self.keys[name] = secret
        self.storage.save_keys(self.keys)
        if name in self.totp_cache:
            del self.totp_cache[name]

    def remove_key(self, name):
        if name in self.keys:
            del self.keys[name]
            self.storage.save_keys(self.keys)
            if name in self.totp_cache:
                del self.totp_cache[name]

    def get_all_keys(self):
        return self.keys

    def backup(self, path, password):
        data = json.dumps(self.keys).encode('utf-8')
        encrypted_data = encrypt_data(data, password)
        with open(path, 'wb') as f:
            f.write(encrypted_data)

    def restore(self, path, password):
        with open(path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = decrypt_data(encrypted_data, password)
        self.keys = json.loads(decrypted_data.decode('utf-8'))
        self.storage.save_keys(self.keys)
        self.totp_cache.clear()
