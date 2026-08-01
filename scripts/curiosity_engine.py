#!/usr/bin/env python3
"""
Curiosity Engine — daily proactive discovery of new tools, technologies, opportunities.

Unlike trend_scout.py (which follows predefined categories),
this engine actively searches for UNEXPECTED things across multiple sources:
- Hacker News (newest)
- GitHub trending
- Reddit r/artificial, r/LocalLLaMA, r/SideProject
- Product Hunt (new launches)
- ArXiv (latest AI papers)

Each discovery is scored by NOVELTY (is this new?) and RELEVANCE (is this useful?).
High-novelty, high-relevance items become goals automatically.

Usage:
    python scripts/curiosity_engine.py            # full scan
    python scripts/curiosity_engine.py --quick    # lightweight scan
    python scripts/curiosity_engine.py --report   # show last discoveries
"""
import json
import os
import re
import sys
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
DISCOVERIES_FILE = CACHE_DIR / "curiosity_discoveries.json"
GOALS_FILE = CACHE_DIR / "goal_queue.json"

# Topics the user cares about (expanded beyond 4 business lines)
INTEREST_KEYWORDS = [
    # AI/ML
    "ai", "agent", "llm", "gpt", "claude", "gemini", "llama", "mistral",
    "machine learning", "deep learning", "neural", "transformer",
    # Automation
    "automate", "automation", "workflow", "pipeline", "orchestrat",
    "agent", "autonomous", "self-healing", "proactive",
    # Business
    "saas", "startup", "mvp", "launch", "revenue", "monetiz",
    "freelance", "client", "customer", "service",
    # Tools
    "api", "sdk", "framework", "library", "tool", "cli",
    "mcp", "plugin", "extension", "integration",
    # Platforms
    "telegram", "whatsapp", "discord", "slack", "notion",
    "github", "gitlab", "vercel", "supabase", "firebase",
    # Emerging
    "brain-computer", "neuralink", "robotics", "iot", "edge",
    "quantum", "crypto", "blockchain", "defi", "web3",
    # Creative
    "image", "video", "music", "3d", "ar", "vr", "game",
    # Security
    "security", "privacy", "encryption", "zero-trust",
    # Open source
    "open-source", "oss", "free", "self-hosted", "local",
]

# What's NOT interesting (filter out)
BOREDOM_KEYWORDS = [
    "hiring", "job", "salary", "interview", "resume",
    "stock", "market", "trading", "crypto price",
    "gossip", "celebrity", "sports", "weather",
    "tutorial hello world", "getting started with",
]


