#!/usr/bin/env python3
"""Review pipeline — прогоняет файл через 3 ревьюеров.

Использование:
  python scripts/review_pipeline.py <file_path>

Выдаёт PASS / WARN / FAIL с краткими вердиктами.
"""
import sys, subprocess, os
from pathlib import Path

HERMES = Path(__file__).resolve().parent.parent
AGENTS = {
    "security-sentinel": "Audit for injection, race conditions, credential leaks. Output PASS/WARN/FAIL + one-liner.",
    "architecture-strategist": "Review for coupling, pattern violations, KISS. Output PASS/WARN/FAIL + one-liner.",
    "code-simplicity-reviewer": "Review for over-engineering, DRY, unnecessary abstraction. Output PASS/WARN/FAIL + one-liner.",
}

def run(target_path: str) -> dict:
    if not os.path.isfile(target_path):
        return {"error": f"File not found: {target_path}"}
    target_path = os.path.normpath(target_path)
    content = Path(target_path).read_text(encoding="utf-8", errors="replace")
    results = {}
    for name, prompt in AGENTS.items():
        print(f"  → {name}...", end=" ", flush=True)
        try:
            r = subprocess.run(
                [sys.executable, str(HERMES / "scripts" / "_review_agent.py"),
                 name, prompt, target_path],
                capture_output=True, text=True, timeout=60,
            )
            line = (r.stdout or "").strip().split("\n")[-1]
            results[name] = line[:120] if line else "FAIL (no output)"
            print(f"{results[name][:60]}")
        except subprocess.TimeoutExpired:
            results[name] = "TIMEOUT"; print("TIMEOUT")
        except Exception as e:
            results[name] = f"ERROR: {e}"; print(f"ERROR")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_pipeline.py <file_path>"); sys.exit(1)
    target = sys.argv[1]
    print(f"Review → {target}\n" + "-" * 40)
    results = run(target)
    print("-" * 40)
    fails = [k for k, v in results.items() if "FAIL" in v.upper()]
    warns = [k for k, v in results.items() if "WARN" in v.upper()]
    verdict = f"❌ FAIL ({', '.join(fails)})" if fails else (
        f"⚠️ WARN ({', '.join(warns)})" if warns else "✅ PASS")
    print(f"\nВердикт: {verdict}")
    for n, r in results.items(): print(f"  {n}: {r}")
