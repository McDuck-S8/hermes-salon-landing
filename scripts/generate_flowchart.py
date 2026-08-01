#!/usr/bin/env python3
"""Generate single Mermaid flowchart with all 50 schemes grouped by flow."""

import re
from pathlib import Path

HERMES = Path("D:/Portable_Soft/hermes")

# Parse all schemes
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
    num = int(title_m.group(1))
    title = title_m.group(2).strip()
    status = status_m.group(1).strip()
    
    # Extract traffic source
    source_m = re.search(r'\*\*Источник трафика:\*\*\s*(.+)', block)
    traffic_source = source_m.group(1).strip() if source_m else ""
    
    # Extract proxy/landing
    proxy_m = re.search(r'\*\*Прокладка:\*\*\s*(.+)', block)
    proxy = proxy_m.group(1).strip() if proxy_m else ""
    
    # Extract offer
    offer_m = re.search(r'\*\*Оффер:\*\*\s*(.+)', block)
    offer = offer_m.group(1).strip() if offer_m else ""
    
    # Extract withdrawal
    withdrawal_m = re.search(r'\*\*Способ вывода:\*\*\s*(.+)', block)
    withdrawal = withdrawal_m.group(1).strip() if withdrawal_m else ""
    
    # Classify status
    u = status.upper()
    if "VERIFIED" in u and "UNVERIFIED" not in u:
        cls = "VERIFIED"
    elif "TESTING" in u:
        cls = "TESTING"
    else:
        cls = "UNVERIFIED"
    
    schemes.append({
        "num": num,
        "title": title,
        "status": status,
        "cls": cls,
        "traffic_source": traffic_source,
        "proxy": proxy,
        "offer": offer,
        "withdrawal": withdrawal,
    })

# Group by traffic source type
source_groups = {}
for s in schemes:
    src = s["traffic_source"]
    # Normalize source name
    if "TG" in src or "Telegram" in src or "TG-канал" in src:
        key = "📱 Telegram Channels"
    elif "YouTube" in src:
        key = "▶️ YouTube Shorts"
    elif "TikTok" in src:
        key = "🎵 TikTok / Reels"
    elif "Pinterest" in src:
        key = "📌 Pinterest"
    elif "Reddit" in src:
        key = "🗣️ Reddit"
    elif "GitHub" in src or "Netlify" in src:
        key = "🌐 SEO Sites (GitHub Pages)"
    elif "Craigslist" in src:
        key = "📋 Craigslist"
    elif "OLX" in src:
        key = "🏪 OLX PL/UA"
    elif "Gumtree" in src:
        key = "🏪 Gumtree UK/AU"
    elif "Locanto" in src:
        key = "🌍 Locanto Global"
    elif "Kijiji" in src:
        key = "🍁 Kijiji CA"
    elif "Avito" in src:
        key = "📦 Авито Услуги"
    elif "Email" in src:
        key = "📧 Email Lead Magnet"
    elif "Kwork" in src or "FL.ru" in src:
        key = "💼 Freelance Marketplaces"
    else:
        key = "🔗 Other"
    
    if key not in source_groups:
        source_groups[key] = []
    source_groups[key].append(s)

# Group proxies by type
proxy_groups = {}
for s in schemes:
    p = s["proxy"]
    if "лендинг" in p.lower() or "landing" in p.lower() or "сайт" in p.lower() or "Taplink" in p:
        key = "🎯 Landing Pages"
    elif "бот" in p.lower() or "Bot" in p or "Telegram" in p:
        key = "🤖 Telegram Bots"
    elif "видео" in p.lower() or "Video" in p or "Short" in p or "CapCut" in p or "FFmpeg" in p:
        key = "🎬 Video Scripts"
    elif "PWA" in p or "PWА" in p:
        key = "📱 PWA Apps"
    elif "прямая" in p.lower() or " диплинк" in p.lower() or "Linktree" in p:
        key = "🔗 Direct Links"
    else:
        key = "📦 Other Proxies"
    
    if key not in proxy_groups:
        proxy_groups[key] = []
    proxy_groups[key].append(s)

# Group offers by network
offer_groups = {}
for s in schemes:
    o = s["offer"]
    if "FinCPA" in o:
        key = "💰 FinCPA Network"
    elif "Admitad" in o:
        key = "🛒 Admitad"
    elif "Travelpayouts" in o:
        key = "✈️ Travelpayouts"
    elif "MaxBounty" in o:
        key = "💵 MaxBounty"
    elif "ClickDealer" in o:
        key = "💵 ClickDealer"
    elif "CPAGrip" in o:
        key = "💵 CPAGrip"
    elif "MyLead" in o:
        key = "💵 MyLead"
    elif "CrakRevenue" in o:
        key = "💘 CrakRevenue"
    elif "AdCombo" in o:
        key = "💊 AdCombo"
    elif "CPAmatica" in o:
        key = "💊 CPAmatica"
    elif "Everad" in o:
        key = "💊 Everad"
    elif "Impact" in o:
        key = "🤝 Impact"
    elif "CJ Affiliate" in o:
        key = "🤝 CJ Affiliate"
    elif "Partnerkin" in o:
        key = "🤝 Partnerkin"
    elif "VPN" in o or "Surfshark" in o or "NordVPN" in o:
        key = "🔒 VPN Offers"
    elif "салон" in o.lower() or "salon" in o.lower():
        key = "💈 Salon Bot (Own Product)"
    else:
        key = "🔗 Other Offers"
    
    if key not in offer_groups:
        offer_groups[key] = []
    offer_groups[key].append(s)

