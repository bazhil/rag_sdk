# Установка и запуск на Windows

> **Примечание:** PostgreSQL использует порт **6432** вместо стандартного 5432, чтобы не конфликтовать с локально установленным PostgreSQL.

## Предварительные требования

1. **Docker Desktop для Windows**
   - Скачайте: https://www.docker.com/products/docker-desktop
   - Установите и запустите
   - Убедитесь, что WSL 2 включен

2. **Git для Windows**
   - Скачайте: https://git-scm.com/download/win
   - Установите с настройками по умолчанию

3. **Опционально: Python 3.11+**
   - Только для локальной разработки
   - Скачайте: https://www.python.org/downloads/

## Быстрый старт

### 1. Клонирование репозитория

Откройте PowerShell:

```powershell
git clone --recurse-submodules <repository-url>
cd rag_sdk
```

### 2. Настройка переменных окружения

Создайте файл `.env` из примера:

```powershell
Copy-Item .env.example .env
```

Отредактируйте `.env` в любом текстовом редакторе (Notepad, VS Code):

**Для Ollama (локально):**
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

**Для OpenAI:**
```env
PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
```

### 3. Запуск через Docker

```powershell
docker compose up --build
```

### 4. Открытие веб-интерфейса

Откройте браузер и перейдите на: http://localhost:8000

## Установка Ollama на Windows (опционально)

Если хотите использовать локальную LLM:

1. Скачайте Ollama: https://ollama.ai/download
2. Установите
3. Откройте PowerShell и запустите:

```powershell
ollama pull llama3
ollama serve
```

В `.env` укажите:
```env
PROVIDER=ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

## Команды для управления

### Запуск

```powershell
docker compose up -d
```

### Остановка

```powershell
docker compose down
```

### Просмотр логов

```powershell
docker compose logs -f
```

### Перезапуск

```powershell
docker compose restart
```

### Очистка всех данных

```powershell
docker compose down -v
Remove-Item -Recurse -Force uploads\*
```

### Проверка состояния

```powershell
docker compose ps
```

## Локальная разработка на Windows

### 1. Установка Python зависимостей

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r llm_manager\requirements.txt
```

Если возникает ошибка с политикой выполнения:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Запуск PostgreSQL через Docker

```powershell
docker run -d `
  --name rag_postgres `
  -e POSTGRES_USER=rag_user `
  -e POSTGRES_PASSWORD=rag_password `
  -e POSTGRES_DB=rag_db `
  -p 6432:5432 `
  pgvector/pgvector:pg16
```

### 3. Инициализация базы данных

```powershell
docker exec -i rag_postgres psql -U rag_user -d rag_db -f init.sql
```

Или, если PostgreSQL установлен локально:

```powershell
psql -h localhost -U rag_user -d rag_db -f init.sql
```

### 4. Запуск приложения

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Загрузка документов через PowerShell

### Загрузить файл

```powershell
$file = Get-Item "C:\path\to\document.pdf"
$uri = "http://localhost:8000/api/upload"

$formData = @{
    file = $file
}

Invoke-RestMethod -Uri $uri -Method Post -Form $formData
```

### Получить список документов

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/documents"
```

### Задать вопрос

```powershell
$body = @{
    query = "Что такое машинное обучение?"
    context_limit = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/chat" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## Использование в Python на Windows

```python
import asyncio
from rag_sdk import RAGManager

async def main():
    rag = RAGManager()
    await rag.initialize()
    
    # Путь в Windows формате
    doc_id = await rag.add_document(
        file_path=r"C:\Users\User\Documents\book.pdf",
        filename="book.pdf"
    )
    
    result = await rag.generate_answer("О чем эта книга?")
    print(result['answer'])
    
    await rag.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Решение проблем на Windows

### Docker не запускается

1. Убедитесь, что WSL 2 установлен:
```powershell
wsl --list --verbose
```

2. Обновите WSL:
```powershell
wsl --update
```

3. Включите виртуализацию в BIOS (Intel VT-x или AMD-V)

### Ошибка "no space left on device"

Очистите Docker:

```powershell
docker system prune -a -f
docker volume prune -f
```

### Ошибка с правами доступа к файлам

Запустите PowerShell от имени администратора:

```powershell
Start-Process powershell -Verb runAs
```

### Ollama не подключается из Docker

В `.env` используйте:
```env
OLLAMA_HOST=http://host.docker.internal:11434
```

Убедитесь, что Ollama запущен в фоне.

### Проблемы с кодировкой файлов

В PowerShell установите UTF-8:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

### Ошибка подключения к PostgreSQL

Проверьте, что контейнер запущен:

```powershell
docker ps | Select-String postgres
```

Проверьте логи:

```powershell
docker logs rag_postgres
```

## Производительность на Windows

### Рекомендации:

1. **Используйте WSL 2** вместо Hyper-V для Docker
2. **Выделите больше памяти** Docker Desktop (Settings → Resources)
3. **Храните проект на диске WSL** для лучшей производительности:
   ```powershell
   wsl
   cd ~
   git clone --recurse-submodules <repository-url>
   ```

### Оптимальные настройки Docker Desktop:

- CPU: 4+ ядра
- Memory: 4+ GB
- Swap: 2 GB
- Disk: 20+ GB

## Работа с файлами Windows в WSL

Доступ к дискам Windows из WSL:

```bash
# В WSL
cd /mnt/c/Users/YourName/Documents
```

Доступ к файлам WSL из Windows:

```
\\wsl$\Ubuntu\home\username\rag_sdk
```

## Антивирус и брандмауэр

Если антивирус блокирует Docker:

1. Добавьте Docker в исключения
2. Добавьте директорию проекта в исключения
3. Разрешите Docker в брандмауэре Windows

## PowerShell скрипты

### Автоматический запуск (start.ps1)

```powershell
Write-Host "Запуск RAG SDK..." -ForegroundColor Green

# Проверка Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker не найден! Установите Docker Desktop." -ForegroundColor Red
    exit 1
}

# Запуск
docker compose up -d

Write-Host "RAG SDK запущен!" -ForegroundColor Green
Write-Host "Откройте http://localhost:8000" -ForegroundColor Cyan
```

### Остановка (stop.ps1)

```powershell
Write-Host "Остановка RAG SDK..." -ForegroundColor Yellow
docker compose down
Write-Host "RAG SDK остановлен." -ForegroundColor Green
```

Запуск скриптов:

```powershell
.\start.ps1
.\stop.ps1
```

## Visual Studio Code

### Рекомендуемые расширения:

- Python
- Docker
- Remote - WSL
- Remote - Containers
- PostgreSQL

### Открытие проекта в WSL:

1. Установите "Remote - WSL" расширение
2. Откройте VSCode
3. Нажмите F1
4. Выберите "WSL: Open Folder in WSL"
5. Выберите папку проекта

## Дополнительные ресурсы

- Docker Desktop документация: https://docs.docker.com/desktop/windows/
- WSL документация: https://docs.microsoft.com/windows/wsl/
- Python на Windows: https://docs.python.org/3/using/windows.html
- PowerShell документация: https://docs.microsoft.com/powershell/

