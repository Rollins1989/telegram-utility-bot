"""Weather feature, backed by the OpenWeatherMap free-tier API."""

import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes

from config import OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)

_ICONS = {
    "clear": "☀️", "clouds": "☁️", "rain": "🌧",
    "drizzle": "🌦", "thunderstorm": "⛈", "snow": "❄️",
    "mist": "🌫", "fog": "🌫", "haze": "🌫",
}


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not OPENWEATHER_API_KEY:
        await update.message.reply_text(
            "Weather isn't configured on this bot yet — the owner needs to "
            "set OPENWEATHER_API_KEY. (Free key: openweathermap.org/api)"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/weather <city>`\nExample: `/weather Ahmedabad`",
            parse_mode="Markdown",
        )
        return

    city = " ".join(context.args)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                },
            )
    except httpx.RequestError as exc:
        logger.warning("Weather API request failed: %s", exc)
        await update.message.reply_text(
            "⚠️ Couldn't reach the weather service right now. Try again in a bit."
        )
        return

    if resp.status_code == 404:
        await update.message.reply_text(f"Couldn't find a city called '{city}'.")
        return
    if resp.status_code != 200:
        logger.warning("Weather API returned %s: %s", resp.status_code, resp.text)
        await update.message.reply_text("⚠️ Weather service returned an error. Try again later.")
        return

    data = resp.json()
    main = data["main"]
    condition = data["weather"][0]["main"]
    description = data["weather"][0]["description"]
    icon = _ICONS.get(condition.lower(), "🌡")
    wind = data.get("wind", {}).get("speed", 0)
    name = data.get("name", city)
    country = data.get("sys", {}).get("country", "")

    text = (
        f"{icon} *{name}{', ' + country if country else ''}*\n\n"
        f"{description.capitalize()}\n"
        f"🌡 Temp: {main['temp']:.1f}°C (feels like {main['feels_like']:.1f}°C)\n"
        f"💧 Humidity: {main['humidity']}%\n"
        f"💨 Wind: {wind} m/s"
    )
    await update.message.reply_markdown(text)
