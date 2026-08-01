#!/usr/bin/env python3
"""Trend Scout — scan for trends in AI, automation, business, creative tools."""
import json
import sys
import argparse
import urllib.request
import re
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
TRENDS_FILE = CACHE_DIR / "trend_scout.json"

CATEGORIES = {
    "ai": ["ai", "llm", "gpt", "claude", "gemini", "llama", "mistral", "machine learning", "deep learning", "neural", "transformer", "agent", "autonomous"],
    "automation": ["automat", "workflow", "pipeline", "orchestrat", "no-code", "low-code", "rpa", "bot", "scripting"],
    "business": ["saas", "startup", "mvp", "launch", "revenue", "monetiz", "freelance", "customer", "growth", "mktg"],
    "tools": ["api", "sdk", "framework", "library", "cli", "tool", "mcp", "plugin", "extension", "integration", "devtool"],
    "creative": ["image", "video", "music", "3d", "ar", "vr", "generative", "design", "figma", "blender"],
    "platforms": ["telegram", "whatsapp", "discord", "slack", "notion", "github", "gitlab", "vercel", "supabase", "firebase"],
    "security": ["security", "privacy", "encryption", "zero-trust", "auth", "vulnerability"],
    "emerging": ["quantum", "robotics", "iot", "edge", "brain-computer", "bio", "crypto", "defi", "web3"],
}

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        pass
    # fallback via proxy
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"}))
        with opener.open(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        return ""

def categorize(text):
    tl = text.lower()
    for cat, kws in CATEGORIES.items():
        for kw in kws:
            if kw in tl:
                return cat
    return "other"

def score(title, source):
    sc = 1.0
    if any(c.isdigit() for c in title):
        sc += 0.5
    if len(title) > 30:
        sc += 0.3
    if "hacker" in source or "github" in source:
        sc += 1.0
    if "show hn" in title.lower():
        sc += 1.5
    if "ask hn" in title.lower():
        sc += 0.5
    return min(10.0, sc)

def scan_hn(limit=40):
    raw = fetch("https://hacker-news.firebaseio.com/v0/newstories.json")
    if not raw:
        return []
    try:
        ids = json.loads(raw)[:limit]
    except Exception:
        return []
    out = []
    for sid in ids:
        item_raw = fetch(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", 8)
        if not item_raw:
            continue
        try:
            item = json.loads(item_raw)
        except Exception:
            continue
        title = item.get("title", "")
        url = item.get("url", "") or f"https://news.ycombinator.com/item?id={sid}"
        if len(title) < 15:
            continue
        out.append({"source": "hacker_news", "title": title, "url": url, "category": categorize(title), "hn_score": item.get("score", 0)})
    return out

def scan_github(limit=20):
    content = fetch("https://github.com/trending/python?since=daily")
    if not content:
        return []
    out = []
    for m in re.finditer(r'href="/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)"', content):
        repo = m.group(1)
        if "/" not in repo or repo.count("/") != 1:
            continue
        name = repo.split("/")[-1]
        if name in [".github", ".gitignore", "LICENSE", "README"]:
            continue
        out.append({"source": "github_trending", "title": name, "url": f"https://github.com/{repo}", "category": categorize(name)})
    # dedup
    seen = set()
    uniq = []
    for d in out:
        if d["title"] not in seen:
            seen.add(d["title"])
            uniq.append(d)
    return uniq[:limit]

def load_trends():
    if TRENDS_FILE.exists():
        try:
            return json.loads(TRENDS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_trends(data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    TRENDS_FILE.write_text(json.dumps(data[-500:], indent=2, ensure_ascii=False), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", choices=["all"] + list(CATEGORIES.keys()), default="all")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    if args.report:
        data = load_trends()
        today = datetime.now().strftime("%Y-%m-%d")
        recent = [d for d in data if d.get("date", "").startswith(today)]
        if args.category != "all":
            recent = [d for d in recent if d.get("category") == args.category]
        print(f"=== TREND SCOUT REPORT ({args.category}) ===")
        print(f"Today: {len(recent)} trends")
        for d in sorted(recent, key=lambda x: -x.get("score", 0))[:20]:
            print(f"  [{d['score']:.1f}] [{d['category']}] {d['title'][:80]}")
        return

    print(f"=== TREND SCOUT ({args.category}) ===")
    print("Scanning...")

    all_found = []
    hn = scan_hn(50 if not args.quick else 20)
    print(f"  Hacker News: {len(hn)}")
    all_found.extend(hn)

    if not args.quick:
        gh = scan_github(30)
        print(f"  GitHub Trending: {len(gh)}")
        all_found.extend(gh)

    # filter by category
    if args.category != "all":
        all_found = [d for d in all_found if d["category"] == args.category]

    existing = load_trends()
    existing_titles = {d.get("title", "").lower() for d in existing}

    new_items = []
    for d in all_found:
        tl = d["title"].lower()
        if tl not in existing_titles and len(tl) > 10:
            d["score"] = score(d["title"], d["source"])
            d["date"] = datetime.now().strftime("%Y-%m-%d")
            d["timestamp"] = datetime.now().isoformat()
            new_items.append(d)
            existing_titles.add(tl)

    new_items.sort(key=lambda x: -x.get("score", 0))
    print(f"\n=== NEW TRENDS: {len(new_items)} ===")
    for d in new_items[:30]:
        print(f"  [{d['score']:.1f}] [{d['category']}] {d['title'][:80]}")

    if new_items:
        save_trends(existing + new_items)
        print(f"\nSaved to {TRENDS_FILE}")

if __name__ == "__main__":
    main()