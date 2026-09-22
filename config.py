"""Application configuration and logging setup."""
from __future__ import annotations
import logging
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def validate_config() -> None:
    """Fail fast when required runtime configuration is missing."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. Create a .env file from .env.example."
        )
    if len(TELEGRAM_BOT_TOKEN.split(":")) != 2:
        raise RuntimeError("TELEGRAM_BOT_TOKEN does not look like a valid Telegram bot token.")

def setup_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
