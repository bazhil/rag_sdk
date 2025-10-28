# Логирование в RAG SDK

## Обзор

В проекте реализовано детальное логирование всех ключевых операций для отладки и мониторинга работы системы.

## Структура логов

Все логи выводятся в stdout с префиксами для идентификации компонента:

- `[API]` - API endpoints (FastAPI)
- `[RAG_MANAGER]` - Главный менеджер RAG системы
- `[VECTOR_STORE]` - Работа с векторной БД (PostgreSQL + pgvector)
- `[EMBEDDINGS]` - Векторизация текста
- `[DOC_PROCESSOR]` - Обработка документов

## Компоненты с логированием

### 1. API Endpoints (`app/main.py`)

#### Загрузка файла
```
[API] ========== UPLOAD REQUEST ==========
[API] Filename: document.pdf
[API] Content-Type: application/pdf
[API] Saving to: uploads/document.pdf
[API] File saved: 1234567 bytes
[API] Upload successful: document_id=1
[API] ========================================
```

#### Чат-запрос
```
[API] ========== CHAT REQUEST ==========
[API] Query: Что такое машинное обучение?
[API] Document ID: None
[API] Context limit: 3
[API] Chat response generated successfully
[API] ======================================
```

#### Поиск
```
[API] ========== SEARCH REQUEST ==========
[API] Query: нейронные сети
[API] Document ID: 1
[API] Limit: 5
[API] Search successful: 5 results
[API] ========================================
```

#### Удаление
```
[API] ========== DELETE REQUEST ==========
[API] Document ID: 1
[API] Deleting document: document.pdf
[API] Physical file deleted: uploads/document.pdf
[API] Delete successful
[API] ========================================
```

### 2. RAG Manager (`RAG/rag_manager.py`)

#### Инициализация
```
[RAG_MANAGER] Initializing RAGManager components...
[RAG_MANAGER] RAGManager initialized
[RAG_MANAGER] Starting initialization...
[RAG_MANAGER] Vector store connected
[RAG_MANAGER] Embedding model loaded
[RAG_MANAGER] Initialization complete
```

#### Добавление документа
```
[RAG_MANAGER] ========== ADD DOCUMENT START ==========
[RAG_MANAGER] File: document.pdf
[RAG_MANAGER] Path: uploads/document.pdf
[RAG_MANAGER] Extracted text: 12345 characters
[RAG_MANAGER] Split into 15 chunks
[RAG_MANAGER] Generated 15 embeddings
[RAG_MANAGER] Created document record: ID=1
[RAG_MANAGER] Stored 15 chunks in database
[RAG_MANAGER] ========== ADD DOCUMENT COMPLETE: ID=1 ==========
```

#### Генерация ответа (полное логирование)
```
================================================================================
[RAG_MANAGER] ========== GENERATE ANSWER START ==========
[RAG_MANAGER] Query: Что такое машинное обучение?
[RAG_MANAGER] Document ID filter: None
[RAG_MANAGER] Context limit: 3
================================================================================
[RAG_MANAGER] Search query: 'Что такое машинное обучение?...' | doc_id: None | limit: 3
[RAG_MANAGER] Generated query embedding: 768 dimensions
[RAG_MANAGER] Search results: 6 total → 3 after filtering (min_similarity: 0.3)
[RAG_MANAGER]   Top 1: document.pdf (similarity: 85.23%)
[RAG_MANAGER]   Top 2: document.pdf (similarity: 78.45%)
[RAG_MANAGER]   Top 3: document.pdf (similarity: 72.10%)
[RAG_MANAGER] Found 3 relevant chunks:
[RAG_MANAGER]   Chunk 1: document.pdf (similarity: 85.23%, index: 5)
[RAG_MANAGER]   Chunk 2: document.pdf (similarity: 78.45%, index: 7)
[RAG_MANAGER]   Chunk 3: document.pdf (similarity: 72.10%, index: 12)
[RAG_MANAGER] Total context: 3456 chars, 567 words

[RAG_MANAGER] ================================================================================
[RAG_MANAGER] FULL CONTEXT SENT TO LLM:
[RAG_MANAGER] --------------------------------------------------------------------------------
[Источник 1 - document.pdf]:
Машинное обучение - это раздел искусственного интеллекта...
[текст контекста полностью]

[Источник 2 - document.pdf]:
В машинном обучении используются алгоритмы...
[текст контекста полностью]
[RAG_MANAGER] --------------------------------------------------------------------------------
[RAG_MANAGER] Prompt length: 4567 chars
[RAG_MANAGER] ================================================================================

[RAG_MANAGER] Loading LLM manager...
[RAG_MANAGER] LLM manager loaded: GigaChatManager
[RAG_MANAGER] Calling LLM: GigaChatManager

[RAG_MANAGER] ================================================================================
[RAG_MANAGER] FULL LLM RESPONSE:
[RAG_MANAGER] --------------------------------------------------------------------------------
Машинное обучение - это подраздел искусственного интеллекта...
[полный ответ LLM]
[RAG_MANAGER] --------------------------------------------------------------------------------
[RAG_MANAGER] Answer length: 1234 chars, 189 words
[RAG_MANAGER] ================================================================================
```

### 3. Vector Store (`RAG/vector_store.py`)

#### Подключение к БД
```
[VECTOR_STORE] VectorStore initialized
[VECTOR_STORE] Connecting to PostgreSQL...
[VECTOR_STORE]   Host: postgres:5432
[VECTOR_STORE]   Database: rag_db
[VECTOR_STORE]   User: rag_user
[VECTOR_STORE] Connection pool created (min_size=2, max_size=10)
```

