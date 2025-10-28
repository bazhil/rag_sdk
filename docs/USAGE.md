# Руководство по использованию RAG SDK

## Содержание

1. [Веб-интерфейс](#веб-интерфейс)
2. [REST API](#rest-api)
3. [Использование SDK в коде](#использование-sdk-в-коде)
4. [Примеры использования](#примеры-использования)

## Веб-интерфейс

### Загрузка документов

1. Откройте http://localhost:8000
2. Нажмите кнопку "📁 Загрузить файл"
3. Выберите файл на вашем компьютере
4. Дождитесь окончания обработки

Поддерживаемые форматы:
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- Markdown (.md)
- HTML (.html, .htm)
- Текст (.txt, .csv, .json, .xml, .log)

### Работа с документами

В левой панели отображаются все загруженные документы:
- **Имя файла** - название документа
- **Размер** - размер файла
- **Количество фрагментов** - на сколько частей разбит документ
- **Дата загрузки** - когда был загружен

**Выбор документа:**
- Кликните на документ для его выбора
- Выбранный документ подсвечивается синим цветом

**Удаление документа:**
- Нажмите кнопку "Удалить" на карточке документа
- Подтвердите удаление

### Режимы поиска

**Все документы:**
- Поиск происходит по всем загруженным документам
- Используется когда нужно найти информацию в любом документе

**Выбранный документ:**
- Поиск происходит только в выбранном документе
- Используется для работы с конкретным документом
- Автоматически активируется при выборе документа

### Чат

1. Введите ваш вопрос в поле внизу
2. Нажмите "📤 Отправить" или Enter
3. Дождитесь ответа

**Ответ включает:**
- Текст ответа на основе документов
- Список источников с указанием:
  - Имени файла
  - Процента совпадения (релевантности)

## REST API

### Документы

#### Получить список документов

```http
GET /api/documents
```

**Ответ:**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "file_size": 1024000,
    "upload_date": "2025-10-25T12:00:00",
    "metadata": {"chunks_count": 50},
    "chunk_count": 50
  }
]
```

#### Получить документ по ID

```http
GET /api/documents/{document_id}
```

**Ответ:**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_size": 1024000,
  "upload_date": "2025-10-25T12:00:00",
  "metadata": {"chunks_count": 50},
  "chunk_count": 50
}
```

#### Загрузить документ

```http
POST /api/upload
Content-Type: multipart/form-data

file: <file>
```

**Ответ:**
```json
{
  "success": true,
  "document_id": 1,
  "filename": "document.pdf",
  "message": "Файл document.pdf успешно загружен и обработан"
}
```

**Пример с curl:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/document.pdf"
```

#### Удалить документ

```http
DELETE /api/documents/{document_id}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Документ document.pdf успешно удален"
}
```

### Чат и поиск

#### Задать вопрос

```http
POST /api/chat
Content-Type: application/json

{
  "query": "Ваш вопрос",
  "document_id": 1,        // опционально, null для поиска по всем
  "context_limit": 3       // количество фрагментов для контекста
}
```

**Ответ:**
```json
{
  "answer": "Ответ на основе документов...",
  "sources": [
    {
      "filename": "document.pdf",
      "document_id": 1,
      "chunk_index": 5,
      "similarity": 0.85
    }
  ],
  "context": [
    "Текст первого релевантного фрагмента...",
    "Текст второго релевантного фрагмента..."
  ]
}
```

**Пример с curl:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Что такое машинное обучение?",
    "context_limit": 3
  }'
```

#### Поиск похожих фрагментов

```http
POST /api/search
Content-Type: application/json

{
  "query": "Запрос для поиска",
  "document_id": 1,        // опционально
  "context_limit": 5       // количество результатов
}
```

**Ответ:**
```json
{
  "success": true,
  "results": [
    {
      "id": 123,
      "content": "Текст фрагмента...",
      "chunk_index": 5,
      "metadata": {"length": 450},
      "filename": "document.pdf",
      "document_id": 1,
      "similarity": 0.85
    }
  ]
}
```

## Использование SDK в коде

### Базовая настройка

```python
import asyncio
from RAG import RAGManager

async def main():
    rag = RAGManager()
    
    await rag.initialize()
    
    await rag.close()

asyncio.run(main())
```

### Загрузка документа

```python
document_id = await rag.add_document(
    file_path="/path/to/document.pdf",
    filename="document.pdf"
)
print(f"Документ загружен с ID: {document_id}")
```

### Получение списка документов

```python
documents = await rag.get_documents()

for doc in documents:
    print(f"ID: {doc['id']}, Имя: {doc['filename']}")
    print(f"Размер: {doc['file_size']} байт")
    print(f"Фрагментов: {doc['chunk_count']}")
```

### Получение информации о документе

```python
document = await rag.get_document(document_id=1)

if document:
    print(f"Имя: {document['filename']}")
    print(f"Загружен: {document['upload_date']}")
else:
    print("Документ не найден")
```

### Поиск похожих фрагментов

```python
results = await rag.search(
    query="машинное обучение",
    document_id=None,
    limit=5
)

for result in results:
    print(f"\nДокумент: {result['filename']}")
    print(f"Релевантность: {result['similarity']:.2%}")
    print(f"Фрагмент: {result['content'][:200]}...")
```

### Генерация ответа

```python
result = await rag.generate_answer(
    query="Что такое нейронные сети?",
    document_id=None,
    context_limit=3
)

print(f"Ответ: {result['answer']}\n")

print("Источники:")
for source in result['sources']:
    print(f"  - {source['filename']} ({source['similarity']:.2%})")
```

### Удаление документа

```python
await rag.delete_document(document_id=1)
print("Документ удален")
```

## Примеры использования

### Пример 1: Обработка PDF документа

```python
import asyncio
from RAG import RAGManager

async def process_pdf():
    rag = RAGManager()
    await rag.initialize()
    
    try:
        print("Загружаем PDF...")
        doc_id = await rag.add_document(
            file_path="research_paper.pdf",
            filename="research_paper.pdf"
        )
        
        print("\nЗадаем вопрос...")
        result = await rag.generate_answer(
            query="Каковы основные выводы исследования?",
            document_id=doc_id
        )
        
        print(f"\nОтвет:\n{result['answer']}")
        
    finally:
        await rag.close()

asyncio.run(process_pdf())
```

### Пример 2: Работа с несколькими документами

```python
import asyncio
from RAG import RAGManager

async def multi_document_search():
    rag = RAGManager()
    await rag.initialize()
    
    try:
        documents = ["book1.pdf", "book2.pdf", "article.docx"]
        
        print("Загружаем документы...")
        doc_ids = []
        for doc_path in documents:
            doc_id = await rag.add_document(doc_path, doc_path)
            doc_ids.append(doc_id)
            print(f"  ✓ {doc_path} - ID: {doc_id}")
        
        print("\nПоиск по всем документам...")
        result = await rag.generate_answer(
            query="Какие общие темы упоминаются?",
            document_id=None,
            context_limit=5
        )
        
        print(f"\nОтвет:\n{result['answer']}")
        print("\nИсточники информации:")
        for source in result['sources']:
            print(f"  - {source['filename']}")
        
    finally:
        await rag.close()

asyncio.run(multi_document_search())
```

### Пример 3: Пакетная обработка вопросов

```python
import asyncio
from RAG import RAGManager

async def batch_questions():
    rag = RAGManager()
    await rag.initialize()
    
    questions = [
        "Что такое машинное обучение?",
        "Какие виды нейронных сетей существуют?",
        "Как работает обратное распространение ошибки?",
    ]
    
    try:
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"Вопрос {i}: {question}")
            print('='*60)
            
            result = await rag.generate_answer(
                query=question,
                context_limit=2
            )
            
            print(f"Ответ: {result['answer']}\n")
            
    finally:
        await rag.close()

asyncio.run(batch_questions())
```

### Пример 4: Использование низкоуровневых компонентов

```python
import asyncio
from RAG import VectorStore, EmbeddingModel, DocumentProcessor

async def low_level_usage():
    vector_store = VectorStore()
    await vector_store.connect()
    
    embedding_model = EmbeddingModel()
    embedding_model.load()
    
    doc_processor = DocumentProcessor()
    
    try:
        text = await doc_processor.extract_text_from_file(
            "document.pdf", 
            "document.pdf"
        )
        
        chunks = doc_processor.split_text_into_chunks(text)
        
        embeddings = embedding_model.encode_batch(chunks)
        
        doc_id = await vector_store.create_document(
            filename="document.pdf",
            file_size=1024,
            metadata={}
        )
        
        prepared_chunks = doc_processor.prepare_chunks_for_storage(
            chunks, 
            embeddings
        )
        
        await vector_store.add_chunks(doc_id, prepared_chunks)
        
        print(f"Документ обработан: {len(chunks)} фрагментов")
        
    finally:
        await vector_store.close()

asyncio.run(low_level_usage())
```

### Пример 5: Интеграция в FastAPI приложение

```python
from fastapi import FastAPI, HTTPException
from RAG import RAGManager
from contextlib import asynccontextmanager

rag_manager = RAGManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await rag_manager.initialize()
    yield
    await rag_manager.close()

app = FastAPI(lifespan=lifespan)

@app.post("/ask")
async def ask_question(question: str):
    try:
        result = await rag_manager.generate_answer(
            query=question,
            context_limit=3
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Настройка параметров

### Размер фрагментов

В `.env`:
```env
CHUNK_SIZE=500          # Размер фрагмента в символах
CHUNK_OVERLAP=50        # Перекрытие между фрагментами
```

Меньший размер = более точный поиск, но больше фрагментов
Больший размер = меньше фрагментов, но может быть менее точным

### Модель эмбеддингов

В `.env`:
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Другие варианты:
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` - мультиязычная
- `sentence-transformers/all-mpnet-base-v2` - более точная, но медленнее

### Параметры поиска

В `.env`:
```env
SEARCH_LIMIT=7         # Количество возвращаемых результатов
MIN_SIMILARITY=0.4     # Минимальный порог схожести (0.0-1.0)
```

Рекомендации:
- `SEARCH_LIMIT`: 5-10 для большинства случаев
- `MIN_SIMILARITY`: 0.3-0.5 (меньше = больше результатов, но менее релевантных)

### Количество контекстных фрагментов

В запросе:
```python
result = await rag.generate_answer(
    query="Вопрос",
    context_limit=5  # Больше контекста = более полный ответ
)
```

Рекомендации:
- 2-3 фрагмента - для кратких ответов
- 5-7 фрагментов - для развернутых ответов
- 10+ фрагментов - для комплексных вопросов

## Советы по использованию

1. **Качество документов** - чем лучше структурирован текст, тем лучше результаты
2. **Размер фрагментов** - подбирайте под ваши документы
3. **Формулировка вопросов** - четкие вопросы дают лучшие ответы
4. **Выбор документа** - используйте фильтр по документу для более точных ответов
5. **LLM провайдер** - выбирайте провайдер под ваши задачи (локальный vs облачный)

