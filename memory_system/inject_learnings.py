#!/usr/bin/env python3
"""
Hermes pre_llm_call hook — injects learnings and goals into LLM context.
Outputs JSON with "context" key for Hermes hook system.
"""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MEMORY_DIR = Path(r"D:\Portable_Soft\hermes\memory_system")
LEARNINGS = MEMORY_DIR / "learnings.md"
GOALS = MEMORY_DIR / "goals.md"
SOUL_PATH = Path(r"D:\Portable_Soft\hermes\SOUL.md")
AGENTS_PATH = Path(r"D:\Portable_Soft\hermes\AGENTS.md")

def read_file(path: Path, max_lines: int = 20) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return "\n".join(lines)

def main():
    parts = []

    learnings = read_file(LEARNINGS, max_lines=15)
    if learnings.strip():
        parts.append(f"## My Learnings:\n{learnings}")

    goals = read_file(GOALS, max_lines=10)
    if goals.strip():
        parts.append(f"## Goals:\n{goals}")

    context = "\n\n---\n\n".join(parts)

    if context.strip():
        output = {"context": context}
    else:
        output = {"context": ""}

    print(json.dumps(output, ensure_ascii=True))

if __name__ == "__main__":
    main()
