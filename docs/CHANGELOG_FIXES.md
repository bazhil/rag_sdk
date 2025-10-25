# 🔧 Журнал исправлений

## Исправления от 25.10.2025

### ✅ Исправленные проблемы

#### 1. **Ошибка инициализации LLM менеджеров при импорте**

**Проблема:**
```
The api_key client option must be set either by passing api_key to the client 
or by setting the OPENAI_API_KEY environment variable
```

**Причина:** 
Все LLM менеджеры (DeepSeek, OpenAI, Ollama, YandexGPT) создавали клиенты на уровне класса с пустыми API ключами, что вызывало ошибки при импорте модулей.

**Решение:**
- Реализована **ленивая инициализация (lazy initialization)** для всех менеджеров
- Клиенты создаются только при первом вызове `get_response()`
- Добавлены проверки наличия обязательных переменных окружения

**Изменённые файлы:**
- `llm_manager/managers/deepseek_manager.py`
- `llm_manager/managers/open_ai_manager.py`
- `llm_manager/managers/ollama_manager.py`
- `llm_manager/managers/yandex_gpt_manager.py`
- `llm_manager/managers/giga_chat_manager.py`

#### 2. **Вложенные исключения в GigaChatManager**

**Проблема:**
```
ValueError: Неожиданная ошибка инициализации GigaChat: GIGA_CHAT_AUTH_KEY не установлен...
During handling of the above exception, another exception occurred:
ValueError: GIGA_CHAT_AUTH_KEY не установлен...
```

**Причина:**
`ValueError` (для placeholder ключа) ловился блоком `except Exception`, создавая вложенное исключение.

**Решение:**
Добавлен отдельный блок `except ValueError` перед `except Exception`, чтобы ValueError проходили напрямую.

**Изменённые файлы:**
- `llm_manager/managers/giga_chat_manager.py`

#### 3. **Конфигурация docker-compose.yml**

**Проблема:**
- Дефолтные значения в `docker-compose.yml` перезаписывали значения из `.env`
- `.env` не был явно указан как источник переменных

**Решение:**
- Добавлена директива `env_file: .env` для обоих сервисов
- Убраны все дефолтные значения (`:-default`)
- Оставлены только Docker-специфичные переменные (`POSTGRES_HOST`, `POSTGRES_PORT`, `PYTHONUNBUFFERED`)

**Изменённые файлы:**
- `docker-compose.yml`

#### 4. **Модель GigaChat**

**Проблема:**
Использовалась `GigaChat-2-Lite`, но пользователь хотел `GigaChat-2`.

**Решение:**
Обновлена модель на `GigaChat-2` во всех местах:
- `.env`: `GIGA_CHAT_MODEL=GigaChat-2`
- `rag_sdk/config.py`: дефолт `"GigaChat-2"`
- `docker-compose.yml`: дефолт `GigaChat-2`

**Изменённые файлы:**
- `.env`
- `rag_sdk/config.py`
- `docker-compose.yml`

### 📝 Добавленная документация

1. **GIGACHAT_KEY_SETUP.md** - Подробная инструкция по настройке GigaChat API ключа
2. **QUICK_START.md** - Краткое руководство для быстрого старта
3. **CHANGELOG_FIXES.md** - Этот файл с описанием исправлений

### 🎯 Текущее состояние

#### ✅ Что работает:
- Приложение запускается без ошибок
- Все переменные окружения корректно загружаются из `.env`
- PostgreSQL работает на порту 6432
- Загрузка документов работает
- Векторное хранилище (pgvector) работает
- Embedding модели загружаются и кешируются

#### ⚠️ Требует настройки:
- **GigaChat API ключ** - необходимо установить настоящий ключ вместо placeholder
  - Альтернатива: переключиться на Ollama (локальный, бесплатный)

#### 🔧 Архитектурные улучшения:
1. **Ленивая инициализация** - клиенты LLM создаются только при необходимости
2. **Единая точка конфигурации** - `.env` файл как единственный источник настроек
3. **Улучшенная обработка ошибок** - понятные сообщения об ошибках конфигурации
4. **Отключение буферизации** - `PYTHONUNBUFFERED=1` для немедленного вывода логов

### 🚀 Следующие шаги для пользователя

1. **Установить API ключ GigaChat** (см. `GIGACHAT_KEY_SETUP.md`)
   ```bash
   # Отредактировать .env
   nano .env
   
   # Установить реальный ключ
   GIGA_CHAT_AUTH_KEY=ваш-client-secret
   
   # Перезапустить
   docker compose restart app
   ```

2. **Или переключиться на Ollama** (см. `QUICK_START.md`)
   ```bash
   # Установить и запустить Ollama
   ollama serve
   ollama pull llama3
   
   # Изменить провайдер в .env
   PROVIDER=ollama
   
   # Перезапустить
   docker compose restart app
   ```

### 📊 Структура исправлений

```
Исправления
├── Критические (блокировали работу)
│   ├── ✅ Инициализация LLM менеджеров
│   └── ✅ Конфигурация docker-compose
│
├── Важные (улучшали UX)
│   ├── ✅ Вложенные исключения
│   ├── ✅ Модель GigaChat
│   └── ✅ Логирование настроек
│
└── Документация
    ├── ✅ GIGACHAT_KEY_SETUP.md
    ├── ✅ QUICK_START.md
    └── ✅ CHANGELOG_FIXES.md
```

---

**Дата:** 25 октября 2025  
**Статус:** ✅ Все критические ошибки исправлены  
**Приложение:** Готово к работе после настройки API ключа

