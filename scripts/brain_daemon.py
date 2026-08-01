#!/usr/bin/env python3
"""
Brain Daemon — Event-driven knowledge cube analyzer.


> Revisit: when brain daemon logic, autonomous cycle, or event processing changes. Last touched: 2026-07-02.
Triggered by 'knowledge_cube_updated' events (NOT cron).
Connects to knowledge_cube.db, queries failures/successes by domain
since last analysis, writes insights to cache/brain_insights.md,
and appends key findings to MEMORY.md.

Usage:
    python brain_daemon.py                    # manual run
    python brain_daemon.py --last-analysis    # show last analysis timestamp
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(PROJECT_ROOT)))

DB_PATH = HERMES_HOME / "cache" / "knowledge_cube.db"
INSIGHTS_PATH = HERMES_HOME / "cache" / "brain_insights.md"
MEMORY_PATH = HERMES_HOME / "MEMORY.md"
STATE_PATH = HERMES_HOME / "cache" / "brain_daemon_state.json"


# ── State Management ─────────────────────────────────────────────────────────

def _load_state() -> dict:
    """Load last analysis state."""
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_analysis_ts": None, "total_analyses": 0}


def _save_state(state: dict):
    """Save analysis state."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── Database Queries ─────────────────────────────────────────────────────────

def _get_connection() -> sqlite3.Connection | None:
    """Connect to knowledge_cube.db with WAL mode."""
    if not DB_PATH.exists():
        print("  [brain_daemon] knowledge_cube.db not found")
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    except Exception as e:
        print(f"  [brain_daemon] DB connection error: {e}")
        return None


def _query_domain_stats(conn: sqlite3.Connection, since_ts: str | None) -> dict:
    """Query failures/successes by domain since a timestamp.

    Returns:
        {
            "domain_stats": {domain: {success: N, failure: N, partial: N, unknown: N}},
            "total_success": N,
            "total_failure": N,
            "total_partial": N,
            "period_start": "..." or None,
            "period_end": "...",
            "new_entries": N,
        }
    """
    where = "1=1"
    params: list = []
    if since_ts:
        where = "ts > ?"
        params.append(since_ts)

    # Per-domain outcome counts
    rows = conn.execute(f"""
        SELECT axis_domain, axis_outcome, COUNT(*) as cnt
        FROM experiences
        WHERE {where}
        GROUP BY axis_domain, axis_outcome
        ORDER BY axis_domain, axis_outcome
    """, params).fetchall()

    domain_stats: dict[str, dict[str, int]] = {}
    totals: dict[str, int] = {"success": 0, "failure": 0, "partial": 0, "unknown": 0}

    for row in rows:
        domain = row["axis_domain"]
        outcome = row["axis_outcome"]
        cnt = row["cnt"]
        if domain not in domain_stats:
            domain_stats[domain] = {}
        domain_stats[domain][outcome] = cnt
        if outcome in totals:
            totals[outcome] += cnt

    # Total new entries
    total_row = conn.execute(
        f"SELECT COUNT(*) as n FROM experiences WHERE {where}", params
    ).fetchone()
    new_entries = total_row["n"] if total_row else 0

    # Period boundaries
    period_row = conn.execute(
        f"SELECT MIN(ts) as first_ts, MAX(ts) as last_ts FROM experiences WHERE {where}",
        params,
    ).fetchone()
    period_start = period_row["first_ts"] if period_row and period_row["first_ts"] else since_ts
    period_end = period_row["last_ts"] if period_row and period_row["last_ts"] else datetime.now(timezone.utc).isoformat()

    return {
        "domain_stats": domain_stats,
        "total_success": totals["success"],
        "total_failure": totals["failure"],
        "total_partial": totals["partial"],
        "total_unknown": totals["unknown"],
        "period_start": period_start,
        "period_end": period_end,
        "new_entries": new_entries,
    }


def _query_top_failures(conn: sqlite3.Connection, since_ts: str | None, limit: int = 10) -> list[dict]:
    """Query the most recent failures with details."""
    where = "axis_outcome = 'failure'"
    params: list = []
    if since_ts:
        where += " AND ts > ?"
        params.append(since_ts)

    rows = conn.execute(f"""
        SELECT ts, axis_domain, raw_text, source, tags
        FROM experiences
        WHERE {where}
        ORDER BY ts DESC
        LIMIT ?
    """, params + [limit]).fetchall()

    return [dict(r) for r in rows]


