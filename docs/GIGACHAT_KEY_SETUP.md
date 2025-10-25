# 🔑 Настройка GigaChat Auth Key

## Проблема

Если вы видите ошибку:
```
Invalid credentials format. Please use only base64 credentials
Can't decode 'Authorization' header
```

Это означает, что `GIGA_CHAT_AUTH_KEY` не установлен или имеет неправильный формат.

## 📋 Как получить правильный ключ

### Шаг 1: Регистрация

1. Перейдите на [GigaChat Developer Portal](https://developers.sber.ru/portal/products/gigachat)
2. Зарегистрируйтесь или войдите

### Шаг 2: Создание проекта

1. Создайте новый проект
2. Выберите нужный тариф:
   - **Физические лица** - бесплатный доступ с ограничениями
   - **Юридические лица** - расширенные возможности

### Шаг 3: Получение Client Secret

1. В настройках проекта найдите раздел **"Авторизационные данные"** или **"Credentials"**
2. Скопируйте **Client Secret** (это будет строка формата `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
3. Это и есть ваш `GIGA_CHAT_AUTH_KEY`

### Шаг 4: Настройка проекта

1. Откройте файл `.env` в корне проекта:
```bash
nano .env
# или
vim .env
```

2. Найдите строку:
```bash
GIGA_CHAT_AUTH_KEY=your-gigachat-auth-key
```

3. Замените на ваш реальный ключ:
```bash
GIGA_CHAT_AUTH_KEY=ваш-client-secret-здесь
```

4. Сохраните файл

### Шаг 5: Перезапуск приложения

```bash
docker compose restart app
```

## 🔍 Проверка настройки

После перезапуска проверьте логи:
```bash
docker logs rag_app 2>&1 | grep -A 5 "GIGACHAT"
```

Вы должны увидеть:
```
GIGACHAT - Initializing client with model: GigaChat-2-Lite
GIGACHAT - Client initialized successfully
```

## 📝 Пример правильного .env

```bash
# GigaChat настройки
PROVIDER=gigachat
GIGA_CHAT_AUTH_KEY=12345678-1234-1234-1234-123456789abc  # Ваш реальный Client Secret
GIGA_CHAT_MODEL=GigaChat-2-Lite
```

## ⚠️ Важно

1. **НЕ** используйте placeholder значения типа `your-gigachat-auth-key`
2. **НЕ** коммитьте `.env` файл в git (он уже в `.gitignore`)
3. Ключ должен быть в формате UUID или специального токена из личного кабинета
4. Проверьте, что у вас есть доступ к модели `GigaChat-2-Lite` в вашем тарифе

## 🐛 Troubleshooting

### Ошибка: "Can't decode 'Authorization' header"

**Причина:** Неправильный формат ключа

**Решение:** 
- Убедитесь, что скопировали **Client Secret** полностью
- Проверьте отсутствие пробелов в начале/конце ключа
- Ключ должен быть из раздела "Авторизационные данные" личного кабинета

### Ошибка: "Invalid credentials format"

**Причина:** Использование placeholder значения

**Решение:** 
- Замените `your-gigachat-auth-key` на реальный ключ
- Перезапустите: `docker compose restart app`

### Ошибка: "Model not available"

**Причина:** Модель недоступна в вашем тарифе

**Решение:** 
- Проверьте доступные модели в личном кабинете
- Измените `GIGA_CHAT_MODEL` на доступную модель
- Доступные модели: `GigaChat`, `GigaChat-Plus`, `GigaChat-Pro`, `GigaChat-2-Lite`

## 📚 Дополнительные ресурсы

- [Официальная документация GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/overview)
- [Python SDK для GigaChat](https://github.com/ai-forever/gigachat)
- [Примеры использования](https://developers.sber.ru/docs/ru/gigachat/examples)

## ✅ Checklist

- [ ] Зарегистрирован на developers.sber.ru
- [ ] Создан проект
- [ ] Получен Client Secret
- [ ] Client Secret добавлен в `.env` как `GIGA_CHAT_AUTH_KEY`
- [ ] Выполнен `docker compose restart app`
- [ ] В логах нет ошибок авторизации
- [ ] Чат работает и отвечает на вопросы

---

После выполнения всех шагов приложение будет готово к работе с GigaChat! 🚀

