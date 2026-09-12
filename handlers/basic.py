"""Core commands: /start, /help, /cancel."""

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

WELCOME = (
    "👋 *Welcome to UtilityBot!*\n\n"
    "I'm a small toolbox that lives in your chat. Here's what I can do:\n\n"
    "🗒 *Notes* — jot things down and get them back later\n"
    "⏰ *Reminders* — \"remind me in 20m to stretch\"\n"
    "🌦 *Weather* — current conditions for any city\n"
    "💱 *Currency* — quick exchange-rate conversions\n\n"
    "Type /help any time to see the full command list."
)

HELP = (
    "*Commands*\n\n"
    "*Notes*\n"
    "`/note <text>` – save a note\n"
    "`/notes` – list your saved notes\n"
    "`/delnote <id>` – delete one note\n"
    "`/clearnotes` – delete all your notes\n\n"
    "*Reminders*\n"
    "`/remind <10m|2h|1d> <text>` – set a reminder\n"
    "`/reminders` – list your pending reminders\n"
    "`/delreminder <id>` – cancel a reminder\n\n"
    "*Weather*\n"
    "`/weather <city>` – current weather for a city\n\n"
    "*Currency*\n"
    "`/convert <amount> <from> <to>` – e.g. `/convert 100 USD INR`\n\n"
    "*Other*\n"
    "`/help` – show this message\n"
    "`/cancel` – cancel whatever you were typing"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(WELCOME)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(HELP)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text(
        "Cancelled.", reply_markup=ReplyKeyboardRemove()
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "I don't recognize that command. Try /help to see what I can do."
    )
