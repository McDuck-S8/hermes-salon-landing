#!/usr/bin/env python3
"""
Cube Feeder — populates Knowledge Cube from various data sources.


> Revisit: when cube feeding logic, event triggers, or knowledge extraction changes. Last touched: 2026-07-02.
Reads from lavra_knowledge.jsonl, cache/*.json, logs/*.log, and scripts/*.py,
extracts knowledge patterns, and writes them to knowledge_cube.db.

Event-Driven (primary path — triggered by event_bus.py DIRECT_EVENT_HANDLERS):
    _run_cube_feeder_on_session_completed(event)  — session outcomes
    _run_cube_feeder_on_new_signal(event)          — external signals
    _run_cube_feeder_on_knowledge_added(event)     — cache source rescan
    _run_cube_feeder_on_error_logged(event)        — error patterns
    _run_cube_feeder_on_boot(event)                — full feed from all

CLI (backup / manual):
    python cube_feeder.py              # feed from all sources, report stats
    python cube_feeder.py --dry-run    # show what would be added without writing
    python cube_feeder.py --source lavra   # feed only from lavra_knowledge.jsonl
    python cube_feeder.py --source cache   # feed only from cache JSON files
    python cube_feeder.py --source logs    # feed only from log files
"""

import json
import os
import re
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter

# ── Resolve paths relative to this script (portable, no hardcoded C:\) ────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(PROJECT_ROOT)))
DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"
LAVRA_PATH = HERMES_HOME / "data" / "lavra_knowledge.jsonl"
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"

# ── Import knowledge_cube.py from the same scripts/ directory ─────────────────
sys.path.insert(0, str(SCRIPT_DIR))
import importlib.util

from event_bus import emit as emit_event

spec = importlib.util.spec_from_file_location("kc", str(SCRIPT_DIR / "knowledge_cube.py"))
kc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kc)

# Domains we consider "underpopulated" (white_spot threshold)
WHITE_SPOT_THRESHOLD = 10


# ── Data Source Readers ───────────────────────────────────────────────────────

def read_lavra_knowledge():
    """Read lavra_knowledge.jsonl — curated knowledge decisions/patterns."""
    entries = []
    if not LAVRA_PATH.exists():
        return entries

    for line in LAVRA_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if not isinstance(obj, dict):
                continue

            content = obj.get("content", "")
            entry_type = obj.get("type", "knowledge")
            tags = obj.get("tags", [])
            source_key = obj.get("key", "")

            # Build a meaningful text for classification
            text = f"[{entry_type}] {content}"

            entries.append({
                "text": text,
                "tools": [],
                "source": f"lavra_{entry_type}",
                "tags": tags + [f"source:lavra", f"entry_type:{entry_type}"],
            })
        except (json.JSONDecodeError, TypeError):
            continue

    return entries


def read_cache_decisions():
    """Read cache/agent_decisions.json — autonomous agent decisions."""
    entries = []
    decisions_path = CACHE_DIR / "agent_decisions.json"
    if not decisions_path.exists():
        return entries

    try:
        data = json.loads(decisions_path.read_text(encoding="utf-8", errors="replace"))
        for d in data.get("decisions", []):
            title = d.get("title", "")
            desc = d.get("description", "")
            result = d.get("result", "")
            action_id = d.get("action_id", "")
            tier_name = d.get("tier_name", "")
            score = d.get("score", 0)

            text = f"[decision:{action_id}] {title}. {desc}"
            if result:
                text += f" Result: {result[:300]}"

            entries.append({
                "text": text,
                "tools": [],
                "source": "agent_decisions",
                "tags": ["source:agent_decisions", f"tier:{tier_name}"],
            })
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return entries


def read_cache_suggestions():
    """Read cache/improvement_suggestions.json — improvement suggestions."""
    entries = []
    sug_path = CACHE_DIR / "improvement_suggestions.json"
    if not sug_path.exists():
        return entries

    try:
        data = json.loads(sug_path.read_text(encoding="utf-8", errors="replace"))
        for s in data.get("suggestions", []):
            title = s.get("title", "")
            desc = s.get("description", "")
            severity = s.get("severity", "unknown")
            issue_type = s.get("issue_type", "unknown")
            actions = s.get("recommended_actions", [])

            text = f"[suggestion:{issue_type}] {title}. {desc}"
            if actions:
                text += " Actions: " + "; ".join(actions[:3])

            entries.append({
                "text": text,
                "tools": [],
                "source": "improvement_suggestions",
                "tags": ["source:improvement", f"severity:{severity}", f"issue:{issue_type}"],
            })
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return entries


