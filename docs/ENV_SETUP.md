# Настройка переменных окружения

## Как это работает

Проект RAG SDK использует **единый файл `.env`** в корневой директории для всех компонентов:

```
rag_sdk/
├── .env                    # Единственный файл с переменными окружения
├── llm_manager/
│   # НЕТ отдельного .env - использует переменные окружения
```

**Важно:** `llm_manager` НЕ требует отдельного `.env` файла!

## Автоматическая настройка

### Linux/Mac:
```bash
./setup_env.sh
```

### Windows PowerShell:
```powershell
.\start.ps1
```
Скрипт автоматически создаст `.env` и необходимые symlink'и.

## Ручная настройка

Если автоматические скрипты не сработали, настройте вручную:

### 1. Создайте основной .env файл

```bash
cat > .env << 'EOF'
# PostgreSQL
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# LLM Provider
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EOF
```

### 2. Готово!

`llm_manager` автоматически использует переменные окружения:
- **В Docker:** через `docker-compose.yml`
- **Локально:** через `load_dotenv()` находит `.env` в корне проекта

Дополнительная настройка **НЕ требуется**.

## Передача переменных в Docker

В **Docker контейнере** переменные окружения передаются через `docker-compose.yml`:

```yaml
services:
  app:
    environment:
      PROVIDER: ${PROVIDER:-ollama}
      OLLAMA_HOST: ${OLLAMA_HOST:-http://host.docker.internal:11434}
      # и т.д.
```

`docker-compose` автоматически:
1. Читает `.env` файл из корня проекта
2. Подставляет переменные в `environment` секцию
3. Передает их в контейнер как переменные окружения

## Как llm_manager получает переменные

### В Docker контейнере:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из окружения (уже установлены Docker)
provider = os.getenv('PROVIDER')  # Получает значение
```

### При локальной разработке:
```python
load_dotenv()  # Загружает из llm_manager/.env (symlink на ../.env)
provider = os.getenv('PROVIDER')
```

## Структура переменных

### Обязательные переменные:

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `PROVIDER` | LLM провайдер | `ollama` |
| `POSTGRES_*` | Настройки БД | см. `.env` |

### Переменные для разных LLM провайдеров:

#### Ollama (по умолчанию):
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

#### OpenAI:
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

#### DeepSeek:
```env
PROVIDER=deepseek
DEEPSEEK_API_KEY=your-api-key
```

#### Yandex GPT:
```env
PROVIDER=yandex
YANDEX_GPT_API_KEY=your-api-key
YANDEX_GPT_FOLDER_ID=your-folder-id
```

#### GigaChat:
```env
PROVIDER=gigachat
GIGA_CHAT_AUTH_KEY=your-auth-key
```

## Проверка конфигурации

### Проверка .env файлов:
```bash
# Основной .env
cat .env

# Symlink в llm_manager
ls -la llm_manager/.env
cat llm_manager/.env
```

### Проверка в Docker:
```bash
# Запуск контейнера
docker-compose up -d

# Проверка переменных в контейнере
docker exec rag_app env | grep PROVIDER
docker exec rag_app env | grep OLLAMA
```

## Безопасность

### ⚠️ Важно:

1. **Никогда** не добавляйте `.env` в git
2. `.env` уже в `.gitignore`
3. API ключи храните в безопасности
4. Для продакшена используйте секреты (Docker secrets, Kubernetes secrets)

### Проверка что .env не в git:
```bash
git status .env
# Должно быть: nothing to commit
```

## Troubleshooting

### Проблема: "llm_manager не находит переменные"

**Решение:**
```bash
# Проверьте что .env существует в корне
cat .env | grep PROVIDER

# Убедитесь что запускаете из корня проекта
pwd
# Должно быть: /path/to/rag_sdk

# В Docker переменные прокинуты через docker-compose.yml
docker exec rag_app env | grep PROVIDER
```

### Проблема: "PROVIDER not found"

**Решение:**
```bash
# Проверьте что .env существует
cat .env | grep PROVIDER

# Пересоздайте контейнер
docker-compose down
docker-compose up --build
```


## Примеры использования

### Пример 1: Быстрый старт с Ollama

```bash
# 1. Установите Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3
ollama serve &

# 2. Настройте окружение
./setup_env.sh

# 3. Запустите проект
docker-compose up --build
```

### Пример 2: Использование OpenAI

```bash
# 1. Настройте окружение
./setup_env.sh

# 2. Отредактируйте .env
nano .env
# Измените:
# PROVIDER=openai
# OPENAI_API_KEY=sk-your-key

# 3. Запустите проект
docker-compose up --build
```

### Пример 3: Локальная разработка

```bash
# 1. Настройте окружение
./setup_env.sh

# 2. Установите зависимости
pip install -r requirements.txt
pip install -r llm_manager/requirements.txt

# 3. Запустите PostgreSQL в Docker
docker run -d -p 6432:5432 \
  -e POSTGRES_USER=rag_user \
  -e POSTGRES_PASSWORD=rag_password \
  -e POSTGRES_DB=rag_db \
  pgvector/pgvector:pg16

# 4. Обновите .env для локальной разработки
# POSTGRES_HOST=localhost
# POSTGRES_PORT=6432

# 5. Запустите приложение
uvicorn app.main:app --reload
```

## Дополнительная информация

- Документация llm_manager: `llm_manager/README.md`
- Примеры использования: `example_usage.py`
- Установка: `INSTALL.md`

