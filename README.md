# UtilityBot 🤖

A lightweight Telegram utility bot that provides useful everyday tools directly inside Telegram.

UtilityBot includes **notes, reminders, weather information, and currency conversion**, with SQLite persistence, automated reminder scheduling, Docker support, and GitHub Actions CI.

## Features

- 📝 **Notes** — Create, view, delete, and clear personal notes
- ⏰ **Reminders** — Create scheduled reminders that persist across bot restarts
- 🌤️ **Weather** — Get current weather information for any city
- 💱 **Currency Conversion** — Convert between currencies using live exchange rates
- 🔒 **Per-user data isolation** — Users can only access their own notes and reminders
- 💾 **SQLite persistence** — Data is stored locally and persists between restarts
- 🐳 **Docker support** — Run the bot using Docker and Docker Compose
- 🧪 **Automated testing** — Unit tests with pytest
- ⚙️ **GitHub Actions CI** — Tests run automatically on pushes and pull requests
- 🛡️ **Global error handling** — Individual errors do not crash the entire bot

## Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/help` | Show available commands |
| `/cancel` | Cancel the current operation |
| `/note <text>` | Save a personal note |
| `/notes` | View saved notes |
| `/delnote <id>` | Delete a specific note |
| `/clearnotes` | Delete all saved notes |
| `/remind <duration> <text>` | Create a reminder |
| `/reminders` | View pending reminders |
| `/delreminder <id>` | Delete a reminder |
| `/weather <city>` | Get current weather information |
| `/convert <amount> <from> <to>` | Convert between currencies |

### Reminder Examples

```text
/remind 10m Take a break
/remind 2h Check the project
/remind 1d Submit the application
/remind 1d2h30m Finish the task
````

### Currency Example

```text
/convert 100 USD INR
```

## How It Works

```text
                 Telegram User
                       │
                       ▼
                Telegram Bot API
                       │
                       ▼
              python-telegram-bot
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Notes       Reminders     External APIs
          │            │          ┌──────┴──────┐
          ▼            ▼          ▼             ▼
       SQLite     APScheduler  Weather      Currency
                              OpenWeather   Exchange API
```

The bot uses **long polling**, so it does not require a public webhook URL.

## Tech Stack

* **Python 3.12**
* **python-telegram-bot 21.6**
* **SQLite**
* **APScheduler**
* **HTTPX**
* **python-dotenv**
* **OpenWeatherMap API**
* **Exchange Rate API**
* **Docker**
* **Docker Compose**
* **pytest**
* **GitHub Actions**

## Project Structure

```text
telegram-utility-bot/
│
├── bot.py
├── config.py
├── database.py
│
├── handlers/
│   ├── basic.py
│   ├── notes.py
│   ├── reminders.py
│   ├── weather.py
│   └── currency.py
│
├── utils/
│   └── timeparse.py
│
├── tests/
│   ├── test_database.py
│   └── test_timeparse.py
│
├── data/
│   └── .gitkeep
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Setup

### 1. Create a Telegram Bot

Open Telegram and message **@BotFather**.

Run:

```text
/newbot
```

Follow the instructions and copy the generated bot token.

Keep your token private.

### 2. Clone the Repository

```bash
git clone https://github.com/Rollins1989/telegram-utility-bot.git
cd telegram-utility-bot
```

### 3. Configure Environment Variables

Create a `.env` file using the example configuration:

#### Windows

```powershell
copy .env.example .env
```

#### Linux / macOS

```bash
cp .env.example .env
```

Add your Telegram bot token:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

For weather functionality, add your OpenWeatherMap API key:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
```

The currency conversion feature can work without an API key using the available keyless exchange-rate endpoint. An optional API key can also be configured:

```env
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key
```

**Never commit `.env` or API keys to GitHub.**

## Running Locally

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the bot:

```bash
python bot.py
```

## Running with Docker

Build and start the bot:

```bash
docker compose up -d --build
```

View the bot logs:

```bash
docker logs utility-bot
```

Stop the bot:

```bash
docker compose down
```

The SQLite database is stored in the `data` directory through a Docker volume, allowing notes and reminders to persist across container rebuilds.

## Testing

Install pytest:

```bash
pip install pytest
```

Run the test suite:

```bash
pytest -v
```

The project also includes a GitHub Actions workflow that automatically runs the tests on pushes and pull requests.

## Deployment

UtilityBot uses long polling and therefore requires a persistent process to remain online.

The project can be deployed using:

* VPS
* Docker-based hosting
* Railway
* Render
* Fly.io
* Your own server

The included `Dockerfile` and `docker-compose.yml` provide a ready-to-use containerized setup.

## Security

* API keys and bot tokens are stored in environment variables.
* `.env` is excluded from Git using `.gitignore`.
* User notes and reminders are isolated by Telegram user ID.
* Database files are excluded from the repository.

## Future Improvements

* More utility commands
* Weather forecasts
* Additional currency providers
* PostgreSQL support for production deployments
* Expanded test coverage
* User-configurable time zones
* Admin and usage-management features

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

```

This is the version I'd use for your **portfolio GitHub repo**.
```

