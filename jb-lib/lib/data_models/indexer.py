from typing import List
from pydantic import BaseModel


class Indexer(BaseModel):
    type: str
    collection_name: str
    files: List[str]