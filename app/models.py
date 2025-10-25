from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    query: str
    document_id: Optional[int] = None
    context_limit: Optional[int] = 7  # Увеличено для лучшего контекста


class SourceInfo(BaseModel):
    filename: str
    document_id: int
    chunk_index: int
    similarity: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    context: List[str]


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_date: datetime
    metadata: Dict[str, Any]
    chunk_count: int

