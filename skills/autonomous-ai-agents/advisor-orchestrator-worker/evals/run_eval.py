#!/usr/bin/env python3
"""
Self-improving skill: run evals for advisor-orchestrator-worker.
Tests the skill's core protocol compliance, parallel dispatch, verification, etc.
"""
import json
import sys
from pathlib import Path


def test_plan_before_dispatch():
    """Test that skill requires plan before worker dispatch."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        return {"name": "plan_before_dispatch", "status": "FAIL", "error": "SKILL.md missing"}
    
    content = skill_md.read_text(encoding='utf-8')
    required = ["plan", "subtasks", "criteria", "tools"]
    missing = [r for r in required if r not in content.lower()]
    
    if missing:
        return {"name": "plan_before_dispatch", "status": "FAIL", "error": f"Missing in SKILL.md: {missing}"}
    
    return {"name": "plan_before_dispatch", "status": "PASS", "error": None}


def test_advisor_consultation():
    """Test that skill mandates advisor consultation before dispatch."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    required = ["advisor", "consult", "review", "feedback"]
    found = [r for r in required if r in content.lower()]
    
    if len(found) < 2:
        return {"name": "advisor_consultation", "status": "FAIL", "error": f"Insufficient advisor mentions: {found}"}
    
    return {"name": "advisor_consultation", "status": "PASS", "error": None}


def test_parallel_dispatch_limit():
    """Test that skill enforces max 3 concurrent workers."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    if "3 concurrent" not in content and "max 3" not in content and "max 3" not in content:
        return {"name": "parallel_dispatch_limit", "status": "FAIL", "error": "No max 3 concurrent limit found"}
    
    return {"name": "parallel_dispatch_limit", "status": "PASS", "error": None}


def test_timeout_handling():
    """Test that skill specifies timeout = fix pattern."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    if "timeout" not in content.lower():
        return {"name": "timeout_handling", "status": "FAIL", "error": "No timeout handling in SKILL.md"}
    
    if "fix" not in content.lower() and "retry" not in content.lower():
        return {"name": "timeout_handling", "status": "PARTIAL", "error": "Timeout mentioned but no fix pattern"}
    
    return {"name": "timeout_handling", "status": "PASS", "error": None}


def test_verification_step():
    """Test that skill requires verification of every worker result."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    required = ["verify", "acceptance criteria", "pass", "fix", "escalate"]
    found = [r for r in required if r in content.lower()]
    
    if len(found) < 3:
        return {"name": "verification_step", "status": "FAIL", "error": f"Insufficient verification mentions: {found}"}
    
    return {"name": "verification_step", "status": "PASS", "error": None}


def test_taste_pass():
    """Test that skill mandates taste/advisor pass before final delivery."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    if "taste" not in content.lower() and "advisor review" not in content.lower():
        return {"name": "taste_pass", "status": "FAIL", "error": "No taste/advisor pass requirement"}
    
    return {"name": "taste_pass", "status": "PASS", "error": None}


def test_delegate_task_usage():
    """Test that skill correctly uses delegate_task for workers."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    if "delegate_task" not in content:
        return {"name": "delegate_task_usage", "status": "FAIL", "error": "delegate_task not mentioned"}
    
    return {"name": "delegate_task_usage", "status": "PASS", "error": None}


def test_isolated_context():
    """Test that skill emphasizes isolated context for workers."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    content = skill_md.read_text(encoding='utf-8')
    if "isolated" not in content.lower() and "isolate" not in content.lower():
        return {"name": "isolated_context", "status": "FAIL", "error": "No isolation requirement for workers"}
    
    return {"name": "isolated_context", "status": "PASS", "error": None}


def run_all_tests():
    """Run all eval tests."""
    tests = [
        test_plan_before_dispatch,
        test_advisor_consultation,
        test_parallel_dispatch_limit,
        test_timeout_handling,
        test_verification_step,
        test_taste_pass,
        test_delegate_task_usage,
        test_isolated_context,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            results.append({"name": test.__name__, "status": "FAIL", "error": str(e)})
    
    return results


def main():
    print("Running advisor-orchestrator-worker evals...")
    results = run_all_tests()
    
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    partial = sum(1 for r in results if r['status'] == 'PARTIAL')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    pass_rate = (passed + 0.5 * partial) / total if total > 0 else 0
    
    print(f"\nResults: {total} total, {passed} passed, {partial} partial, {failed} failed")
    print(f"Pass rate: {pass_rate:.0%}")
    
    for r in results:
        status = r['status']
        name = r['name']
        error = r.get('error', '')
        print(f"  [{status}] {name}" + (f" - {error}" if error else ""))
    
    # Save results
    skill_dir = Path(__file__).parent.parent
    output = {
        "total": total,
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": results
    }
    
    (skill_dir / "evals" / "last_results.json").write_text(json.dumps(output, indent=2), encoding='utf-8')
    
    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()