def read_cache_dimension_proposals():
    """Read cache/dimension_proposals.json — dimension discovery proposals."""
    entries = []
    dp_path = CACHE_DIR / "dimension_proposals.json"
    if not dp_path.exists():
        return entries

    try:
        data = json.loads(dp_path.read_text(encoding="utf-8", errors="replace"))
        if isinstance(data, list):
            for batch in data:
                if not isinstance(batch, dict):
                    continue
                for prop in batch.get("proposals", []):
                    cluster_id = prop.get("cluster_id", "")
                    size = prop.get("size", 0)
                    proposals = prop.get("proposals", [])

                    text = f"[dimension_proposal] Cluster {cluster_id} (size={size}): "
                    text += "; ".join(
                        f"{p[0]}: {p[1]}" if isinstance(p, list) and len(p) >= 2 else str(p)
                        for p in proposals
                    )

                    entries.append({
                        "text": text,
                        "tools": [],
                        "source": "dimension_proposals",
                        "tags": ["source:dimension_proposal", "domain:architecture"],
                    })
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return entries


def read_cache_observer_analyses():
    """Read cache/observer_analyses.json — observer analysis results."""
    entries = []
    oa_path = CACHE_DIR / "observer_analyses.json"
    if not oa_path.exists():
        return entries

    try:
        data = json.loads(oa_path.read_text(encoding="utf-8", errors="replace"))
        analyses = data.get("analyses", data) if isinstance(data, dict) else data
        if isinstance(analyses, list):
            for a in analyses:
                if not isinstance(a, dict):
                    continue
                summary = a.get("summary", a.get("description", ""))
                if not summary:
                    continue
                findings = a.get("findings", [])
                text = f"[observer_analysis] {summary}"
                if findings:
                    text += " Findings: " + "; ".join(str(f) for f in findings[:3])

                entries.append({
                    "text": text,
                    "tools": [],
                    "source": "observer_analyses",
                    "tags": ["source:observer", "domain:research"],
                })
        elif isinstance(analyses, dict):
            for key, val in analyses.items():
                if isinstance(val, dict) and val.get("summary"):
                    entries.append({
                        "text": f"[observer_analysis:{key}] {val['summary']}",
                        "tools": [],
                        "source": "observer_analyses",
                        "tags": ["source:observer", "domain:research"],
                    })
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return entries


def read_error_logs():
    """Extract error patterns from log files."""
    entries = []

    error_files = [
        LOGS_DIR / "errors.log",
        LOGS_DIR / "agent.log",
        LOGS_DIR / "autonomous_agent.log",
    ]

    for log_path in error_files:
        if not log_path.exists():
            continue

        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue

        # Extract ERROR/Traceback patterns — group consecutive error lines
        error_blocks = []
        current_block = []
        in_error = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_error and current_block:
                    error_blocks.append("\n".join(current_block))
                    current_block = []
                    in_error = False
                continue

            if any(kw in stripped for kw in ["ERROR", "Traceback", "Exception", "CRITICAL", "failed"]):
                in_error = True
                current_block.append(stripped[:200])
            elif in_error:
                current_block.append(stripped[:200])

        if current_block:
            error_blocks.append("\n".join(current_block))

        # Deduplicate and summarize error blocks
        seen_hashes = set()
        for block in error_blocks[:20]:  # cap at 20 per log
            h = hashlib.md5(block.encode("utf-8")).hexdigest()[:8]
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            # Extract error type
            error_type = "unknown_error"
            for kw in ["Traceback", "ModuleNotFoundError", "FileNotFoundError",
                       "ConnectionError", "TimeoutError", "ValueError", "KeyError",
                       "PermissionError", "sqlite3", "ImportError"]:
                if kw.lower() in block.lower():
                    error_type = kw.lower().replace("error", "_error")
                    break

            # Extract the log file name as a tag
            log_name = log_path.stem

            entries.append({
                "text": f"[error:{error_type}] {block[:400]}",
                "tools": [],
                "source": f"log_{log_name}",
                "tags": [f"source:log", f"error_type:{error_type}", f"log_file:{log_name}"],
            })

    return entries


