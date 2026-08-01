#!/usr/bin/env python3
"""
KC Populator — auto-fills Knowledge Cube from:
1. Session dumps (past conversations)
2. Script metadata (what scripts do)
3. Error logs (errors and fixes)
4. Meditation insights
5. User profile corrections
"""
import sys
import os
import json
import glob
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from kc_rag import upsert, stats, event

HERMES = os.path.join(os.path.dirname(__file__), "..")

def populate_from_scripts():
    """Index all scripts with their docstrings."""
    scripts_dir = os.path.join(HERMES, "scripts")
    count = 0
    for py_file in glob.glob(os.path.join(scripts_dir, "*.py")):
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)
            
            # Extract docstring
            docstring = ""
            if '"""' in content:
                start = content.index('"""') + 3
                end = content.index('"""', start) if '"""' in content[start:] else start + 200
                docstring = content[start:end].strip()
            
            if docstring:
                name = os.path.basename(py_file)
                upsert(
                    content=f"[{name}] {docstring[:300]}",
                    tags=f"script,{name}",
                    source="scripts",
                    category="tools",
                    importance=6
                )
                count += 1
        except Exception:
            pass
    return count

def populate_from_errors():
    """Index recent error logs."""
    error_log = os.path.join(HERMES, "logs", "errors.log")
    count = 0
    if not os.path.exists(error_log):
        return 0
    
    with open(error_log, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-50:]  # Last 50 errors
    
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:
            upsert(
                content=line[:500],
                tags="error,log",
                source="errors",
                category="issues",
                importance=4
            )
            count += 1
    return count

def populate_from_meditations():
    """Index meditation insights from cache."""
    count = 0
    for f in glob.glob(os.path.join(HERMES, "cache", "meditation_*.json")):
        try:
            with open(f, "r") as fh:
                data = json.load(fh)
            for item in data.get("insights", []):
                upsert(
                    content=f"MEDITATION: {item.get('description', '')}",
                    tags=f"meditation,{item.get('type', 'general')}",
                    source="meditation",
                    category="insights",
                    importance=item.get("severity", 5) + 3
                )
                count += 1
        except Exception:
            pass
    return count

def populate_from_user_profile():
    """Index user preferences and corrections."""
    user_md = os.path.join(HERMES, "memories", "USER.md")
    count = 0
    if os.path.exists(user_md):
        with open(user_md, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if content:
            # Split by sections
            for section in content.split("##"):
                section = section.strip()
                if section:
                    upsert(
                        content=f"USER PROFILE: {section[:300]}",
                        tags="user,profile,preference",
                        source="user",
                        category="preferences",
                        importance=8
                    )
                    count += 1
    return count

def populate_from_channels():
    """Index channel analysis results."""
    count = 0
    for f in glob.glob(os.path.join(HERMES, "cache", "channel_analysis_*.json")):
        try:
            with open(f, "r") as fh:
                data = json.load(fh)
            channel = data.get("channel", "unknown")
            for topic in data.get("key_topics", []):
                upsert(
                    content=f"[{channel}] {topic}",
                    tags=f"channel,{channel},research",
                    source="channels",
                    category="research",
                    importance=6
                )
                count += 1
            for item in data.get("relevant_to_us", []):
                upsert(
                    content=f"[{channel}] ACTIONABLE: {item}",
                    tags=f"channel,{channel},actionable",
                    source="channels",
                    category="actionable",
                    importance=8
                )
                count += 1
        except Exception:
            pass
    return count

def populate_from_session_dumps():
    """Index recent session dump summaries."""
    dumps_dir = os.path.join(HERMES, "sessions")
    count = 0
    if not os.path.exists(dumps_dir):
        return 0
    
    for f in sorted(glob.glob(os.path.join(dumps_dir, "*.json")), reverse=True)[:10]:
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                data = json.load(fh)
            title = data.get("title", "session")
            summary = data.get("summary", "")
            if summary:
                upsert(
                    content=f"[SESSION: {title}] {summary[:300]}",
                    tags=f"session,{title}",
                    source="sessions",
                    category="context",
                    importance=5
                )
                count += 1
        except Exception:
            pass
    return count


def populate_from_external_sources():
    """Index RSS articles, YouTube videos, Reddit posts from cache."""
    count = 0
    
    # RSS Monitor cache
    rss_cache = os.path.join(HERMES, "cache", "rss_monitor", "latest.json")
    if os.path.exists(rss_cache):
        try:
            with open(rss_cache, "r", encoding="utf-8") as f:
                data = json.load(f)
            for feed_id, feed_entries in data.get("feeds", {}).items():
                for entry in feed_entries:
                    title = entry.get("title", "")
                    url = entry.get("url", "")
                    summary = entry.get("summary", "")
                    tags = entry.get("tags", [])
                    topic = entry.get("topic", feed_id)
                    
                    content = f"[{feed_id.upper()}] {title} — {summary[:300]}"
                    if url:
                        content += f" ({url})"
                    
                    tag_str = f"rss,{feed_id},{topic}"
                    if tags:
                        tag_str += "," + ",".join(tags[:5])
                    
                    upsert(
                        content=content,
                        tags=tag_str,
                        source=f"rss_{feed_id}",
                        category="external",
                        importance=7
                    )
                    count += 1
        except Exception:
            pass
    
    # YouTube Watch cache
    yt_cache = os.path.join(HERMES, "cache", "youtube_watch", "latest.json")
    if os.path.exists(yt_cache):
        try:
            with open(yt_cache, "r", encoding="utf-8") as f:
                data = json.load(f)
            for channel_id, channel_data in data.get("channels", {}).items():
                topic = channel_data.get("topic", channel_id)
                for video in channel_data.get("videos", []):
                    title = video.get("title", "")
                    url = video.get("url", "")
                    duration = video.get("duration", "")
                    
                    content = f"[YOUTUBE:{channel_id}] {title}"
                    if duration:
                        content += f" [{duration}]"
                    if url:
                        content += f" ({url})"
                    
                    upsert(
                        content=content,
                        tags=f"youtube,{channel_id},{topic}",
                        source=f"youtube_{channel_id}",
                        category="external",
                        importance=7
                    )
                    count += 1
        except Exception:
            pass
    
    return count


if __name__ == "__main__":
    print("=== KC Populator ===")
    t0 = datetime.now()
    
    n_scripts = populate_from_scripts()
    print(f"Scripts indexed: {n_scripts}")
    
    n_errors = populate_from_errors()
    print(f"Errors indexed: {n_errors}")
    
    n_meditations = populate_from_meditations()
    print(f"Meditations indexed: {n_meditations}")
    
    n_user = populate_from_user_profile()
    print(f"User profile indexed: {n_user}")
    
    n_channels = populate_from_channels()
    print(f"Channel research indexed: {n_channels}")
    
    n_sessions = populate_from_session_dumps()
    print(f"Sessions indexed: {n_sessions}")
    
    n_external = populate_from_external_sources()
    print(f"External sources (RSS/YouTube) indexed: {n_external}")
    
    total = n_scripts + n_errors + n_meditations + n_user + n_channels + n_sessions + n_external
    s = stats()
    elapsed = (datetime.now() - t0).total_seconds()
    
    event("kc_populated", {"total_new": total, "kc_total": s["total"]})
    
    print(f"\n=== RESULT ===")
    print(f"New entries: {total}")
    print(f"KC total: {s['total']}")
    print(f"By source: {s['by_source']}")
    print(f"Time: {elapsed:.1f}s")