def _query_recurring_domains(conn: sqlite3.Connection) -> list[dict]:
    """Find domains with repeated failures across ALL data."""
    rows = conn.execute("""
        SELECT axis_domain,
               SUM(CASE WHEN axis_outcome = 'failure' THEN 1 ELSE 0 END) as failures,
               SUM(CASE WHEN axis_outcome = 'success' THEN 1 ELSE 0 END) as successes,
               COUNT(*) as total
        FROM experiences
        GROUP BY axis_domain
        HAVING failures >= 2
        ORDER BY failures DESC
    """).fetchall()

    return [dict(r) for r in rows]


# ── Insight Generation ───────────────────────────────────────────────────────

def _generate_insights(stats: dict, top_failures: list[dict], recurring: list[dict], event_data: dict) -> str:
    """Generate markdown insights from analysis data."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Brain Insights",
        f"",
        f"**Generated:** {now}",
        f"**Trigger:** knowledge_cube_updated (count={event_data.get('count', '?')}, domains={event_data.get('domains', [])})",
        f"",
    ]

    # Summary
    total = stats["total_success"] + stats["total_failure"] + stats["total_partial"] + stats["total_unknown"]
    lines.append("## Summary")
    lines.append(f"- **New entries analyzed:** {stats['new_entries']}")
    lines.append(f"- **Period:** {stats['period_start'][:19] if stats['period_start'] else 'all-time'} → {stats['period_end'][:19]}")
    lines.append(f"- **Success:** {stats['total_success']} | **Failure:** {stats['total_failure']} | **Partial:** {stats['total_partial']} | **Unknown:** {stats['total_unknown']}")
    if total > 0:
        success_rate = stats['total_success'] / (stats['total_success'] + stats['total_failure']) * 100 if (stats['total_success'] + stats['total_failure']) > 0 else 0
        lines.append(f"- **Success rate:** {success_rate:.1f}%")
    lines.append("")

    # Per-domain breakdown
    lines.append("## Domain Breakdown")
    lines.append("| Domain | Success | Failure | Partial | Unknown |")
    lines.append("|--------|---------|---------|---------|---------|")
    for domain in sorted(stats["domain_stats"].keys()):
        d = stats["domain_stats"][domain]
        lines.append(
            f"| {domain} | {d.get('success', 0)} | {d.get('failure', 0)} | {d.get('partial', 0)} | {d.get('unknown', 0)} |"
        )
    lines.append("")

    # Recurring failure domains
    if recurring:
        lines.append("## Recurring Failure Domains")
        for r in recurring[:5]:
            ratio = r["failures"] / r["total"] * 100 if r["total"] > 0 else 0
            lines.append(f"- **{r['axis_domain']}**: {r['failures']}/{r['total']} failures ({ratio:.0f}%)")
        lines.append("")

    # Recent failures
    if top_failures:
        lines.append("## Recent Failures")
        for f in top_failures[:5]:
            domain = f.get("axis_domain", "?")
            text = f.get("raw_text", "")[:120].replace("\n", " ")
            lines.append(f"- [{f.get('ts', '')[:16]}] **{domain}**: {text}")
        lines.append("")

    # Key findings
    lines.append("## Key Findings")
    findings = []
    if stats["total_failure"] > stats["total_success"] and (stats["total_failure"] + stats["total_success"]) > 0:
        findings.append(f"⚠ More failures than successes in this period ({stats['total_failure']} vs {stats['total_success']})")
    if recurring:
        worst = recurring[0]
        findings.append(f"🔴 Worst domain: {worst['axis_domain']} — {worst['failures']} failures across {worst['total']} entries")
    if stats["new_entries"] > 20:
        findings.append(f"📈 High activity: {stats['new_entries']} new entries added since last analysis")
    if not findings:
        findings.append("✅ No critical issues detected in this period")

    for finding in findings:
        lines.append(f"- {finding}")
    lines.append("")
    lines.append("---")
    lines.append(f"*Auto-generated by brain_daemon.py*")

    return "\n".join(lines)


def _generate_memory_appendix(stats: dict, top_failures: list[dict], recurring: list[dict]) -> str:
    """Generate a short markdown block to append to MEMORY.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"",
        f"## Knowledge Cube Insights ({now})",
        f"- Analyzed {stats['new_entries']} entries: {stats['total_success']} success, {stats['total_failure']} failure",
    ]

    if recurring:
        worst = recurring[0]
        lines.append(f"- 🔴 Recurring failures in: {', '.join(r['axis_domain'] for r in recurring[:3])}")

    if top_failures:
        latest = top_failures[0]
        text = latest.get("raw_text", "")[:80].replace("\n", " ")
        lines.append(f"- Latest failure [{latest.get('domain', '?')}]: {text}")

    if stats["total_failure"] > stats["total_success"] and (stats["total_failure"] + stats["total_success"]) > 0:
        lines.append(f"- ⚠ Failure rate elevated: {stats['total_failure']}/{stats['total_failure'] + stats['total_success']} entries")
    else:
        lines.append(f"- ✅ Health OK: success rate {stats['total_success']}/{stats['total_success'] + stats['total_failure']}")

    lines.append("")
    return "\n".join(lines)