def read_cache_outcomes():
    """Read cache/outcomes/*.jsonl — session outcome data."""
    entries = []
    outcomes_dir = CACHE_DIR / "outcomes"
    if not outcomes_dir.exists():
        return entries

    for f in sorted(outcomes_dir.glob("outcomes_*.jsonl")):
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                o = json.loads(line)
                task = o.get("task_prompt", "")
                result = o.get("final_result", "")
                tools = o.get("tools_used", [])
                task_type = o.get("task_type", "unknown")
                duration = o.get("duration_seconds", "?")

                text = f"{task} -> {result[:500]}"
                entries.append({
                    "text": text,
                    "tools": tools,
                    "source": "outcome_tracker",
                    "tags": [f"task_type:{task_type}"],
                })
        except (json.JSONDecodeError, TypeError):
            continue

    return entries


def read_rss_monitor():
    """Read cache/rss_monitor/latest.json — CPA/arbitrage articles."""
    entries = []
    cache_file = CACHE_DIR / "rss_monitor" / "latest.json"
    if not cache_file.exists():
        return entries

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8", errors="replace"))
        for feed_id, feed_entries in data.get("feeds", {}).items():
            for entry in feed_entries:
                title = entry.get("title", "")
                url = entry.get("url", "")
                summary = entry.get("summary", "")
                tags = entry.get("tags", [])
                topic = entry.get("topic", feed_id)

                text = f"[rss:{feed_id}] {title} — {summary[:300]}"
                if url:
                    text += f" ({url})"

                entry_tags = [f"source:rss", f"feed:{feed_id}", f"topic:{topic}"]
                entry_tags.extend([f"tag:{t}" for t in tags[:5]])

                entries.append({
                    "text": text,
                    "tools": [],
                    "source": f"rss_{feed_id}",
                    "tags": entry_tags,
                })
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return entries


def read_youtube_watch():
    """Read cache/youtube_watch/latest.json — CPA/arbitrage videos."""
    entries = []
    cache_file = CACHE_DIR / "youtube_watch" / "latest.json"
    if not cache_file.exists():
        return entries

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8", errors="replace"))
        for channel_id, channel_data in data.get("channels", {}).items():
            topic = channel_data.get("topic", channel_id)
            for video in channel_data.get("videos", []):
                title = video.get("title", "")
                url = video.get("url", "")
                duration = video.get("duration", "")

                text = f"[youtube:{channel_id}] {title}"
                if duration:
                    text += f" [{duration}]"
                if url:
                    text += f" ({url})"

                entries.append({
                    "text": text,
                    "tools": [],
                    "source": f"youtube_{channel_id}",
                    "tags": [f"source:youtube", f"channel:{channel_id}", f"topic:{topic}"],
                })
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    return entries


# ── Pattern Extractors ────────────────────────────────────────────────────────

def extract_knowledge_patterns():
    """Extract knowledge patterns from existing cube entries and code."""
    entries = []

    # Scan Python scripts for conventions / patterns
    scripts_dir = SCRIPT_DIR
    for py_file in scripts_dir.glob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Extract module docstrings as conventions
        doc_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if doc_match:
            docstring = doc_match.group(1).strip().split("\n")[0][:200]
            if len(docstring) > 20:
                entries.append({
                    "text": f"[convention] {py_file.stem}: {docstring}",
                    "tools": [],
                    "source": f"script_{py_file.stem}",
                    "tags": [f"source:code", f"script:{py_file.stem}", "domain:coding"],
                })

        # Extract TODO/FIXME/HACK patterns as actionable knowledge
        for match in re.finditer(r'#\s*(TODO|FIXME|HACK|NOTE|XXX)\s*[:\-]?\s*(.+)', content):
            tag = match.group(1).lower()
            note = match.group(2).strip()[:200]
            if len(note) > 10:
                entries.append({
                    "text": f"[{tag}] {py_file.stem}: {note}",
                    "tools": [],
                    "source": f"script_{py_file.stem}",
                    "tags": [f"source:code", f"note_type:{tag}", f"script:{py_file.stem}"],
                })

    # Extract error/failure patterns from existing cube for recurring issues
    try:
        conn = kc.get_db()
        rows = conn.execute("""
            SELECT axis_domain, axis_outcome, COUNT(*) as cnt
            FROM experiences
            WHERE axis_outcome = 'failure'
            GROUP BY axis_domain
            HAVING cnt >= 2
        """).fetchall()
        conn.close()

        for row in rows:
            domain = row["axis_domain"] if isinstance(row, dict) else row[0]
            cnt = row["cnt"] if isinstance(row, dict) else row[2]
            entries.append({
                "text": f"[recurring_failure] Domain '{domain}' has {cnt} failures — needs investigation",
                "tools": [],
                "source": "cube_analysis",
                "tags": ["source:cube_analysis", f"domain:{domain}", "pattern:recurring"],
            })
    except Exception:
        pass

    return entries


