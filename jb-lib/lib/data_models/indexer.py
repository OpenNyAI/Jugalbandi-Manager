from enum import Enum
from typing import List

from pydantic import BaseModel


class IndexType(str, Enum):
    default = "default"
    r2r = "r2r"


class Indexer(BaseModel):
    type: str
    chunk_size: int
    chunk_overlap: int
    collection_name: str
    files: List[str]
