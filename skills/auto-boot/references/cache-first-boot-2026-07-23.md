# Cache-First Boot Protocol (2026-07-23)

## Why
User's instruction: "Я открыл терминал — я вижу предложение. Не 'утром будет'. Не 'сейчас запущу'. Сейчас."

The Ripple Engine runs every 15 minutes (cron job `ad859ec5289b`) and saves a JSON cache. At session start, the agent READS the cache instead of running analysis.

## The 15-Minute Pulse
- **Cron:** `cronjob action=list` → find "Ripple Engine (15min pulse)" 
- **Script:** `morning_report.py` — analyzes KC user voice + finds mature keys + generates proposal
- **Output:** `cache/latest_morning_report.json` — structured JSON with health, user_voice signal, mature_keys, top_proposal
- **Frequency:** Every 15 minutes, 24/7. No LLM needed (no_agent=true).

## Boot Behavior
Run `python scripts/auto_boot_scan.py`:
1. Health checks (principal, EE sync, heartbeat, deprecated)
2. Read `cache/latest_morning_report.json`
3. If cache < 15 min old → show with exact age ✅
4. If cache ≥ 15 min old → show stale data with "данные за N минут назад" ⚠️
5. If no cache → run one-shot `morning_report.py` → show

## First Message Format
```
Принципал, [health status]. [N] зрелых ключей. Самый сильный — [KEY] ([count] записей, maturity=[N]%). Предлагаю разблокировать его сегодня.
```

## Verifying at Test Time
To simulate a fresh boot: check that `cache/latest_morning_report.json` exists and is recent.
```bash
python -c "import json; c=json.load(open('cache/latest_morning_report.json')); print(f'{c[\"ts\"]} — {c[\"top_proposal\"][\"label\"]}')"
```