# ── Feeder Engine ─────────────────────────────────────────────────────────────

def feed_entries(entries, dry_run=False):
    """Feed a list of entries into the knowledge cube. Returns count of new entries."""
    added = 0
    skipped = 0

    for entry in entries:
        text = entry.get("text") or ""
        if not text.strip():
            skipped += 1
            continue
        tools = entry.get("tools", [])
        source = entry.get("source", "cube_feeder")
        extra_tags = entry.get("tags", [])

        if dry_run:
            added += 1
            continue

        # Use knowledge_cube's add_experience which handles:
        # - hash deduplication
        # - domain classification
        # - outcome classification
        # - auto-tagging
        # - white spot detection
        result = kc.add_experience(
            text=text,
            tools=tools,
            source=source,
            dynamic_axes={"feeder_source": source},
        )

        if result.get("status") == "added":
            added += 1
            # Add extra tags from the source reader
            if extra_tags:
                try:
                    conn = kc.get_db()
                    row_id = conn.execute(
                        "SELECT id FROM experiences WHERE hash=?",
                        (kc.compute_hash(text),)
                    ).fetchone()
                    if row_id:
                        existing = conn.execute(
                            "SELECT tags FROM experiences WHERE id=?", (row_id["id"],)
                        ).fetchone()
                        if existing:
                            existing_tags = json.loads(existing["tags"])
                            merged = list(set(existing_tags + extra_tags))
                            conn.execute(
                                "UPDATE experiences SET tags=? WHERE id=?",
                                (json.dumps(merged), row_id["id"])
                            )
                            conn.commit()
                    conn.close()
                except Exception:
                    pass
        else:
            skipped += 1

    # Emit knowledge_cube_updated event if records were added
    if added > 0:
        try:
            # Collect domains from newly added entries by re-classifying their text
            added_domains = set()
            for entry in entries:
                text = entry.get("text", "")
                if text:
                    domain = kc.classify_domain(text, entry.get("tools"))
                    added_domains.add(domain)
            emit_event("knowledge_cube_updated", {
                "count": added,
                "domains": sorted(added_domains),
            })
            # Chain heartbeat
            from chain_heartbeat import event_beat
            event_beat("knowledge_added")
            # Event-driven ripple
            try:
                from ripple_consumer import on_knowledge_added
                on_knowledge_added()
            except ImportError:
                pass
        except ImportError:
            pass
        except Exception as e:
            print(f"  [cube_feeder] emit knowledge_cube_updated failed: {e}", file=sys.stderr)

    return added, skipped

def update_white_spot_flags():
    """Mark domains with <WHITE_SPOT_THRESHOLD entries as white spots."""
    if not DB_PATH.exists():
        return 0

    try:
        conn = kc.get_db()

        # Get current domain counts
        domain_counts = {}
        rows = conn.execute(
            "SELECT axis_domain, COUNT(*) as cnt FROM experiences GROUP BY axis_domain"
        ).fetchall()
        for row in rows:
            domain_counts[row["axis_domain"]] = row["cnt"]

        # Find underpopulated domains
        underpopulated = {d for d, c in domain_counts.items() if c < WHITE_SPOT_THRESHOLD}

        # Update white_spot flag for entries in underpopulated domains
        updated = 0
        for domain in underpopulated:
            result = conn.execute(
                "UPDATE experiences SET is_white_spot=1 WHERE axis_domain=? AND is_white_spot=0",
                (domain,)
            )
            updated += result.rowcount

        # Clear white_spot flag for domains that are now above threshold
        for domain, count in domain_counts.items():
            if count >= WHITE_SPOT_THRESHOLD:
                conn.execute(
                    "UPDATE experiences SET is_white_spot=0 WHERE axis_domain=? AND is_white_spot=1",
                    (domain,)
                )

        conn.commit()
        conn.close()
        return updated
    except Exception as e:
        print(f"Warning: white_spot update failed: {e}", file=sys.stderr)
        return 0


