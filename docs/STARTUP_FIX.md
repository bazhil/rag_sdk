# Исправление ошибки при запуске БД

## Проблема

Ошибка при запуске:
```
FATAL: database "rag_user" does not exist
```

## Причина

PostgreSQL пытается подключиться к БД с именем пользователя вместо имени базы данных.

## Решение

### ✅ Уже исправлено:

1. **Healthcheck обновлен** в `docker-compose.yml`:
   ```yaml
   healthcheck:
     test: ["CMD-SHELL", "pg_isready -U rag_user -d rag_db"]
   ```

2. **init.sql корректен** - создает правильную БД

### 🔧 Команды для исправления:

```bash
# 1. Остановить и удалить старые контейнеры и volumes
docker-compose down -v

# 2. Убедиться что удалены volumes
docker volume ls | grep rag_sdk

# 3. Запустить заново
docker-compose up --build
```

### Если проблема сохраняется:

```bash
# Полная очистка
docker-compose down -v
docker volume rm rag_sdk_postgres_data 2>/dev/null || true
docker volume rm rag_sdk_model_cache 2>/dev/null || true

# Запуск
docker-compose up --build
```

## Проверка после запуска

```bash
# Проверить что БД создалась
docker exec rag_postgres psql -U rag_user -d rag_db -c "\l"

# Должно показать:
# rag_db | rag_user | ...
```

## Если нужно пересоздать БД вручную

```bash
# Войти в контейнер
docker exec -it rag_postgres psql -U rag_user -d postgres

# В psql:
CREATE DATABASE rag_db;
\q

# Инициализировать таблицы
docker exec -i rag_postgres psql -U rag_user -d rag_db < init.sql
```

