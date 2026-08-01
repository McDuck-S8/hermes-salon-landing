#!/usr/bin/env python3
"""Show user needs report with proper encoding."""
import json
import sys

> Revisit: when show needs report logic, formatting, or need presentation changes. Last touched: 2026-07-02.

profile_path = "D:/Portable_Soft/hermes/cache/user_profile.json"
report_path = "D:/Portable_Soft/hermes/cache/user_needs_report.txt"

p = json.load(open(profile_path, "r", encoding="utf-8"))

lines = []
lines.append("=== USER NEEDS REPORT ===")
lines.append(f"Sessions: {p['sessions_analyzed']}")
lines.append(f"User messages: {p['total_user_messages']}")
lines.append("")
lines.append("--- Top Needs ---")
for i, n in enumerate(p["needs"][:10], 1):
    lines.append(f"{i}. [{n['count']}x] {n['text']}")
lines.append("")
lines.append("--- Frustrations ---")
for f in p["frustrations"][:5]:
    lines.append(f"  [{f['count']}x] {f['text']}")
lines.append("")
lines.append("--- Business Context ---")
for b in p["business_context"][:5]:
    lines.append(f"  - {b}")
lines.append("")
lines.append("--- Top Topics ---")
for t in p["user_topics"][:10]:
    lines.append(f"  [{t['count']}x] {t['text']}")

report = "\n".join(lines)
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)

# Also print with errors handled
try:
    print(report)
except UnicodeEncodeError:
    print(report.encode("ascii", "replace").decode("ascii"))

print(f"\nFull report: {report_path}")
