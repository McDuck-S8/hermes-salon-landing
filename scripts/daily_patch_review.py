#!/usr/bin/env python3
"""Daily patch review — reads patch_journal.jsonl, outputs summary report.

Runs at 8:00 daily via cron (no_agent=True).

Reports:
- Total patches in last 24h
- Per-skill breakdown with old/new hashes
- Skills patched most frequently
- Any skills with rollback indicators (repeated patches on same file)
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

JOURNAL = Path("D:/Portable_Soft/hermes/cache/patch_journal.jsonl")
REPORT_DIR = Path("D:/Portable_Soft/hermes/reports")

def main():
    if not JOURNAL.exists():
        print("[SILENT] — no patch journal yet")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    entries = []
    with open(JOURNAL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                ts = datetime.fromisoformat(e["ts"])
                if ts >= cutoff:
                    e["_ts"] = ts
                    entries.append(e)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

    if not entries:
        print("[SILENT] — no patches in last 24h")
        return

    # Sort by time
    entries.sort(key=lambda e: e["_ts"])

    # Stats
    total = len(entries)
    by_skill = {}
    repeat_patches = set()
    seen_hashes = {}

    for e in entries:
        skill = e["skill"]
        by_skill.setdefault(skill, {"count": 0, "actions": []})
        by_skill[skill]["count"] += 1
        by_skill[skill]["actions"].append(e["action"])

        # Detect repeated patches — same skill with same old_hash
        key = (skill, e.get("old_hash", ""))
        if key in seen_hashes:
            repeat_patches.add(skill)
        seen_hashes[key] = True

    print(f"=== Patch Review — {cutoff.strftime('%Y-%m-%d')} ===")
    print(f"Total patches: {total}")
    print()

    if repeat_patches:
        print("⚠ Repeated patches (possible oscillation):")
        for s in sorted(repeat_patches):
            print(f"  - {s} ({by_skill[s]['count']}x)")
        print()

    print("By skill:")
    for skill, info in sorted(by_skill.items(), key=lambda x: -x[1]["count"]):
        last_ts = max(e["_ts"] for e in entries if e["skill"] == skill)
        actions = ", ".join(set(info["actions"]))
        print(f"  {info['count']:3d}x  {skill:40s} [{actions}] last: {last_ts.strftime('%H:%M')}")
    print()

    if total <= 3:
        print("Recent patches (last {total}):")
        for e in entries[-3:]:
            print(f"  {e['_ts'].strftime('%H:%M')} {e['skill']} {e['action']} old:{e.get('old_hash','?')}")

    # Save report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"patch_review_{cutoff.strftime('%Y%m%d')}.md"
    report_path.write_text('\n'.join([
        f"# Patch Review — {cutoff.strftime('%Y-%m-%d')}",
        f"**Total patches:** {total}",
        f"**Skills affected:** {len(by_skill)}",
        f"**Repeated patches:** {len(repeat_patches)}" if repeat_patches else "**Repeated patches:** 0",
        "",
        f"Auto-generated daily report from patch_journal.jsonl"
    ]))
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()
