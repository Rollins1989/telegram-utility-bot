# UtilityBot 🤖

A small, well-structured Telegram bot that bundles a few genuinely useful
tools into one chat: notes, reminders, weather, and currency conversion.

Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
(async, v21), SQLite for persistence, and APScheduler-backed reminders that
survive a bot restart.

```
/note buy milk           /remind 20m stretch       /weather Ahmedabad
/notes                   /reminders                /convert 100 USD INR
```

## Features

| Command | What it does |
|---|---|
| `/start`, `/help` | Onboarding and a full command reference |
| `/note <text>` | Save a note |
| `/notes` | List your saved notes |
| `/delnote <id>` | Delete a note |
| `/clearnotes` | Delete all your notes |
| `/remind <duration> <text>` | Set a reminder — `10m`, `2h`, `1d`, `1d2h30m` |
| `/reminders` | List your pending reminders |
| `/delreminder <id>` | Cancel a reminder |
| `/weather <city>` | Current conditions for any city |
| `/convert <amount> <from> <to>` | Exchange rate conversion, e.g. `100 USD INR` |

Notes and reminders are private per Telegram user — no one can see or
delete another user's data.

## Why this is more than a toy script

- **Reminders survive restarts.** They're written to SQLite before being
  scheduled, and re-armed automatically on startup — a redeploy never
  silently drops one.
- **Per-user data isolation** is enforced at the database layer, not just
  the UI.
- **Graceful degradation.** Weather and currency features fail with a
  clear, friendly message (not a crash) if an API key is missing or an
  upstream service is down.
- **A global error handler** means one bad update can't take the bot down.
- **Tested.** Core logic (duration parsing, database operations) has unit
  tests, run automatically in CI on every push.

## Project structure

```
telegram-utility-bot/
├── bot.py                 # Entry point — wires handlers together
├── config.py               # Env-based configuration
├── database.py              # SQLite persistence layer
├── handlers/
│   ├── basic.py            # /start, /help, /cancel
│   ├── notes.py             # Notes feature
│   ├── reminders.py         # Reminders + APScheduler integration
│   ├── weather.py           # OpenWeatherMap integration
│   └── currency.py          # Exchange rate conversion
├── utils/
│   └── timeparse.py         # Parses "10m" / "2h" / "1d2h30m" style durations
├── tests/                  # pytest unit tests
├── .github/workflows/ci.yml # Runs tests on every push/PR
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup

### 1. Create your bot

Message [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`,
and copy the token it gives you.

### 2. Configure

```bash
git clone https://github.com/<your-username>/telegram-utility-bot.git
cd telegram-utility-bot
cp .env.example .env
```

Edit `.env` and paste in your token:

```
TELEGRAM_BOT_TOKEN=123456:ABC-your-token-here
```

The weather and currency features are optional:
- `OPENWEATHER_API_KEY` — free key from [openweathermap.org/api](https://openweathermap.org/api). Without it, `/weather` replies with a clear "not configured" message instead of failing silently.
- `EXCHANGE_RATE_API_KEY` — optional; `/convert` works without one via a free keyless endpoint, but a key raises the rate limit.

### 3a. Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

### 3b. Run with Docker

```bash
docker compose up -d --build
```

The SQLite database is persisted to `./data` on the host via a volume, so
it survives container rebuilds.

## Running tests

```bash
pip install pytest
pytest -v
```

## Deploying for real

This bot uses long polling, so it works anywhere that can run a persistent
Python process — a small VPS, [Railway](https://railway.app),
[Render](https://render.com), [Fly.io](https://fly.io), or your own server.
The included `Dockerfile` and `docker-compose.yml` work as-is on any of
these. There's no webhook or public URL to set up.

## Extending it

Each feature is a self-contained module in `handlers/`. To add a new one:

1. Write a handler function in `handlers/your_feature.py`.
2. Register it with `application.add_handler(CommandHandler(...))` in `bot.py`.
3. Add it to the `/help` text in `handlers/basic.py`.

## License

MIT — see [LICENSE](LICENSE).
