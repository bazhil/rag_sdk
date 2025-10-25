# Диагностика ошибки загрузки файлов

## Проблема
После загрузки файла отображается "Нет загруженных документов"

## Причина
HTTP 500 ошибка при загрузке файла через `/api/upload`

## Диагностика

### 1. Проверка БД
```bash
# Таблицы созданы
docker exec rag_postgres psql -U rag_user -d rag_db -c "\dt"
# ✅ Таблицы documents и chunks существуют

# Но данных нет
docker exec rag_postgres psql -U rag_user -d rag_db -c "SELECT * FROM documents;"
# (0 rows) - файл не сохранился
```

### 2. Получение детальных логов

**Я добавил детальное логирование в код**, теперь нужно:

```bash
# 1. Пересобрать контейнер с новым кодом
docker-compose up --build -d

# 2. Следить за логами в реальном времени
docker logs -f rag_app

# 3. В браузере загрузить файл снова

# 4. В логах вы увидите полный traceback ошибки
```

## Возможные причины ошибки 500:

### 1. Проблема с подключением к БД
Если в логах увидите:
```
password authentication failed for user "mosaic"
```

**Решение:**
```bash
# Полностью очистить и пересоздать
docker-compose down -v
docker volume rm rag_sdk_postgres_data
docker-compose up --build
```

### 2. Проблема с embeddings моделью
Если в логах:
```
Error loading sentence-transformers model
```

**Решение:**
```bash
# Модель загружается при первом использовании
# Дождитесь завершения загрузки (~90MB)
```

### 3. Проблема с обработкой файла
Если ошибка связана с чтением файла:
```bash
# Проверить что файл сохранен
docker exec rag_app ls -la /app/uploads/
```

## Быстрое тестирование

```bash
# 1. Пересобрать
docker-compose down
docker-compose up --build -d

# 2. Проверить логи при старте
docker logs rag_app

# Должно быть:
# INFO:     Application startup complete.
# ✅ Без ошибок

# 3. Следить за логами
docker logs -f rag_app

# 4. Загрузить тестовый текстовый файл
echo "Test document content" > test.txt
# Загрузите через веб-интерфейс

# 5. В логах увидите либо:
# - Success: document_id
# - Или детальный traceback ошибки
```

## Проверка после исправления

```bash
# Проверить что документ добавился в БД
docker exec rag_postgres psql -U rag_user -d rag_db -c "SELECT id, filename FROM documents;"

# Должно показать загруженный файл
```

## Команды для получения логов

```bash
# Все логи app
docker logs rag_app

# Последние 50 строк
docker logs rag_app --tail 50

# В реальном времени
docker logs -f rag_app

# Только ошибки
docker logs rag_app 2>&1 | grep -i error

# С временными метками
docker logs -t rag_app
```

## Следующие шаги

1. ✅ Код обновлен с детальным логированием
2. ⏳ Пересоберите контейнер: `docker-compose up --build -d`
3. ⏳ Загрузите файл снова
4. ⏳ Посмотрите логи: `docker logs rag_app`
5. ⏳ Отправьте мне traceback из логов

После этого я смогу точно определить причину и исправить!

