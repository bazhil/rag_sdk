#!/bin/bash

echo "================================================"
echo "  RAG SDK - Docker Build with Submodules"
echo "================================================"
echo ""

echo "[INFO] Проверка и инициализация submodules..."
if [ ! -f "llm_manager/requirements.txt" ]; then
    echo "[INFO] Submodule llm_manager не инициализирован. Инициализация..."
    git submodule update --init --recursive
    if [ $? -eq 0 ]; then
        echo "[✓] Submodules успешно инициализированы"
    else
        echo "[ERROR] Ошибка при инициализации submodules!"
        exit 1
    fi
else
    echo "[✓] Submodule llm_manager уже инициализирован"
fi

echo ""
echo "[INFO] Запуск Docker Compose..."
docker compose up --build "$@"

