# Структура проекта RAG SDK

## Корневая директория

```
rag_sdk/
├── app/                        # FastAPI приложение
├── rag_sdk/                    # Основной SDK (переиспользуемый)
├── llm_manager/                # Git submodule для работы с LLM
├── uploads/                    # Загруженные файлы
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile                  # Docker образ приложения
├── init.sql                    # Инициализация PostgreSQL
├── requirements.txt            # Python зависимости
├── setup.py                    # Установка как пакет
├── .env                        # Переменные окружения (не в git)
├── .gitignore                  # Git ignore правила
└── .dockerignore               # Docker ignore правила
```

## Документация

### Основные файлы

| Файл | Назначение |
|------|------------|
| `README.md` | Главная документация проекта |
| `QUICKSTART.md` | Быстрый старт за 5 минут |
| `INSTALL.md` | Подробная инструкция по установке |
| `USAGE.md` | Руководство по использованию |
| `ARCHITECTURE.md` | Архитектура и технические детали |
| `WINDOWS.md` | Инструкции для Windows |
| `PROJECT_STRUCTURE.md` | Этот файл - структура проекта |

### Вспомогательные файлы

| Файл | Назначение |
|------|------------|
| `LICENSE` | MIT лицензия |
| `Makefile` | Команды для управления проектом |
| `start.ps1` | PowerShell скрипт запуска (Windows) |
| `stop.ps1` | PowerShell скрипт остановки (Windows) |
| `example_usage.py` | Пример использования SDK |

## SDK (rag_sdk/)

### Структура

```
rag_sdk/
├── __init__.py              # Экспорт главных классов
├── config.py                # Конфигурация (Settings)
├── rag_manager.py           # Главный класс RAGManager
├── vector_store.py          # Работа с PostgreSQL + pgvector
├── embeddings.py            # Модели векторизации
└── document_processor.py    # Обработка документов
```

### Описание компонентов

#### `__init__.py`
Экспортирует главные классы для импорта:
```python
from rag_sdk import RAGManager, VectorStore, DocumentProcessor
```

#### `config.py`
- Класс `Settings` с использованием pydantic-settings
- Загрузка переменных окружения из `.env`
- Валидация конфигурации
- Параметры:
  - База данных (PostgreSQL на порту 6432)
  - LLM провайдер
  - Embedding модель
  - Chunk параметры

#### `rag_manager.py`
**Главный класс** для работы с RAG системой.

**Методы:**
- `initialize()` - инициализация компонентов
- `close()` - закрытие соединений
- `add_document()` - добавление документа
- `search()` - векторный поиск
- `generate_answer()` - генерация ответа с LLM
- `get_documents()` - список документов
- `get_document()` - информация о документе
- `delete_document()` - удаление документа

**Зависимости:**
- VectorStore
- EmbeddingModel
- DocumentProcessor
- LLM Manager (через submodule)

#### `vector_store.py`
Асинхронная работа с PostgreSQL + pgvector.

**Методы:**
- `connect()` - подключение к БД
- `close()` - закрытие соединения
- `create_document()` - создание записи документа
- `add_chunks()` - добавление фрагментов
- `search_similar()` - векторный поиск (cosine similarity)
- `get_documents()` - получение списка
- `get_document()` - получение по ID
- `delete_document()` - удаление

**Технологии:**
- asyncpg (асинхронный драйвер)
- pgvector (векторное расширение)

#### `embeddings.py`
Векторизация текста.

**Класс:** `EmbeddingModel`

**Методы:**
- `load()` - загрузка модели
- `encode()` - кодирование текста/текстов
- `encode_batch()` - пакетное кодирование

**Технологии:**
- sentence-transformers
- Модель по умолчанию: all-MiniLM-L6-v2 (384 размерность)

#### `document_processor.py`
Обработка различных форматов файлов.

**Класс:** `DocumentProcessor`

**Методы:**
- `extract_text_from_file()` - извлечение текста
- `split_text_into_chunks()` - разбиение на фрагменты
- `prepare_chunks_for_storage()` - подготовка к сохранению

**Поддерживаемые форматы:**
- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- Excel (`.xlsx`, `.xls`)
- Markdown (`.md`)
- HTML (`.html`, `.htm`)
- Text (`.txt`, `.csv`, `.json`, `.xml`, `.log`)

**Библиотеки:**
- pypdf - для PDF
- python-docx - для Word
- openpyxl - для Excel
- markdown + BeautifulSoup - для MD/HTML
- chardet - для определения кодировки

## Приложение (app/)

### Структура

```
app/
├── __init__.py              # Пустой файл (пакет)
├── main.py                  # FastAPI приложение
├── models.py                # Pydantic модели
└── static/                  # Статические файлы
    ├── index.html           # Главная страница
    ├── style.css            # Стили
    └── script.js            # Клиентская логика
```

### Описание компонентов

#### `main.py`
FastAPI приложение с REST API.

**Endpoints:**

**Документы:**
- `GET /api/documents` - список документов
- `GET /api/documents/{id}` - документ по ID
- `POST /api/upload` - загрузка документа
- `DELETE /api/documents/{id}` - удаление документа

**Чат и поиск:**
- `POST /api/chat` - вопрос-ответ
- `POST /api/search` - векторный поиск

