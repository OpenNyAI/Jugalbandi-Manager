from typing import Any, Dict
from pydantic import BaseModel


class RAG(BaseModel):
    type: str
    source: str
    turn_id: str
    collection_name: str
    query: str
    top_chunk_k_value: int
    do_hybrid_search: bool


class RAGResponse(BaseModel):
    chunk: str
    metadata: Dict[str, Any] = {}
