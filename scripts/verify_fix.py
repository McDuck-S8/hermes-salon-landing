#!/usr/bin/env python3
"""
Post-fix verification mechanism — standalone module.

> Revisit: when verification logic, fix validation, or rollback triggers change. Last touched: 2026-07-02.

Runs tests, health-checks, and smoke tests after a fix is applied.
Returns structured verification status suitable for Knowledge Cube entry.

Usage:
    # As module (imported by proactive_executor.py):
    from verify_fix import verify_fix_result

    # As script (standalone verification):
    python scripts/verify_fix.py <target_file> [--fix-type patch|command] [--description "..."]

    # As Test Harness integration:
    from verify_fix import verify_fix_result
    result = verify_fix_result(fix_result, target_file)
    # harness uses result["verified"], result["checks_passed"], result["checks_failed"]
"""

import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ──────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KNOWLEDGE_CUBE_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
CORE_ENGINE_DB = HERMES_HOME / "cache" / "core_engine.db"
EVENTS_DB = HERMES_HOME / "cache" / "events.db"
TIMEOUT_SECONDS = 30  # Locked: verify within 30s


def report(msg: str) -> None:
    """Print a verification status line."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def verify_fix_result(fix_result: dict, target_file: str) -> dict:
    """
    Verify that a fix was successful by running tests/health-checks after a fix
    is applied. Returns a structured verification status suitable for KC entry.

    Args:
        fix_result: Dict with at minimum:
            - fix (dict): Contains fix_type, description, etc.
          Or:
            - status (str): Status of the fix
        target_file: The file that was fixed

    Returns:
        Dict with keys:
            verified (bool): True if verification passes
            checks_passed (list[str]): Names of checks that passed
            checks_failed (list[str]): Names of checks that failed
            details (str): Human-readable summary
            kc_entry (dict): Structured data for Knowledge Cube entry
    """
    result = {
        "verified": False,
        "checks_passed": [],
        "checks_failed": [],
        "details": "",
        "kc_entry": {},
    }
    start_time = time.time()

    try:
        fix = fix_result.get("fix", {})
        fix_type = fix.get("fix_type", fix_result.get("fix_type", ""))
        description = fix.get("description", fix_result.get("description", ""))

        report(f"[VERIFY] Verifying fix: {description}")

        # ── Check 1: Syntax check (Python files) ──
        if target_file.endswith(".py"):
            import py_compile

            try:
                py_compile.compile(target_file, doraise=True)
                result["checks_passed"].append("syntax")
                report(f"[VERIFY] Syntax check passed for {target_file}")
            except py_compile.PyCompileError as e:
                result["checks_failed"].append("syntax")
                report(f"[VERIFY] Syntax check FAILED: {e}")
                result["details"] = f"Syntax error: {e}"
                return result

        # ── Check 2: Pytest (if test file exists) ──
        if time.time() - start_time < TIMEOUT_SECONDS:
            test_file = target_file.replace(".py", "_test.py").replace(
                "scripts/", "tests/"
            )
            if not os.path.exists(test_file):
                for test_dir in ["tests", "test"]:
                    test_path = (
                        Path(test_dir)
                        / Path(target_file).name.replace(".py", "_test.py")
                    )
                    if test_path.exists():
                        test_file = str(test_path)
                        break

            if os.path.exists(test_file):
                remaining = max(
                    5, TIMEOUT_SECONDS - int(time.time() - start_time)
                )
                try:
                    proc_result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pytest",
                            test_file,
                            "-v",
                            "--tb=short",
                        ],
                        cwd=HERMES_HOME,
                        capture_output=True,
                        text=True,
                        timeout=remaining,
                    )
                    if proc_result.returncode == 0:
                        result["checks_passed"].append("pytest")
                        report(f"[VERIFY] Tests passed for {test_file}")
                    else:
                        result["checks_failed"].append("pytest")
                        report(
                            f"[VERIFY] Tests FAILED: {proc_result.stdout[-500:]}"
                        )
                        result["details"] = (
                            f"Pytest failed: {proc_result.stdout[-300:]}"
                        )
                        return result
                except subprocess.TimeoutExpired:
                    result["checks_failed"].append("pytest_timeout")
                    report(
                        f"[VERIFY] Pytest timed out after {remaining}s"
                    )
            else:
                report(f"[VERIFY] No specific test file found — skipping pytest")

        # ── Check 3: DB connectivity (if fix touches DB-related code) ──
        if time.time() - start_time < TIMEOUT_SECONDS:
            db_keywords = (
                "db",
                "sqlite",
                "database",
                "knowledge_cube",
                "core_engine",
            )
            if any(kw in target_file.lower() for kw in db_keywords) or any(
                kw in description.lower() for kw in db_keywords
            ):
                try:
                    for db_path in [
                        KNOWLEDGE_CUBE_DB,
                        CORE_ENGINE_DB,
                        EVENTS_DB,
                    ]:
                        if db_path.exists():
                            conn = sqlite3.connect(str(db_path), timeout=5)
                            conn.execute("PRAGMA quick_check")
                            conn.close()
                    result["checks_passed"].append("db_connectivity")
                    report(f"[VERIFY] DB connectivity check passed")
                except Exception as e:
                    result["checks_failed"].append("db_connectivity")
                    report(f"[VERIFY] DB connectivity FAILED: {e}")
                    result["details"] = f"DB connectivity error: {e}"

        # ── Check 4: HTTP health endpoint (if fix touches service code) ──
        if time.time() - start_time < TIMEOUT_SECONDS:
            service_keywords = (
                "api",
                "server",
                "endpoint",
                "http",
                "port",
                "health",
            )
            if any(
                kw in target_file.lower() for kw in service_keywords
            ) or any(kw in description.lower() for kw in service_keywords):
                health_urls = [
                    ("http://127.0.0.1:3264/health", "Qwen API"),
                    ("http://127.0.0.1:3264/v1/models", "Qwen Models"),
                ]
                for url, name in health_urls:
                    try:
                        remaining = max(
                            3,
                            TIMEOUT_SECONDS - int(time.time() - start_time),
                        )
                        req = urllib.request.Request(url, method="GET")
                        resp = urllib.request.urlopen(req, timeout=remaining)
                        if resp.status == 200:
                            result["checks_passed"].append(f"health:{name}")
                            report(
                                f"[VERIFY] Health check passed: {name} ({url})"
                            )
                        else:
                            result["checks_failed"].append(f"health:{name}")
                            report(
                                f"[VERIFY] Health check failed: {name} (status={resp.status})"
                            )
                    except (urllib.error.URLError, OSError, TimeoutError):
                        result["checks_failed"].append(f"health:{name}")
                        report(
                            f"[VERIFY] Health check failed: {name} (unreachable)"
                        )

        # ── Check 5: Indentation pattern (for patch fixes) ──
        if fix_type == "patch" and "indentation" in description.lower():
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                indent_ok = True
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith("if ") and stripped.endswith(":"):
                        for j in range(i + 1, min(i + 5, len(lines))):
                            if lines[j].strip() and not lines[j].startswith(
                                (" ", "\t")
                            ):
                                report(
                                    f"[VERIFY] Found unindented line after if at line {j + 1}"
                                )
                                indent_ok = False
                                break
                        if not indent_ok:
                            break
                if indent_ok:
                    result["checks_passed"].append("indentation")
                    report(f"[VERIFY] Indentation pattern verified")
                else:
                    result["checks_failed"].append("indentation")
                    result["details"] = "Indentation error detected after fix"
                    return result
            except Exception as e:
                report(f"[VERIFY] Indentation check error: {e}")

        # ── Check 6: Command output ──
        if fix_type == "command":
            output = fix_result.get("output", "")
            if output:
                result["checks_passed"].append("command_output")
                report(
                    f"[VERIFY] Command produced output ({len(output)} chars)"
                )

        # ── Overall result ──
        elapsed = time.time() - start_time
        result["verified"] = len(result["checks_failed"]) == 0
        result["details"] = (
            f"Passed: {', '.join(result['checks_passed']) or 'none'} | "
            f"Failed: {', '.join(result['checks_failed']) or 'none'} | "
            f"Elapsed: {elapsed:.1f}s"
        )

        # ── Build KC entry for verified knowledge ──
        result["kc_entry"] = {
            "domain": "bugfix",
            "axis_domain": "bugfix",
            "outcome": "success" if result["verified"] else "error",
            "raw_text": f"Fix verification: {description} — {result['details']}",
            "source_file": target_file,
            "fix_type": fix_type,
            "checks_passed": result["checks_passed"],
            "checks_failed": result["checks_failed"],
            "elapsed_sec": round(elapsed, 2),
        }

        status = "VERIFIED" if result["verified"] else "NOT VERIFIED"
        report(f"[VERIFY] {status} — {result['details']}")

        return result

    except Exception as e:
        report(f"[VERIFY] Verification error: {e}")
        result["details"] = f"Verification error: {e}"
        return result


# ── CLI entry point ────────────────────────────────────────────────

def main() -> int:
    """Standalone CLI for verifying a fix."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify a fix was applied successfully"
    )
    parser.add_argument("target_file", help="File that was fixed")
    parser.add_argument(
        "--fix-type",
        default="patch",
        choices=["patch", "command", "investigation"],
        help="Type of fix applied",
    )
    parser.add_argument(
        "--description", default="", help="Description of the fix"
    )
    parser.add_argument(
        "--output", default="", help="Command output (for command-type fixes)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output result as JSON"
    )

    args = parser.parse_args()

    fix_result = {
        "fix": {
            "fix_type": args.fix_type,
            "description": args.description,
        },
    }
    if args.output:
        fix_result["output"] = args.output

    result = verify_fix_result(fix_result, args.target_file)

    if args.json:
        print(json.dumps(result, indent=2, default=str))

    return 0 if result["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
