# Добавлена функция суммаризации документов

## Что нового?

Добавлена функция автоматической суммаризации (создания краткого содержания) загруженных документов с помощью LLM.

## Основные возможности

### 1. Веб-интерфейс
- Выберите документ из списка
- Введите команду `summary` или `суммаризация`
- Получите структурированное краткое содержание

### 2. REST API
Новый эндпоинт: `POST /api/summarize`

```bash
curl -X POST "http://localhost:8000/api/summarize" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1}'
```

### 3. Python SDK
```python
summary_result = await rag.summarize_document(document_id=1)
print(summary_result['summary'])
```

## Измененные файлы

### Backend
- `app/models.py` - добавлены модели `SummaryRequest` и `SummaryResponse`
- `app/main.py` - добавлен эндпоинт `POST /api/summarize`
- `RAG/rag_manager.py` - добавлен метод `summarize_document()`
- `RAG/vector_store.py` - добавлен метод `get_document_chunks()`

### Frontend
- `app/static/script.js` - добавлена функция `handleSummarization()` и обработка команды "summary"
- `app/static/index.html` - обновлено приветственное сообщение

### Документация
- `README.md` - обновлен с информацией о суммаризации
- `docs/SUMMARIZATION.md` - новая подробная документация
- `docs/USAGE.md` - добавлены примеры использования суммаризации
- `example_usage.py` - добавлен пример суммаризации

## Технические детали

### Как это работает?
1. Система получает все текстовые фрагменты документа из базы данных
2. Фрагменты объединяются в единый текст (с ограничением 15000 символов)
3. Текст отправляется в LLM с специальным промптом для структурированной суммаризации
4. Результат форматируется в Markdown и возвращается пользователю

### Структура суммаризации
- Общее описание в 2-3 предложениях
- Основные темы и разделы
- Маркированные списки ключевых пунктов
- Выделение важных терминов
- Ключевые выводы

### Требования
- Настроенный LLM провайдер (Ollama, OpenAI, DeepSeek, YandexGPT или GigaChat)
- Загруженные документы в системе

## Использование

### Веб-интерфейс
1. Загрузите документ
2. Выберите его в списке слева
3. Введите `summary` в поле ввода
4. Получите краткое содержание

### Python код
```python
from RAG import RAGManager

async def main():
    rag = RAGManager()
    await rag.initialize()
    
    # Суммаризация документа
    result = await rag.summarize_document(1)
    
    print(f"Документ: {result['filename']}")
    print(f"\n{result['summary']}")
    
    await rag.close()
```

### REST API
```python
import requests

response = requests.post(
    "http://localhost:8000/api/summarize",
    json={"document_id": 1}
)

data = response.json()
print(data['summary'])
```

## Полезные ссылки

- [Подробная документация по суммаризации](docs/SUMMARIZATION.md)
- [Примеры использования](docs/USAGE.md#суммаризация-документа)
- [API документация](README.md#api-endpoints)

## Примеры использования

### Суммаризация одного документа
```bash
# Через curl
curl -X POST "http://localhost:8000/api/summarize" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1}'
```

### Суммаризация всех документов
```python
documents = await rag.get_documents()

for doc in documents:
    summary = await rag.summarize_document(doc['id'])
    print(f"\n{'='*60}")
    print(f"{doc['filename']}")
    print('='*60)
    print(summary['summary'])
```

### Сохранение суммаризации в файл
```python
result = await rag.summarize_document(1)

with open(f"{result['filename']}_summary.md", 'w', encoding='utf-8') as f:
    f.write(result['summary'])
```

## Команды для быстрого запуска

```bash
# Запуск приложения
docker compose up --build

# Или локально
uvicorn app.main:app --reload
```

После запуска:
1. Откройте http://localhost:8000
2. Загрузите документ
3. Выберите его и введите `summary`

## Обратная связь

Если возникли вопросы или проблемы с новой функцией:
1. Проверьте [документацию по суммаризации](docs/SUMMARIZATION.md)
2. Убедитесь, что LLM провайдер настроен правильно
3. Проверьте логи приложения

