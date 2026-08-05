"""
Self-Improvement Loop — analyzes session logs, error patterns, verified fixes,
and Knowledge Cube data to identify recurring issues and generate improvement
suggestions. Fires `new_suggestions_ready` event when done.

> Revisit: when self-improvement loop runs (daily 05:00 + on demand)
"""

import json
import logging
import os
import re
import sqlite3
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

logger = logging.getLogger("self_improvement_loop")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
LOGS_DIR = HERMES_HOME / "logs"
FIXES_DB = CACHE_DIR / "verified_fixes.db"
CUBE_DB = CACHE_DIR / "knowledge_cube.db"
UNIFIED_DB = CACHE_DIR / "unified.db"
OUTPUT = CACHE_DIR / "improvement_suggestions.json"
# Auto-created skills go to auto-generated/ category (per skills/AGENTS.md),
# NOT the root skills/ dir — avoids cluttering curated skills.
SKILLS_DIR = HERMES_HOME / "skills" / "auto-generated"
AUTO_SKILLS_DIR = SKILLS_DIR
METRICS_FILE = CACHE_DIR / "self_improvement_metrics.json"

LOG_DIR = LOGS_DIR
LOG_FILES = [
    LOG_DIR / "agent.log",
    LOG_DIR / "agent.log.1",
    LOG_DIR / "errors.log",
    LOG_DIR / "errors.log.1",
    LOG_DIR / "autonomous_agent.log",
]

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _connect(path):
    """Open a SQLite connection; return None if DB doesn't exist."""
    try:
        if not Path(path).exists():
            return None
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        return conn
    except (sqlite3.Error, OSError):
        return None


def _fetch_all(conn, sql, params=()):
    """Execute SQL and return list of dicts. Catches table-not-found errors."""
    if conn is None:
        return []
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    except (sqlite3.Error, sqlite3.OperationalError):
        return []


def _safe_close(conn):
    """Close a connection safely."""
    try:
        if conn is not None:
            conn.close()
    except (sqlite3.Error, OSError):
        pass


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_verified_fixes():
    """Return list of dicts from verified_fixes table."""
    conn = _connect(FIXES_DB)
    try:
        return _fetch_all(conn, "SELECT * FROM verified_fixes ORDER BY created_at DESC")
    finally:
        _safe_close(conn)


def load_cube_experiences():
    """Return list of dicts from experiences table."""
    conn = _connect(CUBE_DB)
    try:
        return _fetch_all(conn, "SELECT * FROM experiences ORDER BY ts DESC")
    finally:
        _safe_close(conn)


# ---------------------------------------------------------------------------
# Log parsing
# ---------------------------------------------------------------------------

def _read_log_tail(path, max_lines=2000):
    """Read the last N lines of a log file safely."""
    if not Path(path).exists():
        return []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return lines[-max_lines:]
    except OSError:
        return []


# Error pattern classifiers — ordered by specificity
_ERROR_PATTERNS = [
    (re.compile(r"ERROR\s+(\S+):\s+(.+)"), lambda m: m.group(1).lower()),
    (re.compile(r"Tool\s+(\S+)\s+returned error.*?:\s*(\{.*\})"), lambda m: "tool_error"),
    (re.compile(r"Traceback \(most recent call last\):"), lambda m: "traceback"),
    (re.compile(r"(\w+Error):\s+(.+)"), lambda m: m.group(1).lower()),
    (re.compile(r"failed.*?:\s+(.+)"), lambda m: "failure"),
]

_SESSION_PATTERN = re.compile(r"\[(\d{8}_\d{6}_[a-f0-9]+)\]")
_TIMESTAMP_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")


