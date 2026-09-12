"""
Lightweight persistence layer.

Uses plain sqlite3 (no ORM) since the schema is small and this keeps the
project dependency-light and easy to read for anyone reviewing the code.
A single module-level connection is reused; sqlite3 objects are safe to
share within one process as long as writes are quick, which they are here.
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from config import DATABASE_PATH

os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


_conn = _connect()


@contextmanager
def get_cursor():
    """Context manager that commits on success and rolls back on error."""
    cur = _conn.cursor()
    try:
        yield cur
        _conn.commit()
    except Exception:
        _conn.rollback()
        raise
    finally:
        cur.close()


def init_db() -> None:
    with get_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                fired INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_reminders_pending "
            "ON reminders (fired, remind_at)"
        )


# ---------- Notes ----------

def add_note(user_id: int, content: str) -> int:
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO notes (user_id, content, created_at) VALUES (?, ?, ?)",
            (user_id, content, datetime.now(timezone.utc).isoformat()),
        )
        return cur.lastrowid


def list_notes(user_id: int) -> list[sqlite3.Row]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, content, created_at FROM notes WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
        return cur.fetchall()


def delete_note(user_id: int, note_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id)
        )
        return cur.rowcount > 0


def clear_notes(user_id: int) -> int:
    with get_cursor() as cur:
        cur.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
        return cur.rowcount


# ---------- Reminders ----------

def add_reminder(user_id: int, chat_id: int, message: str, remind_at: datetime) -> int:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO reminders (user_id, chat_id, message, remind_at, created_at, fired)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                chat_id,
                message,
                remind_at.isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return cur.lastrowid


def list_pending_reminders(user_id: Optional[int] = None) -> list[sqlite3.Row]:
    with get_cursor() as cur:
        if user_id is None:
            cur.execute(
                "SELECT * FROM reminders WHERE fired = 0 ORDER BY remind_at ASC"
            )
        else:
            cur.execute(
                "SELECT * FROM reminders WHERE fired = 0 AND user_id = ? ORDER BY remind_at ASC",
                (user_id,),
            )
        return cur.fetchall()


def mark_fired(reminder_id: int) -> None:
    with get_cursor() as cur:
        cur.execute("UPDATE reminders SET fired = 1 WHERE id = ?", (reminder_id,))


def delete_reminder(user_id: int, reminder_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM reminders WHERE id = ? AND user_id = ?",
            (reminder_id, user_id),
        )
        return cur.rowcount > 0
