#!/usr/bin/env python3
"""
hermes_tools.py — Stub implementations for scripts that import hermes_tools
outside the agent context (cron jobs, standalone scripts).

> Revisit: when tools config, tool registration, or tool discovery changes. Last touched: 2026-07-02.

In agent context (execute_code), hermes_tools is provided by the runtime.
Here we provide basic fallbacks using subprocess calls.
"""
import subprocess
import json
import os
from pathlib import Path


def terminal(command, timeout=30, workdir=None):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=workdir or os.getcwd()
        )
        return {
            "output": result.stdout + result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"output": "TIMEOUT", "exit_code": -1}


def web_search(query, limit=5):
    """Placeholder: returns empty results. Use real search in agent context."""
    return {"data": {"web": []}, "note": "web_search not available outside agent context"}


def read_file(path, offset=1, limit=500):
    """Read a file with line numbers."""
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
        selected = lines[offset-1:offset-1+limit]
        return {"content": "\n".join(f"{i+offset}|{l}" for i, l in enumerate(selected)), "total_lines": len(lines)}
    except Exception as e:
        return {"content": str(e), "total_lines": 0}


def write_file(path, content):
    """Write content to a file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(content, encoding="utf-8")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def search_files(pattern, target="content", path=".", file_glob=None, limit=50):
    """Search files by name or content."""
    try:
        import re
        base = Path(path)
        if target == "files":
            matches = [str(f) for f in base.rglob(pattern) if f.is_file()][:limit]
            return {"matches": matches}
        else:
            regex = re.compile(pattern, re.IGNORECASE)
            matches = []
            for f in base.rglob(file_glob or "*.py"):
                if f.is_file() and len(matches) < limit:
                    try:
                        text = f.read_text(encoding="utf-8", errors="ignore")
                        for i, line in enumerate(text.splitlines(), 1):
                            if regex.search(line):
                                matches.append(f"{f}:{i}: {line.strip()}")
                    except:
                        pass
            return {"matches": matches}
    except Exception as e:
        return {"matches": [], "error": str(e)}
