# Docker Compose с Ollama

Проект включает два варианта Docker Compose файлов для работы с Ollama:

1. **docker-compose.ollama-container.yml** - Ollama запускается в Docker контейнере
2. **docker-compose.ollama-local.yml** - Ollama запущена локально на хост-машине

## Вариант 1: Ollama в контейнере

### Настройка .env

Добавьте в файл `.env`:

```env
PROVIDER=ollama
OLLAMA_MODEL=llama3
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
```

### Запуск

```bash
docker compose -f docker-compose.ollama-container.yml up -d --build
```

### Загрузка модели в Ollama

После запуска контейнера необходимо загрузить модель:

```bash
docker exec -it rag_ollama ollama pull llama3
```

Или другую модель:

```bash
docker exec -it rag_ollama ollama pull mistral
docker exec -it rag_ollama ollama pull codellama
```

### Проверка статуса

```bash
docker compose -f docker-compose.ollama-container.yml ps
```

### Остановка

```bash
docker compose -f docker-compose.ollama-container.yml down
```

### Полная очистка (включая данные)

```bash
docker compose -f docker-compose.ollama-container.yml down -v
```

### Просмотр логов

```bash
docker compose -f docker-compose.ollama-container.yml logs -f
```

Логи конкретного сервиса:

```bash
docker compose -f docker-compose.ollama-container.yml logs -f ollama
docker compose -f docker-compose.ollama-container.yml logs -f app
```

## Вариант 2: Ollama запущена локально

### Предварительные требования

Установите Ollama на хост-машину:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Загрузите нужную модель:

```bash
ollama pull llama3
```

Запустите Ollama:

```bash
ollama serve
```

### Настройка .env

Добавьте в файл `.env`:

```env
PROVIDER=ollama
OLLAMA_MODEL=llama3
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
```

### Запуск

```bash
docker compose -f docker-compose.ollama-local.yml up -d --build
```

### Проверка статуса

```bash
docker compose -f docker-compose.ollama-local.yml ps
```

### Остановка

```bash
docker compose -f docker-compose.ollama-local.yml down
```

### Полная очистка (включая данные)

```bash
docker compose -f docker-compose.ollama-local.yml down -v
```

### Просмотр логов

```bash
docker compose -f docker-compose.ollama-local.yml logs -f app
```

## Поддержка GPU

В варианте с контейнером (docker-compose.ollama-container.yml) уже настроена поддержка GPU через NVIDIA Docker.

### Предварительные требования для GPU

Установите NVIDIA Container Toolkit:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Проверьте доступность GPU:

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Полезные команды

### Проверка доступности Ollama

Из контейнера приложения:

```bash
docker exec -it rag_app curl http://ollama:11434
```

Из хост-машины (для варианта с контейнером):

```bash
curl http://localhost:11434
```

### Список загруженных моделей

```bash
docker exec -it rag_ollama ollama list
```

### Тестирование модели

```bash
docker exec -it rag_ollama ollama run llama3 "Hello, how are you?"
```

### Удаление модели

```bash
docker exec -it rag_ollama ollama rm llama3
```

## Доступные модели Ollama

Популярные модели для RAG систем:

- `llama3` - универсальная модель от Meta
- `mistral` - быстрая и эффективная модель
- `mixtral` - модель с mixture-of-experts архитектурой
- `gemma` - модель от Google
- `phi3` - компактная модель от Microsoft
- `qwen` - модель от Alibaba
- `codellama` - специализированная модель для кода

Полный список: https://ollama.com/library

## Troubleshooting

### Ollama не отвечает

Проверьте статус контейнера:

```bash
docker compose -f docker-compose.ollama-container.yml ps
docker compose -f docker-compose.ollama-container.yml logs ollama
```

### Модель не загружается

Проверьте свободное место на диске:

```bash
df -h
```

Модели занимают от 4 до 40 GB в зависимости от размера.

### Медленная работа

Для ускорения работы:
1. Используйте GPU (вариант с контейнером)
2. Выберите более легкую модель (phi3, gemma)
3. Увеличьте выделенную память для Docker

### Приложение не видит Ollama

Для варианта с локальной Ollama убедитесь, что:
- Ollama запущена на хосте: `ollama serve`
- Порт 11434 доступен
- В .env указан правильный адрес

