Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  RAG SDK - Docker Build with Submodules" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Проверка и инициализация submodules..." -ForegroundColor Green
if (!(Test-Path "llm_manager/requirements.txt")) {
    Write-Host "[INFO] Submodule llm_manager не инициализирован. Инициализация..." -ForegroundColor Yellow
    git submodule update --init --recursive
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Submodules успешно инициализированы" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Ошибка при инициализации submodules!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Submodule llm_manager уже инициализирован" -ForegroundColor Green
}

Write-Host ""
Write-Host "[INFO] Запуск Docker Compose..." -ForegroundColor Green
docker compose up --build $args

