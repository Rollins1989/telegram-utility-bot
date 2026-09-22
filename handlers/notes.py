"""Notes feature: create, list, delete, and clear personal notes."""
from __future__ import annotations
import logging
from telegram import Update
from telegram.ext import ContextTypes
import database as db
logger = logging.getLogger(__name__)

async def note_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /note <text>\nExample: /note buy milk")
        return
    content = " ".join(context.args).strip()
    if len(content) > 1000:
        await update.message.reply_text("Notes are limited to 1,000 characters.")
        return
    note_id = db.add_note(update.effective_user.id, content)
    logger.info("User %s saved note #%s", update.effective_user.id, note_id)
    await update.message.reply_text("✅ Saved as note #" + str(note_id) + ".")

async def note_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notes = db.list_notes(update.effective_user.id)
    if not notes:
        await update.message.reply_text("You don't have any notes yet. Add one with /note <text>.")
        return
    lines = ["#" + str(n["id"]) + " — " + n["content"] for n in notes[:50]]
    if len(notes) > 50:
        lines.append("Showing the 50 most recent notes.")
    await update.message.reply_text("🗒 Your notes:\n\n" + "\n".join(lines))

async def note_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /delnote <id>")
        return
    note_id = int(context.args[0])
    if db.delete_note(update.effective_user.id, note_id):
        await update.message.reply_text("🗑 Deleted note #" + str(note_id) + ".")
    else:
        await update.message.reply_text("No note #" + str(note_id) + " found for you.")

async def note_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    count = db.clear_notes(update.effective_user.id)
    await update.message.reply_text("🧹 Cleared " + str(count) + " note(s).")
