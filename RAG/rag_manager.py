import sys
import os
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'llm_manager'))

from .vector_store import VectorStore
from .embeddings import EmbeddingModel
from .document_processor import DocumentProcessor
from .config import settings
from .language_detector import get_language_detector


class RAGManager:
    
    def __init__(self):
        print("[RAG_MANAGER] Initializing RAGManager components...")
        self.vector_store = VectorStore()
        self.embedding_model = EmbeddingModel()
        self.document_processor = DocumentProcessor()
        self.language_detector = get_language_detector()
        self._llm = None
        print("[RAG_MANAGER] RAGManager initialized with auto language detection")
        
    async def initialize(self):
        print("[RAG_MANAGER] Starting initialization...")
        await self.vector_store.connect()
        print("[RAG_MANAGER] Vector store connected")
        self.embedding_model.load()
        print("[RAG_MANAGER] Embedding model loaded")
        print("[RAG_MANAGER] Initialization complete")
        
    async def close(self):
        print("[RAG_MANAGER] Closing connections...")
        await self.vector_store.close()
        print("[RAG_MANAGER] Closed successfully")
        
    def _get_llm(self):
        if self._llm is None:
            print("[RAG_MANAGER] Loading LLM manager...")
            from llm_factory import get_llm_manager
            self._llm = get_llm_manager()
            print(f"[RAG_MANAGER] LLM manager loaded: {self._llm.__class__.__name__}")
        return self._llm
        
    async def add_document(self, file_path: str, filename: str) -> int:
        print(f"\n[RAG_MANAGER] ========== ADD DOCUMENT START ==========")
        print(f"[RAG_MANAGER] File: {filename}")
        print(f"[RAG_MANAGER] Path: {file_path}")
        
        text = await self.document_processor.extract_text_from_file(file_path, filename)
        print(f"[RAG_MANAGER] Extracted text: {len(text)} characters")
        
        chunks = self.document_processor.split_text_into_chunks(text)
        print(f"[RAG_MANAGER] Split into {len(chunks)} chunks")
        
        # Автоматическое определение языка документа
        document_lang = self.language_detector.detect_document_language(chunks)
        print(f"[RAG_MANAGER] Auto-detected document language: {document_lang or 'unknown'}")
        
        embeddings = self.embedding_model.encode_batch(chunks)
        print(f"[RAG_MANAGER] Generated {len(embeddings)} embeddings")
        
        file_size = os.path.getsize(file_path)
        document_id = await self.vector_store.create_document(
            filename=filename,
            file_size=file_size,
            metadata={
                'chunks_count': len(chunks),
                'language': document_lang  # Сохраняем язык в метаданных
            }
        )
        print(f"[RAG_MANAGER] Created document record: ID={document_id}")
        
        prepared_chunks = self.document_processor.prepare_chunks_for_storage(chunks, embeddings)
        await self.vector_store.add_chunks(document_id, prepared_chunks)
        print(f"[RAG_MANAGER] Stored {len(prepared_chunks)} chunks in database")
        print(f"[RAG_MANAGER] ========== ADD DOCUMENT COMPLETE: ID={document_id} ==========\n")
        
        return document_id
        
    async def search(self, query: str, document_id: Optional[int] = None, limit: Optional[int] = None, min_similarity: Optional[float] = None) -> List[Dict[str, Any]]:
        limit = limit if limit is not None else settings.search_limit
        min_similarity = min_similarity if min_similarity is not None else settings.min_similarity
        print(f"[RAG_MANAGER] Search query: '{query[:100]}...' | doc_id: {document_id} | limit: {limit}")
        
        # Автоматическое определение языка запроса
        query_lang = self.language_detector.detect_language(query)
        print(f"[RAG_MANAGER] Auto-detected query language: {query_lang or 'unknown'}")
        
        # Получаем язык документа(ов) если задан конкретный документ
        document_lang = None
        if document_id:
            doc = await self.vector_store.get_document(document_id)
            if doc and doc.get('metadata'):
                document_lang = doc['metadata'].get('language')
                print(f"[RAG_MANAGER] Document language: {document_lang or 'unknown'}")
        
        # Определяем, нужен ли перевод для улучшения поиска
        queries_to_search = [query]  # Всегда ищем по оригинальному запросу
        
        if query_lang and document_lang and query_lang != document_lang:
            # Кросс-языковой запрос обнаружен - пробуем перевести
            print(f"[RAG_MANAGER] Cross-lingual search detected ({query_lang} -> {document_lang})")
            translated_query = self.language_detector.translate_text(query, document_lang)
            
            if translated_query and translated_query != query:
                queries_to_search.append(translated_query)
                print(f"[RAG_MANAGER] Will search with {len(queries_to_search)} query variants")
        
        # Выполняем поиск по всем вариантам запроса
        all_results = []
        seen_chunks = set()  # Для дедупликации
        
        for i, search_query in enumerate(queries_to_search):
            print(f"[RAG_MANAGER] Searching with query variant {i+1}/{len(queries_to_search)}")
            
            query_embedding = self.embedding_model.encode(search_query)
            print(f"[RAG_MANAGER] Generated query embedding: {len(query_embedding)} dimensions")
            
            results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                document_id=document_id,
                limit=limit * 2
            )
            
            # Добавляем результаты, избегая дубликатов
            for result in results:
                chunk_id = result.get('id')
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    all_results.append(result)
        
        # Сортируем все результаты по similarity
        all_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Фильтруем по минимальной similarity
        filtered_results = [
            result for result in all_results 
            if result.get('similarity', 0) >= min_similarity
        ]
        
        print(f"[RAG_MANAGER] Search results: {len(all_results)} total → {len(filtered_results)} after filtering (min_similarity: {min_similarity})")
        for i, result in enumerate(filtered_results[:limit], 1):
            print(f"[RAG_MANAGER]   Top {i}: {result['filename']} (similarity: {result['similarity']:.2%})")
        
        return filtered_results[:limit]
        
    async def generate_answer(self, query: str, document_id: Optional[int] = None, context_limit: Optional[int] = None) -> Dict[str, Any]:
        context_limit = context_limit if context_limit is not None else settings.search_limit
        print(f"\n{'='*80}")
        print(f"[RAG_MANAGER] ========== GENERATE ANSWER START ==========")
        print(f"[RAG_MANAGER] Query: {query}")
        print(f"[RAG_MANAGER] Document ID filter: {document_id}")
        print(f"[RAG_MANAGER] Context limit: {context_limit}")
        print(f"{'='*80}")
        
        search_results = await self.search(query, document_id, limit=context_limit)
        
        if not search_results:
            print(f"[RAG_MANAGER] WARNING: No relevant documents found")
            return {
                'answer': 'Не найдено релевантной информации в документах.',
                'sources': [],
                'context': []
            }
        
        print(f"[RAG_MANAGER] Found {len(search_results)} relevant chunks:")
        context_parts = []
        for idx, result in enumerate(search_results, 1):
            similarity = result.get('similarity', 0)
            print(f"[RAG_MANAGER]   Chunk {idx}: {result['filename']} (similarity: {similarity:.2%}, index: {result['chunk_index']})")
            context_parts.append(f"[Источник {idx} - {result['filename']}]:\n{result['content']}")
        
        context = '\n\n'.join(context_parts)
        print(f"[RAG_MANAGER] Total context: {len(context)} chars, {len(context.split())} words")
        
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
        
        print(f"\n[RAG_MANAGER] {'='*80}")
        print(f"[RAG_MANAGER] FULL CONTEXT SENT TO LLM:")
        print(f"[RAG_MANAGER] {'-'*80}")
        print(context)
        print(f"[RAG_MANAGER] {'-'*80}")
        print(f"[RAG_MANAGER] Prompt length: {len(prompt)} chars")
        print(f"[RAG_MANAGER] {'='*80}\n")
        
        llm = self._get_llm()
        print(f"[RAG_MANAGER] Calling LLM: {llm.__class__.__name__}")
        answer = await llm.get_response("", prompt)
        
        print(f"\n[RAG_MANAGER] {'='*80}")
        print(f"[RAG_MANAGER] FULL LLM RESPONSE:")
        print(f"[RAG_MANAGER] {'-'*80}")
        print(answer)
        print(f"[RAG_MANAGER] {'-'*80}")
        print(f"[RAG_MANAGER] Answer length: {len(answer)} chars, {len(answer.split())} words")
        print(f"[RAG_MANAGER] {'='*80}\n")
        
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
    
    async def summarize_document(self, document_id: int) -> Dict[str, Any]:
        """
        Генерирует краткое содержание (суммаризацию) указанного документа.
        
        Args:
            document_id: ID документа для суммаризации
            
        Returns:
            Dict с полями: summary, document_id, filename, chunk_count
        """
        print(f"\n{'='*80}")
        print(f"[RAG_MANAGER] ========== SUMMARIZE DOCUMENT START ==========")
        print(f"[RAG_MANAGER] Document ID: {document_id}")
        print(f"{'='*80}")
        
        # Получаем информацию о документе
        document = await self.vector_store.get_document(document_id)
        if not document:
            raise ValueError(f"Документ с ID {document_id} не найден")
        
        print(f"[RAG_MANAGER] Document: {document['filename']}")
        print(f"[RAG_MANAGER] Chunk count: {document['chunk_count']}")
        
        # Получаем все чанки документа
        chunks = await self.vector_store.get_document_chunks(document_id)
        print(f"[RAG_MANAGER] Retrieved {len(chunks)} chunks")
        
        if not chunks:
            return {
                'summary': 'Документ не содержит текстовых данных для суммаризации.',
                'document_id': document_id,
                'filename': document['filename'],
                'chunk_count': 0
            }
        
        # Объединяем чанки в текст (сортируем по chunk_index)
        sorted_chunks = sorted(chunks, key=lambda x: x.get('chunk_index', 0))
        full_text = '\n\n'.join([chunk['content'] for chunk in sorted_chunks])
        
        print(f"[RAG_MANAGER] Full text length: {len(full_text)} chars, {len(full_text.split())} words")
        
        # Если текст слишком большой, берем первые N символов для суммаризации
        max_chars = 15000  # Ограничение для LLM
        if len(full_text) > max_chars:
            print(f"[RAG_MANAGER] Text too long, truncating to {max_chars} chars")
            text_for_summary = full_text[:max_chars] + "\n\n[... текст обрезан ...]"
        else:
            text_for_summary = full_text
        
        # Создаем промпт для суммаризации
        prompt = f"""Создай краткое содержание (суммаризацию) следующего документа.

ТРЕБОВАНИЯ К СУММАРИЗАЦИИ:
1. Начни с общего описания в 2-3 предложениях
2. Выдели основные темы и разделы документа
3. Используй маркированные списки для перечисления ключевых пунктов
4. Выдели важные термины и понятия жирным шрифтом (**термин**)
5. Структурируй информацию с использованием заголовков
6. Сохрани последовательность изложения как в оригинале
7. Укажи ключевые выводы или заключения, если они есть
8. Не добавляй информацию, которой нет в тексте

ДОКУМЕНТ: {document['filename']}

ТЕКСТ ДОКУМЕНТА:
{text_for_summary}

КРАТКОЕ СОДЕРЖАНИЕ:"""
        
        print(f"[RAG_MANAGER] Prompt length: {len(prompt)} chars")
        
        # Получаем ответ от LLM
        llm = self._get_llm()
        print(f"[RAG_MANAGER] Calling LLM: {llm.__class__.__name__}")
        summary = await llm.get_response("", prompt)
        
        print(f"\n[RAG_MANAGER] {'='*80}")
        print(f"[RAG_MANAGER] SUMMARY GENERATED:")
        print(f"[RAG_MANAGER] {'-'*80}")
        print(summary)
        print(f"[RAG_MANAGER] {'-'*80}")
        print(f"[RAG_MANAGER] Summary length: {len(summary)} chars, {len(summary.split())} words")
        print(f"[RAG_MANAGER] {'='*80}\n")
        
        print(f"[RAG_MANAGER] ========== SUMMARIZE DOCUMENT COMPLETE ==========\n")
        
        return {
            'summary': summary,
            'document_id': document_id,
            'filename': document['filename'],
            'chunk_count': len(chunks)
        }

