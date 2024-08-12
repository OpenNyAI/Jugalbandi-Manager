from typing import Dict, Type
from .storage import SyncStorage, AsyncStorage
from .local import LocalAsyncStorage, LocalSyncStorage
from .azure import AzureAsyncStorage, AzureSyncStorage
from .aws import AWSAsyncStorage, AWSSyncStorage
from .gcp import GCPAsyncStorage, GCPSyncStorage

STORAGE_REGISTRY: Dict[str, Type[AsyncStorage]] = {
    "local": LocalAsyncStorage,
    "azure": AzureAsyncStorage,
    "aws": AWSAsyncStorage,
    "gcp": GCPAsyncStorage,
}

SYNC_STORAGE_REGISTRY: Dict[str, Type[SyncStorage]] = {
    "local": LocalSyncStorage,
    "azure": AzureSyncStorage,
    "aws": AWSSyncStorage,
    "gcp": GCPSyncStorage,
}