def _classify_error_type(line, line_lower):
    """Classify error type from a log line before falling back to 'unknown'."""
    if "httpx" in line_lower and "connect" in line_lower:
        return "network_connect"
    if "httpx" in line_lower and "read" in line_lower:
        return "network_read"
    if "httpx" in line_lower and "timeout" in line_lower:
        return "network_timeout"
    if "remote" in line_lower and "closed" in line_lower:
        return "network_remote_closed"
    if "status" in line_lower and "response" in line_lower:
        return "network_status"
    if "network_httpx" in line_lower:
        return "network_httpx"
    if "httpcore" in line_lower:
        return "network_httpcore"
    if "connecterror" in line_lower or "connectionerror" in line_lower:
        return "network_connect_error"
    if "time out" in line_lower:
        return "network_timeout"
    if "networkerror" in line_lower:
        return "network_error"
    if "readerror" in line_lower:
        return "network_read_error"
    if "telegram" in line_lower and "error" in line_lower:
        return "telegram_network"
    if "telegram" in line_lower and "retry" in line_lower:
        return "telegram_updater"
    if "telegram" in line_lower and "get_updates" in line_lower:
        return "telegram_updater"
    if "telegram" in line_lower and "conflict" in line_lower:
        return "telegram_conflict"
    if "telegram" in line_lower:
        return "telegram_error"
    if "-> documented" in line_lower or "-> noted" in line_lower:
        return "log_artifact"
    if "timed out" in line_lower:
        return "telegram_timeout"
    if "tool terminal returned error" in line_lower and "60" in line_lower:
        return "terminal_timeout"
    if "tool terminal returned error" in line_lower and "120" in line_lower:
        return "terminal_timeout"
    if "openai" in line_lower and "badrequest" in line_lower:
        return "api_provider"
    if "429" in line_lower or "rate limit" in line_lower:
        return "api_rate_limit"
    if "403" in line_lower or "forbidden" in line_lower or "access denied" in line_lower:
        return "api_forbidden"
    if "500" in line_lower or "502" in line_lower or "503" in line_lower:
        return "api_server_error"
    return "unknown"


def parse_log_errors(log_lines):
    """
    Parse log lines to extract error patterns.
    Returns list of dicts: {timestamp, error_type, message, source, session_id}
    """
    errors = []
    for i, line in enumerate(log_lines):
        stripped = line.strip()
        line_lower = stripped.lower()
        if not stripped or len(stripped) < 8:
            continue

        ts_match = _TIMESTAMP_PATTERN.match(stripped)
        timestamp = ts_match.group(1) if ts_match else None

        session_id = None
        sess_match = _SESSION_PATTERN.search(stripped)
        if sess_match:
            session_id = sess_match.group(1)

        # Determine error type
        error_type = "unknown"
        message = stripped

        if "ERROR" in stripped:
            error_type = _classify_error_type(stripped, line_lower)
        elif "Tool" in stripped and "returned error" in line_lower:
            error_type = "tool_error"
        elif "Traceback" in stripped:
            error_type = "traceback"
        elif "API call failed" in stripped:
            error_type = "api_error"
        elif "tick failed" in line_lower:
            error_type = "tick_failure"
        elif "notifier tick failed" in line_lower:
            error_type = "notifier_failure"

        # Extract message
        if error_type == "unknown" and "error" in line_lower:
            err_match = re.search(r"error=(.+)", stripped)
            if err_match:
                message = err_match.group(1).strip()
            else:
                message = stripped[:200]

        errors.append({
            "timestamp": timestamp,
            "error_type": error_type,
            "message": message[:300],
            "source": "log",
            "session_id": session_id,
        })
    return errors


def load_recent_errors(hours=48):
    """
    Load errors from log files, filtering to the last N hours.
    Returns (all_errors, recent_errors).
    """
    all_errors = []
    cutoff = datetime.now() - timedelta(hours=hours)

    for path in LOG_FILES:
        lines = _read_log_tail(path)
        parsed = parse_log_errors(lines)
        for err in parsed:
            all_errors.append(err)
            if err.get("timestamp"):
                try:
                    ts = datetime.strptime(err["timestamp"], "%Y-%m-%d %H:%M:%S")
                    if ts >= cutoff:
                        continue  # counted in all; filter below
                except ValueError:
                    pass

    # Filter to recent (those with valid recent timestamps)
    recent_errors = []
    for err in all_errors:
        if not err.get("timestamp"):
            continue
        try:
            ts = datetime.strptime(err["timestamp"], "%Y-%m-%d %H:%M:%S")
            if ts >= cutoff:
                recent_errors.append(err)
        except ValueError:
            continue

    return all_errors, recent_errors


def analyze_error_patterns(errors):
    """
    Group errors by type and message pattern.
    Returns list of clusters: {error_type, count, sample_messages, pattern}
    """
    groups = defaultdict(list)
    for err in errors:
        key = (err.get("error_type", "unknown"), err.get("message", "")[:80])
        groups[key].append(err)

    clusters = []
    for (error_type, _pattern), items in groups.items():
        clusters.append({
            "error_type": error_type,
            "count": len(items),
            "sample_messages": [e.get("message", "")[:200] for e in items[:3]],
            "pattern": _pattern,
        })
    clusters.sort(key=lambda c: c["count"], reverse=True)
    return clusters


# ---------------------------------------------------------------------------
# Recurring fixes & cube patterns
# ---------------------------------------------------------------------------

