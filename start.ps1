Write-Host "==================================" -ForegroundColor Cyan
Write-Host "    RAG SDK - Запуск системы    " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker не найден!" -ForegroundColor Red
    Write-Host "Установите Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Проверка Docker..." -ForegroundColor Green
docker --version

if (!(Test-Path ".env")) {
    Write-Host "[WARNING] Файл .env не найден. Создаем файл..." -ForegroundColor Yellow
    $envContent = @"
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

SEARCH_LIMIT=7
MIN_SIMILARITY=0.4
"@
    $envContent | Out-File -FilePath .env -Encoding UTF8
    Write-Host "[INFO] Файл .env создан. Отредактируйте его при необходимости!" -ForegroundColor Yellow
}

# llm_manager использует переменные окружения напрямую
Write-Host "[INFO] llm_manager будет использовать переменные из основного .env" -ForegroundColor Green

Write-Host "[INFO] Запуск Docker Compose..." -ForegroundColor Green
docker compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "   RAG SDK успешно запущен!     " -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Веб-интерфейс: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API документация: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Health check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Для просмотра логов: docker compose logs -f" -ForegroundColor Yellow
    Write-Host "Для остановки: docker compose down" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Ошибка при запуске!" -ForegroundColor Red
    Write-Host "Проверьте логи: docker compose logs" -ForegroundColor Yellow
}

