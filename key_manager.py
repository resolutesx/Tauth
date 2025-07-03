from kivy.storage.jsonstore import JsonStore
from kivy.app import App
import pyotp
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os
import re

class KeyManager:
    def __init__(self):
        self.keys = {}  
        self._store = None
        self._store_path = None
        self._load_keys()
    
    @property
    def store_path(self):
        if self._store_path is None:
            app = App.get_running_app()
            if app is not None and hasattr(app, 'user_data_dir'):
                self._store_path = os.path.join(app.user_data_dir, 'accounts.json')
            else:
                self._store_path = os.path.abspath('./accounts.json')
        return self._store_path
    
    @property
    def store(self):
        if self._store is None:
            self._store = JsonStore(self.store_path)
        return self._store
    
    def _normalize_secret(self, secret: str) -> str:
        """Normalize and validate TOTP secret"""
        normalized = secret.strip().replace(' ', '').replace('-', '').upper()

        if not re.match(r'^[A-Z2-7]+=*$', normalized):
            raise ValueError("Invalid Base32 format")

        padding_needed = (8 - len(normalized) % 8) % 8
        normalized += '=' * padding_needed
        
        return normalized
    
    def _validate_secret(self, secret: str) -> bool:
        """Validate that secret can generate TOTP codes"""
        try:
            normalized = self._normalize_secret(secret)
            totp = pyotp.TOTP(normalized)
            code = totp.now()
            return len(code) == 6 and code.isdigit()
        except Exception as e:
            print(f"Secret validation failed: {e}")
            return False
    
    def _load_keys(self):
        """Load keys from storage with validation"""
        self.keys = {}
        try:
            for name in self.store:
                stored_data = self.store.get(name)
                if 'secret' in stored_data:
                    secret = stored_data['secret']
                    if self._validate_secret(secret):
                        self.keys[name] = secret
                    else:
                        print(f"Warning: Invalid secret for {name}, skipping")
        except Exception as e:
            print(f"Error loading keys: {e}")
    
    def add_key(self, name: str, secret: str) -> bool:
        """Add a new TOTP key with validation"""
        try:
            if not self._validate_secret(secret):
                raise ValueError("Invalid TOTP secret")
            
            normalized = self._normalize_secret(secret)
            self.store.put(name, secret=normalized)
            self.keys[name] = normalized
            return True
        except Exception as e:
            print(f"Failed to add key {name}: {e}")
            return False
    
    def remove_key(self, name: str) -> bool:
        """Remove a key"""
        try:
            if name in self.keys:
                self.store.delete(name)
                del self.keys[name]
                return True
            return False
        except Exception as e:
            print(f"Failed to remove key {name}: {e}")
            return False
    
    def update_key(self, name: str, new_secret: str) -> bool:
        """Update an existing key with validation"""
        try:
            if not self._validate_secret(new_secret):
                raise ValueError("Invalid TOTP secret")
            
            normalized = self._normalize_secret(new_secret)
            self.store.put(name, secret=normalized)
            self.keys[name] = normalized
            return True
        except Exception as e:
            print(f"Failed to update key {name}: {e}")
            return False
    
    def get_keys(self):
        return dict(self.keys)
    
    def get_totp_code(self, name: str) -> str:
        """Generate current TOTP code for a given account"""
        if name not in self.keys:
            raise KeyError(f"No key found for {name}")
        
        try:
            totp = pyotp.TOTP(self.keys[name])
            return totp.now()
        except Exception as e:
            raise ValueError(f"Failed to generate code for {name}: {e}")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def backup(self, backup_path, password: str):
        import json

        data = json.dumps(self.keys).encode()

        salt = os.urandom(16)
        key = self._derive_key(password, salt)
        f = Fernet(key)
        token = f.encrypt(data)
        with open(backup_path, 'wb') as f_out:
            f_out.write(salt + token)
    
    def restore(self, backup_path, password: str):
        import json
        try:
            with open(backup_path, 'rb') as f_in:
                raw = f_in.read()
            
            salt, token = raw[:16], raw[16:]
            key = self._derive_key(password, salt)
            f = Fernet(key)
            data = f.decrypt(token)
            creds = json.loads(data.decode())
            valid_creds = {}
            for name, secret in creds.items():
                if self._validate_secret(secret):
                    valid_creds[name] = secret
                else:
                    print(f"Warning: Skipping invalid restored key for {name}")

            for name, secret in valid_creds.items():
                self.store.put(name, secret=secret)
            self.keys = valid_creds
            
        except Exception as e:
            raise ValueError(f"Failed to restore backup: {e}")