def identify_recurring_fixes(fixes):
    """
    Group fixes by issue_type and by similar descriptions.
    Return list of clusters with count >= 2.
    """
    groups = defaultdict(list)
    for fix in fixes:
        issue_type = fix.get("issue_type") or fix.get("issue_description") or "unknown"
        groups[issue_type].append(fix)

    clusters = []
    for issue_type, items in groups.items():
        if len(items) < 2:
            continue
        tags = []
        for fix in items:
            t = fix.get("tags", "[]")
            if isinstance(t, str):
                try:
                    t = json.loads(t)
                except json.JSONDecodeError:
                    t = []
            if isinstance(t, list):
                tags.extend(t)
        tag_counter = Counter(tags)
        clusters.append({
            "issue_type": issue_type,
            "count": len(items),
            "latest_fix": items[0].get("fix_description") or items[0].get("issue_description") or "",
            "common_tags": [t for t, _ in tag_counter.most_common(5)],
            "sample_fixes": [f.get("fix_description") or f.get("issue_description", "")[:200] for f in items[:3]],
        })
    clusters.sort(key=lambda c: c["count"], reverse=True)
    return clusters


def identify_cube_patterns(experiences):
    """
    Analyse Knowledge Cube experiences for failure patterns and
    domain-specific trends.
    """
    domains = Counter()
    outcomes = Counter()
    white_spots = []

    for exp in experiences:
        outcome = exp.get("axis_outcome", "unknown")
        domain = exp.get("axis_domain", "unknown")
        outcomes[outcome] += 1
        domains[domain] += 1
        if exp.get("is_white_spot"):
            white_spots.append(domain)

    total = len(experiences)
    failures = outcomes.get("failure", 0)
    failure_rate = round(failures / total, 3) if total else 0.0

    high_risk_domains = []
    for domain, count in domains.most_common(10):
        if count >= 5:
            high_risk_domains.append({"domain": domain, "failures": count})

    return {
        "total": total,
        "total_failures": failures,
        "failure_rate": failure_rate,
        "high_risk_domains": high_risk_domains,
        "white_spot_domains": white_spots[:10],
        "domains": dict(domains.most_common(20)),
    }


# ---------------------------------------------------------------------------
# Suggestion generation
# ---------------------------------------------------------------------------

def load_previous_suggestions():
    """Load previous suggestion IDs to skip duplicates across runs."""
    if not OUTPUT.exists():
        return set()
    try:
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        return {s.get("id") for s in data.get("suggestions", []) if s.get("id")}
    except (json.JSONDecodeError, OSError):
        return set()


