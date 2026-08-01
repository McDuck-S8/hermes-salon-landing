#!/usr/bin/env python3
"""
Proactive Engine — анализирует систему и предлагает новые направления развития.


> Revisit: when knowledge gap analysis, performance trend detection, or suggestion generation changes. Last touched: 2026-07-02.
Использует:
- session_recall для поиска прошлого опыта
- knowledge_cube для анализа пробелов
- autonomous_agent для оценки приоритетов

Использование:
    python proactive_engine.py                  # полный анализ
    python proactive_engine.py --trends         # тренды и возможности
    python proactive_engine.py --gaps           # пробелы в знаниях
    python proactive_engine.py --opportunities  # конкретные предложения
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# Use unified config — single source of truth for paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hermes_config import HERMES_HOME, CACHE_DIR, STATE_DB

KC_DB = CACHE_DIR / "knowledge_cube.db"
OUTPUT = CACHE_DIR / "proactive_analysis.json"


def analyze_knowledge_gaps() -> List[Dict]:
    """Анализирует пробелы в базе знаний."""
    gaps = []
    
    if not KC_DB.exists():
        return gaps
    
    conn = sqlite3.connect(str(KC_DB))
    cur = conn.cursor()
    
    try:
        # Проверяем какие домены есть
        cur.execute("SELECT axis_domain, COUNT(*) FROM experiences GROUP BY axis_domain")
        domains = {row[0]: row[1] for row in cur.fetchall()}
        
        # Определяем ожидаемые домены
        expected_domains = [
            "web", "file", "terminal", "coding", "browser",
            "search", "memory", "todo", "cronjob", "delegation"
        ]
        
        for domain in expected_domains:
            if domain not in domains or domains[domain] < 5:
                gaps.append({
                    "type": "knowledge_gap",
                    "domain": domain,
                    "current_count": domains.get(domain, 0),
                    "recommended_min": 10,
                    "priority": "high" if domains.get(domain, 0) == 0 else "medium"
                })
        
        # Проверяем сущности (объекты, концепции) — используем tags
        cur.execute("SELECT tags, COUNT(*) FROM experiences WHERE tags IS NOT NULL GROUP BY tags ORDER BY COUNT(*) DESC LIMIT 20")
        entities = cur.fetchall()
        
        # Ищем редкие сущности
        for entity, count in entities:
            if count < 3 and entity:
                gaps.append({
                    "type": "entity_gap",
                    "entity": entity,
                    "count": count,
                    "priority": "low"
                })
        
    except Exception as e:
        print(f"KC analysis error: {e}", file=sys.stderr)
    finally:
        conn.close()
    
    return gaps


def analyze_performance_trends() -> List[Dict]:
    """Анализирует тренды производительности."""
    trends = []
    
    # Анализируем state.db
    if STATE_DB.exists():
        conn = sqlite3.connect(str(STATE_DB))
        cur = conn.cursor()
        
        try:
            # Количество сообщений за последние дни
            week_ago = (datetime.now() - timedelta(days=7)).timestamp()
            cur.execute("SELECT COUNT(*) FROM messages WHERE timestamp > ?", (week_ago,))
            recent_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM messages")
            total_count = cur.fetchone()[0]
            
            # Активность
            daily_avg = recent_count / 7
            trends.append({
                "type": "activity",
                "metric": "daily_messages",
                "value": round(daily_avg, 1),
                "total": total_count,
                "trend": "increasing" if daily_avg > 100 else "stable"
            })
            
            # Сессии
            cur.execute("SELECT COUNT(DISTINCT session_id) FROM messages WHERE timestamp > ?", (week_ago,))
            recent_sessions = cur.fetchone()[0]
            
            trends.append({
                "type": "sessions",
                "metric": "weekly_sessions",
                "value": recent_sessions,
                "trend": "active" if recent_sessions > 10 else "low"
            })
            
        except Exception as e:
            print(f"State DB analysis error: {e}", file=sys.stderr)
        finally:
            conn.close()
    
    return trends


def suggest_new_directions(gaps: List[Dict], trends: List[Dict]) -> List[Dict]:
    """Предлагает новые направления развития."""
    suggestions = []
    
    # На основе пробелов в знаниях
    high_priority_gaps = [g for g in gaps if g["priority"] == "high"]
    if high_priority_gaps:
        suggestions.append({
            "type": "knowledge_expansion",
            "title": "Расширить базу знаний",
            "description": f"Обнаружено {len(high_priority_gaps)} критических пробелов",
            "actions": [f"Изучить домен {g['domain']}" for g in high_priority_gaps[:3]],
            "priority": "high"
        })
    
    # На основе трендов
    activity_trend = next((t for t in trends if t["metric"] == "daily_messages"), None)
    if activity_trend and activity_trend["value"] < 50:
        suggestions.append({
            "type": "engagement",
            "title": "Увеличить активность",
            "description": f"Средняя активность: {activity_trend['value']} сообщений/день",
            "actions": [
                "Автоматизировать рутинные задачи",
                "Добавить proactive мониторинг",
                "Создать автоматические отчёты"
            ],
            "priority": "medium"
        })
    
    # Проактивные возможности
    suggestions.append({
        "type": "proactive_opportunity",
        "title": "Автоматизация мониторинга",
        "description": "Система может сама отслеживать проблемы и исправлять их",
        "actions": [
            "Настроить event-driven мониторинг",
            "Автоматическое исправление типичных ошибок",
            "Предиктивный анализ проблем"
        ],
        "priority": "medium"
    })
    
    # Новые направления
    suggestions.append({
        "type": "new_direction",
        "title": "Интеграция с внешними сервисами",
        "description": "Расширить возможности через API",
        "actions": [
            "Интеграция с GitHub (автоматические PR обзоры)",
            "Мониторинг RSS/Telegram каналов",
            "Автоматические отчёты в Telegram"
        ],
        "priority": "low"
    })
    
    return suggestions


def generate_proactive_report(gaps, trends, suggestions) -> Dict:
    """Генерирует отчёт."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "knowledge_gaps": {
            "total": len(gaps),
            "high_priority": len([g for g in gaps if g["priority"] == "high"]),
            "items": gaps[:10]
        },
        "performance_trends": trends,
        "suggestions": {
            "total": len(suggestions),
            "by_priority": {
                "high": len([s for s in suggestions if s["priority"] == "high"]),
                "medium": len([s for s in suggestions if s["priority"] == "medium"]),
                "low": len([s for s in suggestions if s["priority"] == "low"])
            },
            "items": suggestions
        }
    }
    
    return report


def main():
    args = sys.argv[1:]
    
    print(f"[{datetime.now().isoformat()}] Proactive Engine starting...")
    
    # Анализ
    gaps = analyze_knowledge_gaps()
    print(f"  Knowledge gaps: {len(gaps)}")
    
    trends = analyze_performance_trends()
    print(f"  Performance trends: {len(trends)}")
    
    suggestions = suggest_new_directions(gaps, trends)
    print(f"  Suggestions: {len(suggestions)}")
    
    # Отчёт
    report = generate_proactive_report(gaps, trends, suggestions)
    
    # Сохраняем
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  Report saved to {OUTPUT}")
    
    # Вывод
    if "--json" in args:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n=== Proactive Analysis ===")
        print(f"  Knowledge gaps: {report['knowledge_gaps']['total']} "
              f"({report['knowledge_gaps']['high_priority']} high)")
        print(f"  Suggestions: {report['suggestions']['total']}")
        for s in suggestions:
            print(f"    [{s['priority'].upper()}] {s['title']}")
            print(f"      {s['description']}")


if __name__ == "__main__":
    main()
