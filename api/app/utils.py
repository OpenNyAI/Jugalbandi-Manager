import os
from cryptography.fernet import Fernet

def extract_reference_id(text):
    JB_IDENTIFIER = "jbkey"
    if JB_IDENTIFIER not in text:
        return None
    start_index = text.find(JB_IDENTIFIER)
    if start_index == -1:
        return None  # Start magic string not found

    new_index = start_index + len(JB_IDENTIFIER)
    end_index = text.find(JB_IDENTIFIER, new_index)
    if end_index == -1:
        return None  # End magic string not found

    return text[start_index:end_index+len(JB_IDENTIFIER)]

def encrypt_text(text: str) -> str:
    # TODO - implement encryption
    encryption_key = os.getenv("ENCRYPTION_KEY")
    f = Fernet(encryption_key)
    return f.encrypt(text.encode()).decode()


def encrypt_dict(data: dict) -> dict:
    encrypted_data = {}
    for k, v in data.items():
        encrypted_data[k] = encrypt_text(v)
    return encrypted_data