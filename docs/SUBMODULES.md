# Работа с Git Submodules

Проект RAG использует git submodules для подключения модуля `llm_manager`.

## Автоматическая инициализация

При использовании предоставленных скриптов submodules инициализируются автоматически:

### Linux/Mac:
```bash
./scripts/docker-build.sh   # Автоматически инициализирует submodules и запускает Docker
./scripts/setup_env.sh      # Автоматически инициализирует submodules при настройке
```

### Windows PowerShell:
```powershell
.\scripts\docker-build.ps1  # Автоматически инициализирует submodules и запускает Docker
.\scripts\start.ps1         # Автоматически инициализирует submodules при запуске
```

### Makefile:
```bash
make build      # Автоматически инициализирует submodules перед сборкой
make build-up   # Автоматически инициализирует submodules и запускает с сборкой
make install    # Автоматически инициализирует submodules перед установкой зависимостей
```

## Ручная инициализация

Если вы хотите инициализировать submodules вручную:

### При первом клонировании:
```bash
git clone --recurse-submodules https://github.com/bazhil/RAG.git
```

### Если уже клонировали без submodules:
```bash
git submodule update --init --recursive
```

## Обновление submodules

Для обновления submodules до последней версии:

```bash
git submodule update --remote --recursive
```

## Проверка статуса

Проверить статус submodules:

```bash
git submodule status
```

Вывод должен содержать:
```
 f87ac455854e97553809788936144fb4d1c5827b llm_manager (heads/main)
```

Если перед хешем стоит `-`, значит submodule не инициализирован:
```
-f87ac455854e97553809788936144fb4d1c5827b llm_manager
```

## Устранение проблем

### Проблема: "llm_manager submodule not initialized"

**Решение:**
```bash
git submodule update --init --recursive
```

### Проблема: "fatal: не является репозиторием git"

Это означает, что структура submodule повреждена. **Решение:**

```bash
# Удалить поврежденный submodule
rm -rf llm_manager/.git

# Переинициализировать
git submodule deinit -f llm_manager
git submodule update --init --recursive
```

### Проблема: Docker build падает с ошибкой о llm_manager

**Решение:**

1. Убедитесь, что submodule инициализирован:
```bash
ls -la llm_manager/requirements.txt
```

2. Если файла нет, инициализируйте:
```bash
git submodule update --init --recursive
```

3. Используйте предоставленные скрипты сборки:
```bash
./scripts/docker-build.sh    # Linux/Mac
.\scripts\docker-build.ps1   # Windows
```

## Структура проекта

```
RAG/
├── llm_manager/           # Git submodule
│   ├── __init__.py
│   ├── llm_factory.py
│   └── requirements.txt
├── .gitmodules            # Конфигурация submodules
└── ...
```

## Файл .gitmodules

Содержимое:
```ini
[submodule "llm_manager"]
    path = llm_manager
    url = https://github.com/bazhil/llm_manager.git
```

## Docker и submodules

Dockerfile автоматически проверяет наличие файлов submodule:

```dockerfile
RUN if [ ! -f "llm_manager/requirements.txt" ]; then \
        echo "ERROR: llm_manager submodule not initialized!"; \
        echo "Please run: git submodule update --init --recursive"; \
        exit 1; \
    fi
```

Это гарантирует, что сборка не продолжится без инициализированного submodule.

## Зачем используется submodule?

`llm_manager` - это отдельный модуль, который:
- Управляет различными LLM провайдерами (OpenAI, GigaChat, Ollama и др.)
- Может использоваться независимо в других проектах
- Имеет собственный цикл разработки и версионирование

Использование submodule позволяет:
- Переиспользовать код между проектами
- Обновлять llm_manager независимо от основного проекта
- Поддерживать чистоту истории коммитов

## Дополнительные ресурсы

- [Официальная документация Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [llm_manager репозиторий](https://github.com/bazhil/llm_manager)

