# Архитектура RAG SDK

## Обзор

RAG SDK - это модульная система для создания приложений Retrieval-Augmented Generation с использованием векторного поиска в PostgreSQL.

## Компоненты системы

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Interface                          │
│                    (HTML/CSS/JavaScript)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                          │
│                     (app/main.py)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     RAG Manager                             │
│                (RAG/rag_manager.py)                         │
│  ┌──────────────┬──────────────┬──────────────────────┐     │
│  │              │              │                       │    │
│  ▼              ▼              ▼                       ▼    │
│  Document    Embeddings    Vector Store         LLM Manager │
│  Processor     Model         (PostgreSQL)         (submod)  │
└─────────────────────────────────────────────────────────────┘
```

## Архитектурные слои

### 1. Presentation Layer (Слой представления)

**Компоненты:**
- `app/static/index.html` - веб-интерфейс
- `app/static/style.css` - стили
- `app/static/script.js` - логика клиента

**Ответственность:**
- Отображение документов
- Интерфейс чата
- Загрузка файлов
- Взаимодействие с API

### 2. API Layer (Слой API)

**Компоненты:**
- `app/main.py` - FastAPI приложение
- `app/models.py` - Pydantic модели

**Endpoints:**
- `/api/upload` - загрузка документов
- `/api/documents` - управление документами
- `/api/chat` - вопросы-ответы
- `/api/search` - векторный поиск

**Ответственность:**
- Валидация запросов
- Обработка ошибок
- Маршрутизация
- Статика и CORS

### 3. Business Logic Layer (Бизнес-логика)

**Компонент:** `RAG/`

#### RAGManager (`rag_manager.py`)

Главный оркестратор системы.

**Методы:**
- `add_document()` - добавление документа
- `search()` - векторный поиск
- `generate_answer()` - генерация ответа
- `get_documents()` - список документов
- `delete_document()` - удаление документа

**Ответственность:**
- Координация компонентов
- Управление жизненным циклом
- Бизнес-логика RAG

#### DocumentProcessor (`document_processor.py`)

Обработка документов различных форматов.

**Методы:**
- `extract_text_from_file()` - извлечение текста
- `split_text_into_chunks()` - разбиение на фрагменты
- `prepare_chunks_for_storage()` - подготовка к сохранению

**Поддержка форматов:**
- PDF (pypdf)
- DOCX (python-docx)
- XLSX (openpyxl)
- Markdown (markdown + BeautifulSoup)
- HTML (BeautifulSoup)
- Text (с автоопределением кодировки)

#### EmbeddingModel (`embeddings.py`)

Векторизация текста.

**Методы:**
- `load()` - загрузка модели
- `encode()` - кодирование одного текста
- `encode_batch()` - пакетное кодирование

**Технология:**
- sentence-transformers
- Модели: all-MiniLM-L6-v2 (384 dim)

#### VectorStore (`vector_store.py`)

Работа с векторной БД.

**Методы:**
- `create_document()` - создание записи документа
- `add_chunks()` - добавление фрагментов
- `search_similar()` - векторный поиск
- `get_documents()` - получение списка
- `delete_document()` - удаление

**Технология:**
- asyncpg (асинхронный драйвер)
- PostgreSQL + pgvector
- Косинусная близость

### 4. Integration Layer (Слой интеграции)

**Компонент:** `llm_manager/` (git submodule)

Интеграция с различными LLM провайдерами:
- OpenAI (GPT-3.5, GPT-4)
- Ollama (локальные модели)
- DeepSeek
- Yandex GPT
- GigaChat

**Паттерн:** Factory + Strategy

### 5. Data Layer (Слой данных)

**Компоненты:**
- PostgreSQL 16 с расширением pgvector
- Файловая система (uploads/)

**Схема БД:**

```sql
documents
├── id (PRIMARY KEY)
├── filename
├── file_size
├── upload_date
└── metadata (JSONB)

chunks
├── id (PRIMARY KEY)
├── document_id (FOREIGN KEY → documents.id)
├── content (TEXT)
├── embedding (VECTOR(384))
├── chunk_index
└── metadata (JSONB)

Индексы:
- chunks_embedding_idx (IVFFlat для векторного поиска)
- chunks_document_id_idx (для связи с документами)
```

## Поток данных

### Загрузка документа

```
1. User → Upload File
   ↓
2. FastAPI → Save to uploads/
   ↓
3. DocumentProcessor → Extract Text
   ↓
4. DocumentProcessor → Split into Chunks
   ↓
5. EmbeddingModel → Generate Embeddings
   ↓
6. VectorStore → Save to PostgreSQL
   ↓
7. Response → Document ID
```

### Генерация ответа

```
1. User → Question
   ↓
2. FastAPI → Validate Request
   ↓
3. EmbeddingModel → Embed Question
   ↓
4. VectorStore → Vector Search (cosine similarity)
   ↓
5. RAGManager → Construct Context
   ↓
6. LLM Manager → Generate Answer
   ↓
