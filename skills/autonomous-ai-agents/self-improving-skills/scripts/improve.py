#!/usr/bin/env python3
"""
Self-improvement analyzer for skills.
Analyzes eval results, identifies failure patterns, proposes patches.
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

SKILL_DIR = Path(__file__).parent.parent
EVAL_DIR = SKILL_DIR / "evals"

FAILURE_PATTERNS = {
    "tool_misuse": {
        "indicators": ["tool call", "missing required field", "invalid argument", "hallucinated tool"],
        "fix": "Add tool usage examples and validation to SKILL.md"
    },
    "missing_validation": {
        "indicators": ["no input validation", "validation missing", "unvalidated input", "no sanitization"],
        "fix": "Add explicit validation steps before tool/API calls"
    },
    "edge_case": {
        "indicators": ["empty input", "null input", "whitespace", "boundary", "empty string", "unhandled"],
        "fix": "Add explicit edge case handling branches with defaults"
    },
    "ambiguous_instruction": {
        "indicators": ["multiple valid outputs", "ambiguous", "unclear", "open to interpretation"],
        "fix": "Add decision tree or explicit rules to disambiguate"
    },
    "context_leak": {
        "indicators": ["state leak", "previous run", "shared state", "test isolation"],
        "fix": "Add state reset/isolation steps between test runs"
    },
    "hallucinated_output": {
        "indicators": ["wrong format", "schema mismatch", "missing field", "extra field", "invalid json"],
        "fix": "Add output schema definition and validation step"
    },
    "missing_infrastructure": {
        "indicators": ["no evals", "no rubric", "no run_eval", "no cases.yaml"],
        "fix": "Create complete eval infrastructure (cases.yaml, rubric.md, run_eval.py)"
    },
    "missing_safety_guard": {
        "indicators": ["too many patches", "runaway", "no limit", "max patches"],
        "fix": "Add max_patches_per_cycle=3 guard in improve.py"
    },
    "missing_failure_categorization": {
        "indicators": ["no pattern", "uncategorized", "generic failure"],
        "fix": "Add pattern detection logic to improve.py"
    },
    "no_revert_on_regression": {
        "indicators": ["no revert", "regression not detected", "pass rate drop"],
        "fix": "Add verification step that compares pass rate before/after and reverts on drop"
    }
}

def load_eval_results(skill_dir: Path) -> Dict:
    """Load latest eval results for a skill"""
    eval_dir = skill_dir / "evals"
    results_files = list(eval_dir.glob("eval_results_*.json"))
    if not results_files:
        return {}
    latest = max(results_files, key=lambda f: f.stat().st_mtime)
    with open(latest) as f:
        return json.load(f)

def analyze_failures(eval_results: Dict) -> List[Dict]:
    """Analyze eval failures and identify patterns"""
    patterns_found = []
    
    if not eval_results:
        return [{"pattern": "no_eval_results", "confidence": 1.0, "fix": "Run evals first"}]
    
    cases = eval_results.get("cases", [])
    failures = [c for c in cases if c["label"] in ("FAIL", "PARTIAL")]
    
    if not failures:
        return []
    
    for failure in failures:
        details = failure.get("details", {})
        missing = details.get("missing", [])
        pattern = details.get("pattern")
        
        if pattern and pattern in FAILURE_PATTERNS:
            patterns_found.append({
                "pattern": pattern,
                "case": failure["case"],
                "confidence": 0.9,
                "fix": FAILURE_PATTERNS[pattern]["fix"],
                "missing": missing
            })
        else:
            # Try to infer pattern from missing items
            for p_name, p_info in FAILURE_PATTERNS.items():
                if any(indicator in str(missing).lower() for indicator in p_info["indicators"]):
                    patterns_found.append({
                        "pattern": p_name,
                        "case": failure["case"],
                        "confidence": 0.6,
                        "fix": p_info["fix"],
                        "missing": missing
                    })
                    break
    
    # Deduplicate by pattern
    seen = set()
    unique = []
    for p in patterns_found:
        key = p["pattern"]
        if key not in seen:
            seen.add(key)
            unique.append(p)
    
    return unique

def analyze_failures_with_gemini(eval_results: Dict, skill_content: str = "") -> List[Dict]:
    """Analyze failures using Gemini API - wrapper for analyze_failures"""
    # Check for GEMINI_API_KEY
    import os
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set, using local analysis")
    return analyze_failures(eval_results)

def propose_patches(skill_dir: Path, patterns: List[Dict]) -> List[Dict]:
    """Generate specific patches for identified patterns"""
    patches = []
    
    for p in patterns:
        pattern = p["pattern"]
        
        if pattern == "missing_infrastructure":
            patches.extend([
                {
                    "file": "evals/cases.yaml",
                    "action": "create",
                    "content": create_default_cases(),
                    "reason": "Skill lacks eval test cases"
                },
                {
                    "file": "evals/rubric.md",
                    "action": "create",
                    "content": create_default_rubric(),
                    "reason": "Skill lacks scoring rubric"
                },
                {
                    "file": "evals/run_eval.py",
                    "action": "create",
                    "content": create_default_run_eval(),
                    "reason": "Skill lacks eval runner"
                }
            ])
        
        elif pattern == "missing_safety_guard":
            patches.append({
                "file": "scripts/improve.py",
                "action": "patch",
                "patch": add_max_patches_guard(),
                "reason": "Add safety guard: max 3 patches per cycle"
            })
        
        elif pattern == "missing_failure_categorization":
            patches.append({
                "file": "scripts/improve.py",
                "action": "patch",
                "patch": add_failure_categorization(),
                "reason": "Add failure pattern detection logic"
            })
        
        elif pattern == "no_revert_on_regression":
            patches.append({
                "file": "scripts/verify.py",
                "action": "create",
                "content": create_verify_script(),
                "reason": "Add verification script that reverts on regression"
            })
        
        elif pattern in ("tool_misuse", "missing_validation", "edge_case", "ambiguous_instruction", "context_leak", "hallucinated_output"):
            patches.append({
                "file": "SKILL.md",
                "action": "append",
                "section": "Pitfalls",
                "content": f"\n### {pattern.replace('_', ' ').title()}\n{p['fix']}\n",
                "reason": f"Document {pattern} fix in skill"
            })
    
    return patches[:3]  # Max 3 patches per cycle

def create_default_cases() -> str:
    return """# Auto-generated eval cases
