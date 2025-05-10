from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import hashlib, ecdsa, os

TOKEN = "7841134339:AAHzS2bPKSEseWYzulezWFYMWKSw_lmU0xs"  # <-- вставь сюда токен бота

# Генерация seed и BTC адреса
def generate_wallet():
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=128)
    seed = mnemo.to_seed(words)
    private_key = hashlib.sha256(seed).hexdigest()
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    public_key = b'\x04' + vk.to_string()
    public_key_hash = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).digest()
    address = '1' + hashlib.new('sha256', public_key_hash).hexdigest()[:33]
    return words, private_key, address

# Старт команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Оплатите $1, чтобы получить ваш Bitcoin-кошелёк.\n\n(Псевдо-оплата — набери /pay)")

# Заглушка оплаты
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # В реальной версии — проверить оплату через Stripe / крипту
    seed, privkey, address = generate_wallet()
    await update.message.reply_text(f"Ваш Bitcoin кошелёк:\n\nSeed-фраза:\n{seed}\n\nПриватный ключ:\n{privkey}\n\nBTC-адрес:\n{address}\n\nСохраняйте эти данные в секрете!")

# Запуск
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.run_polling()
