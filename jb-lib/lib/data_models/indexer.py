from typing import List
from pydantic import BaseModel

class IndexerInput(BaseModel):
    collection_name: str
    files: List[str]
