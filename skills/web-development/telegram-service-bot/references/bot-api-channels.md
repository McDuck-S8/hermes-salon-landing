# Telegram Bot API: Channels Interaction

## Critical: Adding Bot as Admin ≠ Visibility

When you add a bot as admin to a Telegram channel:
- Bot CAN send messages to the channel (if it has the chat_id)
- Bot does NOT see the channel in `getUpdates` automatically
- `getChat(@username)` may return 404 until the bot has interacted with the channel

## How to Get Channel Access

### Option 1: Forward a message from the channel to the bot
After the bot is admin, forward any channel message to the bot in DM. The forwarded message contains the channel chat_id in `forward_from_chat`.

### Option 2: Use `getUpdates` after bot receives a channel post
If the bot is admin and the channel sends a post, `getUpdates` will include `channel_post` entries with the chat_id.

### Option 3: Known chat_id
If you know the channel username, try `getChat?chat_id=@channel_username`. Works if:
- Bot is admin in the channel
- Channel is public (has @username)
- At least one interaction has occurred

### Option 4: Hardcode chat_id
Once you know the chat_id (e.g., `-1001234567890`), hardcode it in config. The bot can always send to a known chat_id if it has admin rights.

## Sending to Channels

```bash
# By @username (public channels only, bot must be admin)
curl "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d chat_id="@channel_username" \
  -d text="Hello from bot"

# By chat_id (always works if bot is admin)
curl "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d chat_id="-1001234567890" \
  -d text="Hello from bot"
```

## Token Validation

Telegram bot tokens have format: `<bot_id>:<secret>` (colon is mandatory).
Example: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

Quick validation:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getMe"
# Returns {"ok":true,"result":{"id":...,"username":"..."}}
# If 404 → token is invalid/corrupted
```

## Common Pitfalls

- **404 on getMe**: Token is corrupted or wrong format. Check for missing colon, extra whitespace, truncated value.
- **"Not Found" on getChat**: Bot not admin in channel, or channel is private without @username, or no prior interaction.
- **Channel not in getUpdates**: Normal behavior. Channels only appear in updates when the bot receives channel_post events (bot must be admin).
- **Hermes gateway not seeing channels**: Gateway only knows chats from its update stream. For channels, the bot needs to receive at least one update from the channel. Restart gateway after adding bot as admin.
