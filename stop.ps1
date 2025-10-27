Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   RAG SDK - Остановка системы  " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Остановка контейнеров..." -ForegroundColor Yellow
docker compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "   RAG SDK успешно остановлен   " -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Ошибка при остановке!" -ForegroundColor Red
}

