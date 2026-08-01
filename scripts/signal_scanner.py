#!/usr/bin/env python3
"""
Signal Scanner — event-driven对外部信号的检测.


> Revisit: when signal sources, scanning logic, or brick extraction changes. Last touched: 2026-07-02.
Режимы:
  --run    — одноразовый скан (для event_daemon)
  --watch  — непрерывный мониторинг с adaptive backoff

В режиме --watch сканер опрашивает HN и GitHub trending.
При обнаружении нового сигнала → emit new_external_signal в event_bus.

Adaptive backoff:
  - Нет изменений → интервал × 2 (макс 10 мин)
  - Есть изменения → интервал сброс к 60 сек
  - Мёртвый источник → skip + интервал × 3

Usage:
    python scripts/signal_scanner.py --run      # один скан
    python scripts/signal_scanner.py --watch    # непрерывный мониторинг
    python scripts/signal_scanner.py --status   # статистика
"""
import json
import sys
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
SIGNALS_FILE = CACHE_DIR / "signals.jsonl"
PROCESSED_FILE = CACHE_DIR / "signals_processed.json"
SCANNER_STATE = CACHE_DIR / "scanner_state.json"

# Proxy for HTTP requests
PROXY = "socks5://127.0.0.1:10806"
CURL = "curl"

# Crawl4AI (lazy import)
_crawl4ai = None

def _get_crawl4ai():
    global _crawl4ai
    if _crawl4ai is None:
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
            _crawl4ai = {
                "AsyncWebCrawler": AsyncWebCrawler,
                "CrawlerRunConfig": CrawlerRunConfig,
                "BrowserConfig": BrowserConfig,
            }
        except ImportError:
            _crawl4ai = False
    return _crawl4ai if _crawl4ai else None


def crawl4ai_scrape(url: str, timeout: int = 30) -> str:
    """Scrape URL using Crawl4AI. Returns markdown content."""
    import asyncio
    lib = _get_crawl4ai()
    if not lib:
        return ""

    try:
        browser_config = lib["BrowserConfig"](headless=True)
        run_config = lib["CrawlerRunConfig"](
            wait_until="domcontentloaded",
            word_count_threshold=10,
        )

        async def _scrape():
            async with lib["AsyncWebCrawler"](config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)
                if result.success:
                    md = result.markdown
                    return md.raw_markdown if hasattr(md, 'raw_markdown') else str(md)
                return ""

        return asyncio.run(_scrape())
    except Exception as e:
        print(f"  Crawl4AI error ({url}): {e}")
        return ""


def http_get(url: str, timeout: int = 8) -> bytes:
    """HTTP GET через curl + SOCKS proxy. Fail fast."""
    import subprocess
    try:
        result = subprocess.run(
            [CURL, "-s", "--connect-timeout", "3", "--max-time", str(timeout),
             "-x", PROXY, url],
            capture_output=True, timeout=timeout + 2
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        raise Exception(f"curl exit={result.returncode}")
    except Exception:
        try:
            result = subprocess.run(
                [CURL, "-s", "--connect-timeout", "3", "--max-time", str(timeout),
                 url],
                capture_output=True, timeout=timeout + 2
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
            raise Exception(f"direct exit={result.returncode}")
        except Exception:
            return b""


# ─── Utility ──────────────────────────────────────────────────────
def signal_hash(title: str, url: str) -> str:
    raw = f"{title.strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_processed() -> set:
    if PROCESSED_FILE.exists():
        try:
            return set(json.loads(PROCESSED_FILE.read_text("utf-8")))
        except:
            pass
    return set()


def save_processed(processed: set):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(list(processed)), "utf-8")


def save_signal(signal: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SIGNALS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(signal, ensure_ascii=False) + "\n")


def load_state() -> dict:
    if SCANNER_STATE.exists():
        try:
            return json.loads(SCANNER_STATE.read_text("utf-8"))
        except:
            pass
    return {
        "consecutive_empty": 0,
        "last_scan": None,
        "total_signals": 0,
        "backoff_interval": 60,
        "sources": {}
    }


def save_state(state: dict):
    SCANNER_STATE.parent.mkdir(parents=True, exist_ok=True)
    SCANNER_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), "utf-8")


