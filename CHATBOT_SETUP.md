# Fliesen Showroom Frankfurt – Chatbot Setup

## Chatbot-System

### Компоненты

1. **ChatConfig (DB)** — Хранит пользовательские инструкции от админа
2. **ChatBotService** — Работает с OpenAI API, генерирует полный промпт
3. **Routes** — HTTP API endpoint `/api/chat` и админ-страницы

### Как работает

1. **Пользователь отправляет сообщение** через чат-виджет на сайте
2. **Фронтенд** отправляет POST запрос на `/api/chat`
3. **Бэкенд**:
   - Получает базовые инструкции (встроены в код)
   - Получает пользовательские инструкции из БД (ChatConfig)
   - Отправляет оба набора в OpenAI
4. **OpenAI** генерирует ответ на основе полного промпта
5. **Ответ** логируется в БД и отправляется пользователю

### Базовые (встроенные) инструкции

Находятся в `app/services/chat_service.py`:
- Идентичность: "Kundenservice-Assistent für einen Fliesen Showroom in Frankfurt"
- Информация о компании: адрес, телефон, e-mail, время работы
- Основные задачи: консультации, терминология
- Поведение: вежливость, краткость, ответ на языке запроса

### Пользовательские инструкции

Админ может добавить дополнительные инструкции через страницу `/admin/chatbot`:

**Примеры:**
```
- При вопросах о цене: упомянуть, что консультация бесплатна
- Текущая акция: 15% скидка на коллекцию "Marmor Deluxe"
- Часто спрашивают про гарантию: всегда напомнить о 2-летней гарантии
- Если клиент спрашивает про дизайн: рекомендовать визит в showroom
```

## OpenAI API Setup

### 1. Получить API ключ

1. Перейти на https://platform.openai.com/api-keys
2. Создать новый Secret Key
3. Скопировать ключ (больше не будет виден)

### 2. Добавить в `.env`

```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Установить пакет openai

```bash
pip install openai==1.3.9
```

Или через requirements.txt (уже добавлено):
```bash
pip install -r requirements.txt
```

## Admin Pages

### `/admin/chatbot`
- Просмотр базовых инструкций
- Редактирование пользовательских инструкций
- Сохраняется в таблицу `chat_config`

### `/admin/chat-history`
- Смотреть всё история чат-запросов
- Просмотр пользовательских сообщений и ответов бота
- Пагинация по 20 на странице

## Chat Widget Frontend

Виджет находится в [static/js/chat.js](app/static/js/chat.js):

```javascript
// Отправка сообщения
fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userText })
})
.then(res => res.json())
.then(data => displayBotMessage(data.response))
```

## Fallback (когда API недоступен)

Если OpenAI API не сконфигурирован или произошла ошибка, чатбот вернёт:

```
"Vielen Dank für Ihre Anfrage! Leider kann unser Chat gerade keine KI-gestützte Antwort
generieren. Bitte kontaktieren Sie uns direkt: +49 69 123 456 78 oder
info@fliesen-showroom.de. Wir helfen Ihnen gerne weiter!"
```

## Тестирование

### Без OpenAI API (mock responses)

1. Не заполнять `OPENAI_API_KEY` в `.env`
2. Чатбот будет возвращать fallback сообщение
3. Все сообщения всё равно логируются в БД

### С OpenAI API

1. Убедиться, что `OPENAI_API_KEY` правильный в `.env`
2. Тестовое сообщение: откройте чат на http://127.0.0.1:5000/
3. Проверить ответ и логи в `/admin/chat-history`

## Затраты на OpenAI

- **gpt-3.5-turbo**: примерно $0.002 за 1K входящих токенов, $0.004 за 1K исходящих
- Типичный чат-запрос: 200-400 токенов
- Стоимость ~$0.01 за запрос в среднем
- Мониторить использование на https://platform.openai.com/account/billing/overview

## Структура файлов

```
app/
├── services/
│   ├── __init__.py
│   └── chat_service.py          # ChatBotService, get_chat_service()
├── templates/admin/
│   ├── chatbot.html             # Управление инструкциями
│   └── chat_history.html        # История чатов
├── models.py                    # ChatConfig модель
└── routes.py                    # /api/chat endpoint, админ-роуты
```

## Развитие функционала

Возможные улучшения:
- [ ] Интеграция с контекстом (документы о коллекциях)
- [ ] RAG (Retrieval-Augmented Generation) — подсказки из БД
- [ ] Многоязычность (EN, FR, IT)
- [ ] Analytics: популярные вопросы, sentiment анализ
- [ ] Интеграция с CRM для сохранения контактов
- [ ] Rate limiting, spam protection
- [ ] A/B тестирование разных инструкций
