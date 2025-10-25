import asyncpg
from typing import List, Dict, Any, Optional
import numpy as np
import json
from .config import settings


class VectorStore:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            host=settings.postgres_host,
            port=settings.postgres_port,
            min_size=2,
            max_size=10
        )
        
    async def close(self):
        if self.pool:
            await self.pool.close()
            
    async def create_document(self, filename: str, file_size: int, metadata: Optional[Dict[str, Any]] = None) -> int:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO documents (filename, file_size, metadata)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                filename, file_size, json.dumps(metadata or {})
            )
            return row['id']
            
    async def add_chunks(self, document_id: int, chunks: List[Dict[str, Any]]):
        async with self.pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO chunks (document_id, content, embedding, chunk_index, metadata)
                VALUES ($1, $2, $3::vector, $4, $5)
                """,
                [
                    (
                        document_id,
                        chunk['content'],
                        json.dumps(chunk['embedding']),  # Правильный формат для vector: JSON array
                        chunk['chunk_index'],
                        json.dumps(chunk.get('metadata', {}))
                    )
                    for chunk in chunks
                ]
            )
            
    async def search_similar(self, query_embedding: List[float], document_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        query_vector = json.dumps(query_embedding)
        
        async with self.pool.acquire() as conn:
            if document_id:
                rows = await conn.fetch(
                    """
                    SELECT c.id, c.content, c.chunk_index, c.metadata,
                           d.filename, d.id as document_id,
                           1 - (c.embedding <=> $1::vector) as similarity
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE c.document_id = $2
                    ORDER BY c.embedding <=> $1::vector
                    LIMIT $3
                    """,
                    query_vector, document_id, limit
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT c.id, c.content, c.chunk_index, c.metadata,
                           d.filename, d.id as document_id,
                           1 - (c.embedding <=> $1::vector) as similarity
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    ORDER BY c.embedding <=> $1::vector
                    LIMIT $2
                    """,
                    query_vector, limit
                )
                
            return [dict(row) for row in rows]
            
    async def get_documents(self) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT d.id, d.filename, d.file_size, d.upload_date, d.metadata,
                       COUNT(c.id) as chunk_count
                FROM documents d
                LEFT JOIN chunks c ON d.id = c.document_id
                GROUP BY d.id, d.filename, d.file_size, d.upload_date, d.metadata
                ORDER BY d.upload_date DESC
                """
            )
            return [
                {
                    **dict(row),
                    'metadata': json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                }
                for row in rows
            ]
            
    async def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT d.id, d.filename, d.file_size, d.upload_date, d.metadata,
                       COUNT(c.id) as chunk_count
                FROM documents d
                LEFT JOIN chunks c ON d.id = c.document_id
                WHERE d.id = $1
                GROUP BY d.id, d.filename, d.file_size, d.upload_date, d.metadata
                """,
                document_id
            )
            if row:
                result = dict(row)
                result['metadata'] = json.loads(result['metadata']) if isinstance(result['metadata'], str) else result['metadata']
                return result
            return None
            
    async def delete_document(self, document_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM documents WHERE id = $1", document_id)

