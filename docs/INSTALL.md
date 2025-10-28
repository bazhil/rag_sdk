# Инструкция по установке и запуску RAG SDK

> **Примечание:** PostgreSQL в этом проекте использует порт **6432** вместо стандартного 5432, чтобы не конфликтовать с локально установленным PostgreSQL.

## Вариант 1: Запуск через Docker Compose (Рекомендуется)

### Предварительные требования
- Docker версии 20.10+
- Docker Compose версии 2.0+

### Шаги установки

1. **Клонируйте репозиторий с submodule**

```bash
git clone --recurse-submodules <repository-url>
cd RAG
```

Если уже клонировали без submodule:
```bash
git submodule update --init --recursive
```

2. **Настройте файл .env**

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите настройки LLM провайдера:

Для Ollama (локально):
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

Для OpenAI:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

Для DeepSeek:
```env
PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key
```

3. **Запустите Docker Compose**

```bash
docker compose up --build
```

При первом запуске:
- Скачаются все необходимые образы
- Создастся база данных PostgreSQL с расширением pgvector
- Запустится веб-приложение

4. **Откройте браузер**

Перейдите на http://localhost:8000

## Вариант 2: Локальная установка (для разработки)

### Предварительные требования
- Python 3.11+
- PostgreSQL 16+ с расширением pgvector
- Git

### Шаги установки

1. **Клонируйте репозиторий**

```bash
git clone --recurse-submodules <repository-url>
cd RAG
```

2. **Создайте виртуальное окружение**

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate  # Для Windows
```

3. **Установите зависимости**

```bash
pip install -r requirements.txt
pip install -r llm_manager/requirements.txt
```

4. **Настройте PostgreSQL**

Установите PostgreSQL с pgvector:

```bash
# Для Ubuntu/Debian
sudo apt-get install postgresql-16 postgresql-16-pgvector

# Для Mac
brew install postgresql pgvector
```

Или запустите через Docker:

```bash
docker run -d \
  --name rag_postgres \
  -e POSTGRES_USER=rag_user \
  -e POSTGRES_PASSWORD=rag_password \
  -e POSTGRES_DB=rag_db \
  -p 6432:5432 \
  pgvector/pgvector:pg16
```

5. **Инициализируйте базу данных**

```bash
psql -h localhost -U rag_user -d rag_db -f init.sql
```

Или если через Docker:

```bash
docker exec -i rag_postgres psql -U rag_user -d rag_db < init.sql
```

6. **Настройте .env**

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=6432
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db

PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

7. **Запустите приложение**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Откройте браузер**

Перейдите на http://localhost:8000

## Настройка LLM провайдеров

### Ollama (локальный запуск)

1. Установите Ollama: https://ollama.ai/
2. Запустите модель:

```bash
ollama pull llama3
ollama serve
```

3. В `.env`:
```env
PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

### OpenAI

1. Получите API ключ: https://platform.openai.com/api-keys
2. В `.env`:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

### DeepSeek

1. Получите API ключ: https://platform.deepseek.com/
2. В `.env`:
```env
PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key
```

### Yandex GPT

1. Получите API ключ и Folder ID в Yandex Cloud
2. В `.env`:
```env
PROVIDER=yandex
YANDEX_GPT_API_KEY=your-api-key
YANDEX_GPT_FOLDER_ID=your-folder-id
```

### GigaChat

1. Получите Auth Key: https://developers.sber.ru/gigachat
2. В `.env`:
```env
PROVIDER=gigachat
GIGA_CHAT_AUTH_KEY=your-auth-key
```

## Проверка работоспособности

### Проверка health endpoint

```bash
curl http://localhost:8000/health
```

Ответ должен быть:
```json
{"status": "ok"}
```

### Проверка API

```bash
# Получить список документов
curl http://localhost:8000/api/documents

# Загрузить документ
curl -X POST http://localhost:8000/api/upload \
  -F "file=@path/to/document.pdf"

# Задать вопрос
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Ваш вопрос", "context_limit": 3}'
```

## Использование SDK в коде

```python
import asyncio
from RAG import RAGManager

async def main():
    rag = RAGManager()
    await rag.initialize()
    
    documents = await rag.get_documents()
    print(f"Документов в базе: {len(documents)}")
    
    await rag.close()

asyncio.run(main())
```

## Остановка сервисов

### Docker Compose

```bash
# Остановить сервисы
docker compose down

# Остановить и удалить данные
docker compose down -v
```

### Локальный запуск

Нажмите Ctrl+C в терминале где запущен uvicorn

## Устранение проблем

### Ошибка подключения к PostgreSQL

Проверьте, что PostgreSQL запущен:
```bash
docker ps | grep postgres
# или
sudo systemctl status postgresql
```

### Ошибка подключения к Ollama

Проверьте, что Ollama запущен:
```bash
curl http://localhost:11434/api/tags
```

### Проблемы с Docker

Очистите Docker кеш:
```bash
docker system prune -a
docker compose build --no-cache
```

### Проблемы с правами доступа к uploads/

```bash
chmod 777 uploads/
```

## Логи

### Docker Compose

```bash
# Все логи
docker compose logs

# Логи конкретного сервиса
docker compose logs app
docker compose logs postgres

# Следить за логами в реальном времени
docker compose logs -f
```

### Локальный запуск

Логи uvicorn выводятся в консоль.

## Дополнительные ресурсы

### Документация проекта

- [Быстрый старт](QUICKSTART.md) - запуск за 5 минут
- [Руководство по использованию](USAGE.md) - работа с API и SDK
- [Архитектура](ARCHITECTURE.md) - техническая документация
- [Настройка окружения](ENV_SETUP.md) - переменные окружения

### Внешние ресурсы

- [pgvector](https://github.com/pgvector/pgvector) - векторное хранилище
- [FastAPI](https://fastapi.tiangolo.com/) - веб-фреймворк
- [llm_manager](https://github.com/bazhil/llm_manager) - интеграция с LLM
- [sentence-transformers](https://www.sbert.net/) - модели embeddings