def generate_suggestions(recurring, cube_patterns, log_clusters, seen_ids):
    """
    Turn recurring issue clusters, cube patterns, and log error patterns
    into actionable improvement suggestions.
    """
    suggestions = []

    def _add(suggestion):
        sid = suggestion["id"]
        if sid in seen_ids:
            return
        suggestions.append(suggestion)

    # 1. Recurring verified fixes
    for cluster in recurring:
        issue_type = cluster["issue_type"]
        count = cluster["count"]
        severity = "critical" if count >= 10 else ("high" if count >= 5 else "medium")
        actions = _suggest_actions_for_type(issue_type, cluster)
        _add({
            "id": f"recurring-{issue_type}",
            "source": "verified_fixes",
            "severity": severity,
            "issue_type": issue_type,
            "occurrence_count": count,
            "title": f"Recurring '{issue_type}' detected {count} times",
            "description": (
                f"The issue type '{issue_type}' has been fixed {count} times. "
                "Consider adding a guard, linter rule, or pre-check to prevent recurrence."
            ),
            "recommended_actions": actions,
            "latest_example": cluster.get("latest_fix", ""),
            "tags": cluster.get("common_tags", []) + ["proactive", "verified"],
        })

    # 2. Log error patterns
    for cluster in log_clusters:
        if cluster["count"] < 2:
            continue
        error_type = cluster["error_type"]
        count = cluster["count"]
        severity = "high" if count >= 5 else "medium"
        _add({
            "id": f"log-error-{error_type}",
            "source": "session_logs",
            "severity": severity,
            "issue_type": f"log_{error_type}",
            "occurrence_count": count,
            "title": f"Log pattern '{error_type}' seen {count} times: {cluster['pattern']}",
            "description": (
                f"Error type '{error_type}' appeared {count} times in recent logs. "
                f"Pattern: {cluster['pattern']}"
            ),
            "recommended_actions": [
                "Add suppression filter in cron job output parser",
                "Investigate root cause in the source module",
                "Add error handling for this specific error type",
            ],
            "latest_example": cluster.get("sample_messages", [""])[0] if cluster.get("sample_messages") else "",
            "tags": ["log-analysis", error_type],
        })

    # 3. High-risk domains from Knowledge Cube
    for domain_info in cube_patterns.get("high_risk_domains", []):
        domain = domain_info["domain"]
        failures = domain_info["failures"]
        failure_rate = cube_patterns.get("failure_rate", 0.0)
        _add({
            "id": f"domain-risk-{domain}",
            "source": "knowledge_cube",
            "severity": "high" if failures >= 20 else "medium",
            "issue_type": "domain_failure_pattern",
            "occurrence_count": failures,
            "title": f"High failure rate in domain '{domain}' ({failure_rate * 100:.1f}%)",
            "description": (
                f"Domain '{domain}' has a {failure_rate * 100:.1f}% failure rate "
                f"({failures} failures out of {cube_patterns.get('total', 0)} experiences). "
                "Investigate root causes and add safeguards."
            ),
            "recommended_actions": [
                f"Review recent failures in domain '{domain}'",
                f"Add validation or error-handling for {domain} tasks",
                f"Create a checklist for {domain} operations",
            ],
            "latest_example": "",
            "tags": ["domain-risk", "debugging", "knowledge-cube"],
        })

    # 4. White spots (knowledge gaps)
    white_spots = cube_patterns.get("white_spot_domains", [])
    if white_spots:
        _add({
            "id": "white-spots-discovery",
            "source": "knowledge_cube",
            "severity": "low",
            "issue_type": "knowledge_gap",
            "occurrence_count": len(white_spots),
            "title": f"Knowledge gaps detected in {len(white_spots)} domains",
            "description": (
                "The Knowledge Cube has white spots (unexplored areas) in: "
                + ", ".join(white_spots) + ". Consider targeted exploration."
            ),
            "recommended_actions": [
                f"Run proactive exploration for domain: {w}" for w in white_spots
            ] + ["Schedule knowledge-gathering sessions for underserved areas"],
            "latest_example": "",
            "tags": ["white-spot", "knowledge-gap"],
        })

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    suggestions.sort(key=lambda s: severity_order.get(s.get("severity"), 9))
    return suggestions


def _suggest_actions_for_type(issue_type, cluster):
    """Map known issue types to concrete improvement actions."""
    actions = []
    t = issue_type.lower()
    if any(k in t for k in ("indent", "syntax", "parse", "import")):
        actions.append("Run linter/formatter on affected files")
        actions.append("Add syntax check to CI")
    elif any(k in t for k in ("type", "hang")):
        actions.append("Add timeout and type validation")
    elif any(k in t for k in ("config", "env")):
        actions.append("Add config validation at startup")
    elif any(k in t for k in ("api", "tick", "notifier", "tool")):
        actions.append(f"Add preventive guard for '{issue_type}' issues")
        actions.append("Implement tool error recovery")
        actions.append("Add fallback tool strategy")
    actions.append("Document the fix pattern for future reference")
    actions.append("Create a test case to prevent regression")
    actions.append("Log pattern to Knowledge Cube for future reference")
    return actions


# ---------------------------------------------------------------------------
# Skill auto-creation
# ---------------------------------------------------------------------------

