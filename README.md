# 🤖 КОКЦ Telegram Bot - README

Документация для системы автоматизации кадастрового центра в Telegram

## 📋 Оглавление

- [Описание проекта](#описание-проекта)
- [Архитектура](#архитектура)
- [Установка и настройка](#установка-и-настройка)
- [Конфигурация](#конфигурация)
- [Модули](#модули)
- [База данных](#база-данных)
- [Функциональность](#функциональность)
- [Запуск](#запуск)
- [Устранение неполадок](#устранение-неполадок)

## 🎯 Описание проекта

Система представляет собой интеллектуального Telegram-бота для ООО "Кемеровский Областной Кадастровый Центр" (ООО "КОКЦ"). Бот автоматизирует общение с клиентами, используя AI (Groq API) для генерации ответов, и предоставляет админ-панель для управления.

### Основные возможности

- ✅ Автоматические ответы на вопросы клиентов через нейросеть
- 📋 Готовые ответы на часто задаваемые вопросы (кнопки)
- 👨‍💼 Переключение на живого менеджера при необходимости
- 📊 Админ-панель для просмотра статистики и диалогов
- 💾 Сохранение всех диалогов в базу данных
- 🔍 Поиск по истории сообщений

## 🏗 Архитектура

```
project/
├── bot/
│   ├── userbot_telethon.py    # Основной бот
│   ├── admin_panel.py          # Flask админ-панель
│   ├── KOKC.db                 # SQLite база данных
│   └── message_map.json        # Карта сообщений
├── database/
│   └── connection.py           # Класс для работы с БД
└── .env                        # Конфигурация
```

### Компоненты

1. **Telegram Bot (userbot_telethon.py)**
   - Обрабатывает входящие сообщения
   - Генерирует ответы через Groq API
   - Перенаправляет запросы менеджеру

2. **Админ-панель (admin_panel.py)**
   - Flask веб-интерфейс
   - Просмотр всех диалогов
   - Статистика активности

3. **База данных (connection.py)**
   - SQLite с тремя таблицами
   - ORM-подобный интерфейс

## 🚀 Установка и настройка

### Требования

- Python 3.8+
- Telegram аккаунт для бота
- API ключ Groq
- Прокси сервер (опционально)

### Шаг 1: Клонирование и установка зависимостей

```bash
# Клонируем репозиторий
git clone <repository-url>
cd project

# Устанавливаем зависимости
pip install telethon groq python-dotenv flask jwt pymorphy3
```

### Шаг 2: Настройка .env файла

Создайте файл `.env` в корне проекта:

```env
# Telegram API
TG_API_ID=1234567
TG_API_HASH=your_api_hash_here

# Groq AI
GROK_TOKEN=gsk_your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b

# Менеджер
MANAGER_CHAT_ID=123456789  # ID чата менеджера

# Прокси (опционально)
PROXY_HOST=wsip-98-175-31-195.hr.hr.cox.net
PROXY_PORT=4145

# Админ-панель
PASSWORD=your_secure_password
LIVE_TOKEN=your_jwt_secret_key

# Бан-лист
BAN_LIST=["123456789", "987654321"]
```

### Шаг 3: Получение API ключей

#### Telegram API
1. Перейдите на https://my.telegram.org
2. Войдите в аккаунт
3. Создайте приложение
4. Скопируйте `api_id` и `api_hash`

#### Groq API
1. Зарегистрируйтесь на https://console.groq.com
2. Создайте API ключ
3. Скопируйте ключ в `GROK_TOKEN`

## ⚙️ Конфигурация

### Основные параметры

| Переменная | Описание | Пример |
|------------|----------|---------|
| `TG_API_ID` | ID приложения Telegram | `1234567` |
| `TG_API_HASH` | Хеш приложения Telegram | `"abc123..."` |
| `GROK_TOKEN` | API ключ Groq | `"gsk_..."` |
| `MANAGER_CHAT_ID` | ID чата менеджера | `123456789` |
| `PASSWORD` | Пароль админ-панели | `"admin123"` |

### Готовые ответы кнопок

```python
BUTTON_RESPONSES = {
    "Услуги": "Наши услуги: ...",
    "Кадастровая стоимость": "Для получения...",
    "Документы": "Основные документы: ...",
    # и т.д.
}
```

### System Prompt для AI

Бот использует детальный system prompt, который:
- Определяет роль бота (официальный помощник КОКЦ)
- Содержит базу знаний компании
- Устанавливает правила общения
- Запрещает выдумывать цены и обещать результаты

## 📦 Модули

### 1. Database (`database/connection.py`)

Класс для работы с SQLite:

```python
class Database:
    def save_or_update_user(user_id, username, first_name, last_name)
    def save_message(user_id, question, answer)
    def save_manager_request(user_id, question)
    def get_user_messages(user_id)
    def get_all_users()
    def get_all_messages()
```

### 2. Userbot (`userbot_telethon.py`)

Основные обработчики:

```python
@tg_client.on(events.NewMessage(pattern='/start'))
async def start_message(event)  # Приветствие и регистрация

@tg_client.on(events.NewMessage)
async def answer(event)  # Основной обработчик с AI

async def connect_to_manager(event)  # Переключение на менеджера

@tg_client.on(events.NewMessage)
async def manager_reply(event)  # Ответ менеджера клиенту
```

### 3. Admin Panel (`admin_panel.py`)

Flask маршруты:

```python
@app.route('/auth')  # Авторизация
@app.route('/')      # Главная панель
@app.route('/logout') # Выход
```

## 💾 База данных

### Схема БД

**Таблица `clients`**
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    registered_at TIMESTAMP
)
```

**Таблица `messages`**
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    question TEXT,
    answer TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES clients(user_id)
)
```

**Таблица `manager_requests`**
```sql
CREATE TABLE manager_requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    question TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES clients(user_id)
)
```

## 🎮 Функциональность

### Для клиента

1. **Старт** - `/start` - регистрация и приветствие
2. **Кнопки** - быстрые ответы на частые вопросы
3. **Свободный ввод** - AI генерирует ответ
4. **"Нужен живой менеджер"** - переключение на человека

### Для менеджера

1. **Получение уведомлений** - все диалоги клиентов
2. **Ответ клиенту** - реплай на сообщение бота
3. **Просмотр истории** - через админ-панель

### Для администратора

1. **Веб-интерфейс** - http://localhost:5000
2. **Статистика** - график регистраций
3. **Поиск** - по всем сообщениям
4. **Просмотр** - всех таблиц БД

## 🚦 Запуск

### Запуск бота

```bash
cd bot
python userbot_telethon.py
```

### Запуск админ-панели

```bash
cd bot
python admin_panel.py
```

Админ-панель будет доступна по адресу: `http://localhost:5000`

### Запуск через systemd (Linux)

```bash
# Создаем service файлы
sudo nano /etc/systemd/system/kokc-bot.service
sudo nano /etc/systemd/system/kokc-admin.service

# Пример bot.service
[Unit]
Description=KOKC Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/project/bot
ExecStart=/usr/bin/python3 /path/to/project/bot/userbot_telethon.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔧 Устранение неполадок

### Проблема: Бот не отвечает

**Решение:**
```bash
# Проверьте API ключи
echo $GROK_TOKEN

# Проверьте подключение к Telegram
python -c "from telethon import TelegramClient; ..."
```

### Проблема: Ошибка прокси

**Решение:**
```python
# Временно отключите прокси в коде
# proxy_tuple = None
```

### Проблема: Не сохраняются сообщения

**Решение:**
```bash
# Проверьте права на запись
chmod 666 bot/KOKC.db
chmod 666 bot/message_map.json
```

### Проблема: Groq API не отвечает

**Решение:**
```python
# Проверьте лимиты API
# Убедитесь, что MODEL существует
MODEL = 'mixtral-8x7b-32768'  # альтернативная модель
```

## 📊 Мониторинг

### Логирование

Бот выводит в консоль:
- Статус запуска
- Ошибки API
- Действия менеджера

### Проверка статуса

```bash
# Проверить активность бота
ps aux | grep userbot_telethon

# Посмотреть логи
journalctl -u kokc-bot -f

# Проверить БД
sqlite3 bot/KOKC.db "SELECT COUNT(*) FROM clients;"
```

## 🔐 Безопасность

1. **JWT токены** - для админ-панели
2. **Пароль** - доступ к админке
3. **Бан-лист** - блокировка пользователей
4. **Прокси** - скрытие IP бота

## 📝 Лицензия

Проект является собственностью ООО "КОКЦ". Все права защищены.

## 📞 Контакты поддержки

- **Техническая поддержка:** support@kemkad.ru
- **Разработчик:** [Ваше имя]
- **Сайт компании:** https://kemkad.ru

---

**Версия:** 1.0  
**Последнее обновление:** 2024  
**Статус:** Production Ready ✅