# Group withdrawals
withdrawal_groups = {}
for s in schemes:
    w = s["withdrawal"]
    if "USDT" in w:
        key = "💎 USDT → P2P → Карта"
    elif "WebMoney" in w:
        key = "🌐 WebMoney → Карта"
    elif "Payoneer" in w:
        key = "💳 Payoneer → USDT/P2P"
    elif "Wire" in w:
        key = "🏦 Wire Transfer"
    elif "СБП" in w or "прямой" in w.lower():
        key = "⚡ СБП / Прямой перевод"
    else:
        key = "🔗 Other"
    
    if key not in withdrawal_groups:
        withdrawal_groups[key] = []
    withdrawal_groups[key].append(s)

# Status colors
colors = {
    "UNVERIFIED": "#ff6b6b",
    "TESTING": "#ffd93d",
    "VERIFIED": "#6bcb77",
}

# Build Mermaid flowchart
lines = [
    "```mermaid",
    "flowchart LR",
    "    %% ===== STYLE DEFINITIONS =====",
    "    classDef unverified fill:#ff6b6b,color:#fff,stroke:#c92a2a",
    "    classDef testing fill:#ffd93d,color:#000,stroke:#f08c00",
    "    classDef verified fill:#6bcb77,color:#fff,stroke:#37b24d",
    "    classDef source fill:#1e3a5f,color:#fff,stroke:#4d96ff,stroke-width:2px",
    "    classDef proxy fill:#5f3a1e,color:#fff,stroke:#fab005,stroke-width:2px",
    "    classDef offer fill:#1e4d3a,color:#fff,stroke:#6bcb77,stroke-width:2px",
    "    classDef withdrawal fill:#3a1e4d,color:#fff,stroke:#da77f2,stroke-width:2px",
    "    classDef groupBox fill:#0d1117,color:#8b949e,stroke:#30363d,stroke-dasharray: 5 5",
    "",
    "    %% ===== TRAFFIC SOURCES (LEFT) =====",
]

# Traffic sources subgraphs
source_id = 0
for group_name, group_schemes in source_groups.items():
    source_id += 1
    gid = f"SRC{source_id}"
    lines.append(f"    subgraph {gid}[\"{group_name}\"]")
    lines.append(f"        direction TB")
    for s in group_schemes:
        nid = f"S{s['num']}"
        label = f"{s['title'][:35]}"
        lines.append(f"        {nid}[\"{label}\"] :: {s['cls'].lower()}")
    lines.append(f"    end")
    lines.append(f"    class {gid} groupBox")

# Proxies subgraphs
lines.append("")
lines.append("    %% ===== PROXIES / LAYERS (CENTER) =====")
proxy_id = 0
for group_name, group_schemes in proxy_groups.items():
    proxy_id += 1
    gid = f"PRX{proxy_id}"
    lines.append(f"    subgraph {gid}[\"{group_name}\"]")
    lines.append(f"        direction TB")
    for s in group_schemes:
        nid = f"P{s['num']}"
        label = f"{s['proxy'][:40]}"
        lines.append(f"        {nid}[\"{label}\"] :: {s['cls'].lower()}")
    lines.append(f"    end")
    lines.append(f"    class {gid} groupBox")

# Offers subgraphs
lines.append("")
lines.append("    %% ===== OFFERS (RIGHT) =====")
offer_id = 0
for group_name, group_schemes in offer_groups.items():
    offer_id += 1
    gid = f"OFF{offer_id}"
    lines.append(f"    subgraph {gid}[\"{group_name}\"]")
    lines.append(f"        direction TB")
    for s in group_schemes:
        nid = f"O{s['num']}"
        label = f"{s['offer'][:40]}"
        lines.append(f"        {nid}[\"{label}\"] :: {s['cls'].lower()}")
    lines.append(f"    end")
    lines.append(f"    class {gid} groupBox")

# Withdrawal subgraphs
lines.append("")
lines.append("    %% ===== WITHDRAWAL (BOTTOM) =====")
withdrawal_id = 0
for group_name, group_schemes in withdrawal_groups.items():
    withdrawal_id += 1
    gid = f"WDR{withdrawal_id}"
    lines.append(f"    subgraph {gid}[\"{group_name}\"]")
    lines.append(f"        direction TB")
    for s in group_schemes:
        nid = f"W{s['num']}"
        label = f"{s['withdrawal'][:35]}"
        lines.append(f"        {nid}[\"{label}\"] :: {s['cls'].lower()}")
    lines.append(f"    end")
    lines.append(f"    class {gid} groupBox")

