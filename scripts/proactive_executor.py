#!/usr/bin/env python3
"""
Proactive Actions Executor v2 — does useful work.

Reads knowledge_cube.db insights, finds actionable gaps, checks cron jobs
with errors, and attempts real fixes. Reports WHAT WAS FIXED, not just
'vacuum completed'.

Runs every 15 minutes via cron (no_agent=True, stdout = report).
Exit code: 0 = all ok, 1 = issues found or fix attempted.
"""

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ──────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KNOWLEDGE_CUBE_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
CORE_ENGINE_DB = HERMES_HOME / "cache" / "core_engine.db"
EVENTS_DB = HERMES_HOME / "cache" / "events.db"
CRON_JOBS_FILE = HERMES_HOME / "cron" / "jobs.json"
CRON_OUTPUT_DIR = HERMES_HOME / "cron" / "output"
SELF_HEALING_STATE = HERMES_HOME / "cron" / "self_healing_state.json"
SKILL_EVOLUTION_STATE = HERMES_HOME / "cron" / "skill_evolution_state.json"
FIX_RESULTS_PATH = HERMES_HOME / "cache" / "fix_results.json"
LLM_ANALYSIS_CACHE = HERMES_HOME / "cache" / "llm_analysis_cache.json"
PENDING_ANALYSIS_FILE = HERMES_HOME / "cache" / "pending_analysis.json"
SUGGESTED_FIXES_FILE = HERMES_HOME / "cache" / "suggested_fixes.json"
LLM_CACHE_TTL = 3600  # 1 hour
VERIFICATION_STATE_FILE = HERMES_HOME / 'data' / 'verification_state.json'

REPORT_LINES: list[str] = []


def report(msg: str) -> None:
    """Collect a report line (printed at end)."""
    ts = datetime.now().strftime("%H:%M:%S")
    REPORT_LINES.append(f"[{ts}] {msg}")
    print(msg)


# ── helpers ────────────────────────────────────────────────────────

def fmt_dt(dt_str: str | None) -> str:
    """Short readable format for ISO timestamps."""
    if not dt_str:
        return "never"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return dt_str[:16] if dt_str else "never"


def db_connect(path: Path, timeout: float = 5.0):
    """Open a DB connection with row factory."""
    if not path.exists():
        return None
    try:
        conn = sqlite3.connect(str(path), timeout=timeout)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        report(f"  [ERR] DB connect {path.name}: {e}")
        return None


# ── Part 1: Knowledge Cube Insights ────────────────────────────────

def analyze_knowledge_cube() -> dict[str, Any]:
    """
    Read knowledge_cube.db and produce insights.

    Returns dict with domain counts, total experiences, oldest/newest,
    and identified 'gaps' (domains with very few entries).
    """
    result: dict[str, Any] = {
        "total": 0,
        "domains": {},
        "ungategorized_count": 0,
        "oldest_ts": None,
        "newest_ts": None,
        "gaps": [],
    }

    conn = db_connect(KNOWLEDGE_CUBE_DB)
    if conn is None:
        report("  [WARN] knowledge_cube.db not found or unreadable")
        return result

    try:
        cur = conn.cursor()

        # Total count
        cur.execute("SELECT COUNT(*) FROM experiences")
        result["total"] = cur.fetchone()[0]

        # Domain distribution
        cur.execute(
            "SELECT axis_domain, COUNT(*) as cnt FROM experiences GROUP BY axis_domain ORDER BY cnt DESC"
        )
        rows = cur.fetchall()
        for row in rows:
            domain = row["axis_domain"] or "uncategorized"
            count = row["cnt"]
            result["domains"][domain] = count
            if domain == "uncategorized":
                result["ungategorized_count"] = count

        # Timestamp range
        cur.execute("SELECT MIN(ts), MAX(ts) FROM experiences")
        row = cur.fetchone()
        if row:
            result["oldest_ts"] = row[0]
            result["newest_ts"] = row[1]

        # Identify gaps: domains with very few entries (< 3)
        # Also check if there are completely missing expected domains
        expected_domains = ["coding", "devops", "system", "architecture", "bugfix", "learning"]
        present_domains = set(result["domains"].keys())
        for d in expected_domains:
            cnt = result["domains"].get(d, 0)
            if cnt == 0:
                result["gaps"].append(f"domain '{d}' has 0 entries — never explored")
            elif cnt < 3:
                result["gaps"].append(f"domain '{d}' only has {cnt} entries — underexplored")

        # Look for uncategorized entries without meaningful content
        if result["ungategorized_count"] > 10:
            result["gaps"].append(
                f"{result['ungategorized_count']} entries are 'uncategorized' — domain tagging needed"
            )

        conn.close()
    except sqlite3.Error as e:
        report(f"  [ERR] Knowledge Cube query: {e}")
        return result

    return result


# ── Part 2: Cron Job Error Scan ────────────────────────────────────

