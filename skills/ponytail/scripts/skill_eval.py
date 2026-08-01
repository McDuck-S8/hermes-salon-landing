#!/usr/bin/env python3
"""Skill Evaluation Framework for Hermes.

Each skill can have an eval.yaml file defining test cases.
Run with: python -m scripts.skill_eval skills/agent-browser
"""

import yaml
import re
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging


logger = logging.getLogger("hermes.skill_eval")


class MatchType(Enum):
    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"
    JSON_SCHEMA = "json_schema"
    PYTHON = "python"


@dataclass
class EvalCase:
    name: str
    input: str
    expected: Any
    match_type: MatchType = MatchType.CONTAINS
    setup: Optional[str] = None
    teardown: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalResult:
    case_name: str
    passed: bool
    actual: Any
    expected: Any
    error: Optional[str] = None
    duration_ms: float = 0


def load_eval_file(path: Path) -> List[EvalCase]:
    """Load eval cases from a YAML file."""
    if not path.exists():
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data or 'tests' not in data:
        return []
    
    cases = []
    for item in data['tests']:
        match_type = MatchType(item.get('match', 'contains'))
        cases.append(EvalCase(
            name=item['name'],
            input=item['input'],
            expected=item['expected'],
            match_type=match_type,
            setup=item.get('setup'),
            teardown=item.get('teardown'),
            metadata=item.get('metadata', {}),
        ))
    return cases


def match_result(actual: Any, expected: Any, match_type: MatchType) -> tuple[bool, str]:
    """Check if actual matches expected according to match_type."""
    
    if match_type == MatchType.EXACT:
        ok = actual == expected
        return ok, f"expected exact match: {expected}"
    
    elif match_type == MatchType.CONTAINS:
        actual_str = str(actual)
        expected_str = str(expected)
        ok = expected_str in actual_str
        return ok, f"expected to contain: {expected_str}"
    
    elif match_type == MatchType.REGEX:
        actual_str = str(actual)
        try:
            ok = bool(re.search(str(expected), actual_str))
            return ok, f"expected regex match: {expected}"
        except re.error as e:
            return False, f"invalid regex: {e}"
    
    elif match_type == MatchType.JSON_SCHEMA:
        if not isinstance(actual, dict) or not isinstance(expected, dict):
            return False, "both actual and expected must be dicts for json_schema"
        missing = [k for k in expected if k not in actual]
        ok = len(missing) == 0
        return ok, f"missing keys: {missing}" if missing else "ok"
    
    elif match_type == MatchType.PYTHON:
        try:
            ok = bool(eval(str(expected), {"__builtins__": {}}, {"actual": actual}))
            return ok, f"python expression failed: {expected}"
        except Exception as e:
            return False, f"python eval error: {e}"
    
    return False, f"unknown match type: {match_type}"


async def run_skill_eval(
    skill_name: str, 
    skill_dir: Path, 
    skill_invoker: Optional[Callable[[str], Any]] = None
) -> List[EvalResult]:
    """Run all eval tests for a skill."""
    eval_file = skill_dir / "eval.yaml"
    cases = load_eval_file(eval_file)
    
    if not cases:
        logger.info(f"No eval cases found for {skill_name}")
        return []
    
    results = []
    
    for case in cases:
        start = time.perf_counter()
        
        try:
            # Run setup if provided
            if case.setup:
                exec(case.setup, {"skill_name": skill_name})
            
            # Invoke the skill
            if skill_invoker:
                actual = await skill_invoker(case.input)
            else:
                # Mock response for CI/testing without actual skill execution
                actual = f"[MOCK] {case.input}"
            
            # Run teardown if provided
            if case.teardown:
                exec(case.teardown, {"skill_name": skill_name})
            
            # Match result
            ok, msg = match_result(actual, case.expected, case.match_type)
            duration = (time.perf_counter() - start) * 1000
            
            results.append(EvalResult(
                case_name=case.name,
                passed=ok,
                actual=actual,
                expected=case.expected,
                error=None if ok else msg,
                duration_ms=duration,
            ))
            
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(EvalResult(
                case_name=case.name,
                passed=False,
                actual=None,
                expected=case.expected,
                error=str(e),
                duration_ms=duration,
            ))
    
    return results


async def run_all_evals(
    skills_root: Path, 
    skill_invoker: Optional[Callable[[str, str], Any]] = None
) -> Dict[str, List[EvalResult]]:
    """Run evals for all skills under skills_root."""
    results = {}
    
    for skill_dir in skills_root.iterdir():
        if skill_dir.is_dir() and (skill_dir / "eval.yaml").exists():
            skill_name = skill_dir.name
            if skill_invoker:
                results[skill_name] = await run_skill_eval(
                    skill_name, 
                    skill_dir, 
                    lambda inp: skill_invoker(skill_name, inp)
                )
            else:
                results[skill_name] = await run_skill_eval(
                    skill_name, 
                    skill_dir, 
                    None
                )
    
    return results


def print_results(results: Dict[str, List[EvalResult]]) -> int:
    """Print results and return exit code (0 = all passed)."""
    total = 0
    passed = 0
    
    for skill_name, skill_results in results.items():
        print(f"\n=== {skill_name} ===")
        for r in skill_results:
            total += 1
            status = "PASS" if r.passed else "FAIL"
            if r.passed:
                passed += 1
            print(f"  {status} {r.case_name} ({r.duration_ms:.1f}ms)")
            if not r.passed:
                print(f"    Expected: {r.expected}")
                print(f"    Actual:   {r.actual}")
                print(f"    Error:    {r.error}")
    
    print(f"\n=== Summary: {passed}/{total} passed ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    import asyncio
    
    skills_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("skills")
    
    async def main():
        results = await run_all_evals(skills_root)
        sys.exit(print_results(results))
    
    asyncio.run(main())