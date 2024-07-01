import os
from cryptography.fernet import Fernet


class EncryptionHandler:
    __fernet_client__ = None

    @classmethod
    def initialize(cls):
        if cls.__fernet_client__ is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY not found in environment variables")
            cls.__fernet_client__ = Fernet(encryption_key)

    @classmethod
    def encrypt_text(cls, text: str) -> str:
        cls.initialize()
        return cls.__fernet_client__.encrypt(text.encode()).decode()

    @classmethod
    def encrypt_dict(cls, data: dict) -> dict:
        cls.initialize()
        return {key: cls.encrypt_text(value) for key, value in data.items()}

    @classmethod
    def decrypt_text(cls, text: str) -> str:
        cls.initialize()
        return cls.__fernet_client__.decrypt(text.encode()).decode()

    @classmethod
    def decrypt_dict(cls, data: dict) -> dict:
        cls.initialize()
        return {key: cls.decrypt_text(value) for key, value in data.items()}
