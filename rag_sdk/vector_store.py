import asyncpg
from typing import List, Dict, Any, Optional
import numpy as np
import json
from .config import settings


class VectorStore:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        print("[VECTOR_STORE] VectorStore initialized")
        
    async def connect(self):
        print(f"[VECTOR_STORE] Connecting to PostgreSQL...")
        print(f"[VECTOR_STORE]   Host: {settings.postgres_host}:{settings.postgres_port}")
        print(f"[VECTOR_STORE]   Database: {settings.postgres_db}")
        print(f"[VECTOR_STORE]   User: {settings.postgres_user}")
        
        self.pool = await asyncpg.create_pool(
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            host=settings.postgres_host,
            port=settings.postgres_port,
            min_size=2,
            max_size=10
        )
        print(f"[VECTOR_STORE] Connection pool created (min_size=2, max_size=10)")
        
    async def close(self):
        if self.pool:
            print("[VECTOR_STORE] Closing connection pool...")
            await self.pool.close()
            print("[VECTOR_STORE] Connection pool closed")
            
    async def create_document(self, filename: str, file_size: int, metadata: Optional[Dict[str, Any]] = None) -> int:
        print(f"[VECTOR_STORE] Creating document: {filename} ({file_size} bytes)")
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO documents (filename, file_size, metadata)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                filename, file_size, json.dumps(metadata or {})
            )
            doc_id = row['id']
            print(f"[VECTOR_STORE] Document created: ID={doc_id}")
            return doc_id
            
    async def add_chunks(self, document_id: int, chunks: List[Dict[str, Any]]):
        print(f"[VECTOR_STORE] Adding {len(chunks)} chunks for document ID={document_id}")
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
                        json.dumps(chunk['embedding']),
                        chunk['chunk_index'],
                        json.dumps(chunk.get('metadata', {}))
                    )
                    for chunk in chunks
                ]
            )
            
    async def search_similar(self, query_embedding: List[float], document_id: Optional[int] = None, limit: int = 7) -> List[Dict[str, Any]]:
        print(f"[VECTOR_STORE] Searching similar chunks: doc_id={document_id}, limit={limit}")
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
            
            results = [dict(row) for row in rows]
            print(f"[VECTOR_STORE] Found {len(results)} similar chunks")
            if results:
                print(f"[VECTOR_STORE]   Best match: {results[0]['filename']} (similarity: {results[0]['similarity']:.2%})")
            return results
            
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
        print(f"[VECTOR_STORE] Deleting document ID={document_id}")
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM documents WHERE id = $1", document_id)
            print(f"[VECTOR_STORE] Document ID={document_id} deleted (including all chunks)")