**Другое:**
- `GET /` - главная страница (HTML)
- `GET /health` - проверка состояния
- `/static` - статические файлы

**Особенности:**
- Асинхронные endpoint'ы
- Lifespan управление (инициализация/закрытие RAGManager)
- Обработка ошибок
- CORS (опционально)

#### `models.py`
Pydantic модели для валидации.

**Модели:**
- `QueryRequest` - запрос для чата/поиска
- `QueryResponse` - ответ с результатом
- `SourceInfo` - информация об источнике
- `DocumentResponse` - информация о документе

#### `static/index.html`
Веб-интерфейс с:
- Загрузкой файлов
- Списком документов
- Чатом
- Выбором режима поиска

#### `static/style.css`
Современный дизайн:
- Градиентный фон
- Адаптивная верстка
- Анимации
- Красивые карточки документов

#### `static/script.js`
Клиентская логика:
- Загрузка файлов
- Управление документами
- Отправка сообщений
- Отображение ответов
- Работа с API

## LLM Manager (llm_manager/)

Git submodule из https://github.com/bazhil/llm_manager

### Структура

```
llm_manager/
├── llm_factory.py           # Factory для создания LLM менеджеров
├── utils.py                 # Вспомогательные функции
├── requirements.txt         # Зависимости
└── managers/                # Менеджеры для разных провайдеров
    ├── ollama_manager.py
    ├── openai_manager.py
    ├── deepseek_manager.py
    ├── yandex_gpt_manager.py
    └── giga_chat_manager.py
```

### Провайдеры

- **Ollama** - локальные модели (llama3, mistral, и др.)
- **OpenAI** - GPT-3.5, GPT-4
- **DeepSeek** - DeepSeek API
- **Yandex GPT** - Yandex Cloud
- **GigaChat** - Сбер

## Docker

### docker-compose.yml

Сервисы:
- **postgres** - PostgreSQL 16 с pgvector
- **app** - FastAPI приложение

Volumes:
- `postgres_data` - данные PostgreSQL

Networks:
- Автоматическая сеть между сервисами

### Dockerfile

Multi-stage сборка:
1. Установка системных зависимостей
2. Установка Python пакетов
3. Копирование кода
4. Запуск uvicorn

### init.sql

Создает:
- Расширение `vector`
- Таблицу `documents`
- Таблицу `chunks`
- Индексы для поиска

## Конфигурация

### requirements.txt

**Основные:**
- fastapi - веб-фреймворк
- uvicorn - ASGI сервер
- asyncpg - PostgreSQL драйвер
- pgvector - векторное расширение
- sentence-transformers - embeddings
- torch - для ML моделей

**Обработка файлов:**
- pypdf - PDF
- python-docx - Word
- openpyxl - Excel
- markdown, beautifulsoup4 - MD/HTML
- chardet - кодировка

**Другое:**
- pydantic, pydantic-settings - валидация
- aiofiles - асинхронные файлы
- python-multipart - загрузка файлов
- langchain - для RAG

### .env (пример)

```env
# PostgreSQL
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432  # Внутри Docker сети, внешний порт 6432

# LLM Provider
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

## Данные

### uploads/

Директория для загруженных файлов:
- Создается автоматически
- Файлы сохраняются с оригинальными именами
- Удаляются при удалении документа из БД

### PostgreSQL

**База данных:** `rag_db`

**Таблицы:**

**documents:**
- `id` - PRIMARY KEY
- `filename` - имя файла
- `file_size` - размер в байтах
- `upload_date` - дата загрузки
- `metadata` - JSON метаданные

**chunks:**
- `id` - PRIMARY KEY
- `document_id` - FOREIGN KEY
- `content` - текст фрагмента
- `embedding` - вектор (384 dim)
- `chunk_index` - порядковый номер
- `metadata` - JSON метаданные

**Индексы:**
- IVFFlat на `embedding` для векторного поиска
- B-tree на `document_id` для связи

## Использование

### Как импортировать SDK в другом проекте

```python
import sys
sys.path.insert(0, '/path/to/rag_sdk')

from rag_sdk import RAGManager

# Или установить как пакет
# pip install -e /path/to/rag_sdk
```

### Как добавить новый формат файла

1. Открыть `rag_sdk/document_processor.py`
2. Добавить метод `_extract_from_new_format()`
3. Добавить расширение в `extract_text_from_file()`

### Как добавить новый LLM провайдер

1. В `llm_manager/managers/` создать `new_provider_manager.py`
2. Реализовать метод `invoke()`
3. Добавить в `llm_factory.py`

### Как изменить размер фрагментов

В `.env`:
```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
```

## Размер проекта

**Без зависимостей:**
- Исходный код: ~50 KB
- Документация: ~100 KB

**С зависимостями:**
- Python пакеты: ~1 GB
- Docker образ: ~2-3 GB
- Embedding модель: ~90 MB

**База данных:**
- Зависит от количества документов
- 1 документ (100 страниц) ≈ 1-5 MB

## Лицензии

- **Проект:** MIT License
- **llm_manager:** MIT License
- **Зависимости:** Различные (см. requirements.txt)

## Контакты и поддержка

- GitHub Issues для bug reports
- Pull Requests приветствуются
- Документация постоянно обновляется

