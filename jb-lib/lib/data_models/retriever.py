from typing import Any, Dict
from pydantic import BaseModel


class RAG(BaseModel):
    source: str
    turn_id: str
    collection_name: str
    query: str
    top_chunk_k_value: int


class RAGResponse(BaseModel):
    chunk: str
    metadata: Dict[str, Any] = {}
