"""
UtilityBot — a small, well-behaved Telegram bot.

Run it with:
    python bot.py

See README.md for setup instructions.
"""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, validate_config, setup_logging
import database as db
from handlers import basic, notes, reminders, weather, currency

logger = logging.getLogger(__name__)


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler so one bad update never crashes the process."""
    logger.exception("Unhandled exception while processing update: %s", update, exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Something went wrong handling that. It's been logged — try again."
            )
        except Exception:
            pass  # best-effort; never let the error handler itself raise


async def _post_init(application: Application) -> None:
    """Runs once after the bot starts polling, before it processes updates."""
    reminders.reschedule_pending(application)
    bot_user = await application.bot.get_me()
    logger.info("Bot started as @%s", bot_user.username)


def build_application() -> Application:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(_post_init).build()

    # Basic
    application.add_handler(CommandHandler("start", basic.start))
    application.add_handler(CommandHandler("help", basic.help_command))
    application.add_handler(CommandHandler("cancel", basic.cancel))

    # Notes
    application.add_handler(CommandHandler("note", notes.note_add))
    application.add_handler(CommandHandler("notes", notes.note_list))
    application.add_handler(CommandHandler("delnote", notes.note_delete))
    application.add_handler(CommandHandler("clearnotes", notes.note_clear))

    # Reminders
    application.add_handler(CommandHandler("remind", reminders.remind_add))
    application.add_handler(CommandHandler("reminders", reminders.remind_list))
    application.add_handler(CommandHandler("delreminder", reminders.remind_delete))

    # Weather
    application.add_handler(CommandHandler("weather", weather.weather))

    # Currency
    application.add_handler(CommandHandler("convert", currency.convert))

    # Fallback for unrecognized commands (must be added last)
    application.add_handler(MessageHandler(filters.COMMAND, basic.unknown_command))

    application.add_error_handler(_on_error)
    return application


def main() -> None:
    setup_logging()
    validate_config()
    db.init_db()

    application = build_application()
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
