"""Core commands and user-facing bot metadata."""
from __future__ import annotations
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes
WELCOME = "👋 *Welcome to UtilityBot!*\n\nA practical Telegram toolbox for notes, reminders, weather, and currency.\n\nUse /help to see commands, or /about for project details."
HELP = (
    "*UtilityBot commands*\n\n"
    "*Notes*\n/note <text> — save a note\n/notes — list your notes\n/delnote <id> — delete one note\n/clearnotes — delete all your notes\n\n"
    "*Reminders*\n/remind <duration> <text> — set a reminder\n/reminders — list pending reminders\n/delreminder <id> — cancel a reminder\n\n"
    "*Utilities*\n/weather <city> — current weather\n/convert <amount> <from> <to> — e.g. /convert 100 USD INR\n\n"
    "*Other*\n/start — start the bot\n/help — show help\n/about — show bot information\n/cancel — clear local bot state"
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME, parse_mode="Markdown")
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP, parse_mode="Markdown")
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 *UtilityBot*\n\nPython + python-telegram-bot\nPersistence: SQLite\nScheduling: JobQueue / APScheduler\nDeployment: Docker + long polling", parse_mode="Markdown")
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I don't recognize that command. Try /help to see available commands.")
