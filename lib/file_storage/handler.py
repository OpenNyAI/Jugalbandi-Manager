import os

from .storage import Storage
from .registry import STORAGE_REGISTRY

class StorageHandler:
    __client__ = None

    @classmethod
    def get_instance(cls) -> Storage:
        if not cls.__client__:
            storage_type = os.getenv("STORAGE_TYPE")
            if not storage_type:
                raise ValueError("STORAGE_TYPE environment variable not set")
            storage_provider = STORAGE_REGISTRY.get(storage_type)
            if not storage_provider:
                raise ValueError(f"Storage provider {storage_type} not found")
            cls.__client__ = storage_provider()
        return cls.__client__
    