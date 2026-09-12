"""
Reminders feature.

Reminders are persisted to SQLite *and* scheduled with APScheduler.
Persisting them means that on restart (`reschedule_pending`, called once at
startup from bot.py) any reminder that hasn't fired yet gets re-armed --
so a bot restart or redeploy never silently drops someone's reminder.
"""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import database as db
from utils.timeparse import parse_duration, humanize_delta, future_time

logger = logging.getLogger(__name__)


async def _fire_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback invoked by the job queue when a reminder is due."""
    job = context.job
    reminder_id = job.data["reminder_id"]
    message = job.data["message"]
    chat_id = job.chat_id

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ *Reminder:* {message}",
            parse_mode=ParseMode.MARKDOWN,
        )
    finally:
        db.mark_fired(reminder_id)


def _schedule(context: ContextTypes.DEFAULT_TYPE, reminder_id: int, chat_id: int,
              message: str, remind_at: datetime) -> None:
    delay_seconds = max((remind_at - datetime.utcnow()).total_seconds(), 0)
    context.job_queue.run_once(
        _fire_reminder,
        when=delay_seconds,
        chat_id=chat_id,
        data={"reminder_id": reminder_id, "message": message},
        name=f"reminder-{reminder_id}",
    )


async def remind_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: `/remind <duration> <text>`\n"
            "Example: `/remind 20m stretch your legs`\n"
            "Duration formats: `10m`, `2h`, `1d`, `1d2h30m`, or a bare number of minutes.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    duration_text = context.args[0]
    message = " ".join(context.args[1:])

    try:
        delta = parse_duration(duration_text)
    except ValueError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return

    remind_at = future_time(delta)
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    reminder_id = db.add_reminder(user_id, chat_id, message, remind_at)
    _schedule(context, reminder_id, chat_id, message, remind_at)

    logger.info("Scheduled reminder #%s for user %s in %s", reminder_id, user_id, delta)
    await update.message.reply_text(
        f"✅ I'll remind you in {humanize_delta(delta)} (reminder #{reminder_id})."
    )


async def remind_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    pending = db.list_pending_reminders(user_id)

    if not pending:
        await update.message.reply_text("You have no pending reminders.")
        return

    lines = []
    for r in pending:
        remind_at = datetime.fromisoformat(r["remind_at"])
        lines.append(f"*#{r['id']}* — {r['message']} (at {remind_at.strftime('%Y-%m-%d %H:%M UTC')})")

    await update.message.reply_markdown("⏰ *Your pending reminders:*\n\n" + "\n".join(lines))


async def remind_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: `/delreminder <id>`", parse_mode=ParseMode.MARKDOWN)
        return

    reminder_id = int(context.args[0])
    user_id = update.effective_user.id

    if db.delete_reminder(user_id, reminder_id):
        for job in context.job_queue.get_jobs_by_name(f"reminder-{reminder_id}"):
            job.schedule_removal()
        await update.message.reply_text(f"🗑 Cancelled reminder #{reminder_id}.")
    else:
        await update.message.reply_text(f"No pending reminder #{reminder_id} found for you.")


def reschedule_pending(application) -> None:
    """
    Re-arm every unfired reminder in the database against the running
    JobQueue. Called once at startup so reminders survive restarts/redeploys.
    Anything whose time already passed while the bot was offline fires
    almost immediately instead of being lost.
    """
    pending = db.list_pending_reminders()
    for r in pending:
        remind_at = datetime.fromisoformat(r["remind_at"])
        delay_seconds = max((remind_at - datetime.utcnow()).total_seconds(), 0)
        application.job_queue.run_once(
            _fire_reminder,
            when=delay_seconds,
            chat_id=r["chat_id"],
            data={"reminder_id": r["id"], "message": r["message"]},
            name=f"reminder-{r['id']}",
        )
    if pending:
        logger.info("Rescheduled %d pending reminder(s) after startup", len(pending))