# Connections: Sources -> Proxies -> Offers -> Withdrawal
lines.append("")
lines.append("    %% ===== FLOW CONNECTIONS =====")

# Map each scheme through the flow
for s in schemes:
    snum = s['num']
    cls = s['cls'].lower()
    # Source -> Proxy
    lines.append(f"    S{snum} -->|traffic| P{snum} :: {cls}")
    # Proxy -> Offer
    lines.append(f"    P{snum} -->|leads| O{snum} :: {cls}")
    # Offer -> Withdrawal
    lines.append(f"    O{snum} -->|payout| W{snum} :: {cls}")

# Cross-group summary edges (thicker, summary)
lines.append("")
lines.append("    %% ===== SUMMARY AGGREGATE EDGES =====")

# Count by source group
source_counts = {k: len(v) for k, v in source_groups.items()}
proxy_counts = {k: len(v) for k, v in proxy_groups.items()}
offer_counts = {k: len(v) for k, v in offer_groups.items()}
withdrawal_counts = {k: len(v) for k, v in withdrawal_groups.items()}

# Add summary nodes
lines.append("    %% Source Summary")
src_summary_id = 0
for gname, count in source_counts.items():
    src_summary_id += 1
    nid = f"SRC_SUM{src_summary_id}"
    lines.append(f"    {nid}[\"{gname}\\n{count} schemes\"] :: source")
    # Connect first scheme in group to summary
    first = source_groups[gname][0]
    lines.append(f"    S{first['num']} -.-> {nid}")

lines.append("")
lines.append("    %% Proxy Summary")
prx_summary_id = 0
for gname, count in proxy_counts.items():
    prx_summary_id += 1
    nid = f"PRX_SUM{prx_summary_id}"
    lines.append(f"    {nid}[\"{gname}\\n{count} schemes\"] :: proxy")
    first = proxy_groups[gname][0]
    lines.append(f"    P{first['num']} -.-> {nid}")

lines.append("")
lines.append("    %% Offer Summary")
off_summary_id = 0
for gname, count in offer_counts.items():
    off_summary_id += 1
    nid = f"OFF_SUM{off_summary_id}"
    lines.append(f"    {nid}[\"{gname}\\n{count} schemes\"] :: offer")
    first = offer_groups[gname][0]
    lines.append(f"    O{first['num']} -.-> {nid}")

lines.append("")
lines.append("    %% Withdrawal Summary")
wdr_summary_id = 0
for gname, count in withdrawal_counts.items():
    wdr_summary_id += 1
    nid = f"WDR_SUM{wdr_summary_id}"
    lines.append(f"    {nid}[\"{gname}\\n{count} schemes\"] :: withdrawal")
    first = withdrawal_groups[gname][0]
    lines.append(f"    W{first['num']} -.-> {nid}")

# Main aggregate flow
lines.append("")
lines.append("    %% MAIN PIPELINE FLOW")
lines.append("    SRC_MAIN[\"📥 ALL TRAFFIC SOURCES\\n50 schemes\"] :: source")
lines.append("    PRX_MAIN[\"⚙️ ALL PROXIES / LAYERS\\nLanding + Bot + Video + Direct\"] :: proxy")
lines.append("    OFF_MAIN[\"💰 ALL OFFERS / NETWORKS\\nFinCPA, Admitad, Travelpayouts, MaxBounty, VPN, Own\"] :: offer")
lines.append("    WDR_MAIN[\"💸 ALL WITHDRAWAL PATHS\\nUSDT→P2P, WebMoney, Payoneer, Wire, СБП\"] :: withdrawal")
lines.append("")
lines.append("    SRC_MAIN -->|50 schemes traffic| PRX_MAIN")
lines.append("    PRX_MAIN -->|leads/conversions| OFF_MAIN")
lines.append("    OFF_MAIN -->|payouts| WDR_MAIN")

# Status legend
lines.append("")
lines.append("    %% ===== LEGEND =====")
lines.append("    LEG_UNV[\"🔴 UNVERIFIED (47)\"] :: unverified")
lines.append("    LEG_TST[\"🟡 TESTING (2)\"] :: testing")
lines.append("    LEG_VER[\"🟢 VERIFIED (1)\"] :: verified")
lines.append("    style LEG_UNV fill:#ff6b6b,color:#fff")
lines.append("    style LEG_TST fill:#ffd93d,color:#000")
lines.append("    style LEG_VER fill:#6bcb77,color:#fff")

lines.append("```")

output = "\n".join(lines)
out_path = HERMES / "reports" / "income_pipeline_flowchart.md"
out_path.write_text(output, encoding="utf-8")
print(f"Flowchart: {out_path}")
print("Open in VS Code (Ctrl+Shift+V) or GitHub to view rendered diagram")