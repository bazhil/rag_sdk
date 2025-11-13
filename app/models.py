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


class SummaryRequest(BaseModel):
    document_id: int


class SummaryResponse(BaseModel):
    summary: str
    document_id: int
    filename: str
    chunk_count: int


class ReferatRequest(BaseModel):
    document_id: int


class ReferatResponse(BaseModel):
    referat: str
    document_id: int
    filename: str
    chunk_count: int
    pdf_url: str  # URL для скачивания PDF


class WebSearchRequest(BaseModel):
    query: str
    fetch_content: bool = True  # Извлекать ли содержимое страниц


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class WebSearchResponse(BaseModel):
    query: str
    summary: str
    results: List[WebSearchResult]
    sources_count: int

