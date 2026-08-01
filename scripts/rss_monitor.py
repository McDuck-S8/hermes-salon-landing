#!/usr/bin/env python3
"""
RSS/Atom Feed Monitor — fetches CPA, AI, and tech feeds, caches results, delivers digest.
Matches the specification in skills/automation/rss-monitoring-cron/SKILL.md
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser

# ─── Configuration ───
FEEDS = [
    {
        "id": "partnerkin",
        "url": "https://partnerkin.com/rss",
        "topic": "cpa-news",
        "method": "scrape_homepage",
        "keywords": ["беттинг", "гембл", "слот", "казино", "кейс", "нутра", "лендинг", "seo", "трафик", "офер", "оффер", "cpa", "roi"],
    },
    {
        "id": "affiliatefix",
        "url": "https://www.affiliatefix.com/forums/-/index.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_affiliatemarketing",
        "url": "https://www.reddit.com/r/affiliatemarketing/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_passive_income",
        "url": "https://www.reddit.com/r/passive_income/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_crypto",
        "url": "https://www.reddit.com/r/CryptoCurrency/.rss",
        "topic": "crypto",
        "method": "rss",
    },
    {
        "id": "reddit_entrepreneur",
        "url": "https://www.reddit.com/r/Entrepreneur/.rss",
        "topic": "business",
        "method": "rss",
    },
    {
        "id": "reddit_ppa",
        "url": "https://www.reddit.com/r/PPC/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_adtech",
        "url": "https://www.reddit.com/r/adtech/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_growthhacking",
        "url": "https://www.reddit.com/r/growthhacking/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_digital_marketing",
        "url": "https://www.reddit.com/r/digital_marketing/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_seo",
        "url": "https://www.reddit.com/r/SEO/.rss",
        "topic": "cpa-news",
        "method": "rss",
    },
    {
        "id": "reddit_sportsbetting",
        "url": "https://www.reddit.com/r/sportsbetting/.rss",
        "topic": "gambling",
        "method": "rss",
    },
    {
        "id": "reddit_beermoney",
        "url": "https://www.reddit.com/r/beermoney/.rss",
        "topic": "side-income",
        "method": "rss",
    },
    {
        "id": "reddit_workonline",
        "url": "https://www.reddit.com/r/workonline/.rss",
        "topic": "side-income",
        "method": "rss",
    },
    {
        "id": "reddit_juststart",
        "url": "https://www.reddit.com/r/juststart/.rss",
        "topic": "affiliate-seo",
        "method": "rss",
    },
    {
        "id": "reddit_sidehustle",
        "url": "https://www.reddit.com/r/sidehustle/.rss",
        "topic": "side-income",
        "method": "rss",
    },
]

CACHE_DIR = Path(__file__).parent.parent / "cache" / "rss_monitor"
CACHE_FILE = CACHE_DIR / "latest.json"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Only keep articles from the last 7 days
MAX_AGE_DAYS = 7
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)


def log(msg: str, level: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{level}] {timestamp} — {msg}", file=sys.stderr)


def parse_date(date_str: str) -> datetime | None:
    """Parse date string to datetime with timezone."""
    if not date_str:
        return None
    try:
        dt = dateutil_parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def is_recent(entry: dict[str, Any]) -> bool:
    """Check if entry is within the cutoff date."""
    published = entry.get("published", "")
    if not published:
        return True  # Keep entries without dates
    dt = parse_date(published)
    if dt is None:
        return True  # Keep entries with unparseable dates
    return dt >= CUTOFF_DATE


def fetch_rss(url: str) -> list[dict[str, Any]]:
    """Fetch and parse RSS/Atom feed."""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        entries = []
        for entry in feed.entries:
            entries.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "published": entry.get("published", entry.get("updated", "")),
                "summary": (entry.get("summary", entry.get("description", ""))[:500]).strip(),
            })
        return entries
    except Exception as e:
        log(f"RSS fetch failed for {url}: {e}", "ERROR")
        return []


def scrape_partnerkin() -> list[dict[str, Any]]:
    """Scrape Partnerkin homepage for articles (RSS is dead)."""
    entries = []
    base_url = "https://partnerkin.com"
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(base_url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        # Find article links in blog/tribuna/stati/kejsy/intervyu sections
        article_links = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if any(path in href for path in ["/blog/", "/tribuna/", "/stati/", "/kejsy/", "/intervyu/"]):
                full_url = urljoin(base_url, href)
                article_links.add(full_url)

        log(f"Partnerkin: found {len(article_links)} article links")

        for url in list(article_links)[:15]:  # Limit to 15 articles
            try:
                time.sleep(0.5)  # Be polite
                resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, "html.parser")

                # Title
                title_elem = soup.find("h1") or soup.find("title")
                title = title_elem.get_text(strip=True) if title_elem else url

                # Date - try meta tags first
                published = ""
                for meta in soup.find_all("meta"):
                    if meta.get("property") in ("article:published_time", "og:published_time") or meta.get("name") == "date":
                        published = meta.get("content", "")
                        break

                # Summary - first paragraph
                summary = ""
                for p in soup.find_all("p"):
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        summary = text[:500]
                        break

                entries.append({
                    "title": title,
                    "url": url,
                    "published": published,
                    "summary": summary,
                })
            except Exception as e:
                log(f"Partnerkin article fetch failed for {url}: {e}", "WARN")

    except Exception as e:
        log(f"Partnerkin homepage scrape failed: {e}", "ERROR")

    return entries


def categorize_entry(entry: dict[str, Any], feed_topic: str, keywords: list[str] = None) -> dict[str, Any]:
    """Add topic and keyword tags to entry."""
    entry = entry.copy()
    entry["topic"] = feed_topic
    text = f"{entry['title']} {entry['summary']}".lower()

    if keywords:
        matched = [kw for kw in keywords if kw.lower() in text]
        if matched:
            entry["tags"] = matched

    return entry


def is_notable(entry: dict[str, Any]) -> bool:
    """Determine if entry is notable for digest."""
    # Always notable if it has tags (keyword match)
    if entry.get("tags"):
        return True
    # Notable if from priority topics
    if entry.get("topic") in ("cpa-news", "ai"):
        return True
    return False


def fetch_all_feeds() -> dict[str, list[dict[str, Any]]]:
    """Fetch all configured feeds."""
    results = {}
    for feed in FEEDS:
        feed_id = feed["id"]
        log(f"Fetching {feed_id} ({feed['topic']})…")

        if feed["method"] == "scrape_homepage":
            entries = scrape_partnerkin()
        else:
            entries = fetch_rss(feed["url"])

        # Categorize
        categorized = [
            categorize_entry(e, feed["topic"], feed.get("keywords"))
            for e in entries
        ]
        # Filter by date
        recent = [e for e in categorized if is_recent(e)]
        log(f"  OK: {len(categorized)} entries, {len(recent)} recent (last {MAX_AGE_DAYS} days)")
        results[feed_id] = recent[:10]  # Cap per feed

    return results


def load_cache() -> dict[str, Any]:
    """Load previous cache."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"timestamp": "", "feeds": {}}


