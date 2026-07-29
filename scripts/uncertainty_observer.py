#!/usr/bin/env python3
"""
Наблюдатель Неопределенности — стратегический философский анализатор системного состояния.

Основан на 'Принципе Неопределенности' Олега Лукьянова.
Собирает комплексное состояние системы, вызывает LLM для философского анализа,
и сохраняет результат в cache/observer_analyses.json.

Запуск:
    python scripts/uncertainty_observer.py
    python scripts/uncertainty_observer.py --context "пользователь просил обратить внимание на X"
"""

import argparse
import json
import os
import sqlite3
import time
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
HERMES_HOME = SCRIPT_DIR.parent
CACHE_DIR = HERMES_HOME / "cache"
CRON_DIR = HERMES_HOME / "cron"
MEMORIES_DIR = HERMES_HOME / "memories"
OUTPUT_FILE = CACHE_DIR / "observer_analyses.json"
CUBE_DB = CACHE_DIR / "knowledge_cube.db"
FIXES_DB = CACHE_DIR / "verified_fixes.db"
METRICS_FILE = CACHE_DIR / "system_metrics.json"
DECISIONS_FILE = CACHE_DIR / "agent_decisions.json"
USER_PROFILE = MEMORIES_DIR / "USER.md"
CRON_JOBS_FILE = CRON_DIR / "jobs.json"
CRON_OUTPUT_DIR = CRON_DIR / "output"

API_URL = "https://opencode.ai/zen/v1/chat/completions"
MODEL = "mimo-v2.5-free"
MAX_TOKENS = 4000

# ---------------------------------------------------------------------------
# LLM Client
# ---------------------------------------------------------------------------

