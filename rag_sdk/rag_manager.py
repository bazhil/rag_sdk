import sys
import os
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'llm_manager'))

from .vector_store import VectorStore
from .embeddings import EmbeddingModel
from .document_processor import DocumentProcessor


class RAGManager:
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_model = EmbeddingModel()
        self.document_processor = DocumentProcessor()
        self._llm = None
        
    async def initialize(self):
        await self.vector_store.connect()
        self.embedding_model.load()
        
    async def close(self):
        await self.vector_store.close()
        
    def _get_llm(self):
        if self._llm is None:
            from llm_factory import get_llm_manager
            self._llm = get_llm_manager()
        return self._llm
        
    async def add_document(self, file_path: str, filename: str) -> int:
        text = await self.document_processor.extract_text_from_file(file_path, filename)
        
        chunks = self.document_processor.split_text_into_chunks(text)
        
        embeddings = self.embedding_model.encode_batch(chunks)
        
        file_size = os.path.getsize(file_path)
        document_id = await self.vector_store.create_document(
            filename=filename,
            file_size=file_size,
            metadata={'chunks_count': len(chunks)}
        )
        
        prepared_chunks = self.document_processor.prepare_chunks_for_storage(chunks, embeddings)
        await self.vector_store.add_chunks(document_id, prepared_chunks)
        
        return document_id
        
    async def search(self, query: str, document_id: Optional[int] = None, limit: int = 5, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.encode(query)
        
        results = await self.vector_store.search_similar(
            query_embedding=query_embedding,
            document_id=document_id,
            limit=limit * 2  # Получаем больше результатов для фильтрации
        )
        
        # Фильтруем по минимальной релевантности
        filtered_results = [
            result for result in results 
            if result.get('similarity', 0) >= min_similarity
        ]
        
        print(f"RAG_MANAGER - Search: found {len(results)} results, filtered to {len(filtered_results)} (min_similarity: {min_similarity})")
        
        # Возвращаем топ результатов после фильтрации
        return filtered_results[:limit]
        
    async def generate_answer(self, query: str, document_id: Optional[int] = None, context_limit: int = 3) -> Dict[str, Any]:
        search_results = await self.search(query, document_id, limit=context_limit)
        
        if not search_results:
            return {
                'answer': 'Не найдено релевантной информации в документах.',
                'sources': [],
                'context': []
            }
        
        print(f"\n{'='*60}")
        print(f"RAG_MANAGER - generate_answer")
        print(f"Query: {query}")
        print(f"Document ID: {document_id}")
        print(f"Found {len(search_results)} relevant chunks")
        print(f"Chunks: {search_results}")
        print(f"{'='*60}\n")
        
        context_parts = []
        for idx, result in enumerate(search_results, 1):
            similarity = result.get('similarity', 0)
            print(f"Chunk {idx}: {result['filename']} (similarity: {similarity:.2%})")
            context_parts.append(f"[Источник {idx} - {result['filename']}]:\n{result['content']}")
        
        context = '\n\n'.join(context_parts)
        
        prompt = f"""На основе следующего контекста ответь на вопрос пользователя.

ТРЕБОВАНИЯ К ОТВЕТУ:
1. Структурируй ответ с использованием заголовков и подзаголовков
2. Используй нумерованные списки для перечислений
3. Выделяй ключевые термины жирным шрифтом (**термин**)
4. Начинай с краткого резюме в 1-2 предложениях
5. Группируй связанную информацию в логические разделы
6. Если информации недостаточно, четко укажи что известно и чего не хватает
7. Используй только информацию из контекста, не добавляй ничего от себя

КОНТЕКСТ:
{context}

ВОПРОС: {query}

ОТВЕТ:"""
        
        print(f"\n{'='*60}")
        print(f"RAG_MANAGER - Prompt length: {len(prompt)} characters")
        print(f"Context length: {len(context)} characters")
        print(f"Context preview (first 500 chars):\n{context[:500]}...")
        print(f"{'='*60}\n")
        
        llm = self._get_llm()
        print(f"RAG_MANAGER - Calling LLM ({llm.__class__.__name__})...")
        answer = await llm.get_response("", prompt)
        
        print(f"\n{'='*60}")
        print(f"RAG_MANAGER - LLM Response received")
        print(f"Answer length: {len(answer)} characters")
        print(f"Answer preview: {answer[:200]}...")
        print(f"{'='*60}\n")
        
        sources = [
            {
                'filename': result['filename'],
                'document_id': result['document_id'],
                'chunk_index': result['chunk_index'],
                'similarity': float(result['similarity'])
            }
            for result in search_results
        ]
        
        return {
            'answer': answer,
            'sources': sources,
            'context': [result['content'] for result in search_results]
        }
        
    async def get_documents(self) -> List[Dict[str, Any]]:
        return await self.vector_store.get_documents()
        
    async def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        return await self.vector_store.get_document(document_id)
        
    async def delete_document(self, document_id: int):
        await self.vector_store.delete_document(document_id)

