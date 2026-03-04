import os
import json
import telebot
from telebot import types
from groq import Groq
from dotenv import load_dotenv
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from database.connection import Database

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, 'KOKC.db')

db = Database(DB_PATH)

load_dotenv()


BAN = json.loads(os.getenv('BAN_LIST', '[]'))
GROQ_API_KEY = os.getenv('GROK_TOKEN')
TELEGRAM_TOKEN = os.getenv('TG_BOT_TOKEN')
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', 0))
MODEL = "openai/gpt-oss-20b"
ADMIN_IDS = [MANAGER_CHAT_ID]
MAP_FILE = 'message_map.json'

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)


def load_message_map():
    if os.path.exists(MAP_FILE):
        try:
            with open(MAP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_message_map(data):
    try:
        with open(MAP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except:
        pass


message_map = load_message_map()


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("Услуги"),
        types.KeyboardButton("Кадастровая стоимость"),
        types.KeyboardButton("Документы"),
        types.KeyboardButton("Оформление дома"),
        types.KeyboardButton("Нужен живой менеджер"),
        types.KeyboardButton("Контакты")
    ]
    markup.add(*buttons)
    return markup


BUTTON_RESPONSES = {
    "Услуги": "Наши услуги:\n• Кадастровый учет\n• Оценка недвижимости\n• Регистрация прав\n• Межевание\n• Технические планы",
    "Кадастровая стоимость": "Для получения кадастровой стоимости необходимо:\n1. Кадастровый номер объекта\n2. Адрес объекта\n\nНапишите эти данные, и мы поможем",
    "Документы": "Основные документы:\n• Паспорт\n• Правоустанавливающие документы\n• Технический паспорт\n• Кадастровый паспорт",
    "Оформление дома": "Для оформления дома нужны:\n• Документы на землю\n• Технический план\n• Разрешение на строительство (если есть)",
    "Контакты": "📍 Адрес: , г. Кемерово, пр. Шахтёров, 50\n📞 Телефон: +7 (3842) 44-24-00\n📧 Email: info@kadastr42.ru\n🕒 Режим: Пн-Чт 8:00-17:00, Пт 08:00 -15:00\nГенеральный директор — Артёмов Алексей Владимирович."
}

SYSTEM_PROMPT = """
Ты — официальный цифровой помощник ООО "Кемеровский Областной Кадастровый Центр" (ООО "КОКЦ"). Работаешь на сайте kemkad.ru. Твоя задача — консультировать клиентов по услугам центра, используя ТОЛЬКО предоставленную ниже информацию. Представляешь компанию в Кемеровской области — Кузбассе.

БАЗА ЗНАНИЙ (Официальные данные ООО "КОКЦ"):
Полное наименование: Общество с ограниченной ответственностью "Кемеровский Областной Кадастровый Центр" (ООО "КОКЦ")
Сайт: kemkad.ru

Услуги:
• Кадастровый учет
• Оценка недвижимости
• Регистрация прав
• Межевание
• Технические планы

Кадастровая стоимость:
Для получения кадастровой стоимости необходимо:
1. Кадастровый номер объекта
2. Адрес объекта
Напишите эти данные, и мы поможем

Документы:
Основные документы:
• Паспорт
• Правоустанавливающие документы
• Технический паспорт
• Кадастровый паспорт

Оформление дома:
Для оформления дома нужны:
• Документы на землю
• Технический план
• Разрешение на строительство (если есть)

Контакты:
📍 Адрес: г. Кемерово, пр. Шахтёров, 50
📞 Телефоны:
  +7 (3842) 44-24-00
  +7 (3842) 44-24-01
  +7 (3842) 44-24-07
📧 Email: kokc@kemkad.ru
🌐 Сайт: kemkad.ru
🕒 Режим работы: Пн-Чт 8:00-17:00, Пт 08:00-15:00
Генеральный директор — Артёмов Алексей Владимирович

ИНСТРУКЦИИ ПО ОБЩЕНИЮ:
Стиль:
• Вежливый, профессиональный, но дружелюбный
• Обращение на "Вы"
• Четкие и краткие ответы
• При упоминании компании используй полное название или аббревиатуру "КОКЦ"

Структура ответа:
1. Приветствие (если это начало диалога)
2. Ответ на вопрос (используй информацию из БАЗЫ ЗНАНИЙ)
3. Если информации в базе нет — предложи связаться по телефону или email
4. Завершение (предложение дальнейшей помощи)

ОТВЕТЫ НА ЧАСТЫЕ ВОПРОСЫ:

Если спрашивают про кадастровую стоимость:
"Для того чтобы узнать кадастровую стоимость, напишите мне, пожалуйста:
- Кадастровый номер объекта
- Адрес объекта

После этого мы сможем помочь вам с расчетом. Также вы можете отправить эти данные на почту kokc@kemkad.ru"

Если спрашивают про оформление дома:
"Для оформления дома необходимы следующие документы:
• Документы на землю
• Технический план
• Разрешение на строительство (если есть)

Вы можете принести их в наш офис по адресу: пр. Шахтёров, 50, или отправить на почту kokc@kemkad.ru для предварительной проверки."

Если спрашивают про документы:
"Основной пакет документов включает:
• Паспорт
• Правоустанавливающие документы
• Технический паспорт
• Кадастровый паспорт

Обратите внимание: для разных услуг перечень может отличаться. Уточните, какую именно услугу вы хотите получить?"

Если спрашивают контакты/адрес:
"Наш офис находится по адресу: г. Кемерово, пр. Шахтёров, 50.
Режим работы: Пн-Чт с 8:00 до 17:00, Пт с 08:00 до 15:00.

Контакты ООО "КОКЦ":
📞 +7 (3842) 44-24-00
📞 +7 (3842) 44-24-01
📞 +7 (3842) 44-24-07
📧 kokc@kemkad.ru
🌐 kemkad.ru

Генеральный директор — Артёмов Алексей Владимирович."

Если спрашивают про сайт:
"Наш официальный сайт: kemkad.ru. Там вы можете подробнее ознакомиться с услугами и актуальными ценами."

ПРАВИЛА (Что нельзя делать):
❌ НЕ придумывай цены — их нет в базе. Если спросят стоимость, скажи: "Точная стоимость рассчитывается индивидуально. Оставьте телефон, специалист свяжется и назовет цену, или позвоните нам по телефону +7 (3842) 44-24-00".

❌ НЕ обещай 100% результат от Росреестра. Говори: "Мы подготовим документы в соответствии с законом".

❌ НЕ игнорируй вопросы. Если не знаешь — предложи позвонить: "Для точного ответа рекомендую связаться с нашим специалистом по телефону +7 (3842) 44-24-00 или написать на kokc@kemkad.ru".

❌ НЕ используй другие названия компании — только ООО "КОКЦ" или "Кемеровский Областной Кадастровый Центр".

ПРИВЕТСТВИЕ (Начало диалога):
"Здравствуйте! Я цифровой помощник Кемеровского Областного Кадастрового Центра (ООО "КОКЦ").
Помогу с вопросами по:
✅ Кадастровому учету
✅ Оценке недвижимости
✅ Регистрации прав
✅ Межеванию
✅ Техническим планам

Также можем помочь узнать кадастровую стоимость объекта.
Что вас интересует?"
"""


def get_user_info(message):
    return {
        'id': message.from_user.id,
        'name': message.from_user.first_name or "Неизвестный",
        'username': message.from_user.username or "Нет username",
        'last_name': message.from_user.last_name
    }


def save_user_to_db(user_info):
    db.save_or_update_user(
        user_id=user_info['id'],
        username=user_info['username'],
        first_name=user_info['name'],
        last_name=user_info['last_name']
    )


@bot.message_handler(commands=['start'])
def start_message(message):
    user_info = get_user_info(message)
    save_user_to_db(user_info)

    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Вы вошли как администратор. Ожидайте сообщения от клиентов.")
        return

    bot.send_message(
        message.chat.id,
        "Кемеровский Областной Кадастровый Центр приветствует вас!\n"
        "Виртуальный менеджер на связи. Напишите свой вопрос или выберите действие:",
        reply_markup=get_main_keyboard()
    )


def connect_to_manager(message):
    user_info = get_user_info(message)
    db.save_manager_request(user_info['id'], message.text)

    msg = bot.send_message(
        MANAGER_CHAT_ID,
        f"Клиент {user_info['name']} (ID: {user_info['id']}, @{user_info['username']}) просит помощи!\n"
        f"Сообщение: {message.text}\n\n"
        f"Нажмите 'Ответить' на это сообщение, чтобы написать клиенту."
    )

    message_map[str(msg.message_id)] = user_info['id']
    save_message_map(message_map)
    bot.reply_to(message, "Менеджер скоро ответит вам. Ожидайте ответа в этом чате.")


@bot.message_handler(func=lambda m: m.text in BUTTON_RESPONSES.keys() or m.text == "Нужен живой менеджер")
def handle_buttons(message):
    if message.chat.id in ADMIN_IDS:
        return

    if message.text == "Нужен живой менеджер":
        connect_to_manager(message)
        return

    response = BUTTON_RESPONSES[message.text]
    db.save_message(message.from_user.id, message.text, response)
    bot.reply_to(message, response)


@bot.message_handler(func=lambda m: m.chat.id == MANAGER_CHAT_ID and m.reply_to_message)
def manager_reply(message):
    try:
        replied_id = str(message.reply_to_message.message_id)

        if replied_id in message_map:
            client_id = message_map[replied_id]
            db.save_message(client_id, "[Запрос к менеджеру]", f"Ответ менеджера: {message.text}")
            bot.send_message(client_id, f"Ответ от менеджера:\n\n{message.text}")
            bot.reply_to(message, "Ответ отправлен клиенту!")

            del message_map[replied_id]
            save_message_map(message_map)
        else:
            bot.reply_to(message, "Не найден ID клиента. Возможно, сообщение слишком старое.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при отправке: {e}")


@bot.message_handler(func=lambda m: True)
def answer(message):
    if message.from_user.id in BAN:
        bot.reply_to(message, "Вы в черном списке")
    else:
        try:
            if message.chat.id in ADMIN_IDS:
                if not message.reply_to_message:
                    bot.send_message(
                        message.chat.id,
                        "Вы администратор. Используйте функцию 'Ответить' на сообщение бота с вопросом клиента."
                    )
                return

            if message.text in BUTTON_RESPONSES.keys():
                return

            user_info = get_user_info(message)
            save_user_to_db(user_info)

            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": message.text}
                    ],
                    model=MODEL,
                    temperature=0.7,
                    max_tokens=1024
                ).choices[0].message.content

                bot.reply_to(message, response)
                db.save_message(user_info['id'], message.text, response)

                msg = bot.send_message(
                    MANAGER_CHAT_ID,
                    f"Клиент {user_info['name']} (ID: {user_info['id']}, @{user_info['username']}) написал:\n"
                    f"'{message.text}'\n\n"
                    f"Ответ бота:\n{response}\n\n"
                    f"Нажмите 'Ответить', если хотите ответить лично."
                )

                message_map[str(msg.message_id)] = user_info['id']
                save_message_map(message_map)

            except Exception as e:
                print(f"Groq API Error: {e}")
                db.save_message(user_info['id'], message.text, "[Ошибка API]")

                msg = bot.send_message(
                    MANAGER_CHAT_ID,
                    f"Виртуальный менеджер временно недоступен.\n"
                    f"Клиент {user_info['name']} (ID: {user_info['id']}, @{user_info['username']}) спрашивает:\n"
                    f"'{message.text}'\n\n"
                    f"Нажмите 'Ответить', чтобы написать клиенту лично."
                )

                message_map[str(msg.message_id)] = user_info['id']
                save_message_map(message_map)

                bot.reply_to(
                    message,
                    "Извините, виртуальный помощник временно недоступен. "
                    "Ваш вопрос передан живому менеджеру. Ожидайте ответа."
                )

        except Exception as e:
            print(f"Error: {e}")



bot.infinity_polling()
