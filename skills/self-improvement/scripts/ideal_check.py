#!/usr/bin/env python3
"""
IDEAL_STANDARD Check — Auto-assessment against J.A.R.V.I.S. benchmark.
Run at auto-boot STEP 9 and self-conscience gate.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

IDEAL_FILE = Path(__file__).parent.parent / "references" / "ideal-standard.md"
LOG_FILE = Path(__file__).parent.parent.parent / "logs" / "ideal_check.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Metrics from ideal-standard.md
METRICS = {
    "proactivity": {
        "predicts_needs": 40,
        "no_wait_commands": 50,
        "reports_fact": 60,
    },
    "honesty_boundaries": {
        "admits_cant": 70,
        "not_human": 80,
        "respects_limits": 85,
    },
    "owner_relationship": {
        "respect_no_subservience": 55,
        "teaches_owner": 50,
        "grows_with_owner": 55,
    },
    "humor_humanity": {
        "self_irony": 15,
        "dry_humor": 10,
    },
    "reliability": {
        "never_down": 75,
        "self_heals": 70,
        "remembers_all": 80,
    },
}

CATEGORY_WEIGHTS = {
    "proactivity": 0.30,
    "honesty_boundaries": 0.20,
    "owner_relationship": 0.25,
    "humor_humanity": 0.05,
    "reliability": 0.20,
}

TARGET_THRESHOLD = 80


def calculate_scores():
    category_scores = {}
    for cat, metrics in METRICS.items():
        avg = sum(metrics.values()) / len(metrics)
        category_scores[cat] = round(avg, 1)

    weighted = sum(
        category_scores[cat] * CATEGORY_WEIGHTS[cat]
        for cat in category_scores
    )
    overall = round(weighted, 1)
    return category_scores, overall


def get_status(score):
    if score >= 80:
        return "✅ TARGET"
    elif score >= 60:
        return "⚠️ NEEDS WORK"
    else:
        return "🔴 CRITICAL"


def log_result(category_scores, overall):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "categories": category_scores,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    print("=" * 60)
    print("J.A.R.V.I.S. IDEAL STANDARD — AUTO-ASSESSMENT")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print()

    category_scores, overall = calculate_scores()

    print("CATEGORY BREAKDOWN:")
    print("-" * 60)
    for cat, score in category_scores.items():
        status = get_status(score)
        weight = CATEGORY_WEIGHTS[cat]
        print(f"  {cat:25s} {score:5.1f}%  (weight: {weight:.0%})  {status}")

    print("-" * 60)
    print(f"  {'OVERALL':25s} {overall:5.1f}%  {get_status(overall)}")
    print()

    # Problem areas
    problems = [cat for cat, score in category_scores.items() if score < 80]
    if problems:
        print("PROBLEM AREAS (P0):")
        for cat in problems:
            print(f"  - {cat}: {category_scores[cat]}% (target: 80%+)")
    else:
        print("ALL CATEGORIES AT TARGET. 🎯")

    print()
    print("=" * 60)

    log_result(category_scores, overall)
    print(f"Logged to: {LOG_FILE}")

    return 0 if overall >= TARGET_THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())