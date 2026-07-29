#!/usr/bin/env python3
"""Income Pipeline Status Report -- what schemes are ready, what blocks, next step."""

import re
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

        blockers = []
        dl = desc.lower()
        blockers.append(("LANDING_PAGE", "landing page" in dl or "сайт" in dl or "лендинг" in dl))
        blockers.append(("VIDEO_SCRIPT", "video" in dl or "видео" in dl or "short" in dl))
        blockers.append(("BOT", "bot" in dl or "telegram" in dl or "бот" in dl))
        blockers.append(("MANUAL_ACCOUNT", "account" in dl or "регистрация" in dl or "kvv" in dl or "кошел" in dl))
        blockers.append(("API_KEY", "api" in dl or "ключ" in dl))
        blockers.append(("AD_BUDGET", "бюджет" in dl or "деньги" in dl or "$" in desc))

        code_fixable = any(b[0] in ("LANDING_PAGE", "VIDEO_SCRIPT", "BOT") for b in blockers if b[1])

        schemes.append({
            "title": title,
            "status": status,
            "blockers": [b[0] for b in blockers if b[1]],
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


def main():
    schemes = parse_bonds()

    by_status = Counter(classify_status(s["status"]) for s in schemes)

    total = len(schemes)
    unverified = [s for s in schemes if classify_status(s["status"]) == "UNVERIFIED"]
    testing = [s for s in schemes if classify_status(s["status"]) == "TESTING"]
    verified = [s for s in schemes if classify_status(s["status"]) == "VERIFIED"]
    code_fixable = [s for s in unverified if s["code_fixable"]]

    blocker_counts = Counter()
    for s in unverified:
        for b in s["blockers"]:
            blocker_counts[b] += 1

    lines = []
    lines.append("# Income Pipeline Status Report")
    lines.append("*Generated: autonomous scan*\n")
    lines.append("## Summary")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total schemes | {total} |")
    lines.append(f"| UNVERIFIED | {len(unverified)} |")
    lines.append(f"| TESTING | {len(testing)} |")
    lines.append(f"| VERIFIED | {len(verified)} |")
    lines.append(f"| Code-unblockable | {len(code_fixable)} |")
    lines.append("")

    lines.append("## Blocker Distribution (UNVERIFIED schemes)")
    lines.append("| Blocker Type | Count | Code-Fixable? |")
    lines.append("|-------------|-------|--------------|")
    blocker_type_map = {
        "VIDEO_SCRIPT": "Video content generation |  Yes (Python script)",
        "LANDING_PAGE": "Landing page |  Yes (HTML generator)",
        "BOT": "Telegram bot |  Yes (aiogram script)",
        "MANUAL_ACCOUNT": "Manual account registration |  User action",
        "API_KEY": "API key required |  User action",
        "AD_BUDGET": "Ad budget needed |  User action",
    }
    for blocker, count in blocker_counts.most_common():
        label = blocker_type_map.get(blocker, blocker)
        lines.append(f"| {label} | {count} |")

    lines.append("")
    lines.append("## Code-Unblockable Schemes (sorted by potential)")
    lines.append("")

    for i, s in enumerate(code_fixable[:10]):
        blockers_str = ", ".join(s["blockers"])
        lines.append(f"**{s['title']}**")
        lines.append(f"- Blockers: {blockers_str}")
        lines.append(f"- Status: {s['status']}")
        if "VIDEO_SCRIPT" in s["blockers"]:
            lines.append("- > Build: scripts/generate_short_videos.py")
        elif "LANDING_PAGE" in s["blockers"]:
            lines.append("- > Build: scripts/generate_landing.py")
        elif "BOT" in s["blockers"]:
            lines.append("- > Build: scripts/telegram_cpa_bot.py")
        lines.append("")

    lines.append("## Top 3 Income-Ready Schemes")
    lines.append("")
    for s in testing[:2]:
        lines.append(f"### {s['title']}")
        lines.append(f"- Status: {s['status']}")
        lines.append(f"- Blockers: {', '.join(s['blockers']) if s['blockers'] else 'None identified'}")
        lines.append("")
    for s in code_fixable[:1]:
        lines.append(f"### {s['title']}")
        lines.append(f"- Status: {s['status']}")
        lines.append(f"- Blockers: {', '.join(s['blockers']) if s['blockers'] else 'None identified'}")
        if s['blockers']:
            lines.append(f"- Unblock: Write scripts for {', '.join(s['blockers'])}")
        lines.append("")

    report_str = "\n".join(lines)
    output_path = HERMES / "reports" / "income_pipeline_status.md"
    output_path.write_text(report_str, encoding="utf-8")
    print(f"Report: {output_path}")
    print("---")
    print(report_str)


if __name__ == "__main__":
    main()
