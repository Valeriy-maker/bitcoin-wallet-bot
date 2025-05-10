from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# 🔐 Установи эти переменные в Render Dashboard
TOKEN = os.environ.get("7841134339:AAHzS2bPKSEseWYzulezWFYMWKSw_lmU0xs")
WEBHOOK_URL = os.environ.get("t.me/probi439_bot")  # без слеша на конце

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Telegram App
tg_app = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает через webhook.")

tg_app.add_handler(CommandHandler("start", start))

@app.route('/webhook', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    tg_app.update_queue.put(update)
    return "ok", 200

@app.route('/')
def home():
    return "Бот онлайн!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    # Установка webhook (только при первом запуске)
    import asyncio
    async def set_webhook():
        await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    asyncio.run(set_webhook())
    
    app.run(host="0.0.0.0", port=port)