def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> Optional[str]:
    """Call opencode.ai/zen API with system + user message."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }
    for attempt in range(3):
        try:
            r = requests.post(API_URL, json=payload, timeout=120)
            if r.status_code == 200:
                data = r.json()
                msg = data.get("choices", [{}])[0].get("message", {})
                content = msg.get("content") or msg.get("reasoning") or ""
                return content.strip() if content else None
            elif r.status_code == 429:
                wait = 3 + random.random() * 4
                print(f"[Observer] Rate limited, waiting {wait:.1f}s...")
                time.sleep(wait)
                continue
            else:
                print(f"[Observer] API error {r.status_code}: {r.text[:300]}")
                return None
        except Exception as e:
            print(f"[Observer] Request error: {e}")
            return None
    print("[Observer] All retries exhausted.")
    return None


# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------

def _db_query(db_path: Path, sql: str, params=()) -> List[Dict]:
    """Run a query and return list of dicts, or empty list on error."""
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


def _load_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def collect_knowledge_cube_stats() -> Dict[str, Any]:
    """Collect Knowledge Cube: entries, domains, outcomes, white spots, failure rate."""
    info: Dict[str, Any] = {
        "total_entries": 0,
        "domains": {},
        "outcomes": {},
        "white_spots": 0,
        "white_spot_pct": 0.0,
        "failure_rate": 0.0,
        "top_domains": [],
        "recent_entries": [],
    }

    rows = _db_query(CUBE_DB, "SELECT * FROM experiences")
    if not rows:
        return info

    info["total_entries"] = len(rows)

    # Domains
    domain_counts: Dict[str, int] = {}
    outcome_counts: Dict[str, int] = {}
    white_spots = 0

    for r in rows:
        d = r.get("axis_domain", "unknown") or "unknown"
        o = r.get("axis_outcome", "unknown") or "unknown"
        domain_counts[d] = domain_counts.get(d, 0) + 1
        outcome_counts[o] = outcome_counts.get(o, 0) + 1
        if r.get("is_white_spot"):
            white_spots += 1

    info["domains"] = domain_counts
    info["outcomes"] = outcome_counts
    info["white_spots"] = white_spots
    info["white_spot_pct"] = round(100 * white_spots / max(len(rows), 1), 1)

    total = len(rows)
    failures = outcome_counts.get("failure", 0)
    info["failure_rate"] = round(100 * failures / max(total, 1), 1)

    # Top 5 domains
    sorted_domains = sorted(domain_counts.items(), key=lambda x: -x[1])[:5]
    info["top_domains"] = [{"domain": d, "count": c} for d, c in sorted_domains]

    # 10 most recent entries (summary)
    rows_sorted = sorted(rows, key=lambda r: r.get("ts", ""), reverse=True)[:10]
    info["recent_entries"] = [
        {
            "ts": r.get("ts", ""),
            "domain": r.get("axis_domain", ""),
            "outcome": r.get("axis_outcome", ""),
            "preview": (r.get("raw_text", "") or "")[:120],
        }
        for r in rows_sorted
    ]

    return info


def collect_cron_health() -> Dict[str, Any]:
    """Collect cron job stats: jobs, errors, staleness."""
    info: Dict[str, Any] = {
        "total_jobs": 0,
        "enabled_jobs": 0,
        "jobs_with_errors": 0,
        "last_errors": [],
        "stale_jobs": [],
        "recent_outputs": [],
    }

    jobs_data = _load_json(CRON_JOBS_FILE, {"jobs": []})
    jobs = jobs_data.get("jobs", [])
    info["total_jobs"] = len(jobs)
    info["enabled_jobs"] = sum(1 for j in jobs if j.get("enabled"))

    now = datetime.now(timezone.utc)
    stale_threshold_hours = 48

    for j in jobs:
        if j.get("last_error"):
            info["jobs_with_errors"] += 1
            info["last_errors"].append({
                "name": j.get("name", "?"),
                "error": j["last_error"][:200],
            })

        last_run = j.get("last_run_at")
        if last_run and j.get("enabled"):
            try:
                lr = datetime.fromisoformat(last_run)
                delta_h = (now - lr).total_seconds() / 3600
                if delta_h > stale_threshold_hours:
                    info["stale_jobs"].append({
                        "name": j.get("name", "?"),
                        "last_run": last_run,
                        "hours_ago": round(delta_h, 1),
                    })
            except Exception:
                pass

    # Latest cron output files (last 5 across all jobs)
    if CRON_OUTPUT_DIR.exists():
        all_outputs = []
        for job_dir in CRON_OUTPUT_DIR.iterdir():
            if job_dir.is_dir():
                for md_file in job_dir.glob("*.md"):
                    try:
                        stat = md_file.stat()
                        all_outputs.append({
                            "job_id": job_dir.name,
                            "file": md_file.name,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "size": stat.st_size,
                        })
                    except Exception:
                        pass
        all_outputs.sort(key=lambda x: x["modified"], reverse=True)
        info["recent_outputs"] = all_outputs[:5]

    return info


def collect_verified_fixes_stats() -> Dict[str, Any]:
    """Collect verified fixes: count, recent fixes, types."""
    info: Dict[str, Any] = {
        "total_fixes": 0,
        "fix_types": {},
        "recent_fixes": [],
    }

    rows = _db_query(FIXES_DB, "SELECT * FROM verified_fixes ORDER BY created_at DESC")
    if not rows:
        return info

    info["total_fixes"] = len(rows)

    type_counts: Dict[str, int] = {}
    for r in rows:
        t = r.get("fix_type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    info["fix_types"] = type_counts

    for r in rows[:5]:
        info["recent_fixes"].append({
            "issue_type": r.get("issue_type", ""),
            "fix_type": r.get("fix_type", ""),
            "description": (r.get("fix_description", "") or "")[:150],
            "created_at": r.get("created_at", ""),
        })

    return info


def collect_agent_decisions() -> Dict[str, Any]:
    """Collect agent decisions history."""
    data = _load_json(DECISIONS_FILE, {})
    decisions = data.get("decisions", [])
    return {
        "total_runs": data.get("total_runs", 0),
        "last_updated": data.get("last_updated", ""),
        "last_summary": data.get("last_state_summary", {}),
        "recent_decisions": [
            {
                "action_id": d.get("action_id", ""),
                "tier_name": d.get("tier_name", ""),
                "title": d.get("title", ""),
                "score": d.get("score", 0),
                "timestamp": d.get("timestamp", ""),
            }
            for d in decisions[-5:]
        ],
    }


def collect_system_metrics() -> Dict[str, Any]:
    """Collect system metrics: health score, disk, memory, cron stats."""
    metrics_list = _load_json(METRICS_FILE, [])
    if not metrics_list:
        return {"available": False}

    latest = metrics_list[-1] if isinstance(metrics_list, list) else metrics_list
    return latest


def collect_recent_errors() -> List[Dict[str, str]]:
    """Scan for recent error patterns in temp files and logs."""
    errors = []

    # Check cron output dirs for error indicators
    if CRON_OUTPUT_DIR.exists():
        for job_dir in CRON_OUTPUT_DIR.iterdir():
            if not job_dir.is_dir():
                continue
            for md_file in job_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8", errors="replace")[:500]
                    if any(kw in content.lower() for kw in ["error", "traceback", "failed", "ошибка"]):
                        errors.append({
                            "source": f"cron/{job_dir.name}/{md_file.name}",
                            "preview": content[:200],
                        })
                except Exception:
                    pass

    # Check self_assessment_latest.md for errors
    sa_file = CACHE_DIR / "self_assessment_latest.md"
    if sa_file.exists():
        try:
            content = sa_file.read_text(encoding="utf-8", errors="replace")[:500]
            if any(kw in content.lower() for kw in ["error", "failed", "critical"]):
                errors.append({
                    "source": "self_assessment_latest.md",
                    "preview": content[:200],
                })
        except Exception:
            pass

    return errors[:5]


def collect_disk_memory() -> Dict[str, Any]:
    """Collect disk and memory resources."""
    import shutil
    info: Dict[str, Any] = {}
    try:
        usage = shutil.disk_usage("D:/")
        info["disk_total_gb"] = round(usage.total / (1024**3), 1)
        info["disk_free_gb"] = round(usage.free / (1024**3), 1)
        info["disk_used_pct"] = round(100 * usage.used / usage.total, 1)
    except Exception:
        info["disk_error"] = "could not read disk info"

    # Cache directory size
    try:
        cache_size = sum(f.stat().st_size for f in CACHE_DIR.rglob("*") if f.is_file())
        info["cache_size_mb"] = round(cache_size / (1024**2), 1)
    except Exception:
        pass

    return info


def read_user_profile() -> str:
    """Read USER.md and return a concise summary."""
    if not USER_PROFILE.exists():
        return "[USER.md not found]"
    try:
        content = USER_PROFILE.read_text(encoding="utf-8")
        # Split by § and take first 3 sections for context
        sections = [s.strip() for s in content.split("§") if s.strip()]
        summary = " | ".join(sections[:4])
        if len(summary) > 1500:
            summary = summary[:1500] + "..."
        return summary
    except Exception:
        return "[error reading USER.md]"


# ---------------------------------------------------------------------------
# Build analysis context
# ---------------------------------------------------------------------------

def build_context(extra_context: str = "") -> str:
    """Collect all data and build a rich context string for the LLM."""
    sections = []

    # 1. Knowledge Cube
    cube = collect_knowledge_cube_stats()
    lines = [
        "=== KNOWLEDGE CUBE ===",
        f"Total entries: {cube['total_entries']}",
        f"White spots: {cube['white_spots']} ({cube['white_spot_pct']}%)",
        f"Failure rate: {cube['failure_rate']}%",
    ]
    if cube["top_domains"]:
        lines.append("Top domains: " + ", ".join(
            f"{d['domain']}({d['count']})" for d in cube["top_domains"]
        ))
    if cube["outcomes"]:
        lines.append("Outcomes: " + ", ".join(
            f"{k}({v})" for k, v in sorted(cube["outcomes"].items(), key=lambda x: -x[1])
        ))
    if cube["recent_entries"]:
        lines.append("Recent entries:")
        for e in cube["recent_entries"]:
            lines.append(f"  [{e['ts'][:10]}] {e['domain']}/{e['outcome']}: {e['preview']}")
    sections.append("\n".join(lines))

    # 2. Cron Health
    cron = collect_cron_health()
    lines = [
        "=== CRON HEALTH ===",
        f"Total jobs: {cron['total_jobs']}, enabled: {cron['enabled_jobs']}",
        f"Jobs with errors: {cron['jobs_with_errors']}",
    ]
    if cron["last_errors"]:
        lines.append("Recent errors:")
        for e in cron["last_errors"]:
            lines.append(f"  {e['name']}: {e['error'][:120]}")
    if cron["stale_jobs"]:
        lines.append("Stale jobs (>48h):")
        for s in cron["stale_jobs"]:
            lines.append(f"  {s['name']}: last run {s['hours_ago']}h ago")
    sections.append("\n".join(lines))

    # 3. Verified Fixes
    fixes = collect_verified_fixes_stats()
    lines = [
        "=== VERIFIED FIXES ===",
        f"Total fixes: {fixes['total_fixes']}",
    ]
    if fixes["fix_types"]:
        lines.append("Types: " + ", ".join(
            f"{k}({v})" for k, v in fixes["fix_types"].items()
        ))
    if fixes["recent_fixes"]:
        lines.append("Recent:")
        for f in fixes["recent_fixes"]:
            lines.append(f"  [{f['created_at'][:10]}] {f['issue_type']}/{f['fix_type']}: {f['description'][:100]}")
    sections.append("\n".join(lines))

    # 4. Agent Decisions
    decisions = collect_agent_decisions()
    lines = [
        "=== AGENT DECISIONS ===",
        f"Total runs: {decisions['total_runs']}",
        f"Last updated: {decisions['last_updated']}",
    ]
    if decisions["last_summary"]:
        s = decisions["last_summary"]
        lines.append(f"Last state: entries={s.get('cube_entries')}, cron_errors={s.get('cron_errors')}, disk_free={s.get('disk_free')}GB")
    if decisions["recent_decisions"]:
        lines.append("Recent decisions:")
        for d in decisions["recent_decisions"]:
            lines.append(f"  [{d['tier_name']}] {d['title']} (score={d['score']})")
    sections.append("\n".join(lines))

    # 5. System Metrics
    metrics = collect_system_metrics()
    if metrics:
        lines = ["=== SYSTEM METRICS ==="]
        for k, v in metrics.items():
            if isinstance(v, dict):
                lines.append(f"  {k}: {json.dumps(v, ensure_ascii=False)[:200]}")
            else:
                lines.append(f"  {k}: {v}")
        sections.append("\n".join(lines))

    # 6. Recent Errors
    errors = collect_recent_errors()
    if errors:
        lines = ["=== RECENT ERRORS ==="]
        for e in errors:
            lines.append(f"  [{e['source']}] {e['preview'][:150]}")
        sections.append("\n".join(lines))

    # 7. Disk/Memory
    resources = collect_disk_memory()
    if resources:
        lines = ["=== RESOURCES ==="]
        for k, v in resources.items():
            lines.append(f"  {k}: {v}")
        sections.append("\n".join(lines))

    # 8. User Profile
    profile = read_user_profile()
    sections.append(f"=== USER PROFILE ===\n{profile}")

    # 9. Extra context
    if extra_context:
        sections.append(f"=== EXTRA CONTEXT (from user) ===\n{extra_context}")

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# LLM System Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Ты — 'Наблюдатель Неопределенности', стратегический философский аналитик системного состояния, основанный на 'Принципе Неопределенности' Олега Лукьянова.

Философия: Любая сложная система существует на границе между порядком и хаосом. Твоя задача — не просто перечислить метрики, а увидеть глубинные тенденции, скрытые закономерности и точки роста.

Анализируй предоставленные данные системы и сформируй ответ ТОЛЬКО в формате из 3 блоков:

## Философский срез
Опиши текущее состояние системы как баланс между порядком (структура, метрики, исправления) и хаосом (ошибки, белые пятна, неизвестное). Используй метафоры. Какова 'температура' системы? Где напряжение? Что трансформируется?

## Векторы глокального развития
Направи 2-3 стратегических вектора развития, основанных на данных. Каждый вектор должен быть конкретным: что именно развивать, почему это важно сейчас, какой эффект ожидается. Глокальное = одновременно глобальное и локальное.

## Точечные импульсы
Дай 1-2 нетривиальные идеи оптимизации для конкретных модулей системы. Не очевидные (не 'почини ошибки'), а глубинные — например, как переиспользовать данные одного модуля в другом, как сгенерировать новое знание из существующих паттернов, как уменьшить энтропию без прямого вмешательства.

Отвечай на русском языке. Будь глубоким, но конкретным. Не используй общие фразы — ссылайся на реальные цифры и данные из контекста."""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Наблюдатель Неопределенности — стратегический философский анализатор"
    )
    parser.add_argument(
        "--context",
        type=str,
        default="",
        help="Дополнительный контекст от пользователя",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Не печатать ответ LLM в stdout",
    )
    args = parser.parse_args()

    print("[Observer] Сбор системного состояния...")
    context = build_context(extra_context=args.context)

    print(f"[Observer] Контекст собран ({len(context)} символов). Вызов LLM...")
    response = call_llm(SYSTEM_PROMPT, context)

    if not response:
        print("[Observer] ОШИБКА: LLM не вернул ответ.")
        return

    print("\n" + "=" * 70)
    print("  НАБЛЮДАТЕЛЬ НЕОПРЕДЕЛЕННОСТИ — АНАЛИЗ")
    print("=" * 70)
    if not args.no_print:
        print(response)
    print("=" * 70 + "\n")

    # Save to cache/observer_analyses.json (append)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    analysis_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "response": response,
        "context_size": len(context),
        "extra_context": args.context or None,
    }

    existing = _load_json(OUTPUT_FILE, [])
    if not isinstance(existing, list):
        existing = []

    existing.append(analysis_entry)

    # Keep last 50 analyses
    if len(existing) > 50:
        existing = existing[-50:]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"[Observer] Анализ сохранён: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
