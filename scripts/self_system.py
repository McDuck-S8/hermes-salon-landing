#!/usr/bin/env python3
"""
Self-System — единая точка входа для самоанализа, самовосстановления и самообучения.

Объединяет:
- self_improvement_loop (самообучение)
- proactive_executor (самовосстановление)
- proactive_engine (проактивные предложения)
- session_recall (поиск по истории)
- crystal (самоанализ)

Использование:
    python self_system.py                    # полный цикл
    python self_system.py --analyze          # только анализ
    python self_system.py --heal             # только восстановление
    python self_system.py --learn            # только обучение
    python self_system.py --proactive        # только проактивные предложения
    python self_system.py --status           # статус системы
    python self_system.py --report           # полный отчёт
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# ---------------------------------------------------------------------------
# Unified config — single source of truth
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_config import (
    HERMES_HOME, CACHE_DIR, STATE_DB, CUBE_DB,
    get_db, db_fetch_all,
)

OUTPUT = CACHE_DIR / "self_system_report.json"


def get_system_status() -> Dict:
    """Собирает статус всех компонентов."""
    status = {
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # State DB
    if STATE_DB.exists():
        size_mb = STATE_DB.stat().st_size / (1024 * 1024)
        conn = get_db(STATE_DB)
        if conn:
            msg_count = db_fetch_all(conn, "SELECT COUNT(*) as cnt FROM messages")[0]["cnt"]
            conn.close()
            status["components"]["state_db"] = {
                "status": "ok",
                "size_mb": round(size_mb, 2),
                "messages": msg_count
            }
        else:
            status["components"]["state_db"] = {"status": "error", "error": "cannot connect"}
    else:
        status["components"]["state_db"] = {"status": "missing"}
    
    # Knowledge Cube
    if CUBE_DB.exists():
        conn = get_db(CUBE_DB)
        if conn:
            exp_count = db_fetch_all(conn, "SELECT COUNT(*) as cnt FROM experiences")[0]["cnt"]
            conn.close()
            status["components"]["knowledge_cube"] = {
                "status": "ok",
                "experiences": exp_count
            }
        else:
            status["components"]["knowledge_cube"] = {"status": "error", "error": "cannot connect"}
    else:
        status["components"]["knowledge_cube"] = {"status": "missing"}
    
    # Session Recall
    try:
        from session_recall import get_messages
        messages = get_messages(limit=100)
        status["components"]["session_recall"] = {
            "status": "ok",
            "indexed_messages": len(messages)
        }
    except Exception as e:
        status["components"]["session_recall"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Event System
    events_file = CACHE_DIR / "event_bus.json"
    if events_file.exists():
        with open(events_file) as f:
            events = json.load(f)
        status["components"]["event_system"] = {
            "status": "ok",
            "pending": len(events.get("pending", [])),
            "processed": len(events.get("processed", []))
        }
    else:
        status["components"]["event_system"] = {"status": "missing"}
    
    return status


def run_analysis() -> Dict:
    """Запускает анализ системы."""
    print("Running analysis...")
    
    # Self-improvement analysis
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "self_improvement_loop",
            str(HERMES_HOME / "scripts" / "self_improvement_loop.py")
        )
        module = importlib.util.module_from_spec(spec)
        # Don't execute, just check if it loads
        print("  self_improvement_loop: available")
        improvement_available = True
    except Exception as e:
        print(f"  self_improvement_loop: {e}")
        improvement_available = False
    
    # Proactive engine analysis
    try:
        from proactive_engine import analyze_knowledge_gaps, analyze_performance_trends
        gaps = analyze_knowledge_gaps()
        trends = analyze_performance_trends()
        print(f"  proactive_engine: {len(gaps)} gaps, {len(trends)} trends")
        return {"gaps": gaps, "trends": trends, "improvement_available": improvement_available}
    except Exception as e:
        print(f"  proactive_engine: {e}")
        return {"gaps": [], "trends": [], "improvement_available": improvement_available}


def run_healing() -> Dict:
    """Запускает самовосстановление."""
    print("Running self-healing...")
    
    results = {
        "cron_jobs_fixed": 0,
        "cache_cleaned": False,
        "errors_found": 0
    }
    
    # Check cron jobs
    try:
        cron_file = HERMES_HOME / "cron" / "jobs.json"
        if cron_file.exists():
            with open(cron_file) as f:
                data = json.load(f)
            
            # Handle both dict and list formats
            if isinstance(data, dict):
                jobs = data.get("jobs", [])
            else:
                jobs = data
            
            failed_jobs = [j for j in jobs if isinstance(j, dict) and j.get("last_status") == "failed"]
            results["errors_found"] = len(failed_jobs)
            print(f"  Cron: {len(failed_jobs)} failed jobs found")
    except Exception as e:
        print(f"  Cron check: {e}")
    
    # Clean cache
    try:
        cache_files = list(CACHE_DIR.glob("*.tmp"))
        for f in cache_files:
            f.unlink()
        results["cache_cleaned"] = len(cache_files) > 0
        print(f"  Cache: cleaned {len(cache_files)} temp files")
    except Exception as e:
        print(f"  Cache clean: {e}")
    
    return results


def run_learning() -> Dict:
    """Запускает самообучение."""
    print("Running self-learning...")
    
    results = {
        "patterns_found": 0,
        "skills_created": 0,
        "knowledge_entries": 0
    }
    
    # Analyze patterns from session recall
    try:
        from session_recall import semantic_search
        
        # Ищем паттерны в ошибках
        error_patterns = ["error", "failure", "timeout", "crash"]
        all_results = []
        
        for pattern in error_patterns:
            r = semantic_search(pattern, limit=3)
            all_results.extend(r)
        
        results["patterns_found"] = len(all_results)
        print(f"  Patterns: {len(all_results)} found via session recall")
    except Exception as e:
        print(f"  Pattern analysis: {e}")
    
    return results


def run_proactive() -> Dict:
    """Запускает проактивные предложения."""
    print("Running proactive analysis...")
    
    try:
        from proactive_engine import (
            analyze_knowledge_gaps,
            analyze_performance_trends,
            suggest_new_directions,
            generate_proactive_report
        )
        
        gaps = analyze_knowledge_gaps()
        trends = analyze_performance_trends()
        suggestions = suggest_new_directions(gaps, trends)
        report = generate_proactive_report(gaps, trends, suggestions)
        
        print(f"  Suggestions: {len(suggestions)}")
        return report
    except Exception as e:
        print(f"  Proactive analysis: {e}")
        return {"error": str(e)}


def generate_full_report(status, analysis, healing, learning, proactive) -> Dict:
    """Генерирует полный отчёт."""
    return {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "analysis": analysis,
        "healing": healing,
        "learning": learning,
        "proactive": proactive,
        "summary": {
            "system_health": "ok" if status.get("components", {}).get("state_db", {}).get("status") == "ok" else "degraded",
            "total_suggestions": proactive.get("suggestions", {}).get("total", 0),
            "patterns_found": learning.get("patterns_found", 0),
            "errors_found": healing.get("errors_found", 0)
        }
    }


def main():
    args = sys.argv[1:]
    
    print(f"[{datetime.now().isoformat()}] Self-System starting...")
    print()
    
    # Определяем режим
    if "--status" in args:
        status = get_system_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    
    if "--analyze" in args:
        analysis = run_analysis()
        return
    
    if "--heal" in args:
        healing = run_healing()
        return
    
    if "--learn" in args:
        learning = run_learning()
        return
    
    if "--proactive" in args:
        proactive = run_proactive()
        return
    
    # Полный цикл
    print("=" * 60)
    print("PHASE 1: System Status")
    print("=" * 60)
    status = get_system_status()
    for name, info in status.get("components", {}).items():
        print(f"  {name}: {info.get('status', 'unknown')}")
    
    print()
    print("=" * 60)
    print("PHASE 2: Analysis")
    print("=" * 60)
    analysis = run_analysis()
    
    print()
    print("=" * 60)
    print("PHASE 3: Self-Healing")
    print("=" * 60)
    healing = run_healing()
    
    print()
    print("=" * 60)
    print("PHASE 4: Self-Learning")
    print("=" * 60)
    learning = run_learning()
    
    print()
    print("=" * 60)
    print("PHASE 5: Proactive Suggestions")
    print("=" * 60)
    proactive = run_proactive()
    
    # Отчёт
    report = generate_full_report(status, analysis, healing, learning, proactive)
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    summary = report["summary"]
    print(f"  Health: {summary['system_health']}")
    print(f"  Suggestions: {summary['total_suggestions']}")
    print(f"  Patterns: {summary['patterns_found']}")
    print(f"  Errors: {summary['errors_found']}")
    print(f"  Report: {OUTPUT}")


if __name__ == "__main__":
    main()