def save_cache(data: dict[str, Any]) -> None:
    """Save cache to file."""
    CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_digest(feed_results: dict[str, list[dict]]) -> str:
    """Build human-readable digest of notable entries."""
    notable = []
    for feed_id, entries in feed_results.items():
        for entry in entries:
            if is_notable(entry):
                notable.append(entry)

    if not notable:
        return "[rss_monitor] No notable articles this run."

    lines = [f"[rss_monitor] Notable articles ({len(notable)}):", ""]
    for entry in notable:
        tags = f" [{', '.join(entry['tags'])}]" if entry.get("tags") else ""
        lines.append(f"• [{entry['topic'].upper()}] {entry['title']}{tags}")
        lines.append(f"  {entry['url']}")
        if entry.get("summary"):
            lines.append(f"  {entry['summary'][:200]}…")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    log("=== RSS Monitor starting ===")
    start = time.time()

    # Fetch all feeds
    feed_results = fetch_all_feeds()

    # Load previous cache for dedup (optional)
    old_cache = load_cache()
    old_urls = set()
    for feed_data in old_cache.get("feeds", {}).values():
        # Handle both old format (dict with 'entries') and new format (list)
        if isinstance(feed_data, dict) and "entries" in feed_data:
            entries = feed_data["entries"]
        elif isinstance(feed_data, list):
            entries = feed_data
        else:
            continue
        for e in entries:
            if isinstance(e, dict):
                old_urls.add(e.get("url", ""))

    # Filter new entries
    filtered = {}
    for feed_id, entries in feed_results.items():
        new_entries = [e for e in entries if e["url"] not in old_urls]
        filtered[feed_id] = new_entries[:10]  # Cap per feed

    # Build cache data
    cache_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feeds": feed_results,
    }
    save_cache(cache_data)

    # Build and print digest
    digest = build_digest(feed_results)
    print(digest)

    elapsed = time.time() - start
    log(f"=== RSS Monitor done in {elapsed:.1f}s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())