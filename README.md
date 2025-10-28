# RAG - Retrieval-Augmented Generation

Небольшой проект на Python для экспериментов с системой RAG (Retrieval-Augmented Generation) с использованием PostgreSQL + pgvector для хранения векторных представлений документов.

## Возможности

- **Асинхронный SDK** для работы с RAG системами
- **Векторное хранилище** на базе PostgreSQL с расширением pgvector
- **Поддержка множества форматов** файлов: PDF, DOCX, XLSX, TXT, MD, HTML, CSV, JSON и др.
- **Веб-интерфейс** для загрузки документов и чата
- **Интеграция с различными LLM** через llm_manager (OpenAI, Ollama, DeepSeek, Yandex GPT, GigaChat)
- **Docker Compose** для простого развертывания

## Документация

Полная документация находится в директории [`docs/`](docs/):

- [**Быстрый старт**](docs/QUICKSTART.md) - запуск за 5 минут
- [**Установка**](docs/INSTALL.md) - подробная инструкция по установке
- [**Использование**](docs/USAGE.md) - руководство по использованию API и SDK
- [**Docker Compose с Ollama**](docs/DOCKER_OLLAMA.md) - запуск с Ollama в контейнере или локально
- [**Логирование**](docs/LOGGING.md) - система логирования и отладка
- [**Архитектура**](docs/ARCHITECTURE.md) - архитектура и технические детали
- [**Структура проекта**](docs/PROJECT_STRUCTURE.md) - описание файлов и директорий
- [**Настройка окружения**](docs/ENV_SETUP.md) - конфигурация переменных окружения
- [**Настройка GigaChat**](docs/GIGACHAT_SETUP.md) - интеграция с GigaChat
- [**Windows**](docs/WINDOWS.md) - инструкции для Windows
- [**Улучшения**](docs/IMPROVEMENTS.md) - рекомендации по повышению качества

## Структура проекта

```
RAG/
├── RAG/                        # Основной SDK (можно импортировать в других проектах)
│   ├── __init__.py
│   ├── config.py               # Конфигурация
│   ├── vector_store.py         # Работа с PostgreSQL + pgvector
│   ├── embeddings.py           # Модели embeddings
│   ├── document_processor.py   # Обработка различных форматов файлов
│   └── rag_manager.py          # Главный класс для работы с RAG
├── app/                        # FastAPI приложение
│   ├── main.py                 # API endpoints
│   ├── models.py               # Pydantic модели
│   └── static/                 # Веб-интерфейс
│       ├── index.html
│       ├── style.css
│       └── script.js
├── llm_manager/                # Git submodule для работы с LLM
├── uploads/                    # Директория для загруженных файлов
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile                  # Docker образ приложения
├── init.sql                    # Инициализация базы данных
├── requirements.txt            # Python зависимости
└── .env                        # Переменные окружения
```

## Быстрый старт

> **Примечание:** PostgreSQL в Docker доступен на порту **6432** (не 5432), чтобы не конфликтовать с локально установленным PostgreSQL.

### 1. Клонирование репозитория с submodule

```bash
git clone --recurse-submodules https://github.com/yourusername/RAG.git
cd RAG
```

Если уже клонировали без submodule:

```bash
git submodule update --init --recursive
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта с настройками LLM провайдера:

```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

### 3. Запуск через Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

## Использование веб-интерфейса

1. Откройте браузер и перейдите на http://localhost:8000
2. Загрузите документы через кнопку "Загрузить файл"
3. Выберите режим поиска:
   - **Все документы** - поиск по всем загруженным документам
   - **Выбранный документ** - поиск только в выбранном документе
4. Задавайте вопросы в чате и получайте ответы на основе загруженных документов

## Использование SDK в коде

### Базовый пример

```python
from RAG import RAGManager

async def main():
    rag = RAGManager()
    await rag.initialize()
    
    document_id = await rag.add_document(
        file_path="path/to/document.pdf",
        filename="document.pdf"
    )
    
    result = await rag.generate_answer(
        query="Какая основная тема документа?",
        document_id=document_id
    )
    
    print(result['answer'])
    print(result['sources'])
    
    await rag.close()
```

### Поиск похожих фрагментов

```python
results = await rag.search(
    query="машинное обучение",
    document_id=None,
    limit=5
)

for result in results:
    print(f"Документ: {result['filename']}")
    print(f"Релевантность: {result['similarity']:.2f}")
    print(f"Текст: {result['content'][:200]}...")
```

