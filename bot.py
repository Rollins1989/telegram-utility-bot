"""Application entry point for UtilityBot."""
from __future__ import annotations
import logging
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import database as db
from config import TELEGRAM_BOT_TOKEN, setup_logging, validate_config
from handlers import basic, currency, notes, reminders, weather
logger = logging.getLogger(__name__)

async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception while processing update: %s", update, exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Something went wrong handling that. The error was logged; please try again.")
        except Exception:
            logger.debug("Could not send error response to Telegram", exc_info=True)

async def _post_init(application: Application) -> None:
    db.init_db()
    reminders.reschedule_pending(application)
    me = await application.bot.get_me()
    logger.info("Bot started as @%s", me.username)

def build_application() -> Application:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(_post_init).build()
    application.add_handler(CommandHandler("start", basic.start))
    application.add_handler(CommandHandler("help", basic.help_command))
    application.add_handler(CommandHandler("about", basic.about))
    application.add_handler(CommandHandler("cancel", basic.cancel))
    application.add_handler(CommandHandler("note", notes.note_add))
    application.add_handler(CommandHandler("notes", notes.note_list))
    application.add_handler(CommandHandler("delnote", notes.note_delete))
    application.add_handler(CommandHandler("clearnotes", notes.note_clear))
    application.add_handler(CommandHandler("remind", reminders.remind_add))
    application.add_handler(CommandHandler("reminders", reminders.remind_list))
    application.add_handler(CommandHandler("delreminder", reminders.remind_delete))
    application.add_handler(CommandHandler("weather", weather.weather))
    application.add_handler(CommandHandler("convert", currency.convert))
    application.add_handler(MessageHandler(filters.COMMAND, basic.unknown_command))
    application.add_error_handler(_on_error)
    return application

def main() -> None:
    setup_logging()
    validate_config()
    db.init_db()
    application = build_application()
    logger.info("Starting Telegram long polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