def fetch_url(url: str, timeout: int = 15) -> str:
    """Fetch URL content. Try direct first, fall back to proxy."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        # Try direct connection first (faster, works for many sites)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        pass
    # Fallback: try via v2rayN proxy
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        proxy_handler = urllib.request.ProxyHandler({"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"})
        opener = urllib.request.build_opener(proxy_handler)
        with opener.open(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def scan_hacker_news() -> list:
    """Scan Hacker News via Firebase API (no HTML parsing needed)."""
    ids_raw = fetch_url("https://hacker-news.firebaseio.com/v0/newstories.json", timeout=15)
    if not ids_raw:
        return []

    try:
        story_ids = json.loads(ids_raw)[:5]
    except (json.JSONDecodeError, ValueError):
        return []

    discoveries = []
    for sid in story_ids:
        item_raw = fetch_url(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=8)
        if not item_raw:
            continue
        try:
            item = json.loads(item_raw)
        except (json.JSONDecodeError, ValueError):
            continue
        title = item.get("title", "")
        url = item.get("url", "")
        if len(title) < 10:
            continue
        discoveries.append({
            "source": "hacker_news",
            "title": title,
            "url": url or f"https://news.ycombinator.com/item?id={sid}",
            "category": categorize(title),
        })

    return discoveries[:30]


def scan_github_trending() -> list:
    """Scan GitHub trending repos via gh CLI or HTML fallback."""
    import subprocess
    discoveries = []

    # Try gh CLI first (most reliable)
    try:
        result = subprocess.run(
            ["gh", "search", "repos", "--sort=stars", "--order=desc", "--limit=20", "created:>2026-06-16", "language:python"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    discoveries.append({
                        "source": "github_trending",
                        "title": parts[0].strip(),
                        "url": parts[1].strip() if parts[1].strip().startswith("http") else f"https://github.com/{parts[0].strip()}",
                        "category": categorize(parts[0]),
                    })
            return discoveries[:20]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: HTML scraping via proxy
    content = fetch_url("https://github.com/trending/python?since=daily")
    if not content:
        return []

    discoveries = []
    # Find repo links - look for /user/repo patterns
    for match in re.finditer(r'href="/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)"', content):
        repo = match.group(1).strip()
        if "/" in repo and not repo.startswith(".") and "trending" not in repo:
            name = repo.split("/")[-1]
            if len(name) > 2 and name not in [".github", ".gitignore", "LICENSE"]:
                discoveries.append({
                    "source": "github_trending",
                    "title": name,
                    "url": "https://github.com/%s" % repo,
                    "category": categorize(name),
                })

    # Deduplicate
    seen = set()
    unique = []
    for d in discoveries:
        if d["title"] not in seen:
            seen.add(d["title"])
            unique.append(d)

    return unique[:20]


def scan_local_files() -> list:
    """Scan local files for interesting content (fallback when external blocked)."""
    discoveries = []

    # Scan KC for interesting patterns
    try:
        import sqlite3
        conn = sqlite3.connect("D:/Portable_Soft/hermes/cache/knowledge_cube.db")
        cur = conn.cursor()
        # Find recent high-value entries
        cur.execute(
            "SELECT raw_text, axis_domain, ts FROM experiences "
            "WHERE ts > datetime('now', '-7 days') AND is_white_spot = 0 "
            "ORDER BY ts DESC LIMIT 10"
        )
        for row in cur.fetchall():
            text = (row[0] or "")[:200]
            domain = row[1] or "unknown"
            discoveries.append({
                "source": "local_kc",
                "title": "KC entry: %s" % text[:80],
                "url": "",
                "category": domain,
            })
        conn.close()
    except Exception:
        pass

    # Scan error logs for patterns
    error_log = Path("D:/Portable_Soft/hermes/logs/errors.log")
    if error_log.exists():
        try:
            lines = error_log.read_text(encoding="utf-8", errors="replace").splitlines()
            recent_errors = [l for l in lines[-50:] if "ERROR" in l]
            if recent_errors:
                discoveries.append({
                    "source": "local_errors",
                    "title": "Error pattern: %d errors in last 50 lines" % len(recent_errors),
                    "url": "",
                    "category": "system",
                })
        except Exception:
            pass

    # Scan user profile for unmet needs
    profile_file = Path("D:/Portable_Soft/hermes/cache/user_profile.json")
    if profile_file.exists():
        try:
            p = json.loads(profile_file.read_text(encoding="utf-8"))
            needs = p.get("needs", [])
            if needs:
                top_need = needs[0].get("text", "")[:80]
                discoveries.append({
                    "source": "local_needs",
                    "title": "Top user need: %s" % top_need,
                    "url": "",
                    "category": "user_needs",
                })
        except Exception:
            pass

    return discoveries


def scan_reddit() -> list:
    """Scan Reddit for AI/automation discussions."""
    subreddits = ["artificial", "LocalLLaMA", "SideProject", "SaaS", "startups"]
    discoveries = []

    for sub in subreddits:
        content = fetch_url("https://www.reddit.com/r/%s/hot.json?limit=5" % sub, timeout=15)
        if not content:
            continue
        try:
            data = json.loads(content)
            posts = data.get("data", {}).get("children", [])
            for post in posts[:5]:
                p = post.get("data", {})
                title = p.get("title", "")
                url = p.get("url", "")
                if len(title) > 10:
                    discoveries.append({
                        "source": "reddit_%s" % sub,
                        "title": title[:120],
                        "url": url,
                        "category": categorize(title),
                    })
        except (json.JSONDecodeError, KeyError):
            continue

    return discoveries[:25]


def categorize(text: str) -> str:
    """Categorize discovery by keywords."""
    text_lower = text.lower()
    for kw in ["ai", "llm", "agent", "gpt", "claude", "neural"]:
        if kw in text_lower:
            return "ai"
    for kw in ["automat", "workflow", "pipeline", "bot"]:
        if kw in text_lower:
            return "automation"
    for kw in ["saas", "startup", "launch", "revenue", "business"]:
        if kw in text_lower:
            return "business"
    for kw in ["api", "sdk", "tool", "framework", "library"]:
        if kw in text_lower:
            return "tool"
    for kw in ["security", "privacy", "vulnerability"]:
        if kw in text_lower:
            return "security"
    for kw in ["image", "video", "music", "3d", "game"]:
        if kw in text_lower:
            return "creative"
    return "other"


def score_discovery(discovery: dict) -> float:
    """Score a discovery by novelty and relevance."""
    title = discovery.get("title", "").lower()

    # Boredom filter
    for kw in BOREDOM_KEYWORDS:
        if kw in title:
            return 0.0

    # Relevance score
    relevance = 0.0
    for kw in INTEREST_KEYWORDS:
        if kw in title:
            relevance += 1.0

    # Source bonus (HN and GitHub are higher quality)
    source = discovery.get("source", "")
    if "hacker_news" in source:
        relevance += 2.0
    elif "github" in source:
        relevance += 1.5
    elif "reddit" in source:
        relevance += 0.5

    # Title quality bonus
    if len(title) > 20:
        relevance += 0.5
    if any(c.isdigit() for c in title):  # Numbers suggest specific claims
        relevance += 0.3

    return min(10.0, relevance)


def load_discoveries() -> list:
    """Load previous discoveries for dedup."""
    if DISCOVERIES_FILE.exists():
        try:
            return json.loads(DISCOVERIES_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_discoveries(discoveries: list):
    """Save discoveries."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Keep last 500
    if len(discoveries) > 500:
        discoveries = discoveries[-500:]
    DISCOVERIES_FILE.write_text(
        json.dumps(discoveries, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def create_goals_from_discoveries(discoveries: list):
    """Create goals for high-scoring discoveries."""
    if not GOALS_FILE.exists():
        return 0

    data = json.loads(GOALS_FILE.read_text(encoding="utf-8"))
    goals = data.get("goals", [])
    existing_titles = set(g.get("title", "").lower() for g in goals)

    created = 0
    for d in discoveries:
        score = d.get("score", 0)
        if score < 3.0:  # Only high-interest discoveries
            continue

        title = "Investigate: %s" % d["title"][:60]
        if title.lower() in existing_titles:
            continue

        priority = min(6, max(2, int(score)))
        goal = {
            "id": "g-curiosity-%d" % (len(goals) + 1),
            "title": title,
            "tier": 2,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "progress": 0.0,
            "related_actions": [],
            "deadline": None,
            "description": "Auto-discovered from %s (score: %.1f)" % (d["source"], score),
        }
        goals.append(goal)
        existing_titles.add(title.lower())
        created += 1

    data["goals"] = goals
    GOALS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return created


def main():
    args = sys.argv[1:]
    quick = "--quick" in args
    report_only = "--report" in args

    if report_only:
        discoveries = load_discoveries()
        today = datetime.now().strftime("%Y-%m-%d")
        recent = [d for d in discoveries if d.get("date", "").startswith(today)]
        print("=== CURIOSITY ENGINE REPORT ===")
        print("Today: %d discoveries" % len(recent))
        for d in sorted(recent, key=lambda x: -x.get("score", 0))[:10]:
            print("  [%.1f] [%s] %s" % (d.get("score", 0), d.get("category", "?"), d.get("title", "?")[:80]))
        return

    print("=== CURIOSITY ENGINE ===")
    print("Scanning sources...")

    all_discoveries = []
    consecutive_failures = 0

    # Scan Hacker News
    print("  Hacker News...", end=" ")
    hn = scan_hacker_news()
    if not hn:
        consecutive_failures += 1
        print("BLOCKED (0 items)")
    else:
        consecutive_failures = 0
        print("%d items" % len(hn))
    all_discoveries.extend(hn)

    if not quick:
        # GitHub Trending
        print("  GitHub Trending...", end=" ")
        gh = scan_github_trending()
        if not gh:
            consecutive_failures += 1
            print("BLOCKED (0 items)")
        else:
            consecutive_failures = 0
            print("%d items" % len(gh))
        all_discoveries.extend(gh)

        # Reddit - only if not blocked
        if consecutive_failures < 3:
            print("  Reddit...", end=" ")
            rd = scan_reddit()
            if not rd:
                consecutive_failures += 1
                print("BLOCKED (0 items)")
            else:
                consecutive_failures = 0
                print("%d items" % len(rd))
            all_discoveries.extend(rd)

    # Self-awareness: if blocked, log it and switch to local
    if consecutive_failures >= 3:
        print("  WARNING: %d consecutive failures on external sources." % consecutive_failures)
        print("  Switching to local file analysis...")
        try:
            from event_log import log_task
            log_task(
                "Curiosity blocked: %d consecutive failures" % consecutive_failures,
                "Switched to local sources",
                ["curiosity", "blocked", "self-aware"]
            )
        except ImportError:
            pass

    # Score and deduplicate
    existing = load_discoveries()
    existing_titles = set(d.get("title", "").lower() for d in existing)

    new_discoveries = []
    for d in all_discoveries:
        title = d.get("title", "").lower()
        if title not in existing_titles and len(title) > 10:
            d["score"] = score_discovery(d)
            d["date"] = datetime.now().strftime("%Y-%m-%d")
            d["timestamp"] = datetime.now().isoformat()
            if d["score"] > 0:
                new_discoveries.append(d)
                existing_titles.add(title)

    # Sort by score
    new_discoveries.sort(key=lambda x: -x.get("score", 0))

    print()
    print("Found %d new discoveries (%d total scanned)" % (len(new_discoveries), len(all_discoveries)))

    # Show top discoveries
    if new_discoveries:
        print()
        print("TOP DISCOVERIES:")
        for d in new_discoveries[:10]:
            print("  [%.1f] [%s] %s" % (d["score"], d["category"], d["title"][:80]))

    # Create goals for high-scoring
    if new_discoveries:
        goals_created = create_goals_from_discoveries(new_discoveries)
        print()
        print("Created %d new goals from discoveries" % goals_created)

    # Save
    existing.extend(new_discoveries)
    save_discoveries(existing)
    print()
    print("Saved %d total discoveries" % len(existing))


if __name__ == "__main__":
    main()
