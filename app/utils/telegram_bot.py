import os, requests, logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from ..config import settings
API_URL = os.getenv('API_URL', f"http://{settings.API_HOST}:{settings.API_PORT}")
CHAT_ID = settings.TELEGRAM_CHAT_ID
logging.basicConfig(level=logging.INFO)
async def send_signal_card(signal_id: int, symbol: str, entry: float, sl: float, tp: float, rationale: str):
    text = f"🔔 Señal #{signal_id}\n{symbol} BUY\nEntry: {entry:.4f}\nSL: {sl:.4f} TP: {tp:.4f}\n{rationale}"
    keyboard = [[InlineKeyboardButton("✅ Aprobar", callback_data=f"approve:{signal_id}"), InlineKeyboardButton("❌ Rechazar", callback_data=f"reject:{signal_id}")]]
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    await app.bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    await app.shutdown()
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if str(user_id) != str(CHAT_ID):
        await query.edit_message_text("Acción no permitida.")
        return
    action, sid = query.data.split(":")
    sid = int(sid)
    if action == 'approve':
        try:
            r = requests.post(f"{API_URL}/signals/{sid}/approve", timeout=15)
            await query.edit_message_text(f"✅ Señal {sid} aprobada.")
        except Exception as e:
            await query.edit_message_text(f"Error aprobando señal: {e}")
    else:
        try:
            r = requests.post(f"{API_URL}/signals/{sid}/reject", timeout=15)
            await query.edit_message_text(f"❌ Señal {sid} rechazada.")
        except Exception as e:
            await query.edit_message_text(f"Error rechazando señal: {e}")
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(CHAT_ID):
        await update.message.reply_text("No autorizado")
        return
    try:
        r = requests.get(f"{API_URL}/account", timeout=10)
        await update.message.reply_text(str(r.json()))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
def run_bot():
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(CommandHandler('status', cmd_status))
    app.run_polling()
if __name__ == '__main__':
    run_bot()
