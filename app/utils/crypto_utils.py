import os
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key_from_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data, password):
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    f = Fernet(key)
    return salt + f.encrypt(data)

def decrypt_data(encrypted_data, password):
    salt = encrypted_data[:16]
    token = encrypted_data[16:]
    key = generate_key_from_password(password, salt)
    f = Fernet(key)
    try:
        return f.decrypt(token)
    except InvalidToken:
        raise ValueError("Invalid password or corrupted data")