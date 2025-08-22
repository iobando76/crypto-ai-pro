import httpx
from ..config import settings
async def send_telegram_message(text: str):
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return None
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = { "chat_id": settings.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML" }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, data=payload)
        return r.json()
