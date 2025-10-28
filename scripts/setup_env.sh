#!/bin/bash
# Скрипт для автоматической настройки окружения

echo "==================================="
echo "  RAG SDK - Настройка окружения  "
echo "==================================="
echo ""

# Создание .env если не существует
if [ ! -f .env ]; then
    echo "[INFO] Создание файла .env..."
    cat > .env << 'EOF'
# PostgreSQL настройки
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

# Search Settings
SEARCH_LIMIT=7
MIN_SIMILARITY=0.4
EOF
    echo "[✓] Файл .env создан"
else
    echo "[✓] Файл .env уже существует"
fi

# llm_manager использует переменные окружения напрямую
# В Docker они прокинуты через docker compose
# Локально load_dotenv() найдет .env в корне проекта
echo "[INFO] llm_manager будет использовать переменные из основного .env"

# Создание директории uploads
if [ ! -d uploads ]; then
    echo "[INFO] Создание директории uploads..."
    mkdir -p uploads
    touch uploads/.gitkeep
    echo "[✓] Директория uploads создана"
else
    echo "[✓] Директория uploads уже существует"
fi

echo ""
echo "==================================="
echo "   Настройка завершена успешно!  "
echo "==================================="
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте .env для настройки LLM провайдера"
echo "2. Запустите: docker compose up --build"
echo ""