# ── CLI Interface ─────────────────────────────────────────────────────────────

def main():
    # Heartbeat: module alive
    try:
        from chain_heartbeat import beat
        beat("cube_feeder")
    except ImportError:
        pass

    import argparse
    parser = argparse.ArgumentParser(description="Feed knowledge into the Knowledge Cube")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added without writing")
    parser.add_argument("--source", choices=["lavra", "cache", "logs", "scripts", "outcomes", "all"],
                        default="all", help="Which data source to feed from")
    args = parser.parse_args()

    sources = {
        "lavra": read_lavra_knowledge,
        "cache": lambda: (
            read_cache_decisions()
            + read_cache_suggestions()
            + read_cache_dimension_proposals()
            + read_cache_observer_analyses()
        ),
        "logs": read_error_logs,
        "scripts": extract_knowledge_patterns,
        "outcomes": read_cache_outcomes,
        "rss": read_rss_monitor,
        "youtube": read_youtube_watch,
    }

    if args.source == "all":
        reader_funcs = list(sources.values())
    else:
        reader_funcs = [sources[args.source]]

    # Collect entries from all selected sources
    all_entries = []
    source_counts = {}
    for reader in reader_funcs:
        entries = reader()
        all_entries.extend(entries)
        source_counts[reader.__name__ if hasattr(reader, '__name__') else 'unknown'] = len(entries)

    # Deduplicate within this batch (same text)
    seen = set()
    unique_entries = []
    for e in all_entries:
        h = hashlib.md5(e["text"].encode("utf-8")).hexdigest()[:16]
        if h not in seen:
            seen.add(h)
            unique_entries.append(e)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"=== Cube Feeder [{mode}] ===")
    print(f"Sources collected: {len(unique_entries)} unique entries")

    # Feed into cube
    added, skipped = feed_entries(unique_entries, dry_run=args.dry_run)

    # Update white spot flags
    white_spot_updates = 0 if args.dry_run else update_white_spot_flags()

    # Print results
    print(f"New entries added: {added}")
    print(f"Duplicates skipped: {skipped}")
    print(f"White spot flags updated: {white_spot_updates}")

    # Print stats
    if not args.dry_run:
        try:
            stats = kc.get_cube_stats()
            print(f"\n--- Knowledge Cube Stats ---")
            print(f"Total experiences: {stats['total_experiences']}")
            print(f"White spots: {stats['white_spots']} ({stats['white_spot_pct']}%)")
            print(f"Domains: {', '.join(f'{d}({c})' for d,c in list(stats['domains'].items())[:8])}")
            print(f"Outcomes: {', '.join(f'{o}({c})' for o,c in stats['outcomes'].items())}")
        except Exception:
            pass

    return added


# ── Public API (backward-compatible with old cube_feeder.py) ──────────────────

def feed_from_session_summary(summary_text, tools=None):
    """Feed a session summary into the cube."""
    return kc.add_experience(
        text=summary_text,
        tools=tools or [],
        source="session_cron",
    )


def feed_from_outcome(outcome_dict):
    """Feed a single outcome into the cube."""
    o = outcome_dict
    text = f"{o.get('task_prompt', '')} -> {o.get('final_result', '')[:500]}"
    return kc.add_experience(
        text=text,
        tools=o.get("tools_used", []),
        source="outcome",
        dynamic_axes={
            "task_type": o.get("task_type", "unknown"),
            "duration": str(o.get("duration_seconds", "?")),
        },
    )


def feed_all_sources(dry_run=False):
    """Feed from all data sources. Returns (added, skipped)."""
    all_entries = (
        read_lavra_knowledge()
        + read_cache_decisions()
        + read_cache_suggestions()
        + read_cache_dimension_proposals()
        + read_cache_observer_analyses()
        + read_error_logs()
        + read_cache_outcomes()
        + extract_knowledge_patterns()
    )
    added, skipped = feed_entries(all_entries, dry_run=dry_run)
    if not dry_run:
        update_white_spot_flags()
    return added, skipped


def _feed_all_sources_with_heartbeat(dry_run=False):
    """feed_all_sources + heartbeat."""
    added, skipped = feed_all_sources(dry_run=dry_run)
    if not dry_run and added > 0:
        try:
            from chain_heartbeat import event_beat
            event_beat("knowledge_added")
            # Event-driven ripple
            try:
                from ripple_consumer import on_knowledge_added
                on_knowledge_added()
            except ImportError:
                pass
        except ImportError:
            pass
    return added, skipped


