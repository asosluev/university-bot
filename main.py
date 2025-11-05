import os, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
PORT = int(os.environ.get("PORT", 8443))

# --- Завантаження контенту з JSON ---
with open("data.json", "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

# --- Генерація клавіатури ---
def make_keyboard(buttons):
    keyboard = []
    for item in buttons:
        if item[1].startswith("url:"):
            keyboard.append([InlineKeyboardButton(item[0], url=item[1].replace("url:", ""))])
        else:
            keyboard.append([InlineKeyboardButton(item[0], callback_data=item[1])])
    return InlineKeyboardMarkup(keyboard)

# --- Функції ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = CONTENT["menu"]
    await update.message.reply_text(msg["text"], reply_markup=make_keyboard(msg["buttons"]))

async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str):
    data = CONTENT.get(section, {})
    text = data.get("text", "")
    buttons = make_keyboard(data.get("buttons", []))
    image = data.get("image")

    if image:
        await update.callback_query.message.reply_photo(
            photo=image, caption=text, parse_mode="Markdown", reply_markup=buttons
        )
    else:
        await update.callback_query.message.edit_text(
            text=text, parse_mode="Markdown", reply_markup=buttons
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "back_to_menu":
        msg = CONTENT["menu"]
        await query.message.edit_text(msg["text"], reply_markup=make_keyboard(msg["buttons"]))
    elif data in CONTENT:
        await show_section(update, context, data)

# --- Запуск ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    WEBHOOK_URL = f"https://{HOSTNAME}/webhook"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )
