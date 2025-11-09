import sys
import os
import re
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'llm_manager'))

from .vector_store import VectorStore
from .embeddings import EmbeddingModel
from .document_processor import DocumentProcessor
from .config import settings
from .language_detector import get_language_detector
from .pdf_generator import get_pdf_generator


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
    
    async def create_referat(self, document_id: int, output_dir: str = "referats") -> Dict[str, Any]:
        """
        Создает реферативный перевод документа.
        Реферативный перевод - это подробный анализ документа с сохранением
        всех ключевых положений, но значительно сокращенный по объему.
        
        Args:
            document_id: ID документа
            output_dir: директория для сохранения PDF
            
        Returns:
            Dict с полями: referat, document_id, filename, chunk_count, pdf_url, pdf_path
        """
        print(f"\n{'='*80}")
        print(f"[RAG_MANAGER] ========== CREATE REFERAT START ==========")
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
                'referat': 'Документ не содержит текстовых данных для создания реферата.',
                'document_id': document_id,
                'filename': document['filename'],
                'chunk_count': 0,
                'pdf_url': '',
                'pdf_path': ''
            }
        
        # Сортируем чанки по порядку
        sorted_chunks = sorted(chunks, key=lambda x: x.get('chunk_index', 0))
        
        # Разбиваем документ на части для обработки
        # Каждая часть ~10000 символов для качественного анализа
        chunk_size_for_referat = 10000
        parts = []
        current_part = []
        current_length = 0
        
        for chunk in sorted_chunks:
            chunk_text = chunk['content']
            chunk_len = len(chunk_text)
            
            if current_length + chunk_len > chunk_size_for_referat and current_part:
                # Сохраняем текущую часть и начинаем новую
                parts.append('\n\n'.join(current_part))
                current_part = [chunk_text]
                current_length = chunk_len
            else:
                current_part.append(chunk_text)
                current_length += chunk_len
        
        # Добавляем последнюю часть
        if current_part:
            parts.append('\n\n'.join(current_part))
        
        print(f"[RAG_MANAGER] Document split into {len(parts)} parts for analysis")
        
        # Обрабатываем каждую часть
        llm = self._get_llm()
        referat_parts = []
        
        for i, part in enumerate(parts, 1):
            print(f"[RAG_MANAGER] Processing part {i}/{len(parts)}")
            
            # Создаем промпт для реферативного перевода части
            if len(parts) == 1:
                part_info = "весь документ"
            else:
                part_info = f"часть {i} из {len(parts)}"
            
            # Вычисляем целевой размер реферата (35% от оригинала)
            part_word_count = len(part.split())
            target_word_count = int(part_word_count * 0.35)
            min_word_count = int(part_word_count * 0.30)
            max_word_count = int(part_word_count * 0.45)
            
            prompt = f"""Создай ПОДРОБНЫЙ РЕФЕРАТИВНЫЙ ПЕРЕВОД следующей части документа ({part_info}).

⚠️ СТРОГИЕ ТРЕБОВАНИЯ К ОБЪЕМУ (ОБЯЗАТЕЛЬНО ВЫПОЛНИ):
📊 Исходный текст: ~{part_word_count} слов
📊 ЦЕЛЕВОЙ размер реферата: {target_word_count} слов (минимум {min_word_count}, максимум {max_word_count})
📊 Это примерно 35% от объема оригинала

❗ КРИТИЧЕСКИ ВАЖНО:
- Твой реферат ДОЛЖЕН содержать минимум {min_word_count} слов
- Если получится меньше - это ОШИБКА, нужно добавить больше деталей
- Реферативный перевод - это ДЕТАЛЬНОЕ изложение, НЕ краткая выжимка
- Лучше написать больше ({max_word_count} слов), чем упустить важную информацию

СТРАТЕГИЯ НАПИСАНИЯ ПОДРОБНОГО РЕФЕРАТА:
1. **Каждую концепцию раскрывай в 2-4 предложениях**, а не в одном
2. **Добавляй пояснения к терминам** - что они означают в контексте
3. **Включай все примеры и данные** из текста - цифры, факты, случаи
4. **Описывай механизмы и процессы** пошагово, не общими фразами
5. **Сохраняй аргументацию** - если в тексте есть обоснования, включи их
6. **Детализируй списки** - к каждому пункту добавляй описание
7. **Цитируй ключевые определения** и положения

СТРУКТУРА РЕФЕРАТА:
- Заголовки и подзаголовки (## и ###)
- Вводные абзацы перед каждым разделом
- Развернутые параграфы (3-5 предложений каждый)
- Детальные нумерованные и маркированные списки с пояснениями
- Примеры и данные с контекстом
- Промежуточные выводы по подразделам
- Заключение по разделу

СТИЛЬ:
- Академический, профессиональный язык
- Точность - только информация из текста
- Полнота - не пропускай важные детали
- Выделяй термины жирным (**термин**)

ИСХОДНЫЙ ТЕКСТ ({part_info}):
{part}

СОЗДАЙ ПОДРОБНЫЙ РЕФЕРАТИВНЫЙ ПЕРЕВОД (минимум {min_word_count} слов):"""
            
            part_referat = await llm.get_response("", prompt)
            referat_parts.append(part_referat)
            
            # Логирование с проверкой объема
            referat_words = len(part_referat.split())
            compression_ratio = (referat_words / part_word_count * 100) if part_word_count > 0 else 0
            print(f"[RAG_MANAGER] Part {i} processed:")
            print(f"  - Input: {part_word_count} words, {len(part)} chars")
            print(f"  - Output: {referat_words} words, {len(part_referat)} chars")
            print(f"  - Compression: {compression_ratio:.1f}% (target: 30-45%)")
            
            if referat_words < min_word_count:
                print(f"  ⚠️  WARNING: Output is below minimum ({referat_words} < {min_word_count})")
        
        # Если частей больше одной, создаем общую структуру
        if len(referat_parts) > 1:
            print(f"[RAG_MANAGER] Starting hierarchical merging of {len(referat_parts)} parts")
            
            # Иерархическое объединение: объединяем части группами по 8
            # Это позволяет обработать большие документы не упираясь в лимит контекста
            def chunk_list(lst, n):
                """Разбивает список на группы по n элементов"""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]
            
            current_parts = referat_parts
            level = 1
            
            # Объединяем пока не останется одна часть
            while len(current_parts) > 1:
                print(f"[RAG_MANAGER] Merging level {level}: {len(current_parts)} parts")
                next_parts = []
                
                # Разбиваем на группы по 8 частей
                groups = list(chunk_list(current_parts, 8))
                
                for i, group in enumerate(groups, 1):
                    if len(group) == 1:
                        # Если в группе одна часть, просто добавляем её
                        next_parts.append(group[0])
                        continue
                    
                    print(f"[RAG_MANAGER]   Merging group {i}/{len(groups)} ({len(group)} parts)")
                    
                    # Объединяем части группы
                    combined_group = '\n\n---\n\n'.join(group)
                    
                    # Подсчитываем общее количество слов в частях
                    total_words = sum(len(part.split()) for part in group)
                    min_expected_words = int(total_words * 0.85)  # Минимум 85% от суммы частей
                    
                    merge_prompt = f"""У тебя есть {len(group)} частей реферативного перевода документа.
Твоя задача - объединить их в ЕДИНЫЙ СВЯЗНЫЙ текст БЕЗ СОКРАЩЕНИЯ содержания.

⚠️ СТРОГИЕ ТРЕБОВАНИЯ К ОБЪЕМУ:
📊 Суммарный объем частей: ~{total_words} слов
📊 МИНИМАЛЬНЫЙ объем результата: {min_expected_words} слов (не меньше!)
📊 Ты должен СОХРАНИТЬ практически весь объем (85%+)

❗ КРИТИЧЕСКИ ВАЖНО - ЧТО ДЕЛАТЬ:
✅ СОХРАНИ весь текст из всех частей
✅ Просто убери повторы между частями (если есть)
✅ Добавь связки между разделами для плавности
✅ Объедини в логичную структуру с заголовками
✅ Сохрани ВСЕ примеры, данные, термины, детали

❌ НЕ ДЕЛАЙ:
❌ НЕ сокращай описания
❌ НЕ убирай детали
❌ НЕ объединяй разные концепции в одну
❌ НЕ превращай списки в краткие формулировки
❌ НЕ удаляй примеры или данные

ТЕХНИКА ОБЪЕДИНЕНИЯ:
1. Возьми текст из первой части КАК ЕСТЬ
2. Добавь переходную фразу (1-2 предложения)
3. Добавь текст из второй части КАК ЕСТЬ
4. Повтори для всех частей
5. Убери только явные дублирования (одинаковые предложения)
6. Проверь структуру заголовков

ЧАСТИ ДЛЯ ОБЪЕДИНЕНИЯ:
{combined_group}

ОБЪЕДИНИ В СВЯЗНЫЙ ТЕКСТ (минимум {min_expected_words} слов, сохрани все детали):"""
                    
                    merged = await llm.get_response("", merge_prompt)
                    next_parts.append(merged)
                    
                    # Логирование объединения
                    merged_words = len(merged.split())
                    retention_ratio = (merged_words / total_words * 100) if total_words > 0 else 0
                    print(f"[RAG_MANAGER]   Group {i} merged:")
                    print(f"    - Input: {total_words} words (from {len(group)} parts)")
                    print(f"    - Output: {merged_words} words")
                    print(f"    - Retention: {retention_ratio:.1f}% (target: 85%+)")
                    
                    if merged_words < min_expected_words:
                        print(f"    ⚠️  WARNING: Merged output is too short ({merged_words} < {min_expected_words})")
                
                current_parts = next_parts
                level += 1
            
            # Финальная часть - добавляем введение и заключение
            base_referat = current_parts[0]
            
            # Подсчитываем слова в базовом реферате
            base_words = len(base_referat.split())
            min_final_words = base_words + 100  # Минимум: базовый текст + введение + заключение
            
            final_prompt = f"""У тебя есть ПОЛНЫЙ реферативный перевод документа.
Твоя задача - добавить ВВЕДЕНИЕ в начало и ЗАКЛЮЧЕНИЕ в конец.

⚠️ СТРОГОЕ ТРЕБОВАНИЕ К ОБЪЕМУ:
📊 Размер реферата: {base_words} слов
📊 МИНИМАЛЬНЫЙ размер итогового текста: {min_final_words} слов
📊 Весь текст реферата должен остаться БЕЗ ИЗМЕНЕНИЙ!

❗ КРИТИЧЕСКИ ВАЖНО:
❌ НЕ сокращай основной текст реферата!
❌ НЕ изменяй формулировки в реферате!
❌ НЕ удаляй примеры, данные или детали!
❌ НЕ переписывай существующий текст!
✅ ТОЛЬКО добавь введение и заключение

ЧТО ДОБАВИТЬ:
1. **Введение** (2-3 абзаца, ~150-200 слов):
   - О чем документ и его значимость
   - Основные темы, которые будут раскрыты
   - Структура реферата
   
2. **Заключение** (2-3 абзаца, ~150-200 слов):
   - Основные выводы из документа
   - Практическое значение
   - Итоговая оценка

РЕФЕРАТ (сохрани его ПОЛНОСТЬЮ):
{base_referat}

ДОБАВЬ ВВЕДЕНИЕ И ЗАКЛЮЧЕНИЕ (итого минимум {min_final_words} слов):"""
            
            print(f"[RAG_MANAGER] Adding introduction and conclusion")
            final_referat = await llm.get_response("", final_prompt)
            
            # Логирование финального этапа
            final_words = len(final_referat.split())
            print(f"[RAG_MANAGER] Final referat with intro/conclusion:")
            print(f"  - Base: {base_words} words")
            print(f"  - Final: {final_words} words")
            print(f"  - Added: {final_words - base_words} words")
            
            if final_words < min_final_words:
                print(f"  ⚠️  WARNING: Final output is too short ({final_words} < {min_final_words})")
        else:
            final_referat = referat_parts[0]
            final_words = len(final_referat.split())
            print(f"[RAG_MANAGER] Single-part referat (no merging needed)")
        
        # Итоговая статистика
        total_chars = sum(len(chunk['content']) for chunk in chunks)
        total_input_words = sum(len(chunk['content'].split()) for chunk in chunks)
        final_compression = (final_words / total_input_words * 100) if total_input_words > 0 else 0
        
        print(f"\n[RAG_MANAGER] ========== REFERAT STATISTICS ==========")
        print(f"Original document:")
        print(f"  - Total chars: {total_chars}")
        print(f"  - Total words: {total_input_words}")
        print(f"  - Chunks: {len(chunks)}")
        print(f"Referat:")
        print(f"  - Total chars: {len(final_referat)}")
        print(f"  - Total words: {final_words}")
        print(f"  - Compression ratio: {final_compression:.1f}% (target: 30-40%)")
        print(f"==========================================")
        
        # Генерируем PDF
        pdf_generator = get_pdf_generator()
        
        # Создаем URL-безопасное имя файла для PDF
        base_filename = os.path.splitext(document['filename'])[0]
        # Убираем пробелы и специальные символы, заменяем на подчеркивания
        safe_filename = re.sub(r'[^\w\-.]', '_', base_filename)
        # Убираем множественные подчеркивания
        safe_filename = re.sub(r'_+', '_', safe_filename)
        # Убираем подчеркивания в начале и конце
        safe_filename = safe_filename.strip('_')
        pdf_filename = f"{safe_filename}_referat.pdf"
        
        # Генерируем PDF
        pdf_path = pdf_generator.generate_referat_pdf(
            referat_text=final_referat,
            filename=pdf_filename,
            output_path=output_dir,
            original_filename=document['filename'],
            chunk_count=len(chunks),
            metadata=document.get('metadata', {})
        )
        
        # Формируем URL для скачивания
        pdf_url = f"/referats/{pdf_filename}"
        
        print(f"[RAG_MANAGER] PDF generated: {pdf_path}")
        print(f"[RAG_MANAGER] PDF URL: {pdf_url}")
        print(f"[RAG_MANAGER] ========== CREATE REFERAT COMPLETE ==========\n")
        
        return {
            'referat': final_referat,
            'document_id': document_id,
            'filename': document['filename'],
            'chunk_count': len(chunks),
            'pdf_url': pdf_url,
            'pdf_path': pdf_path
        }