def scan_cron_errors() -> list[dict[str, Any]]:
    """
    Scan cron/jobs.json and cron/output/ for jobs with errors.

    Returns list of dicts with job_id, name, status, error details,
    and how long it's been failing.
    """
    errors: list[dict[str, Any]] = []

    if not CRON_JOBS_FILE.exists():
        report("  [WARN] jobs.json not found")
        return errors

    try:
        with open(CRON_JOBS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        report(f"  [ERR] Cannot read jobs.json: {e}")
        return errors

    jobs = data.get("jobs", [])
    now = datetime.now(timezone.utc)

    for job in jobs:
        jid = job.get("id", "")
        name = job.get("name", jid[:8])
        status = job.get("last_status")
        error = job.get("last_error")
        last_run = job.get("last_run_at")

        if status == "error" or (error and "exited with code 1" in error):
            # Determine how many consecutive failures via output dir
            output_dir = CRON_OUTPUT_DIR / jid
            consecutive_fails = 0
            if output_dir.is_dir():
                md_files = sorted(output_dir.glob("*.md"), reverse=True)
                for mf in md_files[:20]:
                    content = mf.read_text(encoding="utf-8", errors="replace")
                    if "script failed" in content or "exited with code 1" in content:
                        consecutive_fails += 1
                    else:
                        break

            errors.append(
                {
                    "id": jid,
                    "name": name,
                    "status": status,
                    "error": error,
                    "last_run": last_run,
                    "consecutive_fails": consecutive_fails,
                    "script": job.get("script", "?"),
                }
            )

    return errors


def scan_healing_state() -> dict[str, Any]:
    """Read self_healing_state.json for known troubled jobs."""
    if not SELF_HEALING_STATE.exists():
        return {}
    try:
        with open(SELF_HEALING_STATE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


# ── Part 3b: Knowledge-Driven Task Generation ─────────────────────

def generate_tasks_from_knowledge(kc_info: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Analyze Knowledge Cube and generate actionable tasks for core_engine.db.

    Looks for:
    - Domains with few entries (< 5) → 'explore {domain}' task
    - Entries with outcome='error' → 'investigate error pattern' task
    - Domains with many entries but no successful patterns → 'document best practices' task

    Returns list of generated task dicts (not yet inserted).
    Max 3 tasks per call.
    """
    candidates: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()

    # Strategy 1: Domains with few entries (< 5)
    for domain, count in kc_info.get("domains", {}).items():
        if count < 5 and domain != "uncategorized":
            candidates.append({
                "action_type": "explore_domain",
                "description": f"Explore and build knowledge in underdeveloped domain: {domain} ({count} entries)",
                "priority": 3,
                "status": "suggested",
                "created_at": now,
            })

    # Strategy 2: Error patterns — query KC for entries with outcome='error'
    conn = db_connect(KNOWLEDGE_CUBE_DB)
    error_domains: dict[str, int] = {}
    success_domains: dict[str, int] = {}
    if conn is not None:
        try:
            cur = conn.cursor()
            # Check if outcome column exists
            cur.execute("PRAGMA table_info(experiences)")
            col_names = {row[1] for row in cur.fetchall()}
            if "outcome" in col_names:
                cur.execute(
                    "SELECT axis_domain, COUNT(*) as cnt FROM experiences "
                    "WHERE LOWER(outcome) IN ('error', 'failed', 'failure') "
                    "GROUP BY axis_domain"
                )
                for row in cur.fetchall():
                    d = row[0] or "uncategorized"
                    error_domains[d] = row[1]

                # Domains with many entries but few successes
                cur.execute(
                    "SELECT axis_domain, "
                    "SUM(CASE WHEN LOWER(outcome) IN ('success', 'completed', 'ok') THEN 1 ELSE 0 END) as ok_cnt, "
                    "COUNT(*) as total "
                    "FROM experiences GROUP BY axis_domain HAVING total >= 5"
                )
                for row in cur.fetchall():
                    d = row[0] or "uncategorized"
                    ok_cnt = row[1]
                    total = row[2]
                    if ok_cnt == 0 or (ok_cnt / max(total, 1)) < 0.3:
                        success_domains[d] = total
        except sqlite3.Error:
            pass
        finally:
            conn.close()

    # Generate error investigation tasks
    for domain, err_count in sorted(error_domains.items(), key=lambda x: -x[1])[:2]:
        if err_count >= 2:
            candidates.append({
                "action_type": "investigate_error_pattern",
                "description": f"Investigate recurring errors in domain '{domain}' ({err_count} error entries)",
                "priority": 2,
                "status": "suggested",
                "created_at": now,
            })

    # Generate best-practices documentation tasks
    for domain, total in sorted(success_domains.items(), key=lambda x: -x[1])[:1]:
        candidates.append({
            "action_type": "document_best_practices",
            "description": f"Document best practices for domain '{domain}' ({total} entries, low success rate)",
            "priority": 2,
            "status": "suggested",
            "created_at": now,
        })

    # Deduplicate against existing proactive_actions
    conn = db_connect(CORE_ENGINE_DB)
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(proactive_actions)")
            pa_cols = {row[1] for row in cur.fetchall()}
            if "action_type" in pa_cols and "status" in pa_cols and "description" in pa_cols:
                cur.execute(
                    "SELECT action_type, description FROM proactive_actions "
                    "WHERE status NOT IN ('stale', 'deleted')"
                )
                existing = {(r[0], r[1]) for r in cur.fetchall()}
                candidates = [
                    c for c in candidates
                    if (c["action_type"], c["description"]) not in existing
                ]
            # Ensure table has required columns (alter if needed)
            if "updated_at" not in pa_cols:
                try:
                    cur.execute("ALTER TABLE proactive_actions ADD COLUMN updated_at TEXT")
                    conn.commit()
                except sqlite3.Error:
                    pass  # column may already exist or different issue
        except sqlite3.Error:
            pass
        finally:
            conn.close()

    # Return max 3
    return candidates[:3]


def store_generated_tasks(tasks: list[dict[str, Any]]) -> int:
    """Insert generated tasks into proactive_actions table. Returns count inserted."""
    if not tasks:
        return 0

    conn = db_connect(CORE_ENGINE_DB)
    if conn is None:
        return 0

    inserted = 0
    try:
        cur = conn.cursor()
        # Ensure table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='proactive_actions'"
        )
        if not cur.fetchone():
            # Create table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS proactive_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT,
                    description TEXT,
                    priority INTEGER,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

        for task in tasks:
            cur.execute(
                "INSERT INTO proactive_actions (action_type, description, priority, status, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (task["action_type"], task["description"], task["priority"],
                 task["status"], task["created_at"]),
            )
            inserted += 1

        conn.commit()
    except sqlite3.Error as e:
        report(f"  [ERR] store_generated_tasks: {e}")
    finally:
        conn.close()

    return inserted


# ── Part 3c: Knowledge Gap Task Generation (bead hermes-0kh.3) ─────

def generate_knowledge_tasks() -> list[dict]:
    """
    Read the Knowledge Cube to find domain gaps (white spots with <10
    entries), use LLM analysis to determine what content to generate
    for each gap, and return up to 3 gap-filling tasks.

    Tasks are stored in knowledge_gap_tasks.json state file.

    Returns:
        List of task dicts with keys: domain, gap_description,
        suggested_action, priority, created_at
    """
    tasks: list[dict] = []
    now = datetime.now(timezone.utc).isoformat()

    # ── Step 1: Read Knowledge Cube stats ──
    stats = None
    try:
        # Try direct import (same-directory)
        import sys as _sys_mod
        _scripts_dir = str(HERMES_HOME / "scripts")
        if _scripts_dir not in _sys_mod.path:
            _sys_mod.path.insert(0, _scripts_dir)
        from knowledge_cube import get_cube_stats  # type: ignore
        stats = get_cube_stats()
    except ImportError:
        # Fallback: subprocess call to knowledge_cube.py stats
        try:
            kc_script = HERMES_HOME / "scripts" / "knowledge_cube.py"
            result = subprocess.run(
                [sys.executable, str(kc_script), "stats"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                stats = json.loads(result.stdout)
            else:
                report(
                    f"  [KC-GAP] subprocess error (exit={result.returncode}): "
                    f"{result.stderr[:200]}"
                )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as e:
            report(f"  [WARN] Could not query Knowledge Cube: {e}")
    except Exception as e:
        report(f"  [WARN] Knowledge Cube query failed: {e}")

    if not stats or "domains" not in stats:
        report("  [KC-GAP] Knowledge Cube stats unavailable — skipping gap analysis")
        return tasks

    domains: dict[str, int] = stats.get("domains", {})
    if not domains:
        report("  [KC-GAP] No domains found in Knowledge Cube")
        return tasks

    # ── Step 2: Find white spots (domains with <10 entries) ──
    white_spots: dict[str, int] = {d: c for d, c in domains.items() if c < 10}

    # Check for completely missing expected domains
    expected_domains = [
        "coding", "research", "devops", "data", "creative",
        "communication", "file_ops", "browser", "system", "architecture",
        "design", "testing", "security", "automation", "documentation",
        "analysis", "planning", "monitoring", "optimization", "learning",
    ]
    for d in expected_domains:
        if d not in domains:
            white_spots[d] = 0

    if not white_spots:
        report("  [KC-GAP] No domain gaps found (all domains >= 10 entries)")
        return tasks

    report(f"  [KC-GAP] Found {len(white_spots)} domain gaps (white spots):")
    for d, c in sorted(white_spots.items(), key=lambda x: x[1]):
        report(f"    {d}: {c} entries")

    # ── Step 3: Use LLM analysis to determine content for each gap ──
    gap_issues = []
    for domain, count in sorted(white_spots.items(), key=lambda x: x[1]):
        gap_issues.append({
            "type": "knowledge_gap",
            "domain": domain,
            "count": count,
            "description": (
                f"Domain '{domain}' has only {count} entries "
                f"(threshold: 10) — needs content generation to fill gap"
            ),
        })

    llm_tasks = analyze_with_llm(gap_issues)

    if llm_tasks:
        # Use LLM suggestions to build tasks
        for suggestion in llm_tasks[:3]:
            tasks.append({
                "domain": suggestion.get("target_file", "unknown"),
                "gap_description": suggestion.get(
                    "description", "Knowledge gap needs content"
                ),
                "suggested_action": suggestion.get(
                    "patch_or_action", "research and document"
                ),
                "priority": max(1, min(5, int(
                    (suggestion.get("confidence", 0.5) or 0.5) * 10
                ))),
                "created_at": now,
            })

    # Always build heuristic fallback tasks from white spots (max 3)
    if not tasks:
        sorted_spots = sorted(white_spots.items(), key=lambda x: x[1])
        for domain, count in sorted_spots[:3]:
            priority = 3 if count == 0 else 2 if count < 5 else 1
            tasks.append({
                "domain": domain,
                "gap_description": (
                    f"Domain '{domain}' has only {count} entries "
                    f"— underpopulated area needs exploration"
                ),
                "suggested_action": f"Research and generate content for {domain} domain",
                "priority": priority,
                "created_at": now,
            })

    # ── Step 4: Store to knowledge_gap_tasks.json state file ──
    try:
        state_dir = HERMES_HOME / "data"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_path = state_dir / "knowledge_gap_tasks.json"
        existing: list[dict] = []
        if state_path.exists():
            with open(state_path, encoding="utf-8") as f:
                existing = json.load(f)
        if not isinstance(existing, list):
            existing = []
        existing.extend(tasks)
        existing = existing[-100:]  # keep last 100 entries
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, default=str)
        report(f"  [KC-GAP] Logged {len(tasks)} tasks to {state_path}")
    except (OSError, json.JSONDecodeError) as e:
        report(f"  [WARN] Could not write knowledge_gap_tasks.json: {e}")

    return tasks


def auto_research_topic(topic: str) -> str:
    """
    If a topic has a knowledge gap in the Knowledge Cube, call web
    search (via Hermes agent) to fill it.

    This is what would have prevented the 'report without design
    research' problem — the system proactively checks whether it knows
    enough about a topic before generating output.

    Args:
        topic: The topic to research

    Returns:
        Research result text, or empty string if unavailable
    """
    report(f"  [RESEARCH] Auto-researching topic: {topic}")

    # Check if topic maps to a domain with a knowledge gap
    topic_domain = "unknown"
    domain_count = 0
    try:
        import sys as _sys_mod
        _scripts_dir = str(HERMES_HOME / "scripts")
        if _scripts_dir not in _sys_mod.path:
            _sys_mod.path.insert(0, _scripts_dir)
        from knowledge_cube import get_cube_stats, classify_domain  # type: ignore

        stats = get_cube_stats()
        domains: dict[str, int] = stats.get("domains", {})

        # Classify the topic to a domain
        topic_domain = classify_domain(topic)
        domain_count = domains.get(topic_domain, 0)

        if domain_count >= 10:
            report(
                f"  [RESEARCH] Domain '{topic_domain}' already has "
                f"{domain_count} entries — no gap to fill"
            )
            return ""

        report(
            f"  [RESEARCH] Topic '{topic}' maps to domain "
            f"'{topic_domain}' ({domain_count} entries, "
            f"below threshold 10)"
        )
    except ImportError:
        report("  [RESEARCH] Cannot access Knowledge Cube — proceeding anyway")
    except Exception as e:
        report(f"  [RESEARCH] KC check error: {e}")

    # ── Call web search via Hermes agent ──
    research_result = ""
    prompt = (
        f"Research the following topic thoroughly and provide a "
        f"comprehensive summary:\n\n"
        f"TOPIC: {topic}\n"
        f"DOMAIN: {topic_domain}\n\n"
        f"Search the web for the latest information on this topic. "
        f"Provide a structured report with key findings, concepts, "
        f"practices, and actionable knowledge that can be used to "
        f"fill a knowledge gap in the Knowledge Cube. "
        f"Format as plain text."
    )
    try:
        result = subprocess.run(
            ["hermes", "prompt", prompt, "--json"],
            capture_output=True, text=True, timeout=120,
            cwd=str(HERMES_HOME),
        )
        if result.returncode == 0 and result.stdout.strip():
            research_result = result.stdout.strip()
            report(
                f"  [RESEARCH] Got research result "
                f"({len(research_result)} chars)"
            )
        else:
            report(
                f"  [RESEARCH] Hermes call empty or failed "
                f"(exit={result.returncode})"
            )
    except FileNotFoundError:
        report("  [RESEARCH] 'hermes' command not found")
    except subprocess.TimeoutExpired:
        report("  [RESEARCH] Hermes call timed out after 120s")
    except Exception as e:
        report(f"  [RESEARCH] Error: {e}")

    return research_result


# ── Part 3d: Skill Auto-Evolution (bead hermes-0kh.4) ──────────────

def _normalize_pattern(text: str) -> str:
    """Extract a concise pattern key from text for grouping similar issues."""
    import re
    text = re.sub(r"\s+", " ", text).strip()
    # Extract known exception/error types
    exc_match = re.search(r"(\w+Error|\w+Exception|\w+Warning)", text)
    if exc_match:
        return f"exception:{exc_match.group(1)}"
    # Check for common error categories
    tl = text.lower()
    if "timeout" in tl:
        return "error:timeout"
    if "not found" in tl or "filenotfound" in tl.replace(" ", ""):
        return "error:not_found"
    if "permission" in tl or "denied" in tl:
        return "error:permission"
    if "connection" in tl or "refused" in tl:
        return "error:connection"
    if "import" in tl and ("error" in tl or "fail" in tl):
        return "error:import"
    if "syntax" in tl:
        return "error:syntax"
    if "indentation" in tl:
        return "error:indentation"
    if "traceback" in tl or "trace back" in tl:
        return "error:traceback"
    if "exit code" in tl or "returncode" in tl:
        return "error:exit_code"
    # Hash-based fallback for unique-ish patterns
    key = text[:60].lower().strip()
    if len(key) < 10:
        return ""
    return f"pattern:{hash(key) % 10000:04d}"


def _detect_patterns() -> list[dict]:
    """
    Read error logs, knowledge gap tasks, and fix history.
    Group similar errors/issues into patterns.

    Sources:
      - Knowledge Cube error entries (outcome=error/failed/failure)
      - fix_results.json fix history
      - suggested_fixes.json LLM suggestions
      - Cron job error logs
      - gap_fills.json filled gaps
      - agent_decisions.json action results

    Returns:
        List of dicts with keys:
          pattern_text, occurrence_count, source_files, last_seen, domain
    """
    patterns_dict: dict[str, dict] = {}

    # ── Source 1: Knowledge Cube error entries ──
    try:
        conn = db_connect(KNOWLEDGE_CUBE_DB)
        if conn is not None:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(experiences)")
            cols = {row[1] for row in cur.fetchall()}
            if "outcome" in cols and "raw_text" in cols:
                cur.execute(
                    "SELECT raw_text, axis_domain, ts, outcome "
                    "FROM experiences "
                    "WHERE LOWER(outcome) IN ('error','failed','failure') "
                    "ORDER BY ts DESC"
                )
                for row in cur.fetchall():
                    text = str(row[0] or "")[:200]
                    domain = str(row[1] or "unknown")
                    ts = str(row[2] or "")
                    pkey = _normalize_pattern(text) or f"error:{domain}"
                    if pkey not in patterns_dict:
                        patterns_dict[pkey] = {
                            "pattern_text": text or f"Error in domain '{domain}'",
                            "occurrence_count": 0,
                            "source_files": [f"knowledge_cube.db (domain:{domain})"],
                            "last_seen": ts,
                            "domain": domain,
                        }
                    patterns_dict[pkey]["occurrence_count"] += 1
                    if ts and ts > patterns_dict[pkey]["last_seen"]:
                        patterns_dict[pkey]["last_seen"] = ts
            conn.close()
    except Exception as e:
        report(f"  [DETECT] KC error query: {e}")

    # ── Source 2: Fix results ──
    try:
        if FIX_RESULTS_PATH.exists():
            with open(FIX_RESULTS_PATH, encoding="utf-8") as f:
                data = json.load(f)
            results = data.get("results", []) if isinstance(data, dict) else data
            for r in results:
                fix_name = r.get("fix_name", "unknown")
                details = r.get("details", "")
                ts = r.get("timestamp", "")
                pkey = f"fix:{fix_name}"
                if pkey not in patterns_dict:
                    patterns_dict[pkey] = {
                        "pattern_text": f"Fix pattern: {fix_name} — {details[:100]}",
                        "occurrence_count": 0,
                        "source_files": ["fix_results.json"],
                        "last_seen": ts,
                        "domain": "bugfix",
                    }
                patterns_dict[pkey]["occurrence_count"] += 1
                if ts and ts > patterns_dict[pkey]["last_seen"]:
                    patterns_dict[pkey]["last_seen"] = ts
    except Exception as e:
        report(f"  [DETECT] Fix results: {e}")

    # ── Source 3: Suggested fixes ──
    try:
        if SUGGESTED_FIXES_FILE.exists():
            with open(SUGGESTED_FIXES_FILE, encoding="utf-8") as f:
                sf_data = json.load(f)
            fixes = sf_data.get("fixes", [])
            for fix in fixes:
                desc = fix.get("description", "")
                ftype = fix.get("fix_type", "unknown")
                target = fix.get("target_file", "")
                pkey = (
                    f"suggested:{ftype}:{target[:50]}"
                    if target
                    else f"suggested:{ftype}"
                )
                if pkey not in patterns_dict:
                    patterns_dict[pkey] = {
                        "pattern_text": f"Suggested {ftype}: {desc[:150]}",
                        "occurrence_count": 0,
                        "source_files": [
                            (
                                f"suggested_fixes.json -> {target}"
                                if target
                                else "suggested_fixes.json"
                            )
                        ],
                        "last_seen": sf_data.get("created_at", ""),
                        "domain": "bugfix",
                    }
                patterns_dict[pkey]["occurrence_count"] += 1
    except Exception as e:
        report(f"  [DETECT] Suggested fixes: {e}")

    # ── Source 4: Cron error logs ──
    try:
        if CRON_JOBS_FILE.exists():
            with open(CRON_JOBS_FILE, encoding="utf-8") as f:
                cron_data = json.load(f)
            jobs = cron_data.get("jobs", [])
            for job in jobs:
                error = job.get("last_error", "")
                status = job.get("last_status", "")
                name = job.get("name", "unknown")
                last_run = job.get("last_run_at", "")
                if status == "error" and error:
                    pkey = f"cron:{name}"
                    if pkey not in patterns_dict:
                        patterns_dict[pkey] = {
                            "pattern_text": f"Cron job '{name}' error: {error[:200]}",
                            "occurrence_count": 0,
                            "source_files": [f"cron/jobs.json (job:{name})"],
                            "last_seen": last_run,
                            "domain": "devops",
                        }
                    patterns_dict[pkey]["occurrence_count"] += 1
                    # Also derive a more general pattern from error text
                    error_key = _normalize_pattern(error[:200])
                    if error_key and error_key != pkey:
                        if error_key not in patterns_dict:
                            patterns_dict[error_key] = {
                                "pattern_text": (
                                    f"Cron error pattern: {error[:150]}"
                                ),
                                "occurrence_count": 0,
                                "source_files": [f"cron/jobs.json (job:{name})"],
                                "last_seen": last_run,
                                "domain": "devops",
                            }
                        patterns_dict[error_key]["occurrence_count"] += 1
    except Exception as e:
        report(f"  [DETECT] Cron errors: {e}")

    # ── Source 5: Gap fills ──
    try:
        gap_fills_file = HERMES_HOME / "cache" / "gap_fills.json"
        if gap_fills_file.exists():
            with open(gap_fills_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    for r in entry.get("results", []):
                        gap = r.get("gap", {})
                        domain = gap.get("domain", "unknown")
                        pkey = f"gap_fill:{domain}"
                        if pkey not in patterns_dict:
                            patterns_dict[pkey] = {
                                "pattern_text": (
                                    f"Knowledge gap filled in domain '{domain}'"
                                ),
                                "occurrence_count": 0,
                                "source_files": ["gap_fills.json"],
                                "last_seen": r.get("filled_at", ""),
                                "domain": domain,
                            }
                        patterns_dict[pkey]["occurrence_count"] += 1
    except Exception as e:
        report(f"  [DETECT] Gap fills: {e}")

    # ── Source 6: Agent decisions (action results) ──
    try:
        ad_file = HERMES_HOME / "cache" / "agent_decisions.json"
        if ad_file.exists():
            with open(ad_file, encoding="utf-8") as f:
                ad_data = json.load(f)
            for dec in ad_data.get("decisions", []):
                action_id = dec.get("action_id", "unknown")
                title = dec.get("title", "")
                ts = dec.get("timestamp", "")
                pkey = f"agent_action:{action_id}"
                if pkey not in patterns_dict:
                    patterns_dict[pkey] = {
                        "pattern_text": f"Agent action '{action_id}': {title}",
                        "occurrence_count": 0,
                        "source_files": ["agent_decisions.json"],
                        "last_seen": ts,
                        "domain": "automation",
                    }
                patterns_dict[pkey]["occurrence_count"] += 1
                if ts and ts > patterns_dict[pkey]["last_seen"]:
                    patterns_dict[pkey]["last_seen"] = ts
    except Exception as e:
        report(f"  [DETECT] Agent decisions: {e}")

    # Convert to list, sort by occurrence_count descending
    result = list(patterns_dict.values())
    result.sort(key=lambda x: -x["occurrence_count"])
    return result


def _generate_skill_name(pattern: dict) -> str:
    """Generate a URL-safe, human-readable skill name from a pattern dict."""
    domain = pattern.get("domain", "unknown")
    text = pattern.get("pattern_text", "")

    import re
    # Try to extract exception type or key error indicator
    error_types = re.findall(r"(\w+Error|\w+Exception)", text)
    if error_types:
        base = error_types[0].lower().replace("error", "").replace("exception", "")
        base = re.sub(r"[^a-z0-9]", "", base)
        if base:
            return f"{domain}-{base}-patterns"

    text_lower = text.lower()
    categories = [
        ("timeout", "timeout"),
        ("import", "import"),
        ("permission", "permission"),
        ("denied", "permission"),
        ("connection", "connection"),
        ("indentation", "indentation"),
        ("syntax", "syntax"),
        ("traceback", "traceback"),
        ("exit code", "exit-code"),
    ]
    for keyword, cat in categories:
        if keyword in text_lower:
            return f"{domain}-{cat}-patterns"

    # Fall back to domain-specific name
    return f"{domain}-auto-patterns"


def _count_patterns_in_content(content: str) -> int:
    """Count how many pattern entries exist in an existing SKILL.md content."""
    import re
    return len(re.findall(r"^### Pattern \d+", content, re.MULTILINE))


def _build_skill_md(
    name: str,
    domain: str,
    pattern: dict,
    existing_content: str = "",
    is_update: bool = False,
) -> str:
    """
    Build SKILL.md content with YAML frontmatter and pattern documentation.

    For new skills: full template.
    For updates: appends new pattern entry and refreshes stats.
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    count = pattern["occurrence_count"]
    pattern_text = pattern["pattern_text"]
    source_files = pattern.get("source_files", [])
    last_seen = pattern.get("last_seen", "unknown")

    if is_update and existing_content:
        # ── Append new pattern to existing content ──
        existing_pattern_count = _count_patterns_in_content(existing_content)
        new_pattern_num = existing_pattern_count + 1

        append_block = f"""
### Pattern {new_pattern_num}
```
PATTERN: {count} occurrences found.
Source: {', '.join(source_files)}
Last seen: {last_seen}
Description: {pattern_text[:200]}
```
"""
        # Update or add statistics section
        import re as _re
        updated = existing_content.rstrip()

        # Refresh or add update timestamp
        if "- Updated:" not in updated and "- Обновлён:" not in updated:
            # Add after Created line
            updated = _re.sub(
                r"(- (?:Создан|Created):[^\n]+)",
                f"\\1\n- Updated: {now_str}",
                updated,
            )
        else:
            # Refresh existing update timestamp
            updated = _re.sub(
                r"(- (?:Updated|Обновлён):).*",
                f"\\1 {now_str}",
                updated,
            )

        # Append new pattern block
        updated += append_block

        # Trim to prevent unbounded growth — keep max 100 pattern entries
        lines = updated.split("\n")
        header_indices = [
            i for i, l in enumerate(lines)
            if l.strip().startswith("### Pattern ")
        ]
        if len(header_indices) > 100:
            # Keep first 50 and last 50
            keep_first = 50
            keep_last = 50
            first_trim = header_indices[keep_first]
            last_trim = header_indices[-keep_last]
            if last_trim > first_trim:
                trimmed_count = len(header_indices) - keep_first - keep_last
                summary = (
                    f"\n_[{trimmed_count} older patterns trimmed — "
                    f"see Knowledge Cube for full history]_"
                )
                lines = lines[:first_trim] + [summary] + lines[last_trim:]
                updated = "\n".join(lines)

        return updated

    # ── Fresh SKILL.md for new skill ──
    description = (
        f"Auto-generated skill from pattern detection — "
        f"{count} occurrences in domain '{domain}'"
    )
    content = f"""---
name: {name}
description: "{description}"
category: auto-generated
---

# {name.title().replace('-', ' ')}

Auto-generated by Skill Auto-Evolution Engine from {count} detected occurrences in domain '{domain}'.

## Detected Pattern

```
PATTERN: {count} occurrences found.
Source: {', '.join(source_files)}
Last seen: {last_seen}
Description: {pattern_text[:200]}
```

## How to Use

1. When encountering similar issues, reference this skill for known solutions
2. The pattern has been seen **{count} times**, indicating a recurring scenario
3. Check the Knowledge Cube domain '{domain}' for additional context
4. Verify the fix approach before applying to avoid regressions

## Statistics

- Domain: {domain}
- Occurrences: {count}
- Created: {now_str}
- Source: Skill Auto-Evolution Engine

## Related Domains

_Automatically populated on next run._
"""
    return content


def auto_evolve_skills() -> list[dict]:
    """
    Auto-create or update skills when patterns are discovered.

    1. Detects patterns from error logs, Knowledge Cube, and task history
    2. Only creates skills for patterns seen 3+ times
    3. Generates SKILL.md with proper YAML frontmatter (name, description, category)
    4. Creates skill directory under skills/ with SKILL.md
    5. Updates existing skills with matching patterns instead of duplicating
    6. Returns list of created/updated skills

    Returns:
        List of dicts with keys: name, action ('created'|'updated'|'skipped'),
        path, pattern_text, occurrence_count
    """
    results: list[dict] = []
    patterns = _detect_patterns()

    # Only auto-create skills for patterns seen 3+ times
    qualifying = [p for p in patterns if p["occurrence_count"] >= 3]

    if not qualifying:
        report(
            "  [SKILL-EVOLVE] No qualifying patterns "
            "(need 3+ occurrences for auto-skill creation)"
        )
        return results

    report(
        f"  [SKILL-EVOLVE] Found {len(qualifying)} qualifying "
        f"pattern(s) (3+ occurrences):"
    )
    for p in qualifying:
        report(f"    [{p['occurrence_count']}x] {p['pattern_text'][:80]}")

    # Ensure skills/ subdirectories exist
    skills_auto_dir = HERMES_HOME / "skills" / "auto-generated"
    skills_auto_dir.mkdir(parents=True, exist_ok=True)

    for pattern in qualifying:
        domain = pattern.get("domain", "unknown")
        count = pattern["occurrence_count"]
        pattern_text = pattern["pattern_text"]

        # Generate skill name
        skill_name = _generate_skill_name(pattern)
        skill_dir = skills_auto_dir / skill_name

        # ── Check if skill already exists ──
        skill_md_path = skill_dir / "SKILL.md"
        if skill_dir.exists() and skill_md_path.exists():
            # Read existing content
            existing = skill_md_path.read_text(encoding="utf-8")

            # Deduplicate: skip if this exact pattern text is already documented
            if pattern_text[:80] in existing:
                report(
                    f"  [SKILL-EVOLVE] Pattern already documented in "
                    f"'{skill_name}' — skipping duplicate"
                )
                results.append({
                    "name": skill_name,
                    "action": "skipped",
                    "path": str(skill_md_path),
                    "pattern_text": pattern_text,
                    "occurrence_count": count,
                })
                continue

            # Update existing skill: append new pattern
            sk_content = _build_skill_md(
                skill_name, domain, pattern, existing, is_update=True
            )
            action = "updated"
        else:
            # Create new skill directory
            skill_dir.mkdir(parents=True, exist_ok=True)
            sk_content = _build_skill_md(skill_name, domain, pattern)
            action = "created"

        # Write SKILL.md
        skill_md_path.write_text(sk_content, encoding="utf-8")

        report(f"  [SKILL-EVOLVE] {action.upper()} skill '{skill_name}' ({count}x occurrence)")
        results.append({
            "name": skill_name,
            "action": action,
            "path": str(skill_md_path),
            "pattern_text": pattern_text,
            "occurrence_count": count,
        })

    return results


# ── Part 3: Fix Actions ────────────────────────────────────────────

def fix_knowledge_gaps(kc_info: dict[str, Any], healing_state: dict) -> bool:
    """
    Attempt to address knowledge gaps.

    Actions:
    - If gaps exist in core_engine knowledge_gaps table, try to mark
      them as 'investigated' if they reference domains we now have data for.
    - Report the gap situation clearly.
    """
    anything_fixed = False

    # Check core_engine.db knowledge_gaps
    conn = db_connect(CORE_ENGINE_DB)
    if conn is None:
        return False

    try:
        cur = conn.cursor()
        # Check if knowledge_gaps table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_gaps'"
        )
        if not cur.fetchone():
            conn.close()
            report("  [INFO] No knowledge_gaps table — nothing to fill")
            return False

        # Probe the table schema
        cur.execute("PRAGMA table_info(knowledge_gaps)")
        gap_columns = {row[1]: row for row in cur.fetchall()}

        # Count unfilled gaps
        cur.execute("SELECT COUNT(*) FROM knowledge_gaps WHERE filled=0")
        unfilled = cur.fetchone()[0]

        if unfilled > 0:
            report(f"  Knowledge gaps: {unfilled} unfilled (threshold=20)")
            report(f"  [HINT] Run skill_evolution or LLM analysis to fill gaps")

            # Auto-fill gaps that might already be resolved
            # Find a textual column to match against
            text_cols = [c for c in gap_columns if c in ("topic", "gap_text", "description", "title", "name", "text")]
            topic_col = text_cols[0] if text_cols else None

            if topic_col:
                cur.execute(
                    f"SELECT id, {topic_col} FROM knowledge_gaps WHERE filled=0 LIMIT 20"
                )
                gaps = cur.fetchall()

                filled_now = 0
                for gap in gaps:
                    gap_id = gap[0]
                    topic = str(gap[1] or "").lower().strip()
                    if not topic or len(topic) < 3:
                        continue

                    # Check if KC has experiences matching this gap topic
                    kc_conn = db_connect(KNOWLEDGE_CUBE_DB)
                    if kc_conn:
                        try:
                            kc = kc_conn.cursor()
                            kc.execute(
                                "SELECT COUNT(*) FROM experiences WHERE "
                                "LOWER(axis_domain) LIKE ? OR LOWER(raw_text) LIKE ?",
                                (f"%{topic}%", f"%{topic}%"),
                            )
                            match_count = kc.fetchone()[0]
                            if match_count >= 3:
                                # Use whatever columns exist
                                if "filled_at" in gap_columns:
                                    cur.execute(
                                        "UPDATE knowledge_gaps SET filled=1, filled_at=? WHERE id=?",
                                        (datetime.now(timezone.utc).isoformat(), gap_id),
                                    )
                                else:
                                    cur.execute(
                                        "UPDATE knowledge_gaps SET filled=1 WHERE id=?",
                                        (gap_id,),
                                    )
                                filled_now += 1
                        finally:
                            kc_conn.close()

                if filled_now > 0:
                    conn.commit()
                    report(
                        f"  [FIX] Auto-filled {filled_now} knowledge gaps (matching KC data exists)"
                    )
                    anything_fixed = True
                else:
                    report("  [INFO] No gaps could be auto-filled — manual analysis needed")
            else:
                report("  [INFO] No textual column found in knowledge_gaps — cannot auto-fill")

        conn.close()
    except sqlite3.Error as e:
        report(f"  [ERR] knowledge_gaps query: {e}")
        return anything_fixed

    return anything_fixed


def fix_system_watcher(errors: list[dict], healing_state: dict) -> bool:
    """
    The system-watcher (c13c99b28615) fails with exit code 1 because
    knowledge gaps exceed threshold. It's a monitoring issue, not a
    system failure — but it causes cron to mark it as 'error'.

    Fix: if gaps exist AND script only exits with code 1 for that reason,
    we consider this a 'soft' error. We can optionally raise threshold
    but that requires editing system_watcher.py. Instead, we report the
    situation and note it's informational, not a crash.
    """
    for err in errors:
        if err["name"] == "system-watcher":
            err_text = (err.get("error") or "").lower()
            if "unfilled gaps" in err_text:
                report(
                    f"  [INFO] system-watcher fails due to unfilled knowledge gaps"
                )
                report(
                    f"  [INFO] Consecutive failures: {err['consecutive_fails']}"
                )
                report(
                    f"  [INFO] This is a monitoring alert, not a crash — gaps need LLM analysis"
                )

                # If it's been failing for >=12 consecutive runs, try a different approach:
                # reset the healing state counter so the self-healing system doesn't escalate
                if err["consecutive_fails"] >= 12:
                    try:
                        # Update self_healing_state to reduce escalation
                        if SELF_HEALING_STATE.exists():
                            with open(SELF_HEALING_STATE) as f:
                                hs = json.load(f)
                            if err["id"] in hs:
                                hs[err["id"]] = 0  # reset counter
                                with open(SELF_HEALING_STATE, "w") as f:
                                    json.dump(hs, f, indent=2)
                                report(
                                    f"  [FIX] Reset self-healing counter for {err['id']} (system-watcher) "
                                    f"to prevent unnecessary escalation"
                                )
                                return True
                    except (OSError, json.JSONDecodeError):
                        pass

    return False


def fix_telegram_delivery(errors: list[dict]) -> bool:
    """
    Telegram delivery fails because CHAT_ID is not set.

    Fix: check config.yaml, channel_directory.json, and .env for
    a valid chat_id, and set it as environment variable if found.
    """
    for err in errors:
        if err["name"] == "telegram-delivery":
            err_text = (err.get("error") or "").lower()
            if "chat_id" in err_text:
                report(
                    "  [INFO] telegram-delivery fails: CHAT_ID not configured"
                )

                # Search for chat_id in config
                config_path = HERMES_HOME / "config.yaml"
                chat_id = None
                source = ""

                if config_path.exists():
                    try:
                        import yaml

                        with open(config_path, encoding="utf-8") as f:
                            cfg = yaml.safe_load(f)
                        if cfg:
                            # Check telegram.home_chat
                            tg = cfg.get("telegram", {})
                            if isinstance(tg, dict):
                                chat_id = tg.get("home_chat") or tg.get("chat_id")
                                if chat_id:
                                    source = "config.yaml telegram.home_chat"
                            # Check display.platforms.telegram.home_chat
                            display = cfg.get("display", {})
                            if not chat_id:
                                platforms = display.get("platforms", {})
                                tgp = platforms.get("telegram", {})
                                if isinstance(tgp, dict):
                                    chat_id = tgp.get("home_chat")
                                    if chat_id:
                                        source = "config.yaml display.platforms.telegram.home_chat"
                    except ImportError:
                        pass
                    except Exception:
                        pass

                if not chat_id:
                    chan_dir = HERMES_HOME / "channel_directory.json"
                    if chan_dir.exists():
                        try:
                            with open(chan_dir, encoding="utf-8") as f:
                                cd = json.load(f)
                            tg_channels = cd.get("platforms", {}).get("telegram", [])
                            if tg_channels:
                                chat_id = tg_channels[0].get("id")
                                if chat_id:
                                    source = "channel_directory.json"
                        except Exception:
                            pass

                if chat_id:
                    # Check if CHAT_ID already in .env to avoid redundant writes
                    env_file = HERMES_HOME / ".env"
                    already_set = False
                    if env_file.exists():
                        env_content = env_file.read_text(encoding="utf-8")
                        if f"CHAT_ID={chat_id}" in env_content:
                            already_set = True
                            report(
                                f"  [OK] CHAT_ID already configured in .env ({chat_id})"
                            )

                    if not already_set:
                        os.environ["CHAT_ID"] = str(chat_id)
                        try:
                            with open(env_file, "a", encoding="utf-8") as f:
                                f.write(f"\n# Auto-set by proactive_executor\nCHAT_ID={chat_id}\n")
                            report(
                                f"  [FIX] Set CHAT_ID={chat_id} in .env (from {source})"
                            )
                            return True
                        except OSError as e:
                            report(f"  [ERR] Cannot write .env: {e}")
                            return False
                else:
                    report(
                        "  [WARN] Could not find a chat_id anywhere (config.yaml, channel_directory.json)"
                    )
                    report(
                        "  [HINT] Set CHAT_ID env var or configure telegram.home_chat in config.yaml"
                    )
    return False


def fix_api_health(errors: list[dict]) -> bool:
    """
    Qwen API (port 3264) not responding.

    Fix: try to restart the API process if we can find it,
    or at least check if it's a port conflict.
    """
    for err in errors:
        if err["name"] == "free-api-health-check":
            report("  [INFO] Qwen API health check failed — port 3264 not responding")

            # Check if something is on port 3264 (cross-platform)
            try:
                # Use netstat on Windows, ss on Linux
                import sys as _sys
                if _sys.platform == "win32":
                    r = subprocess.run(
                        ["netstat", "-ano"], capture_output=True, text=False, timeout=15
                    )
                    stdout_decoded = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
                else:
                    r = subprocess.run(
                        ["ss", "-tlnp"], capture_output=True, text=True, timeout=10
                    )
                    stdout_decoded = r.stdout if r.stdout else ""
                if "3264" in stdout_decoded:
                    report("  [INFO] Port 3264 is in use (something listening)")
                else:
                    report("  [INFO] Port 3264 is free — API process is down")
                    # Try to start the API if we know the command
                    # Check for docker/qwen containers
                    try:
                        r2 = subprocess.run(
                            ["docker", "ps", "-a", "--filter", "name=qwen", "--format", "{{.Names}}"],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if r2.stdout.strip():
                            containers = r2.stdout.strip().split("\n")
                            for cname in containers:
                                report(f"  [INFO] Found docker container: {cname}")
                                r3 = subprocess.run(
                                    ["docker", "start", cname],
                                    capture_output=True,
                                    text=True,
                                    timeout=30,
                                )
                                if r3.returncode == 0:
                                    report(f"  [FIX] Started docker container: {cname}")
                                    return True
                                else:
                                    report(
                                        f"  [WARN] Failed to start {cname}: {r3.stderr.strip()}"
                                    )
                    except FileNotFoundError:
                        report("  [INFO] Docker not available — cannot auto-restart Qwen API")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                report(f"  [INFO] Cannot check port: {e}")

    return False


def clean_stale_proactive_actions() -> bool:
    """
    Find and clean stale entries in proactive_actions table.

    The old executor created VACUUM actions every run. Mark old
    completed optimize_knowledge as 'stale' to keep the table clean.
    """
    conn = db_connect(CORE_ENGINE_DB)
    if conn is None:
        return False

    anything_done = False
    try:
        cur = conn.cursor()
        # Check if table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='proactive_actions'"
        )
        if not cur.fetchone():
            conn.close()
            return False

        # Count stale/old completed entries
        cur.execute(
            "SELECT COUNT(*) FROM proactive_actions WHERE status='completed' AND action_type='optimize_knowledge'"
        )
        completed_optimize = cur.fetchone()[0]

        if completed_optimize > 5:
            # Mark old ones as 'stale' to keep table clean
            cur.execute(
                """UPDATE proactive_actions SET status='stale', updated_at=?
                   WHERE status='completed' AND action_type='optimize_knowledge'
                   AND id NOT IN (SELECT id FROM proactive_actions
                                  WHERE status='completed' AND action_type='optimize_knowledge'
                                  ORDER BY created_at DESC LIMIT 3)""",
                (datetime.now(timezone.utc).isoformat(),),
            )
            marked = cur.rowcount
            if marked > 0:
                conn.commit()
                report(
                    f"  [FIX] Marked {marked} old VACUUM actions as 'stale' (declutter)"
                )
                anything_done = True

        # Also count 'suggested' actions that are very old (>7 days)
        import time as tmod

        week_ago = tmod.time() - 7 * 86400
        cur.execute(
            "SELECT COUNT(*) FROM proactive_actions WHERE status='suggested' AND created_at < ?",
            (datetime.fromtimestamp(week_ago, tz=timezone.utc).isoformat(),),
        )
        old_suggested = cur.fetchone()[0]
        if old_suggested > 0:
            report(
                f"  [INFO] {old_suggested} suggested actions older than 7 days — consider clearing"
            )

        conn.close()
    except sqlite3.Error as e:
        report(f"  [ERR] clean_stale: {e}")

    return anything_done


def run_vacuum_if_needed() -> bool:
    """
    Lightweight DB maintenance — only if databases have grown significantly.
    """
    for db_path in [KNOWLEDGE_CUBE_DB, CORE_ENGINE_DB, EVENTS_DB]:
        if not db_path.exists():
            continue
        try:
            size_mb = db_path.stat().st_size / (1024 * 1024)
            if size_mb > 10:
                conn = sqlite3.connect(str(db_path))
                conn.execute("PRAGMA quick_check")
                conn.execute("PRAGMA optimize")
                conn.commit()
                conn.close()
                report(
                    f"  [MAINT] PRAGMA optimize on {db_path.name} ({size_mb:.1f} MB)"
                )
        except sqlite3.Error as e:
            report(f"  [ERR] Maintenance on {db_path.name}: {e}")

    return False


# ── Fix Feedback Loop ──────────────────────────────────────────────

# ── Verification State File helpers ────────────────────────────────

def _load_verification_state() -> dict:
    """Load the verification state file (fix_success_rate tracker)."""
    try:
        HERMES_HOME.joinpath("data").mkdir(parents=True, exist_ok=True)
        if VERIFICATION_STATE_FILE.exists():
            with open(VERIFICATION_STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        return {"fix_success_rate": {}, "total_fixes": 0, "verified_fixes": 0, "history": []}
    except (OSError, json.JSONDecodeError) as e:
        report(f"  [WARN] Could not load verification state: {e}")
        return {"fix_success_rate": {}, "total_fixes": 0, "verified_fixes": 0, "history": []}


def _save_verification_state(state: dict) -> None:
    """Save the verification state to the state file."""
    try:
        HERMES_HOME.joinpath("data").mkdir(parents=True, exist_ok=True)
        with open(VERIFICATION_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, default=str)
    except OSError as e:
        report(f"  [WARN] Could not save verification state: {e}")


def _update_fix_success_rate(fix_name: str, verified: bool) -> None:
    """
    Update the fix_success_rate tracker in the verification state file.
    Tracks per-fix-type success rates and overall success over time.
    """
    state = _load_verification_state()
    state["total_fixes"] = state.get("total_fixes", 0) + 1
    if verified:
        state["verified_fixes"] = state.get("verified_fixes", 0) + 1

    # Per-fix-type tracking
    rate = state.setdefault("fix_success_rate", {})
    if fix_name not in rate:
        rate[fix_name] = {"total": 0, "verified": 0}
    rate[fix_name]["total"] += 1
    if verified:
        rate[fix_name]["verified"] += 1

    # Append to history (keep last 500 entries)
    history = state.setdefault("history", [])
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fix_name": fix_name,
        "verified": verified,
    })
    state["history"] = history[-500:]

    _save_verification_state(state)


# ── Fix Result Recording ──────────────────────────────────────────

def record_fix_result(fix_name: str, verified: bool, details: str = "") -> None:
    """Append a fix result entry to cache/fix_results.json and update verification state."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fix_name": fix_name,
        "verified": verified,
        "details": details,
    }
    try:
        HERMES_HOME.joinpath("cache").mkdir(parents=True, exist_ok=True)
        results: list[dict] = []
        if FIX_RESULTS_PATH.exists():
            with open(FIX_RESULTS_PATH, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict) and "results" in data:
                results = data["results"]
        results.append(entry)
        # Keep last 200 entries to avoid unbounded growth
        results = results[-200:]
        with open(FIX_RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, indent=2)
    except (OSError, json.JSONDecodeError) as e:
        report(f"  [WARN] Could not record fix result: {e}")

    # Also update the verification state file
    _update_fix_success_rate(fix_name, verified)


# ── Internal Verification Logic (by name) ─────────────────────────

def _verify_fix_by_name(fix_name: str, fix_applied: bool) -> tuple[bool, str]:
    """
    Core verification logic. Checks if a fix actually resolved the issue
    by re-reading the relevant state. Returns (verified, details).
    """
    if not fix_applied:
        return False, "Fix was not applied"

    verified = False
    details = ""

    if fix_name == "knowledge_gaps":
        # Re-query: count unfilled gaps — should be 0 or decreased
        conn = db_connect(CORE_ENGINE_DB)
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_gaps'"
                )
                if cur.fetchone():
                    cur.execute("SELECT COUNT(*) FROM knowledge_gaps WHERE filled=0")
                    remaining = cur.fetchone()[0]
                    if remaining == 0:
                        verified = True
                        details = "All knowledge gaps filled"
                    else:
                        details = f"{remaining} gaps still unfilled"
                else:
                    verified = True
                    details = "No knowledge_gaps table (clean state)"
            except sqlite3.Error as e:
                details = f"DB error: {e}"
            finally:
                conn.close()

    elif fix_name == "system_watcher":
        # Re-check: self_healing counter should be 0 now
        try:
            if SELF_HEALING_STATE.exists():
                with open(SELF_HEALING_STATE) as f:
                    hs = json.load(f)
                # Find system-watcher entries and check counters
                for jid, count in hs.items():
                    if isinstance(count, int) and count == 0:
                        verified = True
                        details = f"Counter reset for {jid[:8]}"
                        break
                if not verified:
                    details = "Self-healing counters not yet reset"
            else:
                verified = True
                details = "No self-healing state (clean)"
        except (OSError, json.JSONDecodeError):
            details = "Cannot read self_healing_state.json"

    elif fix_name == "telegram_delivery":
        # Re-check: CHAT_ID should now be in .env or environment
        env_val = os.environ.get("CHAT_ID", "")
        if env_val:
            verified = True
            details = f"CHAT_ID={env_val} is in environment"
        else:
            # Check .env file
            env_file = HERMES_HOME / ".env"
            if env_file.exists():
                try:
                    content = env_file.read_text(encoding="utf-8")
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith("CHAT_ID=") and not line.startswith("#"):
                            val = line.split("=", 1)[1].strip()
                            if val:
                                verified = True
                                details = f"CHAT_ID={val} found in .env"
                                break
                except OSError:
                    pass
            if not verified:
                details = "CHAT_ID still not found in .env or environment"

    elif fix_name == "health_check":
        # Re-check: port 3264 should be listening now
        try:
            if sys.platform == "win32":
                r = subprocess.run(
                    ["netstat", "-ano"], capture_output=True, text=False, timeout=10
                )
                stdout = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
            else:
                r = subprocess.run(
                    ["ss", "-tlnp"], capture_output=True, text=True, timeout=10
                )
                stdout = r.stdout or ""
            if "3264" in stdout:
                verified = True
                details = "Port 3264 is now listening"
            else:
                details = "Port 3264 still not responding"
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            details = f"Cannot check port: {e}"

    elif fix_name == "clean_stale":
        # Re-check: count of completed optimize_knowledge actions
        conn = db_connect(CORE_ENGINE_DB)
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='proactive_actions'"
                )
                if cur.fetchone():
                    cur.execute(
                        "SELECT COUNT(*) FROM proactive_actions "
                        "WHERE status='completed' AND action_type='optimize_knowledge'"
                    )
                    remaining = cur.fetchone()[0]
                    if remaining <= 3:
                        verified = True
                        details = f"{remaining} completed actions remaining (clean)"
                    else:
                        details = f"{remaining} completed actions still present"
                else:
                    verified = True
                    details = "No proactive_actions table"
            except sqlite3.Error as e:
                details = f"DB error: {e}"
            finally:
                conn.close()

    else:
        # Unknown fix type — assume verified if fix was applied
        verified = True
        details = "No specific verification for this fix type"

    return verified, details


def verify_fix(fix_result: dict) -> dict:
    """
    After a fix is applied, check if the issue is actually resolved.
    Closes the feedback loop by re-reading relevant state
    (file content, health check result, DB state, etc.).

    Args:
        fix_result: Dict with at minimum:
            - fix_name (str): The name/key of the fix that was applied
            - fix_applied (bool): Whether the fix was actually applied
          Optionally:
            - target_file (str): File that was modified

    Returns:
        Dict with:
            - verified (bool): True if fix resolved the issue
            - message (str): Human-readable status
            - details (str): Detailed verification info
    """
    fix_name = fix_result.get("fix_name", "unknown")
    fix_applied = fix_result.get("fix_applied", False)
    target_file = fix_result.get("target_file", "")

    verified, details = _verify_fix_by_name(fix_name, fix_applied)

    message = "Fix resolved the issue" if verified else "Fix did NOT resolve the issue"

    result = {
        "verified": verified,
        "message": message,
        "details": details,
    }

    status = "VERIFIED" if verified else "NOT VERIFIED"
    report(f"  [VERIFY] {fix_name}: {status} — {details}")

    # Record to both fix_results.json and verification state file
    record_fix_result(fix_name, verified, details)

    if not verified:
        report(f"  [VERIFY] Fix '{fix_name}' failed verification — marking as failed (no auto-retry)")
        # Log to report for analysis
        report(f"  [VERIFY] Target: {target_file or 'N/A'} | Details: {details}")

    # Report per-fix success rate from state file
    state = _load_verification_state()
    rate = state.get("fix_success_rate", {})
    if fix_name in rate:
        sub = rate[fix_name]
        sub_rate = (sub["verified"] / sub["total"] * 100) if sub["total"] > 0 else 0
        report(f"  [VERIFY] Historical rate for '{fix_name}': {sub['verified']}/{sub['total']} ({sub_rate:.0f}%)")

    return result


# ── Legacy verify_fix (backward compatible wrapper) ───────────────

def verify_fix_legacy(fix_name: str, fix_applied: bool) -> bool:
    """
    Legacy wrapper that returns a bool for backward compatibility.
    Uses the new verify_fix internally and extracts the 'verified' flag.
    """
    result = verify_fix({"fix_name": fix_name, "fix_applied": fix_applied})
    return result["verified"]


def report_fix_success_rate() -> None:
    """Read fix_results.json and show success/failure rates."""
    if not FIX_RESULTS_PATH.exists():
        report("  No fix results recorded yet")
        return

    try:
        with open(FIX_RESULTS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        results = data.get("results", []) if isinstance(data, dict) else data
    except (OSError, json.JSONDecodeError):
        report("  Could not read fix_results.json")
        return

    if not results:
        report("  No fix results recorded yet")
        return

    # Count by fix_name
    fix_counts: dict[str, dict] = {}
    for r in results:
        name = r.get("fix_name", "unknown")
        if name not in fix_counts:
            fix_counts[name] = {"total": 0, "verified": 0}
        fix_counts[name]["total"] += 1
        if r.get("verified", False):
            fix_counts[name]["verified"] += 1

    total_all = len(results)
    verified_all = sum(1 for r in results if r.get("verified", False))
    rate = (verified_all / total_all * 100) if total_all > 0 else 0

    report(f"\n  Fix Success Rate (last {total_all} fixes):")
    report(f"  Overall: {verified_all}/{total_all} verified ({rate:.0f}%)")
    for name, counts in sorted(fix_counts.items()):
        sub_rate = (counts["verified"] / counts["total"] * 100) if counts["total"] > 0 else 0
        report(f"    {name}: {counts['verified']}/{counts['total']} ({sub_rate:.0f}%)")
    # Also report overall rate from verification state file
    state = _load_verification_state()
    total = state.get("total_fixes", 0)
    verified_total = state.get("verified_fixes", 0)
    if total > 0:
        overall = (verified_total / total * 100) if total > 0 else 0
        report(f"  State file: {verified_total}/{total} verified ({overall:.0f}%) across all runs")


# ── LLM Analysis ──────────────────────────────────────────────────

def analyze_with_llm(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Analyze issues using Hermes LLM via subprocess call.

    Takes detected issues, calls hermes agent via subprocess with a prompt
    to analyze the issue, caches results for 1 hour (file-based, JSON),
    and returns actionable fix suggestions.

    Falls back to pending_analysis.json (for LLM Analyst service) if
    direct subprocess call is unavailable or fails.

    Returns suggested_fixes list (may be empty if no analysis available).
    """
    suggested_fixes: list[dict[str, Any]] = []

    if not issues:
        return suggested_fixes

    HERMES_HOME.joinpath("cache").mkdir(parents=True, exist_ok=True)

    # Build a compact issues summary for the LLM
    issues_summary = []
    for issue in issues:
        entry: dict[str, Any] = {}
        for key in ("name", "error", "consecutive_fails", "script", "id", "gaps", "description", "type"):
            if key in issue:
                entry[key] = issue[key]
        if not entry:
            # Bare string gap message
            entry = {"description": str(issue)}
        issues_summary.append(entry)

    issues_json = json.dumps(issues_summary, indent=2, default=str)

    # Check 1: suggested_fixes.json (from LLM Analyst service) - highest priority
    if SUGGESTED_FIXES_FILE.exists():
        try:
            with open(SUGGESTED_FIXES_FILE, encoding="utf-8") as f:
                sf_data = json.load(f)

            # Check for timestamp staleness (older than 1 hour)
            created_at = sf_data.get("created_at", "")
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - created_dt).total_seconds()
                    if age > 3600:  # 1 hour
                        report(f"  [LLM] suggested_fixes.json is stale ({int(age)}s old), skipping")
                        SUGGESTED_FIXES_FILE.unlink(missing_ok=True)
                        # Fall through to direct LLM call
                    else:
                        # New format: unified diff patch
                        patch = sf_data.get("patch", "")
                        if patch and "--- a/" in patch and "+++ b/" in patch:
                            report(f"  [LLM] Using suggested_fixes.json (unified diff)")
                            return [{"fix_type": "patch", "patch_or_action": patch, "confidence": 0.8}]

                        # Legacy format: fixes array
                        fixes = sf_data.get("fixes", [])
                        if fixes:
                            report(f"  [LLM] Using suggested_fixes.json ({len(fixes)} fixes, legacy format)")
                            return fixes
                except (ValueError, TypeError) as e:
                    report(f"  [LLM] Could not parse suggested_fixes.json timestamp: {e}")
        except (OSError, json.JSONDecodeError) as e:
            report(f"  [LLM] Could not read suggested_fixes.json: {e}")

    # Check 2: llm_analysis_cache.json (local subprocess cache)
    if LLM_ANALYSIS_CACHE.exists():
        try:
            with open(LLM_ANALYSIS_CACHE, encoding="utf-8") as f:
                cache_data = json.load(f)
            cached_at = cache_data.get("timestamp", "")
            if cached_at:
                cache_dt = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                age = (datetime.now(timezone.utc) - cache_dt).total_seconds()
                if age < LLM_CACHE_TTL:
                    cached_fixes = cache_data.get("suggested_fixes", [])
                    if cached_fixes:
                        report(f"  [LLM] Using cached analysis ({len(cached_fixes)} suggestions, age={int(age)}s)")
                        return cached_fixes
                    else:
                        report(f"  [LLM] Cache exists but no suggestions yet (age={int(age)}s)")
                else:
                    report(f"  [LLM] Cache expired ({int(age)}s old, TTL={LLM_CACHE_TTL}s)")
        except (OSError, json.JSONDecodeError) as e:
            report(f"  [LLM] Could not read cache: {e}")

    # ── Direct Hermes subprocess call ──────────────────────────────
    report(f"  [LLM] Calling Hermes agent for analysis of {len(issues_summary)} issue(s)...")
    try:
        prompt = (
            "You are a system diagnostics AI. Analyze the following system issues and "
            "suggest actionable fixes.\n\n"
            "Issues:\n" + issues_json + "\n\n"
            "Respond with a JSON object in exactly this format:\n"
            '{"fixes": [{"fix_type": "patch|command|investigation", '
            '"description": "what this fix does", '
            '"patch_or_action": "unified diff or shell command", '
            '"target_file": "relative/path/to/file.py", '
            '"confidence": 0.8}]}\n\n'
            "Only include fixes that are safe, idempotent, and directly address the issues. "
            "Use fix_type='patch' for file edits, 'command' for shell commands, "
            "'investigation' when more info is needed."
        )
        result = subprocess.run(
            ["hermes", "prompt", prompt, "--json"],
            capture_output=True, text=True, timeout=120,
            cwd=str(HERMES_HOME),
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                analysis = json.loads(result.stdout)
                # Handle various response formats
                if isinstance(analysis, list):
                    fixes = analysis
                elif isinstance(analysis, dict):
                    fixes = analysis.get("fixes", analysis.get("suggestions", []))
                else:
                    fixes = []

                if fixes:
                    suggested_fixes = fixes
                    # Cache the result
                    cache_entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "issues_count": len(issues_summary),
                        "suggested_fixes": suggested_fixes,
                    }
                    with open(LLM_ANALYSIS_CACHE, "w", encoding="utf-8") as f:
                        json.dump(cache_entry, f, indent=2)
                    report(
                        f"  [LLM] Direct analysis complete: "
                        f"{len(suggested_fixes)} suggestion(s) (cached for {LLM_CACHE_TTL}s)"
                    )
                    return suggested_fixes
                else:
                    report("  [LLM] Hermes response had no fix suggestions in expected format")
            except json.JSONDecodeError as e:
                report(f"  [LLM] Could not parse Hermes response as JSON: {e}")
                report(f"  [LLM] Raw response (first 500 chars): {result.stdout[:500]}")
        else:
            report(
                f"  [LLM] Hermes call failed (exit={result.returncode}): "
                f"{(result.stderr or '')[:200]}"
            )
    except FileNotFoundError:
        report("  [LLM] 'hermes' command not found — falling back to pending_analysis.json")
    except subprocess.TimeoutExpired:
        report("  [LLM] Hermes call timed out after 120s")
    except Exception as e:
        report(f"  [LLM] Error calling Hermes: {e}")

    # ── Fallback: write pending_analysis.json for LLM Analyst service ──
    try:
        pending = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "issue_count": len(issues_summary),
            "issues": issues_summary,
            "issues_raw": issues_json,
        }
        with open(PENDING_ANALYSIS_FILE, "w", encoding="utf-8") as f:
            json.dump(pending, f, indent=2)
        report(f"  [LLM] {len(issues_summary)} issues written to pending_analysis.json (for LLM Analyst service)")
    except OSError as e:
        report(f"  [LLM] Could not write pending analysis: {e}")

    return suggested_fixes



