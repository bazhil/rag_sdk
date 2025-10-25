# Конфигурация переменных окружения

## Краткая сводка

✅ **Нужен только ОДИН файл `.env` в корне проекта**  
❌ **НЕ нужен** `.env` в директории `llm_manager`

```
rag_sdk/
├── .env                 ← ЕДИНСТВЕННЫЙ файл конфигурации
├── llm_manager/
│   └── (нет .env)      ← Использует переменные окружения напрямую
```

## Как llm_manager получает переменные

### В Docker (docker-compose up):
```
.env файл
    ↓
docker-compose.yml читает переменные
    ↓
Передает как environment в контейнер
    ↓
llm_manager получает через os.getenv()
```

### Локально (python app/main.py):
```
.env в корне проекта
    ↓
load_dotenv() находит .env автоматически
    ↓
Загружает в переменные окружения
    ↓
llm_manager получает через os.getenv()
```

## Настройка за 3 шага

### 1. Создайте .env

```bash
cat > .env << 'EOF'
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EOF
```

### 2. Настройте LLM провайдер

**Ollama (рекомендуется для начала):**
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

**OpenAI:**
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

**DeepSeek:**
```env
PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key
```

### 3. Запустите проект

```bash
docker-compose up --build
```

## Проверка конфигурации

```bash
# Проверить .env
cat .env | grep PROVIDER

# Проверить что нет .env в llm_manager
ls llm_manager/.env
# Должно быть: No such file or directory

# Запустить и проверить переменные в контейнере
docker-compose up -d
docker exec rag_app env | grep PROVIDER
```

## Переменные окружения

### Обязательные:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `PROVIDER` | LLM провайдер | `ollama` |
| `POSTGRES_USER` | Пользователь БД | `rag_user` |
| `POSTGRES_PASSWORD` | Пароль БД | `rag_password` |
| `POSTGRES_DB` | Имя БД | `rag_db` |
| `POSTGRES_HOST` | Хост БД | `postgres` |
| `POSTGRES_PORT` | Порт БД | `5432` |

### Для Ollama:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `OLLAMA_HOST` | URL Ollama сервера | `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | Модель | `llama3` |

### Для OpenAI:

| Переменная | Описание |
|------------|----------|
| `OPENAI_API_KEY` | API ключ OpenAI |

### Для DeepSeek:

| Переменная | Описание |
|------------|----------|
| `DEEPSEEK_API_KEY` | API ключ DeepSeek |

### Для Yandex GPT:

| Переменная | Описание |
|------------|----------|
| `YANDEX_GPT_API_KEY` | API ключ |
| `YANDEX_GPT_FOLDER_ID` | Folder ID |

### Для GigaChat:

| Переменная | Описание |
|------------|----------|
| `GIGA_CHAT_AUTH_KEY` | Auth ключ |

### Дополнительные:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `EMBEDDING_MODEL` | Модель embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Размер фрагмента | `500` |
| `CHUNK_OVERLAP` | Перекрытие фрагментов | `50` |

## Часто задаваемые вопросы

### Q: Нужно ли создавать .env в llm_manager?
**A:** НЕТ! Используется только один `.env` в корне проекта.

### Q: Как llm_manager находит переменные?
**A:** 
- В Docker: через `docker-compose.yml`
- Локально: через `load_dotenv()` в коде

### Q: Можно ли использовать разные провайдеры одновременно?
**A:** Нет, можно выбрать только один провайдер через `PROVIDER`.

### Q: Что делать если переменные не находятся?
**A:** 
1. Проверьте что `.env` существует в корне
2. Проверьте что запускаете из корня проекта
3. В Docker: перезапустите контейнеры

## Безопасность

⚠️ **Важно:**
- `.env` файл уже в `.gitignore`
- Никогда не коммитьте `.env` в git
- Храните API ключи в безопасности
- Используйте сильные пароли для продакшена

## Дополнительная информация

- Подробная документация: `ENV_SETUP.md`
- Быстрый старт: `QUICKSTART.md`
- Установка: `INSTALL.md`

