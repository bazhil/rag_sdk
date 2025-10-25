# 🚀 Быстрый старт RAG SDK

## ✅ Приложение запущено!

Ваше приложение работает на **http://localhost:8000**

## 📝 Что сделать перед использованием

### 1. Установить API ключ GigaChat

Сейчас в `.env` используется placeholder значение. Чтобы чат заработал:

1. **Получите API ключ:**
   - Перейдите на https://developers.sber.ru/portal/products/gigachat
   - Зарегистрируйтесь и создайте проект
   - Скопируйте **Client Secret**

2. **Обновите `.env`:**
   ```bash
   nano .env
   ```
   
   Замените эту строку:
   ```bash
   GIGA_CHAT_AUTH_KEY=your-gigachat-auth-key
   ```
   
   На ваш реальный ключ:
   ```bash
   GIGA_CHAT_AUTH_KEY=ваш-client-secret-здесь
   ```

3. **Перезапустите приложение:**
   ```bash
   docker compose restart app
   ```

### 2. Альтернатива: использовать Ollama (локально, бесплатно)

Если у вас нет ключа GigaChat, можно использовать Ollama:

1. **Установите Ollama:**
   ```bash
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Mac
   brew install ollama
   
   # Windows - скачайте с https://ollama.com/download
   ```

2. **Запустите Ollama:**
   ```bash
   ollama serve
   ```

3. **Скачайте модель:**
   ```bash
   ollama pull llama3
   ```

4. **Обновите `.env`:**
   ```bash
   PROVIDER=ollama
   ```

5. **Перезапустите:**
   ```bash
   docker compose restart app
   ```

## 🎯 Как использовать

### Шаг 1: Откройте приложение
Перейдите на http://localhost:8000

### Шаг 2: Загрузите документ
- Нажмите "Выберите файл"
- Выберите документ (PDF, DOCX, XLSX, TXT, MD, HTML)
- Нажмите "Загрузить"
- Дождитесь обработки

### Шаг 3: Задайте вопрос
- Введите вопрос о документе
- Выберите документ из списка (опционально)
- Нажмите "Отправить"

## 🔍 Проверка состояния

### Проверить, что приложение работает:
```bash
curl http://localhost:8000/health
```

### Посмотреть логи:
```bash
docker logs rag_app
```

### Посмотреть загруженные документы:
```bash
curl http://localhost:8000/api/documents
```

## 📊 Состояние базы данных

PostgreSQL работает на порту **6432** (чтобы не конфликтовать с локальной PostgreSQL).

Подключиться к БД:
```bash
psql -h localhost -p 6432 -U rag_user -d rag_db
# Пароль: rag_password
```

## 🐛 Проблемы?

### Ошибка: "GIGA_CHAT_AUTH_KEY не установлен"
✅ **Решение:** Установите настоящий ключ GigaChat (см. раздел "Установить API ключ") или переключитесь на Ollama

### Порт 8000 занят
✅ **Решение:** Измените порт в `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Вместо 8000:8000
```

### Порт 6432 занят
✅ **Решение:** Измените порт в `docker-compose.yml`:
```yaml
ports:
  - "6433:5432"  # Вместо 6432:5432
```

## 📚 Дополнительная документация

- `GIGACHAT_KEY_SETUP.md` - Подробная инструкция по настройке GigaChat
- `README.md` - Полная документация проекта
- `ARCHITECTURE.md` - Архитектура приложения
- `USAGE.md` - Примеры использования

## 🎉 Готово!

Ваше RAG-приложение готово к работе!

Если вы установили API ключ GigaChat или настроили Ollama - можете начинать задавать вопросы! 🚀

