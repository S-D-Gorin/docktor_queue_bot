import os
import re
import requests
import telebot
import random
import datetime

# =========================
# Настройки
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_URL = os.getenv("API_URL", "http://task_runner:8000/api/task")  # <-- замени на свой endpoint
API_TIMEOUT = 30

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

START_TEXT = (
    "Привет медпред!\n"
    "Генератор фейковых талонов \"Я только спросить...\"\n\n"
    "Отправь мне сообщение в следующем формате и я пришлю тебе талон на запись.\n\n"
    "Название поликлиники: Текст\n"
    "ФИО: Иванов Иван\n"
    "Дата и Время: 02/02/2026 12:34,\n"
    "Специальность врача: Терапевт\n"
    "ФИО врача: Алексеев Алексей\n"
)

INSTRUCTION_TEXT = (
    "Не получилось распознать сообщение 😕\n\n"
    "Нажмите /template и я отправлю вам пример сообщения, а вы его отредактируете :\n\n"
    
    "Cообщение должно быть в следующем формате.\n\n"
    "Название поликлиники: Текст\n"
    "ФИО: Иванов Иван\n"
    "Дата и Время: 02/02/2026 12:34,\n"
    "Специальность врача: Терапевт\n"
    "ФИО врача: Алексеев Алексей\n"
)

TEMPLATE_TEXT = (
    "Название поликлиники: Текст\n"
    "ФИО: Иванов Иван\n"
    "Дата и Время: 02/02/2026 12:34,\n"
    "Специальность врача: Терапевт\n"
    "ФИО врача: Алексеев Алексей\n"
)

HELP_TEXT = (
    "Возникли проблемы?\n"
    "Связаться с разработчиком: https://t.me/sprotect_bots"
)
# =========================
# Парсинг и валидация
# =========================
# Допускаем пробелы, возможную запятую после времени, Windows/Unix переносы строк
MESSAGE_PATTERN = re.compile(
    r"^\s*"
    r"Название\s+поликлиники:\s*(?P<hospital_name>.+?)\s*\r?\n"
    r"ФИО:\s*(?P<full_name>.+?)\s*\r?\n"
    r"Дата\s+и\s+Время:\s*(?P<datetime>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})\s*,?\s*\r?\n"
    r"Специальность\s+врача:\s*(?P<docktor_type>.+?)\s*\r?\n"
    r"ФИО\s+врача:\s*(?P<docktor_name>.+?)\s*"
    r"$",
    re.IGNORECASE | re.DOTALL
)

def parse_user_message(text: str):
    """Возвращает dict с данными или None."""
    if not text:
        return None
    m = MESSAGE_PATTERN.match(text.strip())
    if not m:
        return None

    data = {k: v.strip() for k, v in m.groupdict().items()}

    # Дополнительные простые проверки
    if any(len(data[k]) < 2 for k in data):
        return None

    return data

# =========================
# Вызов API
# =========================
def build_payload(data: dict) -> dict:
    return {
        "tasks": ["create_docktor_ticket"],
        "options": {
            "create_docktor_ticket": {
                "params": {
                    "data": {
                        "hospital_name": data["hospital_name"],
                        "full_name": data["full_name"],
                        "datetime": data["datetime"],
                        "docktor_type": data["docktor_type"],
                        "docktor_name": data["docktor_name"],
                        "ticket_number": random.randint(100000, 999999)
                    },
                    "template_config": {
                        "hospital_name": {
                                    "coords_x": 30,
                                    "coords_y": 140,
                                    "font_size": 36
                        },
                        "full_name": {
                                    "coords_x": 400,
                                    "coords_y": 280,
                                    "font_size": 38
                        },
                        "datetime": {
                                    "coords_x": 400,
                                    "coords_y": 650,
                                    "font_size": 30
                        },
                        "docktor_type": {
                                    "coords_x": 400,
                                    "coords_y": 750,
                                    "font_size": 30
                        },
                        "docktor_name": {
                                    "coords_x": 400,
                                    "coords_y": 870,
                                    "font_size": 30
                        },
                        "ticket_number": {
                                    "coords_x": 550,
                                    "coords_y": 410,
                                    "font_size": 30
                        }

                    }
                }
           }
        }
}

def call_ticket_api(payload: dict) -> dict:
    """Возвращает JSON-ответ (dict) или кидает исключение."""
    resp = requests.post(API_URL, json=payload, timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def extract_ticket_path(result: dict) -> str | None:
    """
    Ищем ключ 'Output ticket_path' в стандартной структуре:
    result["results"][0]["details"]["Output ticket_path"]
    """
    try:
        results = result.get("results", [])
        if not results:
            return None
        details = results[0].get("details", {})
        # ключ с пробелом — как в твоём примере
        return details.get("Output ticket_path")
    except Exception:
        return None

# =========================
# Отправка картинки
# =========================
def send_ticket_image(chat_id: int, ticket_url: str):
    """
    Вариант 1: если Telegram может забрать по URL, отправляем сразу.
    Вариант 2: если не вышло — скачиваем и отправляем как файл.
    """
    # Сначала пробуем отправить по URL напрямую
    try:
        bot.send_photo(chat_id, ticket_url)
        return
    except Exception:
        pass

    # Если не получилось — скачиваем
    r = requests.get(ticket_url, timeout=API_TIMEOUT)
    r.raise_for_status()

    # Telegram принимает file-like объект
    from io import BytesIO
    bio = BytesIO(r.content)
    bio.name = "ticket.png"
    bot.send_photo(chat_id, bio)

# =========================
# Handlers
# =========================
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, START_TEXT)

@bot.message_handler(commands=["template"])
def handle_template(message):
    bot.send_message(message.chat.id, TEMPLATE_TEXT)

@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(message.chat.id, HELP_TEXT)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    text = message.text or ""
    parsed = parse_user_message(text)

    if not parsed:
        bot.send_message(message.chat.id, INSTRUCTION_TEXT)
        return

    payload = build_payload(parsed)

    # Можно показать короткий статус
    bot.send_message(message.chat.id, "Принял ✅ Генерирую талон...")

    try:
        result = call_ticket_api(payload)
    except requests.RequestException as e:
        bot.send_message(
            message.chat.id,
            f"Ошибка при обращении к сервису генерации.\n{type(e).__name__}: {e}"
        )
        return
    except ValueError:
        bot.send_message(message.chat.id, "Сервис вернул некорректный JSON.")
        return

    ticket_path = extract_ticket_path(result)
    if not ticket_path:
        bot.send_message(
            message.chat.id,
            "Не нашёл ссылку на талон в ответе сервиса.\n"
            "Проверь, что API возвращает ключ: details -> \"Output ticket_path\""
        )
        return

    try:
        send_ticket_image(message.chat.id, ticket_path)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Не получилось отправить изображение.\n{type(e).__name__}: {e}\n\n"
            f"Ссылка на талон: {ticket_path}"
        )

# =========================
# Запуск
# =========================
if __name__ == "__main__":
    if BOT_TOKEN.startswith("PUT_YOUR"):
        print("WARNING: Укажи BOT_TOKEN (переменная окружения BOT_TOKEN или прямо в коде).")
    if "example.com" in API_URL:
        print("WARNING: Укажи API_URL (переменная окружения API_URL или прямо в коде).")

    print("Bot is running...")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