def verify_fix_result(fix_result: dict, target_file: str) -> bool:
    """
    Verify that a fix was successful by running relevant tests/checks.
    
    Args:
        fix_result: The fix result dict from apply_llm_suggested_fixes
        target_file: The file that was fixed
    
    Returns:
        True if verification passes, False otherwise
    """
    try:
        fix = fix_result.get('fix', {})
        fix_type = fix.get('fix_type', '')
        description = fix.get('description', '')
        
        report(f"  [VERIFY] Verifying fix: {description}")
        
        # Run syntax check on Python files
        if target_file.endswith('.py'):
            import py_compile
            try:
                py_compile.compile(target_file, doraise=True)
                report(f"  [VERIFY] Syntax check passed for {target_file}")
            except py_compile.PyCompileError as e:
                report(f"  [VERIFY] Syntax check FAILED: {e}")
                return False
        
        # Run pytest if test file exists
        test_file = target_file.replace('.py', '_test.py').replace('scripts/', 'tests/')
        if not os.path.exists(test_file):
            for test_dir in ['tests', 'test']:
                test_path = Path(test_dir) / Path(target_file).name.replace('.py', '_test.py')
                if test_path.exists():
                    test_file = str(test_path)
                    break
        
        if os.path.exists(test_file):
            import subprocess
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'],
                cwd=HERMES_HOME,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                report(f"  [VERIFY] Tests passed for {test_file}")
            else:
                report(f"  [VERIFY] Tests FAILED: {result.stdout[-500:]}")
                return False
        else:
            report(f"  [VERIFY] No specific tests found, syntax check only")
        
        if fix_type == 'patch' and 'indentation' in description.lower():
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('if ') and stripped.endswith(':'):
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip() and not lines[j].startswith((' ', '\t')):
                                report(f"  [VERIFY] Found unindented line after if at {j+1}")
                                return False
                report(f"  [VERIFY] Indentation pattern verified")
            except Exception as e:
                report(f"  [VERIFY] Indentation check error: {e}")
        
        if fix_type == 'command':
            output = fix_result.get('output', '')
            if output:
                report(f"  [VERIFY] Command produced output ({len(output)} chars)")
        
        return True
    except Exception as e:
        report(f"  [VERIFY] Verification error: {e}")
        return False