7. Response → Answer + Sources
```

## Паттерны проектирования

### 1. Facade (RAGManager)
Упрощает взаимодействие со сложной системой

### 2. Strategy (LLM Manager)
Выбор LLM провайдера в runtime

### 3. Repository (VectorStore)
Абстракция над хранилищем данных

### 4. Factory (llm_factory)
Создание LLM менеджеров

### 5. Dependency Injection
Конфигурация через pydantic-settings

## Асинхронность

**Все операции асинхронные:**
- API endpoints (FastAPI)
- База данных (asyncpg)
- Файловые операции (aiofiles)

**Преимущества:**
- Высокая пропускная способность
- Эффективное использование ресурсов
- Поддержка множества одновременных запросов

## Векторный поиск

**Алгоритм:**
1. Текст → Embedding (sentence-transformers)
2. Embedding → Vector (384 dim)
3. Vector → PostgreSQL pgvector
4. Поиск → Cosine Similarity
5. Результат → Top-K наиболее похожих

**Индексация:**
- IVFFlat (Inverted File with Flat compression)
- Быстрый приближенный поиск
- Балансирует точность и скорость

## Масштабируемость

### Горизонтальное масштабирование

**API Layer:**
- Несколько экземпляров FastAPI
- Load Balancer (nginx/traefik)

**Database Layer:**
- PostgreSQL репликация
- Read replicas для поиска

### Вертикальное масштабирование

**CPU:**
- Embedding generation
- LLM inference (если локально)

**RAM:**
- Модели в памяти
- Кеширование

**Storage:**
- Векторная БД
- Загруженные файлы

## Безопасность

### Реализовано:
- Валидация входных данных (Pydantic)
- Обработка ошибок
- Изоляция через Docker

### Рекомендуется добавить:
- Аутентификация (JWT)
- Rate limiting
- HTTPS
- Шифрование данных
- Проверка типов файлов

## Мониторинг и логирование

### Текущее состояние:
- Логи uvicorn
- Логи PostgreSQL
- Docker logs

### Рекомендуется:
- Structured logging (structlog)
- Metrics (Prometheus)
- Tracing (Jaeger/OpenTelemetry)
- Error tracking (Sentry)

## Конфигурация

**Управление конфигурацией:**
- `.env` файлы
- Переменные окружения
- pydantic-settings
- Валидация при запуске

**Параметры:**
- База данных
- LLM провайдер
- Embedding модель
- Размеры chunks
- Лимиты и пороги

## Тестирование

### Рекомендуемая структура:

```
tests/
├── unit/
│   ├── test_document_processor.py
│   ├── test_embeddings.py
│   └── test_vector_store.py
├── integration/
│   ├── test_rag_manager.py
│   └── test_api.py
└── e2e/
    └── test_full_flow.py
```

### Стратегия:
- Unit tests для каждого компонента
- Integration tests для RAGManager
- E2E tests для API
- Fixtures для тестовых данных

## Производительность

### Узкие места:
1. **Embedding generation** - CPU intensive
2. **Vector search** - Database query
3. **LLM inference** - если локально
4. **File I/O** - загрузка больших файлов

### Оптимизации:
- Batch embedding generation
- Connection pooling (asyncpg)
- Кеширование embeddings
- Асинхронные операции

## Расширяемость

### Добавление нового формата файла:

```python
# В document_processor.py
@staticmethod
async def _extract_from_new_format(file_path: str) -> str:
    # Логика извлечения
    return text
```

### Добавление нового LLM провайдера:

```python
# В llm_manager/managers/
class NewProviderManager:
    def invoke(self, prompt: str) -> str:
        # Логика вызова
        return response
```

### Добавление нового типа поиска:

```python
# В vector_store.py
async def search_with_filters(
    self, 
    query_embedding, 
    filters: Dict
) -> List[Dict]:
    # Логика с фильтрами
    return results
```

## Зависимости

### Основные:
- **FastAPI** - веб-фреймворк
- **asyncpg** - PostgreSQL драйвер
- **pgvector** - векторное расширение
- **sentence-transformers** - embeddings
- **pypdf/docx/openpyxl** - обработка файлов

### Размер:
- Docker образ: ~2-3 GB
- База данных: зависит от документов
- Модель embeddings: ~90 MB

## Развертывание

### Docker Compose (dev/test):
```yaml
services:
  - postgres (pgvector)
  - app (FastAPI)
```

### Production (рекомендации):
- Kubernetes
- Отдельный PostgreSQL кластер
- Redis для кеширования
- S3 для файлов
- Load Balancer

## Дополнительная документация

- [Быстрый старт](QUICKSTART.md) - начните работу за 5 минут
- [Установка](INSTALL.md) - детальная инструкция по установке
- [Использование](USAGE.md) - руководство по API и SDK
- [Структура проекта](PROJECT_STRUCTURE.md) - описание файлов
- [Улучшения](IMPROVEMENTS.md) - повышение качества

## Лицензия

MIT License - свободное использование

