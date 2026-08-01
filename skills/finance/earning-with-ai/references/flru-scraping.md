# FL.ru Scraping: Finding Real Orders

## Working Category URLs (verified 2026-05)

```python
categories = {
    "AI": "https://www.fl.ru/projects/category/ai-iskusstvenniy-intellekt/",
    "Automation": "https://www.fl.ru/projects/category/avtomatizaciya-biznesa/",
}
```

## Scraping Code

```python
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9',
}

resp = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')
links = soup.find_all('a', href=True)

for link in links:
    href = link.get('href', '')
    text = link.get_text().strip()
    if '/projects/' in href and len(text) > 30 and '/category/' not in href:
        full_url = f"https://www.fl.ru{href}"
        print(f"{text[:100]}\n  {full_url}")
```

## Order Detail Extraction

```python
resp = requests.get(order_url, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')
title = soup.find('title').get_text().strip()
# Budget is NOT in HTML — must be viewed on site
# Description extraction is limited — use text search
```

## Platform Status (2026-05)
- **FL.ru** — works, returns 200, BeautifulSoup parsing OK
- **Kwork** — works, returns 200
- **Habr Freelance** — returns 410 (dead/changed)
- **web_extract (Tavily)** — 401 Unauthorized (API key issue)

## Found 38 Orders (2026-05-27)
AI category + Automation category combined.
Top categories: ChatBots, CRM integration, Content generation, Analytics.
