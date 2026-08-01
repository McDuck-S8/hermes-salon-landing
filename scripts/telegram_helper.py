"""Telegram API helper with proxy support."""
import httpx

PROXY = "http://127.0.0.1:10809"

> Revisit: when telegram helper logic, message formatting, or bot utilities change. Last touched: 2026-07-02.

def check_telegram_api(timeout=8):
    """Check Telegram API via HTTP proxy."""
    try:
        r = httpx.get("https://api.telegram.org", 
                      proxy=PROXY, 
                      timeout=timeout, 
                      follow_redirects=True)
        return True, r.status_code
    except Exception as e:
        return False, str(e)

def get_updates(token, limit=50):
    """Get Telegram updates via HTTP proxy."""
    try:
        r = httpx.get(f"https://api.telegram.org/bot{token}/getUpdates?limit={limit}",
                      proxy=PROXY,
                      timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def send_message(token, chat_id, text):
    """Send Telegram message via HTTP proxy."""
    try:
        r = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                       proxy=PROXY,
                       json={"chat_id": chat_id, "text": text},
                       timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}