# ── Public API ───────────────────────────────────────────────────────────────

def handle_knowledge_cube_updated(event_data: dict):
    """Event handler for 'knowledge_cube_updated'.

    Args:
        event_data: dict with 'type', 'payload' keys (event bus format).
            payload should have 'count' (int) and 'domains' (list[str]).
    """
    payload = event_data.get("payload", {})
    count = payload.get("count", 0)
    domains = payload.get("domains", [])

    print(f"  [brain_daemon] knowledge_cube_updated: {count} new entries, domains={domains}")

    # Load state for last analysis timestamp
    state = _load_state()
    last_ts = state.get("last_analysis_ts")

    # Connect to DB
    conn = _get_connection()
    if conn is None:
        print("  [brain_daemon] Cannot proceed — DB unavailable")
        return

    try:
        # Query domain stats since last analysis
        stats = _query_domain_stats(conn, last_ts)

        # Query recent failures
        top_failures = _query_top_failures(conn, last_ts)

        # Query recurring failure domains (all-time)
        recurring = _query_recurring_domains(conn)

        # Generate insights markdown
        insights_md = _generate_insights(stats, top_failures, recurring, event_data)

        # Write insights to cache/brain_insights.md
        INSIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        INSIGHTS_PATH.write_text(insights_md, encoding="utf-8")
        print(f"  [brain_daemon] Wrote insights -> {INSIGHTS_PATH}")

        # Append key findings to MEMORY.md (don't overwrite)
        memory_appendix = _generate_memory_appendix(stats, top_failures, recurring)
        if MEMORY_PATH.exists():
            existing = MEMORY_PATH.read_text(encoding="utf-8")
            # Don't double-append: check if last section already matches today's date
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if f"Knowledge Cube Insights ({today}" not in existing:
                with open(str(MEMORY_PATH), "a", encoding="utf-8") as f:
                    f.write(memory_appendix)
                print(f"  [brain_daemon] Appended findings -> {MEMORY_PATH}")
            else:
                print(f"  [brain_daemon] Today's insights already in MEMORY.md — skipping append")
        else:
            MEMORY_PATH.write_text(f"# agent memory\n{memory_appendix}", encoding="utf-8")
            print(f"  [brain_daemon] Created MEMORY.md with findings")

        # Update state
        state["last_analysis_ts"] = stats["period_end"]
        state["total_analyses"] = state.get("total_analyses", 0) + 1
        state["last_event"] = {
            "count": count,
            "domains": domains,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        _save_state(state)
        print(f"  [brain_daemon] Analysis #{state['total_analyses']} complete")

    except Exception as e:
        print(f"  [brain_daemon] ERROR: {e}")
    finally:
        conn.close()


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    """Manual trigger for brain_daemon analysis."""
    import sys
    if "--last-analysis" in sys.argv:
        state = _load_state()
        print(f"Last analysis: {state.get('last_analysis_ts', 'never')}")
        print(f"Total analyses: {state.get('total_analyses', 0)}")
        return

    # Simulate an event for manual run
    event = {
        "type": "knowledge_cube_updated",
        "payload": {"count": 0, "domains": ["manual"]},
    }
    handle_knowledge_cube_updated(event)


if __name__ == "__main__":
    main()
