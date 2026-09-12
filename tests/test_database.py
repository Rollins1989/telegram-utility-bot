"""
Tests for database.py, run against a throwaway sqlite file so they never
touch real bot data.
"""

import os
import sys

os.environ.setdefault("DATABASE_PATH", "tests/_test.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timedelta

import database as db


@pytest.fixture(autouse=True)
def clean_db():
    db.init_db()
    yield
    # Wipe tables between tests for isolation
    with db.get_cursor() as cur:
        cur.execute("DELETE FROM notes")
        cur.execute("DELETE FROM reminders")


def test_add_and_list_notes():
    db.add_note(user_id=1, content="buy milk")
    db.add_note(user_id=1, content="call mom")
    db.add_note(user_id=2, content="someone else's note")

    notes = db.list_notes(user_id=1)
    assert len(notes) == 2
    assert {n["content"] for n in notes} == {"buy milk", "call mom"}


def test_delete_note_only_own():
    note_id = db.add_note(user_id=1, content="temp")
    assert db.delete_note(user_id=2, note_id=note_id) is False
    assert db.delete_note(user_id=1, note_id=note_id) is True
    assert db.list_notes(user_id=1) == []


def test_clear_notes():
    db.add_note(user_id=1, content="a")
    db.add_note(user_id=1, content="b")
    count = db.clear_notes(user_id=1)
    assert count == 2
    assert db.list_notes(user_id=1) == []


def test_add_and_list_pending_reminders():
    remind_at = datetime.utcnow() + timedelta(minutes=5)
    rid = db.add_reminder(user_id=1, chat_id=100, message="stretch", remind_at=remind_at)

    pending = db.list_pending_reminders(user_id=1)
    assert len(pending) == 1
    assert pending[0]["id"] == rid
    assert pending[0]["message"] == "stretch"


def test_mark_fired_removes_from_pending():
    remind_at = datetime.utcnow() + timedelta(minutes=5)
    rid = db.add_reminder(user_id=1, chat_id=100, message="stretch", remind_at=remind_at)
    db.mark_fired(rid)
    assert db.list_pending_reminders(user_id=1) == []


def test_delete_reminder_only_own():
    remind_at = datetime.utcnow() + timedelta(minutes=5)
    rid = db.add_reminder(user_id=1, chat_id=100, message="stretch", remind_at=remind_at)
    assert db.delete_reminder(user_id=2, reminder_id=rid) is False
    assert db.delete_reminder(user_id=1, reminder_id=rid) is True