# ─── Source scanners ──────────────────────────────────────────────
def scan_hacker_news(limit=1) -> list:
    """Scan HN top stories via jina.ai summarizer (works without proxy)."""
    try:
        data = http_get("https://r.jina.ai/http://hacker-news.firebaseio.com/v0/topstories.json")
        if not data:
            return []
        text = data.decode() if isinstance(data, bytes) else data
        import re
        match = re.search(r'Markdown Content:\s*\n+(\[.*?\])', text, re.DOTALL)
        if not match:
            match = re.search(r'(\[\s*\d+(?:\s*,\s*\d+)*)', text)
        if match:
            ids = json.loads(match.group(1))[:limit]
        else:
            print("  HN: could not parse IDs from response")
            return []
    except Exception as e:
        print(f"  HN top stories error: {e}")
        return []

    results = []
    for story_id in ids:
        try:
            data = http_get(f"https://r.jina.ai/http://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            if not data:
                continue
            text = data.decode() if isinstance(data, bytes) else data
            import re
            match = re.search(r'Markdown Content:\s*\n+(\{.*?\})', text, re.DOTALL)
            if not match:
                match = re.search(r'(\{.*?\})', text, re.DOTALL)
            if match:
                item = json.loads(match.group(1))
            else:
                continue
            if not item or item.get("type") != "story":
                continue
            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
            score = item.get("score", 0)

            # Categorization by keywords
            title_lower = title.lower()
            category = "tech"
            if any(w in title_lower for w in ["ai", "llm", "gpt", "model", "machine learning", "neural"]):
                category = "ai"
            elif any(w in title_lower for w in ["money", "revenue", "profit", "saas", "startup", "business"]):
                category = "business"
            elif any(w in title_lower for w in ["security", "hack", "vulnerability", "exploit"]):
                category = "security"
            elif any(w in title_lower for w in ["tool", "cli", "terminal", "editor", "ide"]):
                category = "tools"
            elif any(w in title_lower for w in ["arbitrage", "affiliate", "cpa", "traffic"]):
                category = "arbitrage"

            results.append({
                "title": title,
                "url": url,
                "category": category,
                "score": score,
            })
        except Exception as e:
            print(f"  HN item {story_id} error: {e}")
            continue

    return results


def scan_github_trending() -> list:
    """Scan GitHub trending via direct API (works without proxy)."""
    try:
        data = http_get("https://api.github.com/search/repositories?q=created:>2026-06-21&sort=stars&order=desc&per_page=10")
        data = json.loads(data.decode() if isinstance(data, bytes) else data)
    except Exception as e:
        print(f"  GitHub trending error: {e}")
        return []

    results = []
    for repo in data.get("items", [])[:10]:
        desc = repo.get("description", "") or ""
        topics = [t.lower() for t in repo.get("topics", [])]
        all_text = f"{desc} {' '.join(topics)}".lower()

        category = "tool"
        if any(w in all_text for w in ["ai", "llm", "gpt", "ml", "neural"]):
            category = "ai"
        elif any(w in all_text for w in ["security", "vulnerability", "pentest"]):
            category = "security"
        elif any(w in all_text for w in ["web", "html", "css", "react", "svelte"]):
            category = "web"
        elif any(w in all_text for w in ["automation", "bot", "scrape"]):
            category = "automation"
        elif any(w in all_text for w in ["money", "payment", "crypto", "finance"]):
            category = "finance"

        results.append({
            "title": repo.get("name", ""),
            "url": repo.get("html_url", ""),
            "description": desc[:200],
            "category": category,
            "stars": repo.get("stargazers_count", 0),
        })

    return results


def scan_rss_feeds() -> list:
    """Scan tech RSS feeds via jina.ai summarizer (no proxy needed)."""
    feeds = [
        "https://r.jina.ai/http://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://r.jina.ai/http://feeds.arstechnica.com/arstechnica/index",
        "https://r.jina.ai/http://feeds.feedburner.com/TheHackersNews",
    ]
    results = []
    for feed_url in feeds:
        try:
            data = http_get(feed_url)
            if not data:
                continue
            text = data.decode() if isinstance(data, bytes) else data
            # Extract titles from markdown
            import re
            titles = re.findall(r'### \[([^\]]+)\]\(([^)]+)\)', text)
            for title, url in titles[:5]:
                title_lower = title.lower()
                category = "tech"
                if any(w in title_lower for w in ["ai", "llm", "gpt", "model", "machine learning"]):
                    category = "ai"
                elif any(w in title_lower for w in ["security", "hack", "vulnerability", "breach"]):
                    category = "security"
                elif any(w in title_lower for w in ["tool", "cli", "terminal", "automation"]):
                    category = "tools"
                results.append({
                    "title": title,
                    "url": url,
                    "category": category,
                    "score": 0,
                })
        except Exception as e:
            print(f"  RSS feed error ({feed_url}): {e}")
            continue
    return results


def scan_local_files() -> list:
    """Scan local cache/files for new patterns (always works)."""
    results = []
    try:
        # Check for new bricks in workshop
        workshop = HERMES_HOME / "ARBITRAGE_WORKSHOP.md"
        if workshop.exists():
            stat = workshop.stat()
            content = workshop.read_text(encoding="utf-8", errors="ignore")
            if "UNVERIFIED" in content:
                results.append({
                    "title": "New UNVERIFIED bricks in ARBITRAGE_WORKSHOP",
                    "url": "file://ARBITRAGE_WORKSHOP.md",
                    "category": "arbitrage",
                    "score": 1,
                })
    except Exception:
        pass
    return results


# ─── Event emission ───────────────────────────────────────────────
def emit_signal_event(signal: dict):
    """Score signal via Bayesian scorer, emit if score >= 0.3."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from bayesian_scorer import score_signal

        result = score_signal(signal)
        score = result["score"]
        verdict = result["verdict"]

        signal["bayesian_score"] = score
        signal["bayesian_reason"] = result["reason"]

        if verdict == "reject":
            print(f"    REJECTED (score={score:.3f}): {signal.get('title', '')[:40]}")
            return False

        # Accept: emit to event_bus
        from event_bus import emit
        emit("new_external_signal", {
            "title": signal.get("title", ""),
            "url": signal.get("url", ""),
            "source": signal.get("source", ""),
            "category": signal.get("category", ""),
            "bayesian_score": score,
        })
        return True
    except Exception as e:
        # Fallback: emit without scoring
        try:
            from event_bus import emit
            emit("new_external_signal", {
                "title": signal.get("title", ""),
                "url": signal.get("url", ""),
                "source": signal.get("source", ""),
                "category": signal.get("category", ""),
                "bayesian_score": 0.5,
            })
            return True
        except:
            print(f"  emit error: {e}")
            return False


# ─── Single scan ──────────────────────────────────────────────────
def run_once() -> int:
    """Run one scan cycle. Returns number of new signals."""
    processed = load_processed()
    new_count = 0

    # HN
    try:
        hn = scan_hacker_news()
        for item in hn:
            h = signal_hash(item["title"], item.get("url", ""))
            if h in processed:
                continue
            signal = {
                "source": "hacker_news",
                "title": item["title"],
                "url": item.get("url", ""),
                "category": item.get("category", "tech"),
                "score": item.get("score", 0),
                "ts": datetime.now(timezone.utc).isoformat(),
                "hash": h,
            }
            save_signal(signal)
            processed.add(h)
            new_count += 1
            print(f"  [HN] {item['title'][:60]}")
            # Emit event
            emit_signal_event(signal)
    except Exception as e:
        print(f"  HN scan error: {e}")

    # GitHub trending
    try:
        gh = scan_github_trending()
        for item in gh:
            h = signal_hash(item["title"], item.get("url", ""))
            if h in processed:
                continue
            signal = {
                "source": "github",
                "title": item["title"],
                "url": item.get("url", ""),
                "category": item.get("category", "tool"),
                "description": item.get("description", ""),
                "stars": item.get("stars", 0),
                "ts": datetime.now(timezone.utc).isoformat(),
                "hash": h,
            }
            save_signal(signal)
            processed.add(h)
            new_count += 1
            print(f"  [GH] {item['title'][:60]}")
            emit_signal_event(signal)
    except Exception as e:
        print(f"  GitHub scan error: {e}")

    # RSS feeds
    try:
        rss = scan_rss_feeds()
        for item in rss:
            h = signal_hash(item["title"], item.get("url", ""))
            if h in processed:
                continue
            signal = {
                "source": "rss",
                "title": item["title"],
                "url": item.get("url", ""),
                "category": item.get("category", "tech"),
                "score": item.get("score", 0),
                "ts": datetime.now(timezone.utc).isoformat(),
                "hash": h,
            }
            save_signal(signal)
            processed.add(h)
            new_count += 1
            print(f"  [RSS] {item['title'][:60]}")
            emit_signal_event(signal)
    except Exception as e:
        print(f"  RSS scan error: {e}")

    # Local files
    try:
        local = scan_local_files()
        for item in local:
            h = signal_hash(item["title"], item.get("url", ""))
            if h in processed:
                continue
            signal = {
                "source": "local",
                "title": item["title"],
                "url": item.get("url", ""),
                "category": item.get("category", "arbitrage"),
                "score": item.get("score", 0),
                "ts": datetime.now(timezone.utc).isoformat(),
                "hash": h,
            }
            save_signal(signal)
            processed.add(h)
            new_count += 1
            print(f"  [LOCAL] {item['title'][:60]}")
            emit_signal_event(signal)
    except Exception as e:
        print(f"  Local scan error: {e}")

    save_processed(processed)
    return new_count


# ─── Watch mode ───────────────────────────────────────────────────
def watch():
    """
    Continuous monitoring with adaptive backoff.
    No timers. Reactive to data freshness.
    """
    state = load_state()
    interval = state.get("backoff_interval", 60)
    consecutive_empty = state.get("consecutive_empty", 0)

    print(f"Signal Scanner — WATCH mode. Initial interval: {interval}s")
    print(f"  Ctrl+C to stop.\n")

    while True:
        try:
            scan_start = time.time()
            new = run_once()
            scan_duration = time.time() - scan_start

            state["last_scan"] = datetime.now(timezone.utc).isoformat()
            state["total_signals"] = state.get("total_signals", 0) + new

            if new > 0:
                # Found signals → reset backoff
                consecutive_empty = 0
                interval = 60
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] +{new} signals ({scan_duration:.1f}s) -> backoff reset to {interval}s")
            else:
                # No signals → backoff
                consecutive_empty += 1
                interval = min(interval * 2, 600)  # max 10 min
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] nothing new ({scan_duration:.1f}s) -> backoff to {interval}s")

            state["consecutive_empty"] = consecutive_empty
            state["backoff_interval"] = interval
            save_state(state)

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\nWatch stopped.")
            save_state(state)
            break
        except Exception as e:
            print(f"  Error: {e}")
            interval = min(interval * 3, 600)
            state["backoff_interval"] = interval
            save_state(state)
            time.sleep(interval)


# ─── Status ───────────────────────────────────────────────────────
def status():
    state = load_state()
    print(f"Scanner state:")
    print(f"  Total signals: {state.get('total_signals', 0)}")
    print(f"  Last scan: {state.get('last_scan', 'never')}")
    print(f"  Backoff interval: {state.get('backoff_interval', 60)}s")
    print(f"  Consecutive empty: {state.get('consecutive_empty', 0)}")

    if SIGNALS_FILE.exists():
        lines = SIGNALS_FILE.read_text("utf-8").strip().split("\n")
        print(f"  Signals in file: {len(lines)}")

    if PROCESSED_FILE.exists():
        processed = json.loads(PROCESSED_FILE.read_text("utf-8"))
        print(f"  Processed hashes: {len(processed)}")


# ─── Main ─────────────────────────────────────────────────────────
def main():
    if "--watch" in sys.argv:
        watch()
    elif "--run" in sys.argv:
        new = run_once()
        print(f"New signals: {new}")
    elif "--status" in sys.argv:
        status()
    else:
        # Default: single run
        new = run_once()
        print(f"New signals: {new}")


if __name__ == "__main__":
    main()
