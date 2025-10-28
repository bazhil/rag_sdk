# Шаблон файла .env

Скопируйте содержимое в файл `.env` в корне проекта.

## Полный шаблон .env

```env
# ===============================
# PostgreSQL Database Settings
# ===============================
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# ===============================
# LLM Provider Settings
# ===============================
# Выберите провайдер: ollama / openai / deepseek / yandex / gigachat
PROVIDER=ollama

# ===============================
# Ollama Settings
# ===============================
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# ===============================
# OpenAI Settings
# ===============================
# OPENAI_API_KEY=sk-your-api-key-here
# OPENAI_MODEL=gpt-4o-mini

# ===============================
# DeepSeek Settings
# ===============================
# DEEPSEEK_API_KEY=your-api-key-here

# ===============================
# Yandex GPT Settings
# ===============================
# YANDEX_GPT_API_KEY=your-api-key-here
# YANDEX_GPT_FOLDER_ID=your-folder-id-here

# ===============================
# GigaChat Settings
# ===============================
# GIGA_CHAT_AUTH_KEY=your-auth-key-here
# GIGA_CHAT_MODEL=GigaChat-2

# ===============================
# Embeddings Settings
# ===============================
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# ===============================
# Search Settings
# ===============================
SEARCH_LIMIT=7
MIN_SIMILARITY=0.4
```

## Описание параметров

### PostgreSQL
- `POSTGRES_USER` - имя пользователя БД
- `POSTGRES_PASSWORD` - пароль БД
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_HOST` - хост БД (`postgres` для Docker, `localhost` для локального запуска)
- `POSTGRES_PORT` - порт БД (5432 внутри Docker, 6432 снаружи)

### LLM Provider
- `PROVIDER` - выбранный провайдер LLM

### Embeddings
- `EMBEDDING_MODEL` - модель для векторизации текста
- `CHUNK_SIZE` - размер фрагмента текста в символах
- `CHUNK_OVERLAP` - размер перекрытия между фрагментами в символах

### Search
- `SEARCH_LIMIT` - максимальное количество возвращаемых результатов поиска
- `MIN_SIMILARITY` - минимальный порог схожести (0.0-1.0) для фильтрации результатов

## Быстрый старт

### Для Ollama (локальный):
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

### Для OpenAI:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

### Для GigaChat:
```env
PROVIDER=gigachat
GIGA_CHAT_AUTH_KEY=your-key
GIGA_CHAT_MODEL=GigaChat-2
```

## Создание файла

### Linux/Mac:
```bash
./scripts/setup_env.sh
```

### Windows PowerShell:
```powershell
.\scripts\start.ps1
```

### Вручную:
```bash
# Скопируйте шаблон выше в файл .env
nano .env
# или
vim .env
```

## Проверка конфигурации

После создания файла `.env` проверьте, что переменные загружены:

```bash
# Запустите приложение
docker compose up

# В логах вы увидите:
# ============================================================
# RAG_SDK CONFIG - Settings loaded:
# PROVIDER: ollama
# CHUNK_SIZE: 500
# CHUNK_OVERLAP: 50
# SEARCH_LIMIT: 7
# MIN_SIMILARITY: 0.4
# ...
# ============================================================
```

## Дополнительная информация

- [Настройка переменных окружения](ENV_SETUP.md) - подробное руководство
- [Быстрый старт](QUICKSTART.md) - начните работу за 5 минут
- [Настройка GigaChat](GIGACHAT_SETUP.md) - интеграция с GigaChat