#### Создание документа
```
[VECTOR_STORE] Creating document: document.pdf (1234567 bytes)
[VECTOR_STORE] Document created: ID=1
```

#### Добавление чанков
```
[VECTOR_STORE] Adding 15 chunks for document ID=1
```

#### Поиск похожих
```
[VECTOR_STORE] Searching similar chunks: doc_id=None, limit=3
[VECTOR_STORE] Found 3 similar chunks
[VECTOR_STORE]   Best match: document.pdf (similarity: 85.23%)
```

#### Удаление
```
[VECTOR_STORE] Deleting document ID=1
[VECTOR_STORE] Document ID=1 deleted (including all chunks)
```

### 4. Embeddings (`RAG/embeddings.py`)

#### Загрузка модели
```
[EMBEDDINGS] EmbeddingModel initialized: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
[EMBEDDINGS] Loading embedding model: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
[EMBEDDINGS] Model loaded successfully
```

#### Кодирование
```
[EMBEDDINGS] Encoding single text: 123 chars
[EMBEDDINGS] Generated embedding: 768 dimensions

[EMBEDDINGS] Batch encoding 15 texts (batch_size=32)
[EMBEDDINGS] Generated 15 embeddings
```

### 5. Document Processor (`RAG/document_processor.py`)

#### Извлечение текста
```
[DOC_PROCESSOR] Extracting text from: document.pdf (type: .pdf)
[DOC_PROCESSOR] PDF has 42 pages
[DOC_PROCESSOR] Extracted 12345 characters from PDF
```

#### Разбиение на чанки
```
[DOC_PROCESSOR] Splitting text: 12345 chars into chunks (size=1200, overlap=200)
[DOC_PROCESSOR] Created 15 chunks
```

#### Подготовка к хранению
```
[DOC_PROCESSOR] Preparing 15 chunks for storage
[DOC_PROCESSOR] Prepared 15 chunks
```

## Просмотр логов

### Docker Compose
```bash
# Все логи
docker compose logs -f

# Только логи приложения
docker compose logs -f app

# Последние 100 строк
docker compose logs --tail=100 app

# Поиск по логам
docker compose logs app | grep "\[RAG_MANAGER\]"
```

### Локальный запуск
Логи выводятся напрямую в консоль при запуске через `uvicorn`.

## Фильтрация логов по компоненту

```bash
# API запросы
docker logs rag_app 2>&1 | grep "\[API\]"

# Работа с RAG
docker logs rag_app 2>&1 | grep "\[RAG_MANAGER\]"

# База данных
docker logs rag_app 2>&1 | grep "\[VECTOR_STORE\]"

# Embeddings
docker logs rag_app 2>&1 | grep "\[EMBEDDINGS\]"

# Обработка документов
docker logs rag_app 2>&1 | grep "\[DOC_PROCESSOR\]"
```

## Отслеживание полного потока запроса

Для отслеживания полного потока обработки запроса смотрите логи с префиксами в порядке:

1. `[API]` - Входящий запрос
2. `[RAG_MANAGER]` - Обработка в RAG Manager
3. `[EMBEDDINGS]` - Векторизация запроса
4. `[VECTOR_STORE]` - Поиск в БД
5. `[RAG_MANAGER]` - Контекст и вызов LLM
6. `[RAG_MANAGER]` - Ответ LLM
7. `[API]` - Возврат ответа клиенту

## Настройка уровня детализации

Для изменения уровня детализации логов отредактируйте соответствующие `print()` вызовы в коде:

- Закомментируйте ненужные логи для уменьшения verbose
- Раскомментируйте для детальной отладки

## Полезные команды

### Сохранение логов в файл
```bash
docker compose logs app > rag_logs.txt
```

### Анализ производительности
```bash
# Время обработки запросов
docker logs rag_app 2>&1 | grep "Time:"

# Статистика по embeddings
docker logs rag_app 2>&1 | grep "\[EMBEDDINGS\].*Generated"
```

### Отладка ошибок
```bash
# Все ошибки
docker logs rag_app 2>&1 | grep "ERROR"

# Traceback
docker logs rag_app 2>&1 | grep -A 10 "Traceback"
```

## Примеры типичных сценариев

### Отладка проблемы с загрузкой файла
```bash
docker logs rag_app 2>&1 | grep -E "\[API\].*UPLOAD|\[RAG_MANAGER\].*ADD DOCUMENT|\[DOC_PROCESSOR\]"
```

### Отладка качества ответов
```bash
docker logs rag_app 2>&1 | grep -E "FULL CONTEXT|FULL LLM RESPONSE"
```

### Мониторинг производительности БД
```bash
docker logs rag_app 2>&1 | grep "\[VECTOR_STORE\]"
```

## Интеграция с системами мониторинга

Логи выводятся в stdout и могут быть интегрированы с:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **CloudWatch** (AWS)
- **Azure Monitor**
- **Google Cloud Logging**

Пример конфигурации для Fluentd/Filebeat - собирать логи из Docker containers.

## Рекомендации

1. **Prod окружение**: Рассмотрите использование structured logging (JSON формат)
2. **Ротация логов**: Настройте в Docker Compose limits для логов
3. **Безопасность**: Не логируйте API ключи и sensitive данные
4. **Производительность**: Избыточное логирование может замедлить систему

## Дополнительная документация

- [Быстрый старт](QUICKSTART.md)
- [Архитектура](ARCHITECTURE.md)
- [Использование](USAGE.md)

