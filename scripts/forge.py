#!/usr/bin/env python3
"""
Forge-lite — Dynamic Tool Creation System for Hermes.
LLM generates Python code → runs in isolated sandbox → returns result.

Now uses unified llm_client (Cerebras primary) instead of raw call_deepseek().
"""

import json
import subprocess
import tempfile
import uuid
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

HERMES_HOME = Path(__file__).resolve().parent.parent
FORGE_CACHE = HERMES_HOME / "cache" / "forge"
FORGE_CACHE.mkdir(parents=True, exist_ok=True)

# Import unified LLM client
sys.path.insert(0, str(HERMES_HOME / "scripts"))
from llm_client import call_llm

# Allowed libraries for generated code
ALLOWED_IMPORTS = {
    "json", "os", "sys", "pathlib", "datetime", "uuid", "hashlib",
    "re", "csv", "html", "urllib", "urllib.request", "urllib.parse", "urllib.error",
    "base64", "mimetypes", "tempfile", "shutil", "textwrap", "string",
    "random", "math", "statistics", "collections", "itertools", "functools",
    "dataclasses", "typing", "enum", "decimal", "fractions", "zoneinfo",
    "time", "calendar", "email", "html.parser", "xml.etree.ElementTree"
}

# Forbidden patterns (security)
FORBIDDEN_PATTERNS = [
    "import subprocess", "import os.system", "os.popen", "subprocess.run",
    "subprocess.Popen", "eval(", "exec(", "compile(", "__import__",
    "socket", "threading", "multiprocessing",
    "ctypes", "importlib", "pkgutil", "runpy", "import shutil", "shutil.rmtree",
    "os.remove", "os.unlink", "pathlib.Path.unlink", "pathlib.Path.rmdir",
]

FORGE_PROMPT = """Ты — Python-разработчик. Напиши самодостаточный скрипт, который решает задачу.

ПРАВИЛА:
1. Код должен быть одним файлом, без внешних зависимостей кроме стандартной библиотеки.
2. Разрешённые импорты: json, os, sys, pathlib, datetime, uuid, hashlib, re, csv, html, urllib, base64, mimetypes, tempfile, textwrap, string, random, math, statistics, collections, itertools, functools, dataclasses, typing, enum, decimal, fractions, time, calendar, email, html.parser, xml.etree.ElementTree.
3. ЗАПРЕЩЕНО: subprocess, os.system, eval, exec, open() для записи вне tempfile, socket, threading, multiprocessing, ctypes, importlib, pkgutil, runpy, import shutil, shutil.rmtree, os.remove, os.unlink, path.Path.unlink, pathlib.Path.rmdir.
4. Результат выводи в stdout как JSON: {{"success": true, "data": ..., "message": "..."}} или {{"success": false, "error": "..."}}.
5. Используй tempfile для временных файлов.
6. Код должен быть production-ready: обработка ошибок, типы, docstrings.

ЗАДАЧА:
{task}

Верни ТОЛЬКО код на Python, без markdown, без объяснений.
"""


def validate_code(code: str) -> tuple[bool, str]:
    """Basic security validation of generated code."""
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in code:
            return False, f"Forbidden pattern detected: {pattern}"

    import_lines = [line.strip() for line in code.split('\n') if line.strip().startswith(('import ', 'from '))]
    for line in import_lines:
        parts = line.replace('import ', '').replace('from ', '').split()
        if parts:
            mod = parts[0].split('.')[0]
            if mod not in ALLOWED_IMPORTS and mod not in ('tempfile', 'html'):
                return False, f"Disallowed import: {mod}"

    return True, "OK"


def run_in_sandbox(code: str, timeout: int = 30) -> Dict[str, Any]:
    """Run code in isolated subprocess with restricted environment."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=FORGE_CACHE) as f:
        f.write(code)
        temp_path = f.name

    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = ''
        env['PYTHONDONTWRITEBYTECODE'] = '1'

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=FORGE_CACHE,
            env=env
        )

        if result.returncode == 0:
            try:
                output = json.loads(result.stdout.strip())
                return output
            except json.JSONDecodeError:
                return {"success": False, "error": f"Invalid JSON output: {result.stdout[:500]}"}
        else:
            return {"success": False, "error": f"Exit code {result.returncode}: {result.stderr[:500]}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


def forge(task: str, max_retries: int = 2, provider: str = None) -> Dict[str, Any]:
    """
    Main forge function: task → LLM code → sandbox execution → result.

    Args:
        task: Natural language description of what to build
        max_retries: Number of retries if code generation/execution fails
        provider: Optional provider override (e.g. "cerebras", "deepseek")

    Returns:
        Dict with success, data, error, message, code
    """
    print(f"[FORGE] Task: {task[:120]}...")

    for attempt in range(max_retries + 1):
        # Step 1: Generate code via unified LLM client
        prompt = FORGE_PROMPT.format(task=task)
        code = call_llm(
            prompt,
            max_tokens=3000,
            temperature=0.2,
            provider=provider,
        )

        if not code:
            return {"success": False, "error": "LLM returned no response"}

        # Clean code (remove markdown fences)
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        # Step 2: Validate
        valid, msg = validate_code(code)
        if not valid:
            print(f"[FORGE] Validation failed (attempt {attempt+1}): {msg}")
            if attempt == max_retries:
                return {"success": False, "error": f"Code validation failed: {msg}"}
            continue

        # Step 3: Execute in sandbox
        print(f"[FORGE] Executing in sandbox (attempt {attempt+1})...")
        result = run_in_sandbox(code)

        if result.get("success"):
            print(f"[FORGE] Success!")
            return {"success": True, "data": result.get("data"),
                    "message": result.get("message", "OK"), "code": code}
        else:
            print(f"[FORGE] Execution failed (attempt {attempt+1}): {result.get('error')}")
            if attempt == max_retries:
                return {"success": False, "error": result.get("error"), "code": code}

    return {"success": False, "error": "Max retries exceeded"}


def forge_and_save(task: str, output_path: str = None, provider: str = None) -> Dict[str, Any]:
    """Forge a tool and save the generated code to a file."""
    result = forge(task, provider=provider)
    if result.get("success") and output_path:
        Path(output_path).write_text(result["code"], encoding="utf-8")
        result["saved_to"] = output_path
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python forge.py \"task description\" [output_file.py] [--provider NAME]")
        sys.exit(1)

    task = sys.argv[1]
    output = None
    provider = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
            provider = sys.argv[i + 1]
            i += 2
        elif not sys.argv[i].startswith("--"):
            output = sys.argv[i]
            i += 1
        else:
            i += 1

    result = forge_and_save(task, output, provider=provider)
    print(json.dumps(result, ensure_ascii=False, indent=2))