### Работа с документами

```python
documents = await rag.get_documents()

for doc in documents:
    print(f"ID: {doc['id']}, Имя: {doc['filename']}")
    print(f"Фрагментов: {doc['chunk_count']}")

await rag.delete_document(document_id)
```

## API Endpoints

### Документы

- `GET /api/documents` - Получить список всех документов
- `GET /api/documents/{id}` - Получить информацию о документе
- `POST /api/upload` - Загрузить документ
- `DELETE /api/documents/{id}` - Удалить документ

### Чат и поиск

- `POST /api/chat` - Задать вопрос и получить ответ
  ```json
  {
    "query": "Ваш вопрос",
    "document_id": 1,  // optional
    "context_limit": 3
  }
  ```

- `POST /api/search` - Поиск похожих фрагментов
  ```json
  {
    "query": "Ваш запрос",
    "document_id": 1,  // optional
    "context_limit": 5
  }
  ```

### Health Check

- `GET /health` - Проверка состояния сервиса

## Конфигурация

### Переменные окружения

#### PostgreSQL
- `POSTGRES_USER` - пользователь БД
- `POSTGRES_PASSWORD` - пароль БД
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_HOST` - хост БД
- `POSTGRES_PORT` - порт БД (по умолчанию 6432)

#### LLM Provider
- `PROVIDER` - провайдер LLM (ollama / openai / deepseek / yandex / gigachat)
- `OLLAMA_HOST` - хост Ollama
- `OLLAMA_MODEL` - модель Ollama
- `OPENAI_API_KEY` - ключ OpenAI API
- `DEEPSEEK_API_KEY` - ключ DeepSeek API
- `YANDEX_GPT_API_KEY` - ключ Yandex GPT API
- `GIGA_CHAT_AUTH_KEY` - ключ GigaChat

#### Embeddings и Поиск
- `EMBEDDING_MODEL` - модель для векторизации (по умолчанию: sentence-transformers/all-MiniLM-L6-v2)
- `CHUNK_SIZE` - размер фрагмента текста (по умолчанию: 500)
- `CHUNK_OVERLAP` - перекрытие между фрагментами (по умолчанию: 50)
- `SEARCH_LIMIT` - количество возвращаемых результатов поиска (по умолчанию: 7)
- `MIN_SIMILARITY` - минимальный порог схожести для фильтрации результатов, 0.0-1.0 (по умолчанию: 0.4)

## Поддерживаемые форматы файлов

- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Microsoft Excel (`.xlsx`, `.xls`)
- Markdown (`.md`, `.markdown`)
- HTML (`.html`, `.htm`)
- Текстовые файлы (`.txt`, `.csv`, `.json`, `.xml`, `.log`)

## Требования

### Для работы через Docker (рекомендуется)
- Docker
- Docker Compose

### Для локальной разработки
- Python 3.11+
- PostgreSQL 16+ с расширением pgvector
- LLM provider (Ollama, OpenAI API и др.)

## Локальная разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
pip install -r llm_manager/requirements.txt
```

### Запуск PostgreSQL с pgvector

```bash
docker run -d \
  --name rag_postgres \
  -e POSTGRES_USER=rag_user \
  -e POSTGRES_PASSWORD=rag_password \
  -e POSTGRES_DB=rag_db \
  -p 6432:5432 \
  pgvector/pgvector:pg16
```

### Инициализация базы данных

```bash
psql -h localhost -U rag_user -d rag_db -f init.sql
```

### Запуск приложения

```bash
uvicorn app.main:app --reload
```

## Интеграция в другие проекты

SDK можно использовать как библиотеку в других проектах:

```python
import sys
sys.path.insert(0, 'path/to/RAG')

from RAG import RAGManager, VectorStore, DocumentProcessor

rag = RAGManager()
```

Или установить как пакет:

```bash
pip install -e path/to/RAG
```

## Лицензия

MIT License

## Благодарности

- [llm_manager](https://github.com/bazhil/llm_manager) - для работы с различными LLM
- [pgvector](https://github.com/pgvector/pgvector) - для векторного поиска в PostgreSQL
- [sentence-transformers](https://www.sbert.net/) - для создания embeddings
- [FastAPI](https://fastapi.tiangolo.com/) - веб-фреймворк