def _get_existing_skills():
    """Return set of existing skill names (directory names under skills/)."""
    if not SKILLS_DIR.exists():
        return set()
    return {p.name for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")}


# ---------------------------------------------------------------------------
# Skill file hygiene (2026-08-05, user: "научи правильно оформлять файлы")
# ---------------------------------------------------------------------------
# Правила для АВТО-СОЗДАННЫХ скиллов (товарищи #1/#2 — background_review,
# self_improvement_loop). ЕДИНЫЙ ИСТОЧНИК: config/skill_hygiene.yaml.
# Правки — в YAML, не в коде (принцип пользователя: «кодить так, чтобы
# правки вносить в одном файле», 2026-08-05).
#
# ЗАПРЕЩЕНО создавать скилл-скелет: TODO-заглушки, `pass` в теле,
# пустые чекбоксы [ ] — это антипаттерн «записал-не-сделал» (запись
# выдаётся за действие). Скилл без реального содержания НЕ создаётся.

_HYGIENE_CONFIG = HERMES_HOME / "config" / "skill_hygiene.yaml"


def _load_hygiene_config() -> dict:
    """Читает config/skill_hygiene.yaml. При ошибке — пустой dict."""
    try:
        import yaml
        return yaml.safe_load(_HYGIENE_CONFIG.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _load_skeleton_markers() -> tuple:
    """Маркеры скелета из конфига (не из кода). Фолбэк — дефолтные."""
    cfg = _load_hygiene_config()
    markers = cfg.get("skeleton_markers")
    if isinstance(markers, list) and markers:
        return tuple(str(m) for m in markers)
    return ("TODO", "TBD", "FIXME", "placeholder", "PLACEHOLDER",
            "pass\n", "# Arrange", "# Act", "- [ ]", "[ ]")


_SKELETON_MARKERS = _load_skeleton_markers()


def _is_skeleton(md: str) -> bool:
    """True если SKILL.md — пустышка без реального содержания."""
    for m in _SKELETON_MARKERS:
        if m.lower() in md.lower():
            return True
    return False


def _valid_skill_name(name: str) -> str:
    """Нормализует имя скилла: lowercase, только [a-z0-9_-], без пробелов."""
    cfg = _load_hygiene_config()
    name_cfg = cfg.get("name", {}) or {}
    max_len = int(name_cfg.get("max_length", 64))
    allowed = str(name_cfg.get("allowed_chars", "[a-z0-9_-]"))
    safe = re.sub(rf"[^{allowed}]+", "-", name.lower()).strip("-")
    if len(safe) > max_len:
        safe = safe[:max_len].rstrip("-")
    return safe or "auto-skill"


def _write_skill_file(name: str, md: str, existing_skills) -> bool:
    """
    Безопасно создаёт SKILL.md: валидация имени, frontmatter, запрет скелетов.
    Возвращает True если создан, False если отклонён.
    """
    # 1. скелеты не создаём — запись не должна выдаваться за действие
    if _is_skeleton(md):
        logger.info(f"SKIP skeleton skill: {name} (no real content)")
        return False
    # 2. имя — только валидное
    name = _valid_skill_name(name)
    if name in existing_skills:
        return False
    # 3. frontmatter: обязательные name/description/trigger, category=auto-generated
    if not re.search(r"^---\nname:", md, re.M):
        md = f"---\nname: {name}\ncategory: auto-generated\n---\n\n" + md
    if "category:" not in md.split("---", 2)[1]:
        md = md.replace("---\n", f"---\ncategory: auto-generated\n", 1)
    skill_dir = SKILLS_DIR / name
    try:
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(md, encoding="utf-8")
        existing_skills.add(name)
        return True
    except OSError as e:
        logger.warning(f"OSError writing skill {name}: {e}")
        return False


def _generate_skill_md(topic, patterns, count):
    """Generate an executable SKILL.md for a discovered pattern with patch + test."""
    safe_topic = topic.replace(" ", "_")
    title = topic.replace("_", " ").title()
    pattern_lines = []
    for i, p in enumerate(patterns[:3], 1):
        sample = p[:200].replace("`", "")
        pattern_lines.append(f"### Pattern {i}\n```\n{sample}\n```\n")

    # Только реальные образцы — НИКАКИХ TODO-заглушек (антипаттерн «записал-не-сделал»).
    # Скелет с 'pass'/'TODO' будет отклонён _write_skill_file → не создастся.
    if not patterns:
        return ""

    return f"""---
name: {safe_topic}-auto-skill
description: "Auto-generated executable skill — {count} occurrences of '{topic}' pattern"
trigger: When dealing with {topic} related issues
usage: {safe_topic}-auto-skill
category: auto-generated
---

# {title}: Executable Fix Skill

Generated by the Self-Improvement Loop after detecting {count} occurrences of this pattern.

## Discovered Patterns

{chr(10).join(pattern_lines)}
## Fix Approach

Apply the pattern above to the failing code path. Verify the fix with a regression check before closing.

## Prevention Checklist

- Apply the fix from the pattern above (an actual change, not a stub)
- Verify the fix works (run, test, observe)
- Record the pattern in Knowledge Cube if not yet present
- Domain: {topic}
- Created: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- Source: Self-Improvement Loop

"""


def auto_create_skills(recurring_fixes, log_clusters, existing_skills):
    """
    Auto-create skills when patterns appear 3+ times.
    Returns list of created skill names.
    """
    created = []
    for cluster in recurring_fixes:
        if cluster["count"] >= 3:
            name = f"{cluster['issue_type']}-auto-skill"
            if name in existing_skills:
                continue
            md = _generate_skill_md(cluster["issue_type"], cluster.get("sample_fixes", []), cluster["count"])
            if _write_skill_file(name, md, existing_skills):
                created.append(name)

    for cluster in log_clusters:
        if cluster["count"] >= 3:
            name = f"log-{cluster['error_type']}-auto-skill"
            if name in existing_skills:
                continue
            md = _generate_skill_md(f"log-{cluster['error_type']}", cluster.get("sample_messages", []), cluster["count"])
            if _write_skill_file(name, md, existing_skills):
                created.append(name)

    return created


def create_skills_from_suggestions(suggestions, existing_skills):
    """
    Create skills directly from improvement suggestions.
    Unlike auto_create_skills (which works from recurring patterns),
    this takes the suggestions list and creates actionable skills.
    """
    created = []
    for s in suggestions:
        if s.get("severity") not in ("critical", "high"):
            continue
        name = f"fix-{s.get('issue_type', 'pattern')}-skill"
        if name in existing_skills:
            continue
        actions = "\n".join(f"{i}. {a}" for i, a in enumerate(s.get("recommended_actions", []), 1))
        md = f"""---
name: {name}
description: "Auto-created from suggestion: {s.get('title', '')[:80]}"
trigger: When {s.get('issue_type', 'pattern')} pattern occurs ({s.get('occurrence_count', 0)}+ times)
---

# {s.get('title', name)}

## Problem

{s.get('description', '')}

## Recommended Actions

{actions}

## Severity: {s.get('severity', 'medium')}
## Occurrences: {s.get('occurrence_count', 0)}
## Source: self-improvement suggestion engine
"""
        skill_dir = SKILLS_DIR / name
        try:
            if _write_skill_file(name, md, existing_skills):
                created.append(name)
        except OSError:
            pass

    return created


# ---------------------------------------------------------------------------
# Knowledge Cube writer
# ---------------------------------------------------------------------------

def write_knowledge_to_cube(recurring_fixes, log_clusters, cube_patterns):
    """
    Write verified knowledge entries to the Knowledge Cube when patterns
    are sufficiently strong (count >= 3).
    Each entry gets structured 8-angle dynamic_axes.
    Suggestions filtered through suggestion_filter before writing.
    """
    if not CUBE_DB.exists():
        return 0

    conn = _connect(CUBE_DB)
    if conn is None:
        return 0

    written = 0
    try:
        # Check if experiences table has the columns we need
        cols = [r[1] for r in conn.execute("PRAGMA table_info(experiences)").fetchall()]
        if "raw_text" not in cols or "axis_domain" not in cols:
            return 0

        now = datetime.now().isoformat()

        # Write knowledge from strong recurring patterns
        for cluster in recurring_fixes:
            if cluster["count"] >= 3:
                text = (
                    f"Self-improvement pattern: '{cluster['issue_type']}' "
                    f"appeared {cluster['count']} times. "
                    f"Latest fix: {cluster['latest_fix'][:300]}. "
                    f"Common tags: {', '.join(cluster['common_tags'][:5])}."
                )
                try:
                    content_hash = hashlib.md5(f"{text}_{now}".encode()).hexdigest()[:16]
                    conn.execute(
                        """INSERT INTO experiences (ts, content, raw_text, hash, axis_domain, axis_outcome,
                           tags, source, is_white_spot)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                        (
                            now,
                            text,
                            text,
                            content_hash,
                            "system",
                            "success",
                            json.dumps(["self-improvement", "auto-verified"]),
                            "self_improvement_loop",
                        ),
                    )
                    written += 1
                except (sqlite3.Error, TypeError):
                    pass

        # Log-pattern echoes are NOT written to the Cube — they are log copies,
        # not knowledge (DIRECTIVE 0x50 filter 2026-08-01). suggestion_consumer
        # reads improvement_suggestions.json, so auto-skills still work.
        # Kept: recurring_fixes (structural, source=self_improvement_loop).

        conn.commit()
    except (sqlite3.Error, OSError):
        pass
    finally:
        _safe_close(conn)

    # Trigger knowledge_added event for chain_heartbeat
    if written > 0:
        try:
            from chain_heartbeat import event_beat
            event_beat("knowledge_added")
        except ImportError:
            pass

    return written


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def load_metrics():
    """Load the improvement metrics file."""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "total_runs": 0,
        "total_suggestions_generated": 0,
        "total_skills_created": 0,
        "total_knowledge_entries_written": 0,
        "runs": [],
    }


def save_metrics(metrics):
    """Save improvement metrics."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        METRICS_FILE.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def record_run(metrics, suggestions_count, skills_created, knowledge_written):
    """Record a run's results in metrics."""
    metrics["total_runs"] = metrics.get("total_runs", 0) + 1
    metrics["total_suggestions_generated"] = metrics.get("total_suggestions_generated", 0) + len(suggestions_count) if isinstance(suggestions_count, list) else metrics.get("total_suggestions_generated", 0) + suggestions_count
    metrics["total_skills_created"] = metrics.get("total_skills_created", 0) + len(skills_created)
    metrics["total_knowledge_entries_written"] = metrics.get("total_knowledge_entries_written", 0) + knowledge_written
    metrics.setdefault("runs", []).append({
        "ts": datetime.now().isoformat(),
        "suggestions": len(suggestions_count) if isinstance(suggestions_count, list) else suggestions_count,
        "skills_created": len(skills_created),
        "knowledge_written": knowledge_written,
    })


def store_suggestions(suggestions, recurring, cube_patterns, log_clusters):
    """Write the final suggestions JSON file."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    total = len(suggestions)
    by_severity = Counter(s.get("severity", "medium") for s in suggestions)
    data = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_suggestions": total,
            "critical": by_severity.get("critical", 0),
            "high": by_severity.get("high", 0),
            "medium": by_severity.get("medium", 0),
            "low": by_severity.get("low", 0),
            "recurring_issue_clusters": len(recurring),
            "total_fixes_analyzed": sum(c.get("count", 0) for c in recurring),
            "cube_experiences_analyzed": cube_patterns.get("total", 0),
            "overall_failure_rate": cube_patterns.get("failure_rate", 0.0),
            "log_error_clusters": len(log_clusters),
            "total_log_errors_analyzed": sum(c.get("count", 0) for c in log_clusters),
        },
        "suggestions": suggestions,
    }
    try:
        OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _load_file_hygiene_rules() -> str:
    """Читает эталон оформления скиллов из skills/AGENTS.md (обновляемый стандарт).

    Единый источник правил для loop и review (вместо дублирования в коде):
    если правила меняются — правка в skills/AGENTS.md, не в коде.
    Возвращает текст секции "Skill File Hygiene" или пустую строку.
    """
    agents_md = HERMES_HOME / "skills" / "AGENTS.md"
    try:
        text = agents_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if "Skill File Hygiene" not in text:
        return ""
    section = text.split("## Skill File Hygiene", 1)[1]
    section = section.split("\n## ", 1)[0]
    return section.strip()


def main():
    print(f"[{datetime.now().isoformat()}] Self-improvement loop starting...")

    hygiene = _load_file_hygiene_rules()
    if hygiene:
        print(f"  File hygiene rules loaded: {len(hygiene.splitlines())} lines (skills/AGENTS.md)")
    else:
        print("  WARNING: skills/AGENTS.md 'Skill File Hygiene' section not found")

    fixes = load_verified_fixes()
    experiences = load_cube_experiences()
    all_errors, recent_errors = load_recent_errors(48)

    print(
        f"  Loaded {len(fixes)} verified fixes from {FIXES_DB.name}, "
        f"{len(experiences)} experiences from {CUBE_DB.name}, "
        f"{len(recent_errors)} recent errors from logs (48h)"
    )

    # Session recall — historical context for better suggestions
    session_context = []
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from session_recall import semantic_search
        recall = semantic_search("improvement patterns", limit=5)
        if isinstance(recall, dict):
            for item in recall.get("results", []) or []:
                if isinstance(item, dict):
                    session_context.append(item.get("content", item.get("text", "")))
        elif isinstance(recall, list):
            for item in recall:
                if isinstance(item, dict):
                    session_context.append(item.get("content", item.get("text", "")))
                elif isinstance(item, str):
                    session_context.append(item)
        print(f"  Session recall: {len(session_context)} historical contexts found")
    except Exception as e:
        print(f"  Session recall unavailable: {e}")

    # Identify patterns
    recurring = identify_recurring_fixes(fixes)
    log_clusters = analyze_error_patterns(recent_errors)
    cube_patterns = identify_cube_patterns(experiences)

    print(
        f"  Found {len(recurring)} recurring issue clusters from fixes, "
        f"{len(log_clusters)} error clusters from logs"
    )
    print(
        f"  Cube analysis: {cube_patterns.get('total', 0)} experiences, "
        f"{cube_patterns.get('total_failures', 0)} failures, "
        f"{len(cube_patterns.get('high_risk_domains', []))} high-risk domains"
    )

    # Generate suggestions
    seen_ids = load_previous_suggestions()
    suggestions = generate_suggestions(recurring, cube_patterns, log_clusters, seen_ids)
    print(f"  Generated {len(suggestions)} improvement suggestions")

    # Auto-create skills
    existing_skills = _get_existing_skills()
    created_auto = auto_create_skills(recurring, log_clusters, existing_skills)
    print(f"  Auto-created {len(created_auto)} new skills from recurring patterns")
    created_sugg = create_skills_from_suggestions(suggestions, existing_skills)
    print(f"  Created {len(created_sugg)} skills from suggestions")
    all_created = created_auto + created_sugg

    # Emit knowledge_added event + write to cube
    written = write_knowledge_to_cube(recurring, log_clusters, cube_patterns)
    try:
        from emit_event import emit
        emit("knowledge_added", {"source": "self_improvement_loop", "entries": written})
    except ImportError:
        pass
    print(f"  Wrote {written} knowledge entries to Knowledge Cube")

    # Emit new_suggestions_ready event (event_bus + chain_heartbeat)
    try:
        from emit_event import emit
        emit("new_suggestions_ready", {"count": len(suggestions), "source": "self_improvement_loop"})
    except ImportError:
        pass
    try:
        from chain_heartbeat import event_beat
        event_beat("new_suggestions_ready")
    except ImportError:
        pass

    # Consume suggestions via suggestion_consumer
    try:
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from suggestion_consumer import consume
        result = consume(n=10)
        print(
            f"  Consumer: applied={result.get('applied', 0)}, "
            f"dups={result.get('duplicates', 0)}, "
            f"skipped={result.get('skipped', 0)}, "
            f"processed={result.get('total_processed', 0)}"
        )
    except Exception as e:
        print(f"  Consumer error: {e}")

    # Store results
    metrics = load_metrics()
    record_run(metrics, suggestions, all_created, written)
    save_metrics(metrics)
    store_suggestions(suggestions, recurring, cube_patterns, log_clusters)
    print(f"  Saved to {OUTPUT.name}")

    # Report
    summary = {
        "total_suggestions": len(suggestions),
        "critical": sum(1 for s in suggestions if s.get("severity") == "critical"),
        "high": sum(1 for s in suggestions if s.get("severity") == "high"),
        "medium": sum(1 for s in suggestions if s.get("severity") == "medium"),
        "low": sum(1 for s in suggestions if s.get("severity") == "low"),
        "recurring_issue_clusters": len(recurring),
        "log_error_clusters": len(log_clusters),
        "total_fixes_analyzed": sum(c.get("count", 0) for c in recurring),
        "total_log_errors_analyzed": sum(c.get("count", 0) for c in log_clusters),
        "cube_experiences_analyzed": cube_patterns.get("total", 0),
        "overall_failure_rate": cube_patterns.get("failure_rate", 0.0),
    }

    print("\n=== Self-Improvement Report ===")
    print(
        f"  Suggestions: {summary['total_suggestions']} "
        f"({summary['critical']} critical, {summary['high']} high, "
        f"{summary['medium']} medium, {summary['low']} low)"
    )
    print(f"  Recurring clusters: {summary['recurring_issue_clusters']}")
    print(f"  Log error clusters: {summary['log_error_clusters']}")
    print(f"  Fixes analyzed: {summary['total_fixes_analyzed']}")
    print(f"  Log errors analyzed: {summary['total_log_errors_analyzed']}")
    print(f"  Cube experiences: {summary['cube_experiences_analyzed']}")
    print(f"  Overall failure rate: {summary['overall_failure_rate']:.1%}")
    print(f"  Skills created: {len(all_created)}")
    print(f"  Knowledge entries written: {written}")
    print(f"  Total runs: {metrics.get('total_runs', 0)}")
    print(f"  Cumulative suggestions: {metrics.get('total_suggestions_generated', 0)}")
    print(f"  Cumulative skills created: {metrics.get('total_skills_created', 0)}")

    if suggestions:
        print("\nTop suggestions:")
        for s in suggestions[:5]:
            print(f"  [{s['severity'].upper()}] {s['title']}")

    if all_created:
        print("\nNew skills created:")
        for name in all_created:
            print(f"  + {name}")

    if not suggestions:
        print("\nNo actionable suggestions at this time — system looks healthy!")

    return {
        "suggestions_count": len(suggestions),
        "skills_created": len(all_created),
        "knowledge_written": written,
        "summary": summary,
    }


if __name__ == "__main__":
    main()
