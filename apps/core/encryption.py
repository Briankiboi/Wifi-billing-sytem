from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os

class Encryptor:
    """Utility to encrypt/decrypt sensitive data using a master key."""
    def __init__(self):
        key = settings.env('ENCRYPTION_KEY', default=None)
        if not key:
            # For development only. In production, this MUST be in .env
            key = base64.urlsafe_b64encode(b"32-byte-long-secret-key-for-dev!!")
        self.fernet = Fernet(key)

    def encrypt(self, text):
        if not text: return None
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text):
        if not encrypted_text: return None
        try:
            return self.fernet.decrypt(encrypted_text.encode()).decode()
        except Exception:
            return None
