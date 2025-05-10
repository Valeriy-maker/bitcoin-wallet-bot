
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os, requests, time

TOKEN = os.environ.get("7841134339:AAHzS2bPKSEseWYzulezWFYMWKSw_lmU0xs")
WEBHOOK_URL = os.environ.get("t.me/probi439_bot")

USDT_ADDRESS = "TCPmn4p3toTU5c1fJnFCqAjD7CS34YKqXd"
CHECK_AMOUNT = 1.0  # USD

bot = Bot(token=TOKEN)
app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

ASK_TXID = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Use /pay to send $1 USDT (TRC20) via Binance and receive your Bitcoin wallet password.")

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "💰 Please send *1 USDT (TRC20)* to the address below:

"
        f"`{USDT_ADDRESS}`

"
        "After sending, reply with the *TXID* (transaction hash)."
    )
    await update.message.reply_markdown(msg)
    return ASK_TXID

def check_transaction(txid: str):
    url = f"https://apilist.tronscanapi.com/api/transaction-info?hash={txid}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if 'contractData' in data and data.get("confirmed", False):
            contract = data['contractData']
            to_address = contract.get("to_address", "")
            amount = float(contract.get("amount", 0)) / 1_000_000  # TRC20 decimals

            if to_address == USDT_ADDRESS and amount >= CHECK_AMOUNT:
                return True
    except:
        pass
    return False

async def receive_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txid = update.message.text.strip()
    await update.message.reply_text("⏳ Checking transaction...")

    if check_transaction(txid):
        await update.message.reply_text("✅ Payment confirmed!
Here is your Bitcoin wallet password:

*bitpass-XYZ123456*", parse_mode='Markdown')
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Transaction not found or incorrect.
Please make sure you sent 1 USDT (TRC20) to the correct address and try again.")
        return ASK_TXID

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Payment cancelled.")
    return ConversationHandler.END

@app.route('/webhook', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    tg_app.update_queue.put(update)
    return "ok", 200

@app.route('/')
def home():
    return "Bot is running and waiting for payments.")

if __name__ == "__main__":
    from telegram.ext import CommandHandler, MessageHandler, filters

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("pay", pay)],
        states={ASK_TXID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_txid)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(conv_handler)

    port = int(os.environ.get("PORT", 5000))
    import asyncio
    async def set_webhook():
        await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=port)
