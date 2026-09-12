"""
Central configuration for the bot.

All secrets are loaded from environment variables (via a local .env file
in development, or real environment variables in production). Nothing
sensitive is ever hard-coded here.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# --- Required ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Optional (features degrade gracefully if missing) ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")  # exchangerate-api.com (free tier)

# --- Misc ---
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def validate_config() -> None:
    """Fail fast and loudly if required configuration is missing."""
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. Create a .env file (see .env.example) "
            "or export it in your environment before starting the bot."
        )


def setup_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    )
    # Quiet down noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