# ── Event-Driven Handlers ───────────────────────────────────────────────────
# These are called by event_bus.py DIRECT_EVENT_HANDLERS when specific
# events arrive. They do lightweight, targeted feeds instead of full scans.

def _run_cube_feeder_on_session_completed(event):
    """Event handler: session_completed → feed session outcomes into cube."""
    payload = event.get("payload", {})
    session_id = payload.get("session_id", "unknown")
    # Read only outcomes (newest session data)
    entries = read_cache_outcomes()
    if not entries:
        print(f"  [cube_feeder] session_completed: no new outcomes to feed")
        return
    added, skipped = feed_entries(entries)
    print(f"  [cube_feeder] session_completed ({session_id}): +{added} new, {skipped} dupes")
    if added > 0:
        update_white_spot_flags()


def _run_cube_feeder_on_new_signal(event):
    """Event handler: new_external_signal → feed new signal data into cube."""
    payload = event.get("payload", {})
    signal_text = payload.get("text", "") or payload.get("title", "")
    signal_source = payload.get("source", "signal_daemon")

    if not signal_text:
        print(f"  [cube_feeder] new_external_signal: no text in payload, skipping")
        return

    # Feed the signal directly as an experience
    result = kc.add_experience(
        text=f"[signal:{signal_source}] {signal_text[:500]}",
        tools=[],
        source=f"event_signal_{signal_source}",
        dynamic_axes={"signal_source": signal_source},
    )
    status = result.get("status", "unknown")
    print(f"  [cube_feeder] new_external_signal: {status} (source={signal_source})")


def _run_cube_feeder_on_knowledge_added(event):
    """Event handler: knowledge_added → feed new knowledge entries into cube."""
    payload = event.get("payload", {})
    domain = payload.get("domain", "unknown")
    count = payload.get("count", 1)

    # Re-scan cache sources for any new entries since last full feed
    entries = (
        read_cache_decisions()
        + read_cache_suggestions()
        + read_cache_dimension_proposals()
        + read_cache_observer_analyses()
    )
    if not entries:
        print(f"  [cube_feeder] knowledge_added: no cache entries to feed")
        return
    added, skipped = feed_entries(entries)
    print(f"  [cube_feeder] knowledge_added ({domain}): +{added} new, {skipped} dupes (event count={count})")
    if added > 0:
        update_white_spot_flags()


def _run_cube_feeder_on_error_logged(event):
    """Event handler: error_logged → capture error patterns into cube."""
    payload = event.get("payload", {})
    script = payload.get("script", "unknown")
    error_msg = payload.get("error", "") or payload.get("text", "")

    if not error_msg:
        print(f"  [cube_feeder] error_logged: no error text, skipping")
        return

    # Feed the error as a cube experience (will be classified as failure)
    result = kc.add_experience(
        text=f"[error] {script}: {error_msg[:400]}",
        tools=[],
        source=f"event_error_{script}",
        dynamic_axes={"error_source": script},
    )
    status = result.get("status", "unknown")
    print(f"  [cube_feeder] error_logged ({script}): {status}")


def _run_cube_feeder_on_boot(event):
    """Event handler: boot_completed → full feed from all sources."""
    print(f"  [cube_feeder] boot_completed: running full feed from all sources")
    added, skipped = feed_all_sources()
    print(f"  [cube_feeder] boot_completed: +{added} new, {skipped} dupes")


def get_runtime_context():
    """Get cube context for runtime skill injection."""
    stats = kc.get_cube_stats()
    white = kc.get_white_spots(10)

    lines = [
        f"## Knowledge Cube ({stats['total_experiences']} experiences)",
        f"White spots: {stats['white_spots']} ({stats['white_spot_pct']}%)",
        f"Top domains: {', '.join(f'{d}({c})' for d,c in list(stats['domains'].items())[:5])}",
        f"Outcomes: {', '.join(f'{o}({c})' for o,c in stats['outcomes'].items())}",
    ]

    if white:
        lines.append("\n### Recent White Spots (unclassified)")
        for w in white[:5]:
            lines.append(f"- [{w['ts'][:10]}] {w['raw_text'][:100]}")

    if stats["pending_clusters"]:
        lines.append(f"\n### Pending Dimension Proposals: {len(stats['pending_clusters'])}")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
    sys.exit(0)
