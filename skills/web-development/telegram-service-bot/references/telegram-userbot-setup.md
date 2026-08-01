# Telegram Userbot API Setup (my.telegram.org)

For monitoring business chats, outreach automation, and competitive analysis using a real Telegram account (not bot API).

## Why Userbot vs Bot API
- **Bot API**: limited to bot interactions, can't read group messages unless added
- **Userbot (Pyrogram/Telethon)**: acts as a real user, can join groups, read messages, monitor competitors

## Setup at my.telegram.org

1. Go to https://my.telegram.org
2. Log in with phone number + code from Telegram
3. "API development tools"
4. Fill form:
   - **App title**: any name (e.g. "Hermes Agent")
   - **Short name**: lowercase, no spaces (e.g. "hermesagent")
   - **URL**: leave empty
   - **Platform**: Desktop
   - **Description**: leave empty
5. Solve CAPTCHA ("I'm not a robot")
6. Click "Create application"
7. Save: **api_id** (number) and **api_hash** (string)

## Pyrogram Quick Start

```python
from pyrogram import Client

api_id = 12345678  # from my.telegram.org
api_hash = "abcdef1234567890abcdef1234567890"

app = Client("my_account", api_id=api_id, api_hash=api_hash)

with app:
    # Join a group
    app.join_chat("salon_chat_link")
    
    # Read recent messages
    for msg in app.get_chat_history("salon_chat", limit=50):
        print(f"{msg.from_user.first_name}: {msg.text}")
    
    # Send DM
    app.send_message("username", "Привет! Видел ваш салон...")
```

## Install
```bash
pip install pyrogram tgcrypto
```

## Pitfalls
- **Rate limits**: Telegram limits joins to ~20 groups/day, messages to ~30 DMs/hour
- **Account ban risk**: aggressive automation = phone ban. Use delays, don't spam
- **Session file**: Pyrogram creates `.session` file — treat like a password, don't share
- **Proxy**: In Russia, need SOCKS5 proxy for Telegram access
- **CAPTCHA on my.telegram.org**: sometimes shows image CAPTCHA, not just checkbox — solve manually
- **my.telegram.org login**: sometimes doesn't send code immediately, retry after 30s
- **api_id is numeric**: don't confuse with api_hash (string). api_id goes without quotes in Python
