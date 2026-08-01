# Telegram Digest Pipeline Architecture

## Chain: collect → digest → deliver

```
[Cron 9:00 AM]
    │
    ▼
collect_channels.py --channels "ch1,ch2" --output /tmp/digest.json
    │
    ▼
generate_digest.py --input /tmp/digest.json --style telegram
    │
    ▼
[Hermes agent sends digest to user via Telegram]
```

## Script Responsibilities

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `auth.py` | interactive | session file | One-time Telethon auth |
| `collect_channels.py` | channel list + hours | JSON | Raw message collection |
| `generate_digest.py` | JSON | markdown | Format digest |
| `digest_pipeline.py` | channel list | markdown | All-in-one (for cron) |

## Cron Setup

```python
# Via hermes cron tool:
cronjob(action='create',
    name='telegram-daily-digest',
    schedule='0 9 * * *',
    script='telegram-digest/scripts/digest_pipeline.py --channels "openai,anthropic,deepseek" --hours 24 --style telegram',
    no_agent=True,
    deliver='origin')
```

## .env Location Resolution

Always use HERMES_HOME, never parent chain:
```python
env_path = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / '.env'
session_dir = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes')) / 'sessions'
```

## Channel List Management

Default channels stored in `templates/channels.txt`. User can edit or pass custom list via `--channels`.