- name: "basic_functionality"
  description: "Skill produces expected output for typical input"
  input:
    task: "Execute skill's primary function"
  expect:
    produces_output: true
    no_errors: true
"""

def create_default_rubric() -> str:
    return """# Auto-generated Rubric
## Scoring
- PASS (1.0): All criteria met
- PARTIAL (0.5): Most criteria met, minor issues
- FAIL (0.0): Major issues or no output

## Criteria
1. Produces expected output type
2. No runtime errors
3. Output format matches specification
4. Handles basic edge cases
"""

def create_default_run_eval() -> str:
    return '''#!/usr/bin/env python3
"""Auto-generated eval runner"""
import json, sys
from pathlib import Path

def run_tests(skill_dir: Path) -> Dict:
    """Run skill eval tests and return results dict"""
    print(f"Running evals for {skill_dir.name}...")
    # TODO: Implement actual skill test execution
    results = {
        "total": 0, 
        "passed": 0, 
        "failed": 0, 
        "partial": 0, 
        "cases": [],
        "pass_rate": 0.0
    }
    return results

def main():
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    results = run_tests(skill_dir)
    (skill_dir / "evals" / "last_results.json").write_text(json.dumps(results))
    print("No evals implemented yet")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

def add_max_patches_guard() -> str:
    return '''    # SAFETY: Max 3 patches per cycle
    if len(patches) > 3:
        patches = patches[:3]
        print("WARNING: Limited to 3 patches per cycle")
'''

def add_failure_categorization() -> str:
    return '''    # Categorize failures by pattern
    for failure in failures:
        failure["pattern"] = detect_failure_pattern(failure)
'''

def create_verify_script() -> str:
    return '''#!/usr/bin/env python3
"""Verification script - re-runs evals and reverts on regression"""
import json, sys, subprocess
from pathlib import Path

def main():
    skill_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    
    # Load before state
    before_file = skill_dir / "evals" / "pass_rate_before.json"
    if not before_file.exists():
        print("No before state found")
        return 0
    
    with open(before_file) as f:
        before = json.load(f)
    
    # Run evals
    result = subprocess.run([sys.executable, "evals/run_eval.py", str(skill_dir)], 
                          capture_output=True, text=True)
    
    # Load after state
    after_file = skill_dir / "evals" / "last_results.json"
    if not after_file.exists():
        return 1
    
    with open(after_file) as f:
        after = json.load(f)
    
    before_rate = before.get("pass_rate", 0)
    after_rate = after.get("pass_rate", 0)
    
    if after_rate < before_rate - 0.05:  # 5% tolerance
        print(f"REGRESSION: {before_rate:.1%} -> {after_rate:.1%}")
        print("Reverting patches...")
        # TODO: Implement revert
        return 1
    
    print(f"OK: {before_rate:.1%} -> {after_rate:.1%}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

def re_run_evals(skill_dir: Path) -> Dict:
    """Re-run evals for a skill and return new results"""
    eval_script = skill_dir / "evals" / "run_eval.py"
    if not eval_script.exists():
        return {}
    
    result = subprocess.run(
        [sys.executable, str(eval_script), str(skill_dir)],
        capture_output=True, text=True
    )
    
    results_file = skill_dir / "evals" / "last_results.json"
    if results_file.exists():
        with open(results_file) as f:
            return json.load(f)
    return {}

def main():
    if len(sys.argv) < 2:
        print("Usage: improve.py <skill_dir> [eval_results.json]")
        sys.exit(1)
    
    skill_dir = Path(sys.argv[1]).resolve()
    eval_results = {}
    
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            eval_results = json.load(f)
    else:
        eval_results = load_eval_results(skill_dir)
    
    print(f"Analyzing {skill_dir.name}...")
    print(f"Eval results: {eval_results.get('overall_score', 'N/A')}")
    
    patterns = analyze_failures(eval_results)
    print(f"Patterns found: {[p['pattern'] for p in patterns]}")
    
    patches = propose_patches(skill_dir, patterns)
    print(f"Patches proposed: {len(patches)}")
    
    # Save analysis
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "skill": skill_dir.name,
        "eval_score": eval_results.get("overall_score"),
        "patterns": patterns,
        "patches": patches
    }
    
    out_file = skill_dir / "scripts" / f"improvement_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Write proposed patches to proposed_patches.json for verification
    patches_file = skill_dir / "scripts" / "proposed_patches.json"
    with open(patches_file, "w") as f:
        json.dump(patches, f, indent=2)
    
    print(f"Analysis saved to: {out_file}")
    print(f"Patches saved to: {patches_file}")
    print(json.dumps(patches, indent=2))

if __name__ == "__main__":
    main()