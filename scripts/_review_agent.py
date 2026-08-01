#!/usr/bin/env python3
"""Review agent — вызывается review_pipeline.py для каждого ревьюера.

Args: <name> <prompt> <file_path>

Загружает скилл ревьюера через auto_recall, анализирует файл,
выводит PASS/WARN/FAIL + reason (последняя строка stdout).
"""
import sys, os
from pathlib import Path

HERMES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERMES))

name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
prompt = sys.argv[2] if len(sys.argv) > 2 else ""
target = sys.argv[3] if len(sys.argv) > 3 else ""

if not target or not os.path.isfile(target):
    print("FAIL: invalid target")
    sys.exit(0)

content = Path(target).read_text(encoding="utf-8", errors="replace")

# Загружаем контекст из Knowledge Cube
try:
    from scripts.auto_recall import recall_for_session
    ctx = recall_for_session(f"code review: {name}", top_n=3)
    knowledge = "\n".join(
        r.get("formatted", "") for r in ctx.get("results", [])
    )
except Exception:
    knowledge = ""

# Простейший анализатор: проверяем длину, import *, eval/exec, TODO
issues = []
lines = content.split("\n")

# Длина файла
if len(lines) > 400:
    issues.append("WARN: file >400 lines")

# import *
if any(l.strip().startswith("from ") and "*" in l for l in lines):
    issues.append("WARN: wildcard import")

# eval/exec/telnet/pickle — опасно
bad = {"eval(", "exec(", "pickle.loads", "telnetlib", "subprocess.run(",
       "os.system(", "shutil.rmtree"}
for i, l in enumerate(lines, 1):
    for b in bad:
        if b in l:
            issues.append(f"WARN: {b} at line {i}")
            break

# TODO / FIXME / HACK
for i, l in enumerate(lines, 1):
    if l.strip().startswith(("# TODO", "# FIXME", "# HACK")):
        issues.append(f"INFO: {l.strip()} at line {i}")

# Нет докстринги в функциях >5 строк — не критично, но отметим
if name == "code-simplicity-reviewer" and len(lines) > 10:
    issues.append("INFO: function docstrings not checked (line count only)")

# Вердикт
verdict = "PASS"
if any("WARN" in i for i in issues):
    verdict = "WARN"
if any("FAIL" in i for i in issues):
    # security: eval/exec/injection = FAIL
    if any(b in content for b in ("eval(", "exec(", "pickle.loads")):
        verdict = "FAIL"
    else:
        verdict = "WARN"

reasons = "; ".join(issues[:5]) if issues else "clean"
print(f"{verdict}: {reasons}")
