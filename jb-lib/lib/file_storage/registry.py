from typing import Dict, Type
from .storage import Storage
from .local import LocalStorage
from .azure import AzureStorage

STORAGE_REGISTRY: Dict[str, Type[Storage]] = {
    "local": LocalStorage,
    "azure": AzureStorage,
}