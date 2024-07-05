import os

from .storage import SyncStorage, AsyncStorage
from .registry import STORAGE_REGISTRY, SYNC_STORAGE_REGISTRY


class StorageHandler:
    __async_client__ = None
    __sync_client__ = None

    @classmethod
    def get_instance(cls) -> AsyncStorage:
        """DeprecationWarning: Use get_sync_instance or get_async_instance instead"""
        return cls.get_async_instance()

    @classmethod
    def get_sync_instance(cls) -> SyncStorage:
        if not cls.__sync_client__:
            storage_type = os.getenv("STORAGE_TYPE")
            if not storage_type:
                raise ValueError("STORAGE_TYPE environment variable not set")
            storage_provider = SYNC_STORAGE_REGISTRY.get(storage_type)
            if not storage_provider:
                raise ValueError(f"Storage provider {storage_type} not found")
            cls.__sync_client__ = storage_provider()
        return cls.__sync_client__

    @classmethod
    def get_async_instance(cls) -> AsyncStorage:
        if not cls.__async_client__:
            storage_type = os.getenv("STORAGE_TYPE")
            if not storage_type:
                raise ValueError("STORAGE_TYPE environment variable not set")
            storage_provider = STORAGE_REGISTRY.get(storage_type)
            if not storage_provider:
                raise ValueError(f"Storage provider {storage_type} not found")
            cls.__async_client__ = storage_provider()
        return cls.__async_client__
