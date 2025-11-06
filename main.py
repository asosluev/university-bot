import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
PORT = int(os.environ.get("PORT", 8443))

# --- Налаштування мови ---
LANG = "ua"  # можна змінити на "en"

# --- Завантаження контенту ---
with open("data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

CONTENT = DATA[LANG]["menu"]
UNIVERSITY_NAME = DATA[LANG]["university_name"]


# --- Допоміжні функції ---
def make_main_menu():
    """Створює головне меню з назвами розділів."""
    keyboard = [
        [InlineKeyboardButton(v["title"], callback_data=k)] for k, v in CONTENT.items()
    ]
    return InlineKeyboardMarkup(keyboard)


def make_back_button():
    """Кнопка 'Назад до меню'."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]]
    )


# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"📘 *{UNIVERSITY_NAME}*\n\nОберіть розділ:"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=make_main_menu())


# --- Відображення розділів ---
async def show_section(update: Update, section_key: str):
    section = CONTENT[section_key]
    title = section.get("title", "")
    text = section.get("text", "")
    image = section.get("image")

    # Якщо є список спеціальностей
    if "list" in section:
        for item in section["list"]:
            text += f"\n\n• *{item['name']}* ({item['code']}) — {item['description']}"

    # Якщо є посилання
    if "items" in section and "url" in section["items"][0]:
        for item in section["items"]:
            text += f"\n\n🔗 [{item['name']}]({item['url']})"

    # Якщо це FAQ
    if "items" in section and "q" in section["items"][0]:
        for qa in section["items"]:
            text += f"\n\n❓ *{qa['q']}*\n➡️ {qa['a']}"

    # Якщо є контакти
    if section_key == "contacts":
        text += f"\n\n📞 {section['phone']}\n✉️ {section['email']}\n📍 {section['address']}\n[🗺 Відкрити на мапі]({section['map_url']})"

    # Якщо є консультант
    if section_key == "consultant":
        text += f"\n\nЗвʼязатися: {section['username']}"

    # Якщо є реквізити
    if section_key == "payment":
        text += f"\n\n💳 {section['text']}"

    # Відправка
    if image:
        await update.callback_query.message.reply_photo(
            photo=image,
            caption=f"*{title}*\n\n{text}",
            parse_mode="Markdown",
            reply_markup=make_back_button()
        )
    else:
        await update.callback_query.message.edit_text(
            f"*{title}*\n\n{text}",
            parse_mode="Markdown",
            reply_markup=make_back_button()
        )


# --- Обробник callback ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "back_to_menu":
        await query.message.edit_text(
            f"📘 *{UNIVERSITY_NAME}*\n\nОберіть розділ:",
            parse_mode="Markdown",
            reply_markup=make_main_menu()
        )
    elif data in CONTENT:
        await show_section(update, data)


# --- Запуск ---
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN не знайдено у .env")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    WEBHOOK_URL = f"https://{HOSTNAME}/webhook"

    print(f"✅ Webhook URL: {WEBHOOK_URL}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )
