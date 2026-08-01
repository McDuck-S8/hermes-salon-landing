#!/usr/bin/env python3
"""Generate standalone HTML dashboard with Chart.js for income pipeline."""

import re
import json
from collections import Counter
from pathlib import Path

HERMES = Path("D:/Portable_Soft/hermes")

def parse_bonds():
    text = (HERMES / "ARBITRAGE_BONDS.md").read_text(encoding="utf-8")
    schemes_raw = re.split(r'(?=^## СВЯЗКА)', text, flags=re.MULTILINE)
    schemes = []
    for block in schemes_raw:
        if not block.strip() or "Статус:" not in block:
            continue
        title_m = re.search(r'^## СВЯЗКА #(\d+):\s*(.+)', block, re.MULTILINE)
        status_m = re.search(r'\*\*Статус:\*\*\s*(.+)', block)
        if not title_m or not status_m:
            continue
        title = f"СВЯЗКА #{title_m.group(1)}: {title_m.group(2).strip()}"
        status = status_m.group(1).strip()
        desc = block[:2000]
        dl = desc.lower()
        blockers = []
        if "landing page" in dl or "сайт" in dl or "лендинг" in dl:
            blockers.append("LANDING_PAGE")
        if "video" in dl or "видео" in dl or "short" in dl:
            blockers.append("VIDEO_SCRIPT")
        if "bot" in dl or "telegram" in dl or "бот" in dl:
            blockers.append("BOT")
        if "account" in dl or "регистрация" in dl or "kvv" in dl or "кошел" in dl:
            blockers.append("MANUAL_ACCOUNT")
        if "api" in dl or "ключ" in dl:
            blockers.append("API_KEY")
        if "бюджет" in dl or "деньги" in dl or "$" in desc:
            blockers.append("AD_BUDGET")
        code_fixable = any(b in ("LANDING_PAGE", "VIDEO_SCRIPT", "BOT") for b in blockers)
        schemes.append({
            "title": title,
            "status": status,
            "blockers": blockers,
            "code_fixable": code_fixable,
        })
    return schemes

def classify_status(status: str) -> str:
    u = status.upper()
    if "VERIFIED" in u and "UNVERIFIED" not in u:
        return "VERIFIED"
    if "TESTING" in u:
        return "TESTING"
    if "UNVERIFIED" in u:
        return "UNVERIFIED"
    return "OTHER"

schemes = parse_bonds()
total = len(schemes)
unverified = [s for s in schemes if classify_status(s["status"]) == "UNVERIFIED"]
testing = [s for s in schemes if classify_status(s["status"]) == "TESTING"]
verified = [s for s in schemes if classify_status(s["status"]) == "VERIFIED"]
code_fixable = [s for s in unverified if s["code_fixable"]]

blocker_counts = Counter()
for s in unverified:
    for b in s["blockers"]:
        blocker_counts[b] += 1

# Top 10 code-unblockable schemes for table
top10 = code_fixable[:10]

# Blockers label map
blocker_labels = {
    "LANDING_PAGE": "Landing Page",
    "VIDEO_SCRIPT": "Video Script",
    "BOT": "Telegram Bot",
    "MANUAL_ACCOUNT": "Manual Account",
    "API_KEY": "API Key",
    "AD_BUDGET": "Ad Budget",
}

# Status colors
status_colors = {
    "UNVERIFIED": "#ff6b6b",
    "TESTING": "#ffd93d",
    "VERIFIED": "#6bcb77",
    "CODE_UNBLOCKABLE": "#4d96ff",
}

# Prepare data for Chart.js
pie_data = {
    "labels": [
        f"UNVERIFIED ({len(unverified)})",
        f"TESTING ({len(testing)})",
        f"VERIFIED ({len(verified)})",
        f"Code-unblockable ({len(code_fixable)})"
    ],
    "values": [len(unverified), len(testing), len(verified), len(code_fixable)],
    "colors": [
        status_colors["UNVERIFIED"],
        status_colors["TESTING"],
        status_colors["VERIFIED"],
        status_colors["CODE_UNBLOCKABLE"],
    ]
}

bar_data = {
    "labels": [blocker_labels.get(b, b) for b, _ in blocker_counts.most_common()],
    "values": [c for _, c in blocker_counts.most_common()],
    "colors": [
        status_colors["CODE_UNBLOCKABLE"] if b in ("LANDING_PAGE", "VIDEO_SCRIPT", "BOT") else "#999"
        for b, _ in blocker_counts.most_common()
    ]
}

# Table rows
table_rows = []
for i, s in enumerate(top10, 1):
    blockers_str = ", ".join(blocker_labels.get(b, b) for b in s["blockers"])
    unblock = []
    if "LANDING_PAGE" in s["blockers"]:
        unblock.append("landing_generator.py")
    if "VIDEO_SCRIPT" in s["blockers"]:
        unblock.append("video_scripts.py")
    if "BOT" in s["blockers"]:
        unblock.append("cpa_bot_generator.py")
    unblock_str = ", ".join(unblock) if unblock else "—"
    action = "Deploy → TESTING" if s["code_fixable"] else "Manual steps needed"
    status_cls = classify_status(s["status"])
    table_rows.append({
        "num": i,
        "title": s["title"].replace("СВЯЗКА #", "").replace(":", ""),
        "status": status_cls,
        "blockers": blockers_str or "—",
        "unblock": unblock_str,
        "action": action,
    })

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Income Pipeline Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #e6edf3; min-height: 100vh; padding: 20px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ font-size: 1.8rem; margin-bottom: 8px; color: #fff; }}
    .subtitle {{ color: #8b949e; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }}
    .card h2 {{ font-size: 1.1rem; margin-bottom: 16px; color: #fff; display: flex; align-items: center; gap: 8px; }}
    .chart-wrap {{ position: relative; height: 300px; }}
    .table-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #30363d; }}
    th {{ color: #8b949e; font-weight: 600; background: #0d1117; position: sticky; top: 0; }}
    tr:hover {{ background: #1f2428; }}
    .status-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }}
    .status-unverified {{ background: #ff6b6b; color: #fff; }}
    .status-testing {{ background: #ffd93d; color: #000; }}
    .status-verified {{ background: #6bcb77; color: #fff; }}
    .refresh-btn {{ background: #238636; color: #fff; border: none; padding: 10px 20px; border-radius: 6px; font-size: 0.9rem; cursor: pointer; transition: background 0.2s; margin-bottom: 20px; }}
    .refresh-btn:hover {{ background: #2ea043; }}
    .refresh-btn:disabled {{ background: #30363d; color: #8b949e; cursor: not-allowed; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; font-size: 0.8rem; }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; }}
    .legend-color {{ width: 12px; height: 12px; border-radius: 3px; }}
    .code-unblockable-badge {{ background: #4d96ff; color: #fff; padding: 2px 6px; border-radius: 3px; font-size: 0.7rem; }}
    @media (max-width: 768px) {{
        .grid {{ grid-template-columns: 1fr; }}
        .chart-wrap {{ height: 250px; }}
    }}
</style>
</head>
<body>
<div class="container">
    <h1>📊 Income Pipeline Dashboard</h1>
    <p class="subtitle">50 схем арбитража • Автообновление: запустите <code>python scripts/generate_dashboard.py</code></p>
    
    <button class="refresh-btn" id="refreshBtn" onclick="location.reload()">🔄 Обновить данные</button>

    <div class="grid">
        <div class="card">
            <h2>📈 Статусы схем</h2>
            <div class="chart-wrap">
                <canvas id="pieChart"></canvas>
            </div>
            <div class="legend">
                <span class="legend-item"><span class="legend-color" style="background:{status_colors['UNVERIFIED']}"></span>UNVERIFIED ({len(unverified)})</span>
                <span class="legend-item"><span class="legend-color" style="background:{status_colors['TESTING']}"></span>TESTING ({len(testing)})</span>
                <span class="legend-item"><span class="legend-color" style="background:{status_colors['VERIFIED']}"></span>VERIFIED ({len(verified)})</span>
                <span class="legend-item"><span class="legend-color" style="background:{status_colors['CODE_UNBLOCKABLE']}"></span>Code-unblockable ({len(code_fixable)})</span>
            </div>
        </div>

        <div class="card">
            <h2>🧱 Блокеры (UNVERIFIED)</h2>
            <div class="chart-wrap">
                <canvas id="barChart"></canvas>
            </div>
            <div class="legend">
                <span class="legend-item"><span class="legend-color" style="background:{status_colors['CODE_UNBLOCKABLE']}"></span>Code-fixable</span>
                <span class="legend-item"><span class="legend-color" style="background:#999"></span>Требует пользователя</span>
            </div>
        </div>
    </div>

    <div class="table-card">
        <h2>🚀 Топ-10 готовых к запуску (Code-unblockable)</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Схема</th>
                    <th>Статус</th>
                    <th>Блокеры</th>
                    <th>Что разблокирует код</th>
                    <th>Действие</th>
                </tr>
            </thead>
            <tbody>
"""

for row in table_rows:
    status_cls = row["status"].lower()
    html += f"""                <tr>
                    <td>{row["num"]}</td>
                    <td>{row["title"]}</td>
                    <td><span class="status-badge status-{status_cls}">{row["status"]}</span></td>
                    <td>{row["blockers"]}</td>
                    <td>{row["unblock"]}</td>
                    <td>{row["action"]}</td>
                </tr>
"""

html += f"""            </tbody>
        </table>
    </div>

    <div style="text-align: center; color: #8b949e; font-size: 0.85rem; margin-top: 20px;">
        Данные из <code>ARBITRAGE_BONDS.md</code> • Сгенерировано: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>

<script>
const pieData = {json.dumps(pie_data)};
const barData = {json.dumps(bar_data)};

// Pie Chart
new Chart(document.getElementById('pieChart'), {{
    type: 'pie',
    data: {{
        labels: pieData.labels,
        datasets: [{{
            data: pieData.values,
            backgroundColor: pieData.colors,
            borderWidth: 2,
            borderColor: '#0d1117'
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{
                callbacks: {{
                    label: function(ctx) {{
                        const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        const pct = ((ctx.raw / total) * 100).toFixed(1);
                        return `${{ctx.label}}: ${{ctx.raw}} (${{pct}}%)`;
                    }}
                }}
            }}
        }}
    }}
}});

// Bar Chart
new Chart(document.getElementById('barChart'), {{
    type: 'bar',
    data: {{
        labels: barData.labels,
        datasets: [{{
            label: 'Количество схем',
            data: barData.values,
            backgroundColor: barData.colors,
            borderRadius: 6,
            borderSkipped: false,
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{
                callbacks: {{
                    label: function(ctx) {{
                        return `Схем: ${{ctx.raw}}`;
                    }}
                }}
            }}
        }},
        scales: {{
            x: {{
                beginAtZero: true,
                grid: {{ color: '#30363d' }},
                ticks: {{ color: '#8b949e' }}
            }},
            y: {{
                grid: {{ display: false }},
                ticks: {{ color: '#e6edf3' }}
            }}
        }}
    }}
}});

// Keyboard shortcut: R to refresh
document.addEventListener('keydown', (e) => {{
    if (e.key === 'r' || e.key === 'R') location.reload();
}});
</script>
</body>
</html>
"""

output_path = HERMES / "reports" / "income_pipeline_dashboard.html"
output_path.write_text(html, encoding="utf-8")
print(f"Dashboard: {output_path}")
print(f"Open in browser: file://{output_path.absolute().as_posix()}")