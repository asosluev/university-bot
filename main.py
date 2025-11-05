import json
import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Завантажуємо токен
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Логування
logging.basicConfig(level=logging.INFO)

# Завантажуємо JSON
with open("content.json", "r", encoding="utf-8") as f:
    content = json.load(f)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть мову / Choose language:", reply_markup=reply_markup)

# Обробка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Вибір мови
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        await show_main_menu(query, lang)
        return

    # Основне меню
    if data.startswith("menu_"):
        lang = context.user_data.get("lang", "ua")
        key = data.replace("menu_", "")
        await show_content(query, lang, key)
        return

    # FAQ питання
    if data.startswith("faq_"):
        lang = context.user_data.get("lang", "ua")
        index = int(data.replace("faq_", ""))
        faq_item = content[lang]["menu"]["faq"]["items"][index]
        await query.edit_message_text(text=f"❓ {faq_item['q']}\n\n💡 {faq_item['a']}", reply_markup=None)

async def show_main_menu(query, lang):
    menu = content[lang]["menu"]
    keyboard = [
        [InlineKeyboardButton(menu["about"]["title"], callback_data="menu_about")],
        [InlineKeyboardButton(menu["specialties"]["title"], callback_data="menu_specialties")],
        [InlineKeyboardButton(menu["how_to_apply"]["title"], callback_data="menu_how_to_apply")],
        [InlineKeyboardButton(menu["required_docs"]["title"], callback_data="menu_required_docs")],
        [InlineKeyboardButton(menu["contacts"]["title"], callback_data="menu_contacts")],
        [InlineKeyboardButton(menu["payment"]["title"], callback_data="menu_payment")],
        [InlineKeyboardButton(menu["schedule"]["title"], callback_data="menu_schedule")],
        [InlineKeyboardButton(menu["links"]["title"], callback_data="menu_links")],
        [InlineKeyboardButton(menu["consultant"]["title"], callback_data="menu_consultant")],
        [InlineKeyboardButton(menu["faq"]["title"], callback_data="menu_faq")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"🔹 {content[lang]['university_name']}", reply_markup=reply_markup)

async def show_content(query, lang, key):
    menu = content[lang]["menu"]
    item = menu[key]

    # Спеціальності
    if key == "specialties":
        text = "\n\n".join([f"🔹 {s['name']} ({s['code']})\n{s['description']}" for s in item["list"]])
        await query.edit_message_text(text=text)
        return

    # FAQ
    if key == "faq":
        keyboard = [
            [InlineKeyboardButton(f"❓ {i['q']}", callback_data=f"faq_{idx}")] for idx, i in enumerate(item["items"])
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Обери питання / Choose question:", reply_markup=reply_markup)
        return

    # Посилання
    if key == "links":
        keyboard = [[InlineKeyboardButton(l["name"], url=l["url"])] for l in item["items"]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Корисні посилання / Useful links:", reply_markup=reply_markup)
        return

    # Консультант
    if key == "consultant":
        username = item["username"]
        keyboard = [[InlineKeyboardButton("💬 Написати консультанту", url=f"https://t.me/{username[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Звʼязатися з консультантом: {username}", reply_markup=reply_markup)
        return

    # Зображення
    if "image" in item and item["image"]:
        await query.edit_message_media(media={"type":"photo","media":item["image"]})
        if "text" in item and item["text"]:
            await query.message.reply_text(item["text"])
        return

    # Інший текст
    if "text" in item:
        await query.edit_message_text(item["text"])

# Основний запуск
if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 8443))
    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

