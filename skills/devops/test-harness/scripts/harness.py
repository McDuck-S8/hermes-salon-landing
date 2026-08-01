#!/usr/bin/env python3
"""
Test Harness — Main Orchestrator

Implements the SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER cycle.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─── paths ──────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SKILL_DIR = HERMES_HOME / "skills" / "devops" / "test-harness"
TEMPLATES_DIR = SKILL_DIR / "templates"
REFERENCES_DIR = SKILL_DIR / "references"
SCRIPTS_DIR = SKILL_DIR / "scripts"

MAX_LOOPS = int(os.environ.get("HERMES_TEST_HARNESS_MAX_LOOPS", "3"))
TIMEOUT = int(os.environ.get("HERMES_TEST_HARNESS_TIMEOUT", "300"))
ENABLED = os.environ.get("HERMES_TEST_HARNESS_ENABLED", "true").lower() == "true"


class TestHarness:
    """Orchestrates the SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER cycle."""

    def __init__(self, spec_path: str, tests_path: str, target_file: str = ""):
        self.spec_path = Path(spec_path)
        self.tests_path = Path(tests_path)
        self.target_file = Path(target_file) if target_file else Path("")
        self.spec = {}
        self.tests = {}
        self.loop_count = 0
        self.history = []

    def load_spec(self) -> bool:
        """Load and parse SPEC.md"""
        if not self.spec_path.exists():
            print(f"[HARNESS] SPEC not found: {self.spec_path}")
            return False
        content = self.spec_path.read_text(encoding="utf-8")
        self.spec = self._parse_spec(content)
        return True

    def load_tests(self) -> bool:
        """Load and parse TESTS.md"""
        if not self.tests_path.exists():
            print(f"[HARNESS] TESTS not found: {self.tests_path}")
            return False
        content = self.tests_path.read_text(encoding="utf-8")
        self.tests = self._parse_tests(content)
        return True

    def _parse_spec(self, content: str) -> Dict[str, Any]:
        """Parse SPEC.md into structured data"""
        spec = {"raw": content}
        # Extract key sections
        lines = content.split("\n")
        current_section = ""
        for line in lines:
            if line.startswith("## "):
                current_section = line[3:].strip().lower().replace(" ", "_")
                spec[current_section] = []
            elif current_section and line.strip():
                spec[current_section].append(line.strip())
        # Flatten lists to strings
        for k, v in spec.items():
            if isinstance(v, list):
                spec[k] = "\n".join(v)
        return spec

    def _parse_tests(self, content: str) -> Dict[str, Any]:
        """Parse TESTS.md into structured test suite"""
        # Simple YAML-like parsing for test suite
        tests = {"raw": content, "tests": []}
        # TODO: Implement full YAML parsing
        # For now, store raw and parse basic structure
        return tests

    def validate(self) -> Dict[str, Any]:
        """Run validation tests against target file"""
        from verify_fix import verify_fix_result

        fix_result = {
            "fix": {
                "fix_type": "patch",
                "description": self.spec.get("goal", "Fix from SPEC"),
            }
        }

        result = verify_fix_result(fix_result, str(self.target_file))

        # Add harness metadata
        result["harness"] = {
            "spec": str(self.spec_path),
            "tests": str(self.tests_path),
            "loop": self.loop_count,
            "timestamp": datetime.now().isoformat(),
        }

        return result

    def run_cycle(self, max_loops: int = MAX_LOOPS) -> Dict[str, Any]:
        """Run full SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER cycle"""

        print(f"[HARNESS] Starting cycle for {self.spec_path}")
        print(f"[HARNESS] Max loops: {max_loops}")

        # Phase 1: Load SPEC and TESTS
        if not self.load_spec():
            return {"error": "Failed to load SPEC"}
        if not self.load_tests():
            return {"error": "Failed to load TESTS"}

        # Phase 2-5: LOOP
        for loop in range(1, max_loops + 1):
            self.loop_count = loop
            print(f"\n[HARNESS] === LOOP {loop}/{max_loops} ===")

            # GENERATE phase (placeholder - would invoke agent)
            print("[HARNESS] GENERATE phase: (agent invocation placeholder)")

            # VALIDATE phase
            print("[HARNESS] VALIDATE phase: running tests...")
            result = self.validate()

            self.history.append({
                "loop": loop,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            })

            if result.get("verified"):
                print(f"[HARNESS] ✓ All tests passed on loop {loop}")
                break
            else:
                print(f"[HARNESS] ✗ Tests failed on loop {loop}: {result.get('details')}")
                if loop == max_loops:
                    print(f"[HARNESS] Max loops reached. Escalating to human.")
                    break
                # LOOP: would feed failure back to agent for regeneration
                print(f"[HARNESS] LOOP: feeding failure back to agent...")

        # DELIVER phase (only if verified)
        final_result = self.history[-1]["result"] if self.history else {"verified": False}
        if final_result.get("verified"):
            self.deliver(final_result)
        else:
            print("[HARNESS] Cycle completed without verification. No DELIVER.")

        return {
            "verified": final_result.get("verified", False),
            "loops": self.loop_count,
            "history": self.history,
            "final": final_result,
        }

    def deliver(self, result: Dict[str, Any]) -> None:
        """Record verified knowledge to Knowledge Cube and update skills"""
        print("[HARNESS] DELIVER: recording to Knowledge Cube...")

        # Build KC entry
        kc_entry = result.get("kc_entry", {})
        kc_entry.update({
            "harness_spec": str(self.spec_path),
            "harness_tests": str(self.tests_path),
            "harness_loops": self.loop_count,
            "harness_verified_at": datetime.now().isoformat(),
        })

        # Write to cache for KC ingestion
        cache_dir = HERMES_HOME / "cache" / "test_harness"
        cache_dir.mkdir(parents=True, exist_ok=True)
        entry_file = cache_dir / f"verified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        entry_file.write_text(json.dumps(kc_entry, indent=2, default=str), encoding="utf-8")

        # Update DECISION_LOG.md
        decision_log = HERMES_HOME / "DECISION_LOG.md"
        if decision_log.exists():
            content = decision_log.read_text(encoding="utf-8")
        else:
            content = "# Decision Log\n\n"
        entry = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} — Test Harness Verified\n"
        entry += f"- Spec: {self.spec_path}\n"
        entry += f"- Target: {self.target_file}\n"
        entry += f"- Loops: {self.loop_count}\n"
        entry += f"- Verified: True\n\n"
        decision_log.write_text(content + entry, encoding="utf-8")

        print(f"[HARNESS] DELIVER complete. KC entry: {kc_entry.get('domain', 'unknown')}")

    def start_new_cycle(self, spec_content: str, tests_content: str, target: str = "") -> Dict[str, Any]:
        """Create new SPEC/TESTS files and start cycle"""
        spec_file = HERMES_HOME / "cache" / "test_harness" / f"SPEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        tests_file = HERMES_HOME / "cache" / "test_harness" / f"TESTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        (HERMES_HOME / "cache" / "test_harness").mkdir(parents=True, exist_ok=True)

        spec_file.write_text(spec_content, encoding="utf-8")
        tests_file.write_text(tests_content, encoding="utf-8")

        self.spec_path = spec_file
        self.tests_path = tests_file = tests_file
        self.target_file = Path(target) if target else Path("")

        return self.run_cycle()


def main():
    parser = argparse.ArgumentParser(description="Test Harness — SPEC → TESTS → GENERATE → VALIDATE → LOOP → DELIVER")
    parser.add_argument("command", choices=["start", "validate", "cycle", "create"], help="Command to run")
    parser.add_argument("--spec", help="Path to SPEC.md")
    parser.add_argument("--tests", help="Path to TESTS.md")
    parser.add_argument("--target", help="Target file to verify")
    parser.add_argument("--max-loops", type=int, default=MAX_LOOPS, help="Max loop iterations")
    parser.add_argument("--spec-content", help="SPEC content (for create command)")
    parser.add_argument("--tests-content", help="TESTS content (for create command)")
    parser.add_argument("--target-file", help="Target file (for create command)")

    args = parser.parse_args()

    if not ENABLED:
        print("[HARNESS] Disabled via HERMES_TEST_HARNESS_ENABLED=false")
        sys.exit(0)

    harness = TestHarness(args.spec or "", args.tests or "", args.target or "")

    if args.command == "start":
        if not args.spec or not args.tests:
            print("Error: --spec and --tests required for start")
            sys.exit(1)
        result = harness.run_cycle(args.max_loops)
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result.get("verified") else 1)

    elif args.command == "validate":
        if not args.target:
            print("Error: --target required for validate")
            sys.exit(1)
        result = harness.validate()
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result.get("verified") else 1)

    elif args.command == "cycle":
        if not args.spec or not args.tests:
            print("Error: --spec and --tests required for cycle")
            sys.exit(1)
        result = harness.run_cycle(args.max_loops)
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result.get("verified") else 1)

    elif args.command == "create":
        if not args.spec_content or not args.tests_content:
            print("Error: --spec-content and --tests-content required for create")
            sys.exit(1)
        result = harness.start_new_cycle(args.spec_content, args.tests_content, args.target_file or "")
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result.get("verified") else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()