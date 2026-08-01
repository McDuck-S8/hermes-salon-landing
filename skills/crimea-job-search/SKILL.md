---
name: crimea-job-search
description: "CLI tool for searching jobs on hh.ru in Crimea/Simferopol. Async hh.ru API client with SQLite cache, filtering, and multiple output formats. Designed for autonomous operation via cron."
category: productivity
version: 1.0.0
author: Hermes Agent
tags:
  - hh-ru
  - job-search
  - crimea
  - simferopol
  - async
  - cli
  - telegram
platforms:
  - linux
  - macos
  - windows
dependencies:
  - python >= 3.11
  - aiohttp >= 3.9
  - pyyaml >= 6.0
  - python-dotenv >= 1.0
---

# Crimea Job Search Skill

## Purpose
Autonomous job search CLI for hh.ru focused on Crimea region (Simferopol, Sevastopol, Kerch, Evpatoria, Feodosia). Built for integration with Hermes Agent's autonomous income pipeline.

## Architecture

### Components
- **HHApiClient** — Async hh.ru API client with rate limiting (200 req/min)
- **VacancyCache** — SQLite deduplication cache with TTL and max entries
- **VacancyFilter** — Criteria filtering (keywords, salary, experience, schedule, employment, city)
- **JobSearchCLI** — Main entry point with search, daemon, and test modes

### Data Flow
```
Search params → HHApiClient → Parse → Cache check → Filter → Output
                                      ↓
                              Save new vacancies
```

## Usage

### CLI Tool
```bash
# Install dependencies
pip install aiohttp pyyaml python-dotenv

# Test API connection
python skills/crimea-job-search/scripts/search.py --test

# Single search (default: Python backend in Simferopol, 80k+ RUR)
python skills/crimea-job-search/scripts/search.py \
  --keywords "python,fastapi,django" \
  --city "Симферополь" \
  --salary-min 80000 \
  --experience "between1And3,between3And6" \
  --schedule "remote,flexible" \
  --employment "full,part" \
  --output table

# JSON output for programmatic use
python skills/crimea-job-search/scripts/search.py \
  --keywords "python" \
  --output json \
  --file results.json

# Daemon mode (continuous polling)
python skills/crimea-job-search/scripts/search.py \
  --daemon \
  --interval 3600 \
  --keywords "python,backend"

# New only mode (skip cached)
python skills/crimea-job-search/scripts/search.py \
  --new-only \
  --output json
```

### Required Environment
```bash
# .env file (optional - for Telegram notifications)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=737433175
```

### Configuration
```yaml
# config.yaml
hh_api:
  user_agent: "Your-Agent/1.0"
  rate_limit: 200
  timeout: 30

search:
  default_area: 1002
  cities:
    - "Симферополь"
    - "Севастополь"
  default_keywords: "python,django,fastapi,backend,api"
  salary_min: 80000
  experience: "between1And3,between3And6"
  schedule: "remote,flexible"
  employment: "full,part"

cache:
  db_path: "cache/vacancies.db"
  ttl_hours: 24
  max_entries: 10000

notify:
  telegram_enabled: true
  telegram_chat_id: "737433175"
```

## hh.ru API Parameters Reference

| Parameter | Values | Description |
|-----------|--------|-------------|
| `area` | 1002 | Crimea region ID |
| `experience` | noExperience, between1And3, between3And6, moreThan6 | Experience level |
| `schedule` | fullDay, shift, flexible, remote, flyInFlyOut | Work schedule |
| `employment` | full, part, project, volunteer, probation | Employment type |
| `order_by` | relevance, publication_time, salary_desc, salary_asc | Sort order |
| `search_field` | name, description, company_name | Search fields |

## Output Formats

### Table (default)
```
 1. Python Developer (Django/FastAPI)  | Company Name         | Simferopol       |         80 000 - 120 000 RUR | between1And3  🆕
 2. Backend Python Engineer            | Another Company      | Севастополь      |              от 100 000 RUR | between3And6
```

### JSON
```json
[
  {
    "id": "12345678",
    "name": "Python Developer",
    "company": "Company Name",
    "city": "Симферополь",
    "salary_from": 80000,
    "salary_to": 120000,
    "currency": "RUR",
    "experience": "between1And3",
    "schedule": "remote",
    "employment": "full",
    "description": "We need...",
    "skills": ["Python", "Django", "PostgreSQL"],
    "published_at": "2026-07-18T10:30:00+00:00",
    "url": "https://hh.ru/vacancy/12345678",
    "is_new": true
  }
]
```

### CSV
```csv
id,name,company,city,salary_from,salary_to,currency,experience,schedule,employment,description,skills,published_at,url,is_new
12345678,"Python Developer","Company Name","Симферополь",80000,120000,"RUR","between1And3","remote","full","We need...","[\"Python\", \"Django\"]","2026-07-18T10:30:00+00:00","https://hh.ru/vacancy/12345678",true
```

## Integration with Hermes

### Cron Job (daily at 9 AM)
```json
{
  "name": "crimea-job-search-daily",
  "schedule": "0 9 * * *",
  "prompt": "Run job search for Python backend positions in Crimea",
  "skills": ["crimea-job-search"],
  "script": "skills/crimea-job-search/scripts/search.py --new-only --output json --file reports/jobs_$(date +%Y%m%d).json"
}
```

### Telegram Bot Notification
```python
# Add to search.py after _output()
if self.config.get("notify", {}).get("telegram_enabled"):
    await self._notify_telegram(vacancies)
```

## Pitfalls & Lessons Learned

### ❌ Don't filter duplicates by description
**Wrong:** Drop proposals with similar keywords — "I already saw this"
**Right:** Count repetitions → if >3 without artifact → `REPEATED_3X` goal_queue task

### ❌ Don't ignore rate limits
hh.ru returns 429 after ~200 req/min. Use semaphore + Retry-After header.

### ✅ Use area=1002 for Crimea
Searching "Крым" in text is unreliable. Official area ID = 1002.

### ✅ Cache with SQLite
Memory cache lost on restart. SQLite persists + supports `is_new` flag.

### ✅ Search remote + flexible schedules
Crimea market has few local tech jobs. Remote opens 10x more opportunities.

### ✅ Salary filter server-side
`salary` + `only_with_salary=true` reduces payload 10x vs client-side filter.

## Verification
```bash
# Test API
python scripts/search.py --test

# Dry run
python scripts/search.py --keywords python --output table

# Full cycle
python scripts/search.py --new-only --output json --file test_output.json
```

## Changelog
- **2026-07-18 v1.0.0** — Initial release. Async client, SQLite cache, filtering, table/JSON/CSV output, daemon mode.