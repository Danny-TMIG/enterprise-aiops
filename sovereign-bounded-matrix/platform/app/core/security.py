import hashlib
import hmac
import time
import base64

class SovereignAuthEngine:
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
        if not salt:
            salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return base64.b64encode(pwd_hash).decode('utf-8'), base64.b64encode(salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
        salt = base64.b64decode(stored_salt.encode('utf-8'))
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return base64.b64encode(pwd_hash).decode('utf-8') == stored_hash
