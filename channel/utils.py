import os
from cryptography.fernet import Fernet

def decrypt_credentials(credentials: dict) -> dict:
    decrypted_credentials = {}
    for key in credentials:
        decrypted_credentials[key] = (
            Fernet(os.getenv("ENCRYPTION_KEY")).decrypt(credentials[key].encode()).decode()
        )
    return decrypted_credentials