"""
Daily Knowledge Report — читает Knowledge Cube напрямую и сохраняет отчёт.

Собирает статистику: количество записей, свежие инсайты, белые пятна.
Сохраняет в cron/output/reports/knowledge_$(date +%Y-%m-%d).md
"""

import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path


def get_hermes_home():
    """Определяем HERMES_HOME."""
    env_home = os.environ.get("HERMES_HOME", "")
    if env_home and Path(env_home).exists():
        return Path(env_home)
    candidates = [
        Path("D:/Portable_Soft/hermes"),
        Path.home() / ".hermes",
        Path.cwd(),
    ]
    for c in candidates:
        if (c / "cache" / "knowledge_cube.db").exists():
            return c
    return Path("D:/Portable_Soft/hermes")


def query_cube(db_path: Path) -> dict:
    """Query Knowledge Cube for stats and recent entries."""
    if not db_path.exists():
        return {"error": "Knowledge Cube DB not found"}

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    result = {}

    # Total entries (kc_entries or experiences)
    for tbl in ["kc_entries", "experiences"]:
        try:
            cur.execute(f"SELECT COUNT(*) as total FROM {tbl}")
            row = cur.fetchone()
            result[f"{tbl}_total"] = row["total"] if row else 0
        except sqlite3.OperationalError:
            result[f"{tbl}_total"] = 0

    # kc_entries by category
    try:
        cur.execute("SELECT category, COUNT(*) as cnt FROM kc_entries WHERE category != '' GROUP BY category ORDER BY cnt DESC LIMIT 15")
        result["categories"] = [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        result["categories"] = []

    # kc_entries by source
    try:
        cur.execute("SELECT source, COUNT(*) as cnt FROM kc_entries WHERE source != '' GROUP BY source ORDER BY cnt DESC LIMIT 10")
        result["sources"] = [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        result["sources"] = []

    # Recent experiences (last 30 days)
    try:
        cur.execute("""
            SELECT content, substr(raw_text, 1, 200) as preview, ts
            FROM experiences
            WHERE ts >= date('now', '-30 days')
            ORDER BY ts DESC
            LIMIT 10
        """)
        result["recent"] = [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        result["recent"] = []

    # White spots (clusters)
    try:
        cur.execute("""
            SELECT cluster_id, proposed_dimension, representative_text
            FROM white_spot_clusters
            WHERE status != 'resolved'
            ORDER BY size DESC
            LIMIT 10
        """)
        result["white_spots"] = [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        result["white_spots"] = []

    conn.close()
    return result


def main():
    hermes_home = get_hermes_home()
    today = datetime.now().strftime("%Y-%m-%d")
    db_path = hermes_home / "cache" / "knowledge_cube.db"
    report_path = hermes_home / "cron" / "output" / "reports" / f"knowledge_{today}.md"

    report_path.parent.mkdir(parents=True, exist_ok=True)

    data = query_cube(db_path)

    lines = []
    lines.append(f"# 📅 Знаниевый отчёт — {today}")
    lines.append("")
    lines.append(f"*Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    if "error" in data:
        lines.append(f"_Ошибка: {data['error']}_")
        lines.append("")
        lines.append("Проверь: существует ли Knowledge Cube (cache/knowledge_cube.db)")
    else:
        kc_total = data.get('kc_entries_total', 0)
        exp_total = data.get('experiences_total', 0)
        lines.append(f"**Knowledge Cube:** {kc_total} записей, {exp_total} опытов")
        lines.append("")

        # Categories
        if data.get("categories"):
            lines.append("### Распределение по категориям")
            lines.append("")
            lines.append("| Категория | Записей |")
            lines.append("|----------|--------:|")
            for d in data["categories"][:10]:
                lines.append(f"| {d['category']} | {d['cnt']} |")
            lines.append("")

        # Sources
        if data.get("sources"):
            lines.append("### Источники")
            lines.append("")
            for s in data["sources"][:5]:
                lines.append(f"- {s['source']}: {s['cnt']} записей")
            lines.append("")

        # Recent entries
        if data.get("recent"):
            lines.append("### Свежие записи (последние 30 дней)")
            lines.append("")
            for e in data["recent"]:
                preview = (e.get("preview", "") or "")[:120]
                ts = e.get("ts", "")
                lines.append(f"- [{ts}] {preview}")
            lines.append("")

        # White spots
        if data.get("white_spots"):
            lines.append("### Белые пятна (нераспознанные кластеры)")
            lines.append("")
            for w in data["white_spots"]:
                spot_text = (w.get("representative_text", "") or "")[:80]
                dim = w.get("proposed_dimension", "?")
                lines.append(f"- {dim}: {spot_text}")
            lines.append("")

    lines.append("---")
    lines.append(f"*Hermes Agent — Daily Knowledge Report*")

    report_content = "\n".join(lines)
    report_path.write_text(report_content, encoding="utf-8")
    print(str(report_path))


if __name__ == "__main__":
    main()
