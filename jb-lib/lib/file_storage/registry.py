from typing import Dict, Type
from .storage import SyncStorage, AsyncStorage
from .local import LocalAsyncStorage, LocalSyncStorage
from .azure import AzureAsyncStorage, AzureSyncStorage

STORAGE_REGISTRY: Dict[str, Type[AsyncStorage]] = {
    "local": LocalAsyncStorage,
    "azure": AzureAsyncStorage,
}

SYNC_STORAGE_REGISTRY: Dict[str, Type[SyncStorage]] = {
    "local": LocalSyncStorage,
    "azure": AzureSyncStorage,
}
