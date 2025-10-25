# Быстрый старт RAG SDK

## За 5 минут до работающего приложения

> **Примечание:** PostgreSQL доступен на порту **6432**, чтобы не конфликтовать с локально установленным PostgreSQL на порту 5432.

### Шаг 1: Клонирование

```bash
git clone --recurse-submodules <repository-url>
cd rag_sdk
```

### Шаг 2: Настройка LLM

Отредактируйте файл `.env` (он уже создан) и укажите настройки LLM:

**Для локального Ollama:**
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

Убедитесь, что Ollama запущен:
```bash
ollama pull llama3
ollama serve
```

**Для OpenAI:**
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

### Шаг 3: Запуск

```bash
docker-compose up --build
```

### Шаг 4: Использование

Откройте http://localhost:8000 в браузере

**Готово!** Вы можете:
1. Загружать документы
2. Задавать вопросы
3. Получать ответы на основе документов

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

- Подробная документация: [README.md](README.md)
- Инструкция по установке: [INSTALL.md](INSTALL.md)
- Примеры использования: [USAGE.md](USAGE.md)
- Пример кода: [example_usage.py](example_usage.py)

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

