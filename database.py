"""SQLite persistence layer for notes and reminders."""
from __future__ import annotations
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator
from config import DATABASE_PATH

os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn

@contextmanager
def get_cursor() -> Iterator[sqlite3.Cursor]:
    conn = _connect()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def init_db() -> None:
    with get_cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            fired INTEGER NOT NULL DEFAULT 0
        )""")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id, id DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reminders_pending ON reminders(fired, remind_at)")

def add_note(user_id: int, content: str) -> int:
    with get_cursor() as cur:
        cur.execute("INSERT INTO notes(user_id, content, created_at) VALUES (?, ?, ?)",
                    (user_id, content, datetime.now(timezone.utc).isoformat()))
        return int(cur.lastrowid)

def list_notes(user_id: int) -> list[sqlite3.Row]:
    with get_cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM notes WHERE user_id = ? ORDER BY id DESC", (user_id,))
        return cur.fetchall()

def delete_note(user_id: int, note_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        return cur.rowcount > 0

def clear_notes(user_id: int) -> int:
    with get_cursor() as cur:
        cur.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
        return cur.rowcount

def add_reminder(user_id: int, chat_id: int, message: str, remind_at: datetime) -> int:
    if remind_at.tzinfo is None:
        raise ValueError("remind_at must be timezone-aware")
    with get_cursor() as cur:
        cur.execute("""INSERT INTO reminders(user_id, chat_id, message, remind_at, created_at, fired)
                       VALUES (?, ?, ?, ?, ?, 0)""",
                    (user_id, chat_id, message, remind_at.astimezone(timezone.utc).isoformat(),
                     datetime.now(timezone.utc).isoformat()))
        return int(cur.lastrowid)

def list_pending_reminders(user_id: int | None = None) -> list[sqlite3.Row]:
    with get_cursor() as cur:
        if user_id is None:
            cur.execute("SELECT * FROM reminders WHERE fired = 0 ORDER BY remind_at ASC")
        else:
            cur.execute("SELECT * FROM reminders WHERE fired = 0 AND user_id = ? ORDER BY remind_at ASC", (user_id,))
        return cur.fetchall()

def mark_fired(reminder_id: int) -> None:
    with get_cursor() as cur:
        cur.execute("UPDATE reminders SET fired = 1 WHERE id = ?", (reminder_id,))

def delete_reminder(user_id: int, reminder_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM reminders WHERE id = ? AND user_id = ? AND fired = 0", (reminder_id, user_id))
        return cur.rowcount > 0
