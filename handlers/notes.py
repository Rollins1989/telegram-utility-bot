"""Notes feature: save, list, delete, clear."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

import database as db

logger = logging.getLogger(__name__)


async def note_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Usage: `/note <text>`\nExample: `/note buy milk`",
            parse_mode="Markdown",
        )
        return

    content = " ".join(context.args)
    user_id = update.effective_user.id
    note_id = db.add_note(user_id, content)
    logger.info("User %s saved note #%s", user_id, note_id)
    await update.message.reply_text(f"✅ Saved as note #{note_id}.")


async def note_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    notes = db.list_notes(user_id)

    if not notes:
        await update.message.reply_text(
            "You don't have any notes yet. Add one with `/note <text>`.",
            parse_mode="Markdown",
        )
        return

    lines = [f"*#{n['id']}* — {n['content']}" for n in notes]
    text = "🗒 *Your notes:*\n\n" + "\n".join(lines)
    await update.message.reply_markdown(text)


async def note_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: `/delnote <id>`", parse_mode="Markdown")
        return

    note_id = int(context.args[0])
    user_id = update.effective_user.id
    if db.delete_note(user_id, note_id):
        await update.message.reply_text(f"🗑 Deleted note #{note_id}.")
    else:
        await update.message.reply_text(f"No note #{note_id} found for you.")


async def note_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    count = db.clear_notes(user_id)
    await update.message.reply_text(f"🧹 Cleared {count} note(s).")
