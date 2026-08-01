# TikTok Farm Architecture — Implementation (2026-07-21)

## File: `scripts/tiktok_farm.py`

### Modules

```
TikTokFarmOrchestrator        # Главный класс
├── FarmDB                    # SQLite persistence
│   ├── accounts              # Аккаунты (fingerprint, proxy, cookies)
│   ├── posts_queue           # Очередь публикаций
│   └── health_log            # Лог проверок здоровья
├── CaptchaHandler            # CAPTCHA detection + 2captcha solve
└── warmup()                  # Playwright scroll + like

CLI:
  --create --geo US     → создаёт аккаунт
  --list                → список аккаунтов
  --post <id> <video>   → пост с сессией
  --queue [dir]         → добавить все mp4 в очередь
  --process-queue       → обработать очередь
  --warmup <id>         → прогрев
  --health [id]         → здоровье фермы
```

### SQLite Schema (cache/tiktok_farm.db)

```sql
accounts     — id, username, geo, fingerprint_json, proxy, status, cookies_path, posts_count
posts_queue  — account_id, video_path, caption, hashtags, status, posted_at, error
health_log   — account_id, check_type, result, detail, checked_at
```

### Session Persistence

- Playwright `storage_state` → `cache/tiktok_sessions/<id>/state.json`
- При старте: `new_context(storage_state=...)`
- После успешного логина: `context.storage_state()` → write

### CAPTCHA Flow

1. `page.locator()` поиск известных селекторов `#captcha-container`, `.captcha-verify-container`
2. Если найден → 2captcha API solve через `twocaptcha-python`
3. Если solve failed → manual fallback

### Anti-ban дефолты

- Между постами: 15-30 мин
- Между одинаковыми аккаунтами: 30+ мин  
- Warmup: scroll 3-8s между свайпами, 20% chance like
