# Быстрый старт RAG SDK

## За 5 минут до работающего приложения

> **Примечание:** PostgreSQL доступен на порту **6432**, чтобы не конфликтовать с локально установленным PostgreSQL на порту 5432.

### Шаг 1: Клонирование

```bash
git clone --recurse-submodules https://github.com/yourusername/rag_sdk.git
cd rag_sdk
```

### Шаг 2: Настройка LLM провайдера

Создайте файл `.env` или отредактируйте существующий:

**Вариант 1: Ollama (локально, бесплатно)**
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

Установите и запустите Ollama:
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama serve

# Windows - скачайте с https://ollama.com/download
```

**Вариант 2: OpenAI**
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

**Вариант 3: GigaChat**
```env
PROVIDER=gigachat
GIGA_CHAT_AUTH_KEY=your-client-secret
GIGA_CHAT_MODEL=GigaChat
```

### Шаг 3: Запуск

```bash
docker-compose up --build
```

### Шаг 4: Использование

Откройте http://localhost:8000 в браузере

**Готово!** Теперь вы можете:
1. Загружать документы (PDF, DOCX, TXT, MD и др.)
2. Задавать вопросы по документам
3. Получать ответы на основе содержимого

## Проверка работы

```bash
# Проверка health
curl http://localhost:8000/health

# Список документов
curl http://localhost:8000/api/documents
```

## Примеры использования

### Загрузить документ через API

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"
```

### Задать вопрос через API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Что такое машинное обучение?",
    "context_limit": 3
  }'
```

### Использовать в Python коде

```python
import asyncio
from rag_sdk import RAGManager

async def main():
    rag = RAGManager()
    await rag.initialize()
    
    doc_id = await rag.add_document("book.pdf", "book.pdf")
    
    result = await rag.generate_answer("О чем эта книга?")
    print(result['answer'])
    
    await rag.close()

asyncio.run(main())
```

## Команды Makefile

```bash
make up       # Запустить
make down     # Остановить
make logs     # Показать логи
make clean    # Очистить все данные
make restart  # Перезапустить
```

## Что дальше?

- [Полная документация](README.md) - оглавление всей документации
- [Детальная установка](INSTALL.md) - подробная инструкция по установке
- [Руководство по использованию](USAGE.md) - примеры работы с API и SDK
- [Архитектура системы](ARCHITECTURE.md) - технические детали
- [Пример кода](../example_usage.py) - примеры использования SDK

## Решение проблем

### Ollama не подключается

В `.env` измените:
```env
OLLAMA_HOST=http://host.docker.internal:11434
```

на (для Linux):
```env
OLLAMA_HOST=http://172.17.0.1:11434
```

### Ошибка при загрузке файла

Проверьте права доступа:
```bash
chmod 777 uploads/
```

### База данных не инициализировалась

Пересоздайте контейнеры:
```bash
docker-compose down -v
docker-compose up --build
```

## Поддерживаемые форматы файлов

✅ PDF, DOCX, XLSX, TXT, MD, HTML, CSV, JSON, XML, LOG и другие текстовые форматы

## Системные требования

- Docker + Docker Compose
- 4GB RAM минимум
- 10GB свободного места

