import os

from cryptography.fernet import Fernet


def decrypt_credentials(credentials: str) -> str:
    decrypted_credentials = (
        Fernet(os.getenv("ENCRYPTION_KEY")).decrypt(credentials.encode()).decode()
    )
    return decrypted_credentials
