# Настройка GigaChat для RAG SDK

## Обзор

GigaChat - российская языковая модель от Сбера. Этот гид поможет настроить интеграцию с RAG SDK.

## 🔧 Настройка

### Шаг 1: Получите Auth Key

1. Зарегистрируйтесь на https://developers.sber.ru/gigachat
2. Создайте проект
3. Получите Auth Key (Client Secret)

### Шаг 2: Обновите .env

Откройте файл `.env` и укажите настройки GigaChat:

```env
PROVIDER=gigachat
GIGA_CHAT_AUTH_KEY=ваш-auth-key-здесь
GIGA_CHAT_MODEL=GigaChat
```

### Шаг 3: Запустите проект

```bash
docker-compose up --build
```

## 📊 Поток данных для GigaChat

```
1. .env файл
   ↓
   PROVIDER=gigachat
   GIGA_CHAT_AUTH_KEY=your-key
   GIGA_CHAT_MODEL=GigaChat-2-Lite
   ↓
2. docker-compose.yml читает переменные
   ↓
3. Передает в контейнер как environment
   ↓
4. llm_manager/managers/giga_chat_manager.py
   ↓
   client = GigaChat(
       credentials=os.getenv('GIGA_CHAT_AUTH_KEY'),
       model=os.getenv('GIGA_CHAT_MODEL')  ← GigaChat-2-Lite
   )
   ↓
5. RAGManager вызывает get_response()
   ↓
6. Ответ возвращается пользователю
```

## ✅ Проверка конфигурации

### 1. Проверьте .env файл

```bash
cat .env | grep -A 2 "GigaChat"
```

Должно показать:
```
# --- GigaChat ---
# GIGA_CHAT_AUTH_KEY=your-gigachat-auth-key
GIGA_CHAT_MODEL=GigaChat-2-Lite
```

### 2. Проверьте docker-compose.yml

```bash
grep GIGA_CHAT docker-compose.yml
```

Должно показать:
```
GIGA_CHAT_AUTH_KEY: ${GIGA_CHAT_AUTH_KEY}
GIGA_CHAT_MODEL: ${GIGA_CHAT_MODEL:-GigaChat-2-Lite}
```

### 3. Проверьте что библиотека установлена

```bash
grep gigachat llm_manager/requirements.txt
```

Должно показать:
```
gigachat==0.1.40
```

### 4. Проверьте в контейнере (после запуска)

```bash
docker exec rag_app env | grep GIGA_CHAT
```

Должно показать:
```
GIGA_CHAT_AUTH_KEY=ваш-ключ
GIGA_CHAT_MODEL=GigaChat-2-Lite
```

## 🎯 Полный .env для GigaChat

```env
# PostgreSQL
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# LLM Provider
PROVIDER=gigachat

# GigaChat
GIGA_CHAT_AUTH_KEY=ваш-auth-key-здесь
GIGA_CHAT_MODEL=GigaChat-2-Lite

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

## 🔍 Доступные модели GigaChat

В зависимости от вашего тарифа доступны следующие модели:

| Модель | Описание | Контекст | Область применения |
|--------|----------|----------|-------------------|
| `GigaChat` | Базовая модель | 8K токенов | Общие задачи |
| `GigaChat-Plus` | Расширенная | 32K токенов | Сложные задачи |
| `GigaChat-Pro` | Профессиональная | 32K токенов | Продакшен |

Для смены модели измените значение `GIGA_CHAT_MODEL` в `.env`.

## 🚀 Запуск и тестирование

### 1. Запустите проект

```bash
docker-compose up --build
```

### 2. Откройте веб-интерфейс

http://localhost:8000

### 3. Загрузите тестовый документ

Например, любой PDF или TXT файл

### 4. Задайте вопрос

Система использует GigaChat-2-Lite для генерации ответов на основе загруженных документов.

## 🔧 Параметры GigaChat в коде

В `giga_chat_manager.py` настроены следующие параметры:

```python
response = cls.client.chat(
    Chat(
        messages=[...],
        temperature=0.7,      # Креативность (0.0-1.0)
        max_tokens=1024       # Максимум токенов в ответе
    )
)
```

Эти параметры можно настроить под ваши задачи.

## ⚠️ Важные примечания

1. **verify_ssl_certs=False** - отключена проверка SSL сертификатов (для разработки)
   - Для продакшена рекомендуется `verify_ssl_certs=True`

2. **Auth Key** - храните в безопасности, не коммитьте в git

3. **Лимиты** - GigaChat имеет лимиты по количеству запросов в зависимости от тарифа

4. **Контекст** - GigaChat-2-Lite поддерживает до 8192 токенов контекста

## 🐛 Troubleshooting

### Ошибка: "Invalid credentials"

**Решение:** Проверьте правильность Auth Key
```bash
cat .env | grep GIGA_CHAT_AUTH_KEY
```

### Ошибка: "Model not found"

**Решение:** Проверьте что модель доступна в вашем тарифе
```bash
cat .env | grep GIGA_CHAT_MODEL
```

### Ошибка: "gigachat module not found"

**Решение:** Пересоберите контейнер
```bash
docker-compose down
docker-compose up --build
```

### Медленные ответы

**Решение:** 
- Используйте `GigaChat-2-Lite` (уже настроено)
- Уменьшите `CHUNK_SIZE` и `context_limit` в запросах

## 📚 Дополнительная информация

- Документация GigaChat: https://developers.sber.ru/gigachat
- Примеры использования: https://github.com/ai-forever/gigachat
- Тарифы: https://developers.sber.ru/gigachat/tariffs

## ✅ Итоговый чеклист

Перед запуском проверьте:

- [ ] Получен Auth Key от GigaChat
- [ ] `PROVIDER=gigachat` указан в `.env`
- [ ] `GIGA_CHAT_AUTH_KEY` указан в `.env`
- [ ] `GIGA_CHAT_MODEL` указан в `.env` (опционально)
- [ ] Приложение перезапущено: `docker-compose restart app`

**Готово к работе с GigaChat!**

