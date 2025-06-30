import json
from pathlib import Path
import keyring
import pyotp
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os

CONFIG_DIR = Path.home() / '.config' / 'authenticator_app'
ACCOUNTS_FILE = CONFIG_DIR / 'accounts.json'
SERVICE_NAME = 'AuthenticatorApp'

class KeyManager:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.keys = {}  # name -> secret
        self._load_keys()

    def _load_keys(self):
        if ACCOUNTS_FILE.exists():
            try:
                accounts = json.loads(ACCOUNTS_FILE.read_text())
            except json.JSONDecodeError:
                accounts = []
        else:
            accounts = []
        for name in accounts:
            secret = keyring.get_password(SERVICE_NAME, name)
            if secret:
                self.keys[name] = secret

    def add_key(self, name: str, secret: str):
        norm = secret.strip().replace(' ', '').upper()
        pyotp.TOTP(norm).now()
        keyring.set_password(SERVICE_NAME, name, norm)
        self.keys[name] = norm
        self._save_accounts()

    def remove_key(self, name: str):
        if name in self.keys:
            keyring.delete_password(SERVICE_NAME, name)
            del self.keys[name]
            self._save_accounts()

    def update_key(self, name: str, new_secret: str):
        norm = new_secret.strip().replace(' ', '').upper()
        pyotp.TOTP(norm).now()
        keyring.set_password(SERVICE_NAME, name, norm)
        self.keys[name] = norm

    def _save_accounts(self):
        accounts = list(self.keys.keys())
        ACCOUNTS_FILE.write_text(json.dumps(accounts))

    def get_keys(self):
        return dict(self.keys)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def backup(self, backup_path: Path, password: str):
        # serialize secrets dict
        data = json.dumps(self.keys).encode()
        # generate salt
        salt = os.urandom(16)
        key = self._derive_key(password, salt)
        f = Fernet(key)
        token = f.encrypt(data)
        # write salt + token
        with open(backup_path, 'wb') as f_out:
            f_out.write(salt + token)

    def restore(self, backup_path: Path, password: str):
        raw = backup_path.read_bytes()
        salt, token = raw[:16], raw[16:]
        key = self._derive_key(password, salt)
        f = Fernet(key)
        data = f.decrypt(token)
        creds = json.loads(data.decode())
        # overwrite existing keys
        for name, secret in creds.items():
            keyring.set_password(SERVICE_NAME, name, secret)
        # update account list
        self.keys = creds
        self._save_accounts()
