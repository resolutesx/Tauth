import pyotp

def validate_account_name(name):
    return bool(name and name.strip())

def validate_totp_secret(secret):
    if not secret or not secret.strip():
        return False
    try:
        pyotp.TOTP(secret).now()
        return True
    except Exception:
        return False