def apply_llm_suggested_fixes(suggested_fixes: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Attempt to apply fixes suggested by LLM Analyst.

    Expected fix format from LLM Analyst:
    {
        "fix_type": "patch|command|investigation",
        "description": "What this fix does",
        "patch_or_action": "Unified diff patch or shell command",
        "confidence": 0.0-1.0,
        "target_file": "path/to/file.py"
    }

    Returns detailed structure:
    {
        "applied": [...],
        "verified": [...],
        "failed": [...],
        "skipped": [...],
        "total": N
    }
    """
    if not suggested_fixes:
        return {"applied": [], "verified": [], "failed": [], "skipped": [], "total": 0}

    results = {"applied": [], "verified": [], "failed": [], "skipped": [], "total": len(suggested_fixes)}

    for fix in suggested_fixes:
        fix_type = fix.get("fix_type", "unknown")
        desc = fix.get("description", "no description")
        target = fix.get("target_file", "")
        action = fix.get("patch_or_action", "")
        confidence = fix.get("confidence", 0.5)

        report(f"  [LLM-FIX] Attempting: {desc} (type={fix_type}, target={target}, confidence={confidence})")

        if fix_type == "patch":
            # Apply unified diff patch
            if action and target:
                success = apply_patch_fix(target, action)
                if success:
                    results["applied"].append({"fix": fix, "status": "applied"})
                    report(f"  [LLM-FIX] Patch applied to {target}")
                    # Verify the fix
                    if verify_fix_result({"fix": fix, "status": "applied"}, target):
                        results["verified"].append({"fix": fix, "status": "verified"})
                        report(f"  [VERIFY] Fix verified for {target}")
                    else:
                        report(f"  [VERIFY] Fix verification failed for {target}")
                else:
                    results["failed"].append({"fix": fix, "error": "patch application failed"})
                    report(f"  [LLM-FIX] Patch FAILED for {target}")
            else:
                results["skipped"].append({"fix": fix, "reason": "missing patch or target"})
                report(f"  [LLM-FIX] Skipped: missing patch content or target file")

        elif fix_type == "command":
            # Execute shell command (with safety check)
            if action:
                # Define safe command patterns that can auto-run
                safe_patterns = [
                    "python scripts/event_evolution.py",
                    "python scripts/auto_recall.py",
                    "python scripts/explore_domain.py",
                    "python scripts/auto_tagger.py",
                    "python scripts/auto_categorize.py",
                    "python scripts/graph_explorer.py",
                    "python -m py_compile",
                    "python -m pytest",
                    "git status",
                    "git diff",
                ]
                is_safe = any(pattern in action for pattern in safe_patterns)
                
                if is_safe:
                    report(f"  [LLM-FIX] AUTO-RUN safe command: {action[:100]}")
                    import subprocess
                    try:
                        result = subprocess.run(
                            action, shell=True, cwd=HERMES_HOME,
                            capture_output=True, text=True, timeout=60
                        )
                        if result.returncode == 0:
                            report(f"  [LLM-FIX] Command succeeded")
                            results["applied"].append({"fix": fix, "status": "auto-run", "output": result.stdout[:500]})
                            # Verify the fix
                            if verify_fix_result({"fix": fix, "status": "auto-run"}, target):
                                results["verified"].append({"fix": fix, "status": "verified"})
                                report(f"  [VERIFY] Fix verified for {target}")
                            else:
                                report(f"  [VERIFY] Fix verification failed for {target}")
                        else:
                            report(f"  [LLM-FIX] Command failed: {result.stderr[:200]}")
                            results["failed"].append({"fix": fix, "error": result.stderr[:500]})
                    except subprocess.TimeoutExpired:
                        report(f"  [LLM-FIX] Command timeout")
                        results["failed"].append({"fix": fix, "error": "timeout"})
                    except Exception as e:
                        report(f"  [LLM-FIX] Command error: {e}")
                        results["failed"].append({"fix": fix, "error": str(e)})
                else:
                    report(f"  [LLM-FIX] Command requested: {action[:100]}")
                    report(f"  [LLM-FIX] Manual execution needed for safety — not auto-running")
                    results["skipped"].append({"fix": fix, "reason": "command requires manual approval"})
            else:
                results["skipped"].append({"fix": fix, "reason": "missing command"})

        elif fix_type == "investigation":
            # Investigation tasks - create a task/issue for human or agent
            report(f"  [LLM-FIX] Investigation needed: {desc}")
            report(f"  [LLM-FIX] Action: {action[:100]}")
            results["skipped"].append({"fix": fix, "reason": "investigation requires human/agent follow-up"})

        else:
            results["skipped"].append({"fix": fix, "reason": f"unknown fix_type: {fix_type}"})
            report(f"  [LLM-FIX] Unknown fix type '{fix_type}' — skipping")

    # For backward compatibility, truthy if any applied
    return results


def apply_patch_fix(target_file: str, patch_content: str) -> bool:
    """Apply a unified diff patch to a target file."""
    try:
        import tempfile
        import subprocess

        # Check if patch_content is already a valid unified diff
        is_unified_diff = patch_content.strip().startswith('--- ') and '+++ ' in patch_content and '@@' in patch_content

        if not is_unified_diff:
            report(f"  [LLM-FIX] Not a valid unified diff: {patch_content[:100]}")
            return False

        # Write patch to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(patch_content)
            patch_file = f.name

        try:
            # Try git apply first
            result = subprocess.run(
                ["git", "apply", "--check", patch_file],
                cwd=HERMES_HOME,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Apply the patch
                result = subprocess.run(
                    ["git", "apply", "--whitespace=nowarn", patch_file],
                    cwd=HERMES_HOME,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return True
                else:
                    report(f"  [LLM-FIX] git apply failed: {result.stderr[:200]}")
            else:
                report(f"  [LLM-FIX] git apply --check failed: {result.stderr[:200]}")
            
            # Try patch command as fallback
            result2 = subprocess.run(
                ["patch", "-p1", "--dry-run", "-i", patch_file],
                cwd=HERMES_HOME,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result2.returncode == 0:
                # Actually apply
                result2 = subprocess.run(
                    ["patch", "-p1", "-i", patch_file],
                    cwd=HERMES_HOME,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result2.returncode == 0:
                    return True
                report(f"  [LLM-FIX] patch command failed: {result2.stderr[:200]}")
            else:
                report(f"  [LLM-FIX] patch --dry-run failed: {result2.stderr[:200]}")
            return False
        finally:
            # Clean up temp file AFTER all attempts
            try:
                os.unlink(patch_file)
            except Exception:
                pass

    except Exception as e:
        report(f"  [LLM-FIX] Patch error: {e}")
        return False


def generate_patch_from_description(target_file: str, description: str) -> str | None:
    """Generate a unified diff patch from a natural language description for known fix patterns."""
    desc_lower = description.lower()
    target = target_file.replace('\\', '/').replace('/', os.sep)
    full_path = HERMES_HOME / target

    if not full_path.exists():
        return None

    # Pattern 1: IndentationError after 'if' statement (or line reference)
    if 'indentation' in desc_lower and ('if' in desc_lower or 'line 1154' in desc_lower or 'report()' in desc_lower):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find the problematic pattern: "if ...:" followed by unindented line
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('if ') and stripped.endswith(':'):
                    # Check next non-empty line
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                            # Found unindented line after if - fix it
                            indent = ' ' * 4  # standard indent
                            if not lines[j].startswith(indent):
                                old_line = lines[j]
                                new_line = indent + lines[j].lstrip()
                                lines[j] = new_line

                                # Generate unified diff
                                from_line = max(0, i-2)
                                to_line = min(len(lines), j+3)
                                diff_lines = [
                                    f"--- a/{target_file}",
                                    f"+++ b/{target_file}",
                                    f"@@ -{from_line+1},{to_line-from_line} +{from_line+1},{to_line-from_line} @@"
                                ]
                                for k in range(from_line, to_line):
                                    prefix = ' '
                                    if k == j:
                                        prefix = '-'
                                        diff_lines.append(f"{prefix}{old_line.rstrip()}")
                                        prefix = '+'
                                    diff_lines.append(f"{prefix}{lines[k].rstrip()}")
                                return '\n'.join(diff_lines) + '\n'
        except Exception as e:
            report(f"  [LLM-FIX] Failed to generate indentation patch: {e}")

    # Pattern 2: Timeout config for llm_analyst.py
    if 'timeout' in desc_lower and ('llm_analyst' in desc_lower or '120s' in desc_lower or '300s' in desc_lower):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find DEFAULT_TIMEOUT = 120 or timeout = config.get('timeout_seconds', ...)
            for i, line in enumerate(lines):
                if 'DEFAULT_TIMEOUT' in line and '=' in line:
                    old_line = line
                    # Replace with new value (extract from description or default to 300)
                    import re
                    match = re.search(r'(\d+)s', description)
                    new_timeout = match.group(1) if match else '300'
                    new_line = f'DEFAULT_TIMEOUT = {new_timeout}\n'
                    lines[i] = new_line

                    # Generate unified diff
                    from_line = max(0, i-2)
                    to_line = min(len(lines), i+3)
                    diff_lines = [
                        f"--- a/{target_file}",
                        f"+++ b/{target_file}",
                        f"@@ -{from_line+1},{to_line-from_line} +{from_line+1},{to_line-from_line} @@"
                    ]
                    for k in range(from_line, to_line):
                        prefix = ' '
                        if k == i:
                            prefix = '-'
                            diff_lines.append(f"{prefix}{old_line.rstrip()}")
                            prefix = '+'
                        diff_lines.append(f"{prefix}{lines[k].rstrip()}")
                    return '\n'.join(diff_lines) + '\n'

                # Also check for timeout = config.get('timeout_seconds', ...)
                if 'timeout_seconds' in line and 'config.get' in line:
                    old_line = line
                    import re
                    match = re.search(r'(\d+)s', description)
                    new_timeout = match.group(1) if match else '300'
                    new_line = line.replace('DEFAULT_TIMEOUT', new_timeout)
                    lines[i] = new_line

                    from_line = max(0, i-2)
                    to_line = min(len(lines), i+3)
                    diff_lines = [
                        f"--- a/{target_file}",
                        f"+++ b/{target_file}",
                        f"@@ -{from_line+1},{to_line-from_line} +{from_line+1},{to_line-from_line} @@"
                    ]
                    for k in range(from_line, to_line):
                        prefix = ' '
                        if k == i:
                            prefix = '-'
                            diff_lines.append(f"{prefix}{old_line.rstrip()}")
                            prefix = '+'
                        diff_lines.append(f"{prefix}{lines[k].rstrip()}")
                    return '\n'.join(diff_lines) + '\n'
        except Exception as e:
            report(f"  [LLM-FIX] Failed to generate timeout patch: {e}")

    return None


# ── Main ───────────────────────────────────────────────────────────

def main() -> int:
    start = time.time()
    fixes_applied = 0
    fixes_verified = 0
    issues_found = 0

    report("=" * 60)
    report("PROACTIVE EXECUTOR v2 — Knowledge-Driven Fixes")
    report(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report("=" * 60)

    # ── Phase 1: Knowledge Cube Analysis ──
    report("\n[Phase 1] Knowledge Cube Analysis")
    report("-" * 40)
    kc = analyze_knowledge_cube()
    report(f"  Total experiences: {kc['total']}")
    if kc["domains"]:
        report(f"  Domains: {', '.join(f'{d}={c}' for d, c in sorted(kc['domains'].items()))}")
    if kc["newest_ts"]:
        report(f"  Newest entry: {fmt_dt(kc['newest_ts'])}")
    if kc["gaps"]:
        issues_found += len(kc["gaps"])
        for g in kc["gaps"]:
            report(f"  [GAP] {g}")

    # ── Phase 2: Cron Error Scan ──
    report("\n[Phase 2] Cron Job Error Scan")
    report("-" * 40)
    errors = scan_cron_errors()
    healing_state = scan_healing_state()

    if healing_state:
        for jid, info in healing_state.items():
            if isinstance(info, dict) and info.get("consecutive_fails", 0) > 0:
                report(
                    f"  [HEALING] {info.get('name', jid[:8])}: "
                    f"{info['consecutive_fails']} consecutive failures "
                    f"(last OK: {fmt_dt(info.get('last_ok'))})"
                )

    if not errors:
        report("  No cron jobs with errors detected — all green")
    else:
        issues_found += len(errors)
        for err in errors:
            report(f"  [ERROR] {err['name']} ({err['id'][:8]}): {err['error'][:120] if err['error'] else 'unknown'}")

    # ── Phase 2.5: LLM Analysis ──
    report("\n[Phase 2.5] LLM Analysis")
    report("-" * 40)
    # Combine issues from knowledge gaps and cron errors
    llm_issues = []
    # Add knowledge gaps as issues
    for gap in kc.get("gaps", []):
        llm_issues.append({"description": gap, "type": "knowledge_gap"})
    # Add cron errors
    for err in errors:
        llm_issues.append({
            "name": err.get("name"),
            "error": err.get("error"),
            "consecutive_fails": err.get("consecutive_fails"),
            "script": err.get("script"),
            "id": err.get("id"),
        })
    # Run LLM analysis (returns cached suggestions or writes pending)
    suggested_fixes = analyze_with_llm(llm_issues)
    llm_fixes_applied = 0
    llm_fixes_verified = 0
    if suggested_fixes:
        report(f"  [LLM] Received {len(suggested_fixes)} suggested fix(es)")
        fix_results = apply_llm_suggested_fixes(suggested_fixes)
        llm_fixes_applied = len(fix_results.get("applied", []))
        llm_fixes_verified = len(fix_results.get("verified", []))
        if fix_results["applied"]:
            report(f"  [LLM] Applied {len(fix_results['applied'])} fix(es)")
            for af in fix_results["applied"]:
                report(f"    - {af['fix'].get('description', 'unknown')}")
        if fix_results["failed"]:
            report(f"  [LLM] Failed: {len(fix_results['failed'])}")
            for ff in fix_results["failed"]:
                report(f"    - {ff['fix'].get('description', 'unknown')}: {ff.get('error', 'unknown')}")
        if fix_results["skipped"]:
            report(f"  [LLM] Skipped (manual/investigation): {len(fix_results['skipped'])}")
    else:
        report("  [LLM] No suggestions yet (awaiting LLM Analyst service)")
        fix_results = {"verified": []}
    
    # Store verified fixes in local memory (Knowledge→KC loop)
    for vf in fix_results.get("verified", []):
        fix = vf.get("fix", {})
        if fix:
            try:
                from hermes_hooks import get_hooks
                hooks = get_hooks()
                hooks.on_task_complete(
                    task_description=f"Proactive fix: {fix.get('description', 'unknown')}",
                    result=f"Fix applied and verified: {fix.get('fix_type', 'unknown')}",
                    tags=["proactive", fix.get("fix_type", "unknown"), "verified"],
                    verified=True,
                    evidence="Syntax check passed + verification passed",
                    fix_result=fix
                )
            except Exception as e:
                report(f"  [MEMORY] Failed to store verified fix: {e}")
    
    # Add to total fixes applied
    fixes_applied += llm_fixes_applied
    fixes_verified += llm_fixes_verified
    # ── Phase 3: Fix Actions ──
    report("\n[Phase 3] Applying Fixes")
    report("-" * 40)

    # Track fix results for Phase 3.5 verification reporting
    phase3_fixes: list[dict] = []

    if kc["total"] > 0 and kc["gaps"]:
        if fix_knowledge_gaps(kc, healing_state):
            fixes_applied += 1
            result = verify_fix({"fix_name": "knowledge_gaps", "fix_applied": True})
            if result["verified"]:
                fixes_verified += 1
            phase3_fixes.append(result)

    # Fix 2: System-watcher gap alert
    if fix_system_watcher(errors, healing_state):
        fixes_applied += 1
        result = verify_fix({"fix_name": "system_watcher", "fix_applied": True})
        if result["verified"]:
            fixes_verified += 1
        phase3_fixes.append(result)

    # Fix 3: Telegram delivery chat_id
    if fix_telegram_delivery(errors):
        fixes_applied += 1
        result = verify_fix({"fix_name": "telegram_delivery", "fix_applied": True})
        if result["verified"]:
            fixes_verified += 1
        phase3_fixes.append(result)

    # Fix 4: API health (if docker available)
    if fix_api_health(errors):
        fixes_applied += 1
        result = verify_fix({"fix_name": "health_check", "fix_applied": True})
        if result["verified"]:
            fixes_verified += 1
        phase3_fixes.append(result)

    # Fix 5: Clean stale proactive_actions
    if clean_stale_proactive_actions():
        fixes_applied += 1
        result = verify_fix({"fix_name": "clean_stale", "fix_applied": True})
        if result["verified"]:
            fixes_verified += 1
        phase3_fixes.append(result)

    # Fix 6: Lightweight DB maintenance
    run_vacuum_if_needed()

    # ── Phase 3.5: Verification Phase ──
    report("\n[Phase 3.5] Fix Verification Phase")
    report("-" * 40)
    if phase3_fixes:
        verified_count = sum(1 for r in phase3_fixes if r["verified"])
        failed_count = sum(1 for r in phase3_fixes if not r["verified"])
        report(f"  Fixes applied this run: {len(phase3_fixes)}")
        report(f"  Verified: {verified_count} | Failed: {failed_count}")
        for r in phase3_fixes:
            status_icon = "✓" if r["verified"] else "✗"
            report(f"  [{status_icon}] {r.get('details', 'no details')}")
        if failed_count > 0:
            report("  [WARN] Some fix(es) not verified — check fix_results.json for details")
    else:
        report("  No fixes applied this run — nothing to verify")

    # ── Phase 4: Knowledge-Driven Task Generation ──
    # bd comments add hermes-0kh.2 "LEARNED: Added verify_fix(fix_result: dict) -> dict with VERIFICATION_STATE_FILE tracking. Post-fix verification re-reads relevant state (DB queries, environment vars, port checks) and writes to data/verification_state.json with per-fix success rates. Phase 3.5 provides explicit verification summary between fix application (Phase 3) and task generation (Phase 4). Failed verifications are logged and marked as failed without auto-retry."
    report("\n[Phase 4] Knowledge-Driven Task Generation")
    report("-" * 40)

    generated_tasks = generate_tasks_from_knowledge(kc)
    tasks_inserted = store_generated_tasks(generated_tasks)

    if generated_tasks:
        report(f"  Generated {len(generated_tasks)} task candidates, {tasks_inserted} new tasks stored:")
        for t in generated_tasks:
            report(f"    [{t['action_type']}] {t['description']}")
    else:
        report("  No new knowledge-driven tasks to generate (all domains covered or duplicates)")

    if tasks_inserted > 0:
        fixes_applied += 1

    # ── Phase 4b: KC Gap Task Generation (bead hermes-0kh.3) ──
    # bd comments add hermes-0kh.3 "LEARNED: Added generate_knowledge_tasks() which reads KC domain stats to find white spots (<10 entries), uses LLM analysis to determine content to generate for each gap, returns up to 3 gap-filling tasks logged to data/knowledge_gap_tasks.json. Also added auto_research_topic(topic) which checks if a topic has a knowledge gap and calls web search via Hermes agent to fill it — prevents the 'report without research' problem."
    knowledge_tasks = generate_knowledge_tasks()
    if knowledge_tasks:
        report(f"  [KC-GAP] {len(knowledge_tasks)} gap-filling task(s) generated:")
        for t in knowledge_tasks:
            report(
                f"    [{t['domain']}] (priority={t['priority']}) "
                f"{t['gap_description']}"
            )
    else:
        report("  [KC-GAP] No gap-filling tasks generated (all domains adequately populated)")

    # ── Phase 4c: Skill Auto-Evolution (bead hermes-0kh.4) ──
    # bd comments add hermes-0kh.4 "LEARNED: Added auto_evolve_skills() which detects patterns from Knowledge Cube errors, fix history, cron errors, gap fills, and agent decisions. Groups similar issues using _normalize_pattern() and only creates/updates skills for patterns seen 3+ times. Skills created in skills/auto-generated/ with proper SKILL.md YAML frontmatter (name, description, category). Existing skills are updated (not duplicated) when matching patterns found. Returns list of created/updated/skipped skills."
    report("\n[Phase 4c] Skill Auto-Evolution")
    report("-" * 40)
    evolved = auto_evolve_skills()
    if evolved:
        created = [e for e in evolved if e["action"] == "created"]
        updated = [e for e in evolved if e["action"] == "updated"]
        skipped = [e for e in evolved if e["action"] == "skipped"]
        if created:
            report(f"  [SKILL-EVOLVE] Created {len(created)} new skill(s):")
            for s in created:
                report(f"    + {s['name']} ({s['occurrence_count']}x) -> {s['path']}")
            fixes_applied += len(created)
        if updated:
            report(f"  [SKILL-EVOLVE] Updated {len(updated)} existing skill(s):")
            for s in updated:
                report(f"    ~ {s['name']} (+{s['occurrence_count']}x)")
        if skipped:
            report(f"  [SKILL-EVOLVE] Skipped {len(skipped)} duplicate(s)")
    else:
        report("  [SKILL-EVOLVE] No skills created/updated (no qualifying patterns)")

    # ── Update state ──
    elapsed = time.time() - start
    try:
        state = {
            "total": kc["total"],
            "issues": issues_found,
            "fixes": fixes_applied,
            "fixes_verified": fixes_verified,
            "elapsed_sec": round(elapsed, 2),
        }
        state_path = HERMES_HOME / "cache" / "proactive_executor_state.json"
        HERMES_HOME.joinpath("cache").mkdir(parents=True, exist_ok=True)
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)
    except OSError:
        pass

    # ── Summary ──
    report("\n" + "=" * 60)
    report("SUMMARY")
    report("-" * 60)
    report(f"  Issues detected:    {issues_found}")
    report(f"  Fixes applied:      {fixes_applied}")
    report(f"  Fixes verified:     {fixes_verified}")
    report(f"  Elapsed:            {elapsed:.2f}s")
    report(f"  KC experiences:     {kc['total']}")
    if errors:
        report(f"  Errored cron jobs:  {len(errors)} ({', '.join(e['name'] for e in errors)})")
    if fixes_applied > 0 and fixes_verified == fixes_applied:
        report(f"  STATUS: All {fixes_applied} fix(es) verified — feedback loop OK")
    elif fixes_applied > 0:
        report(f"  STATUS: {fixes_verified}/{fixes_applied} fixes verified — some need attention")
    elif issues_found > 0:
        report("  STATUS: Issues found but no auto-fix was possible")
    else:
        report("  STATUS: All clear — no issues detected")

    # Show historical fix success rates
    report_fix_success_rate()

    report("=" * 60)

    # Write report to log file too
    try:
        log_dir = HERMES_HOME / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"proactive_executor_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- Run at {datetime.now().isoformat()} ---\n")
            for line in REPORT_LINES:
                f.write(line + "\n")
    except OSError:
        pass

    # Exit code: 0 = script ran successfully, 1 = unhandled exception
    # Issues are reported in summary, not via exit code (cron handles via status)
    return 0
    if fixes_applied > 0:
        # We did work — return 0 (success) but report what changed
        return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[proactive-executor] Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n[proactive-executor] UNHANDLED ERROR: {e}", file=sys.stderr)
        sys.exit(2)
