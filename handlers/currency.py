"""
Currency conversion feature.

Uses the free exchangerate-api.com endpoint, which doesn't require a key
for the `/v4/latest/<BASE>` route (rate-limited, but fine for personal use).
If EXCHANGE_RATE_API_KEY is set, the paid v6 endpoint is used instead for
higher limits — the handler works either way.
"""

import logging
import httpx
from telegram import Update
from telegram.ext import ContextTypes

from config import EXCHANGE_RATE_API_KEY

logger = logging.getLogger(__name__)


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 3:
        await update.message.reply_text(
            "Usage: `/convert <amount> <from> <to>`\nExample: `/convert 100 USD INR`",
            parse_mode="Markdown",
        )
        return

    amount_raw, from_cur, to_cur = context.args
    from_cur, to_cur = from_cur.upper(), to_cur.upper()

    try:
        amount = float(amount_raw)
    except ValueError:
        await update.message.reply_text("Amount must be a number, e.g. `100`.", parse_mode="Markdown")
        return

    try:
        rate = await _get_rate(from_cur, to_cur)
    except _CurrencyError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return
    except httpx.RequestError as exc:
        logger.warning("Currency API request failed: %s", exc)
        await update.message.reply_text(
            "⚠️ Couldn't reach the exchange rate service right now. Try again in a bit."
        )
        return

    converted = amount * rate
    await update.message.reply_text(
        f"💱 {amount:,.2f} {from_cur} = *{converted:,.2f} {to_cur}*\n"
        f"(1 {from_cur} = {rate:.4f} {to_cur})",
        parse_mode="Markdown",
    )


class _CurrencyError(Exception):
    pass


async def _get_rate(from_cur: str, to_cur: str) -> float:
    if EXCHANGE_RATE_API_KEY:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{from_cur}/{to_cur}"
    else:
        url = f"https://open.er-api.com/v6/latest/{from_cur}"

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise _CurrencyError("Exchange rate service returned an error. Try again later.")

    data = resp.json()

    if EXCHANGE_RATE_API_KEY:
        if data.get("result") != "success":
            raise _CurrencyError(f"Couldn't get a rate for {from_cur} → {to_cur}. Check the currency codes.")
        return float(data["conversion_rate"])
    else:
        rates = data.get("rates", {})
        if to_cur not in rates:
            raise _CurrencyError(f"Couldn't get a rate for {from_cur} → {to_cur}. Check the currency codes.")
        return float(rates[to_cur])
