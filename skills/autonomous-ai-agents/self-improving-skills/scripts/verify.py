#!/usr/bin/env python3
"""
Self-improving skill: verify patches by re-running evals.
Applies patches, re-runs evals, checks for improvement, reverts on regression.
"""
import json
import sys
import subprocess
from pathlib import Path


def apply_patches(skill_dir: Path, patches: list) -> list:
    """Apply patches to skill files. Returns list of results."""
    results = []
    for patch in patches:
        file_path = skill_dir / patch.get("file", "")
        action = patch.get("action", "patch")
        
        try:
            if action == "create":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(patch.get("content", ""), encoding='utf-8')
                results.append({"file": str(file_path), "success": True, "action": "created"})
            elif action == "append":
                # Append to section in markdown
                content = file_path.read_text(encoding='utf-8')
                section = patch.get("section", "")
                new_content = patch.get("content", "")
                if section in content:
                    content = content.replace(section, section + new_content)
                    file_path.write_text(content, encoding='utf-8')
                    results.append({"file": str(file_path), "success": True, "action": "appended"})
                else:
                    results.append({"file": str(file_path), "success": False, "error": f"Section not found: {section}"})
            elif action == "patch":
                # Apply unified diff
                diff = patch.get("patch", "")
                if diff:
                    # Use git apply or patch command
                    result = subprocess.run(["git", "apply", "--check", "-"], 
                                          input=diff.encode(), capture_output=True, cwd=skill_dir)
                    if result.returncode == 0:
                        subprocess.run(["git", "apply", "-"], input=diff.encode(), cwd=skill_dir)
                        results.append({"file": str(file_path), "success": True, "action": "patched"})
                    else:
                        results.append({"file": str(file_path), "success": False, "error": "Patch doesn't apply cleanly"})
                else:
                    results.append({"file": str(file_path), "success": False, "error": "No patch content"})
            else:
                results.append({"file": str(file_path), "success": False, "error": f"Unknown action: {action}"})
        except Exception as e:
            results.append({"file": str(file_path), "success": False, "error": str(e)})
    
    return results


def re_run_evals(skill_dir: Path) -> dict:
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


def verify_improvement(skill_dir: Path, before_results: dict, after_results: dict) -> dict:
    """Compare before/after pass rates. Return verification result."""
    before_rate = before_results.get("pass_rate", before_results.get("overall_score", 0))
    after_rate = after_results.get("pass_rate", after_results.get("overall_score", 0))
    
    improved = after_rate > before_rate
    regressed = after_rate < before_rate - 0.05  # 5% tolerance
    
    return {
        "before_rate": before_rate,
        "after_rate": after_rate,
        "improved": improved,
        "regressed": regressed,
        "delta": after_rate - before_rate
    }


def revert_patches(skill_dir: Path, applied_patches: list):
    """Revert applied patches using git"""
    try:
        # Reset to HEAD
        subprocess.run(["git", "checkout", "HEAD", "--", str(skill_dir)], 
                      capture_output=True, cwd=skill_dir.parent.parent.parent)
        return True
    except Exception as e:
        print(f"Revert failed: {e}")
        return False


def log_improvement(skill_dir: Path, skill_name: str, pattern: str, 
                   before_rate: float, after_rate: float, reverted: bool):
    """Log improvement to .improvement-log.json"""
    log_file = skill_dir / ".improvement-log.json"
    entries = []
    if log_file.exists():
        with open(log_file) as f:
            entries = json.load(f)
    
    entries.append({
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "skill": skill_name,
        "pattern": pattern,
        "pass_rate_before": before_rate,
        "pass_rate_after": after_rate,
        "reverted": reverted
    })
    
    with open(log_file, "w") as f:
        json.dump(entries, f, indent=2)


def verify(skill_dir: Path, patches_file: Path) -> bool:
    """Main verification flow"""
    # Load patches
    with open(patches_file) as f:
        patches = json.load(f)
    
    # Load before state
    before_file = skill_dir / "evals" / "last_results.json"
    before_results = {}
    if before_file.exists():
        with open(before_file) as f:
            before_results = json.load(f)
    
    # Apply patches
    print("Applying patches...")
    results = apply_patches(skill_dir, patches)
    print(f"Applied: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    if not all(r['success'] for r in results):
        print("Some patches failed to apply")
        return False
    
    # Re-run evals
    print("Re-running evals...")
    after_results = re_run_evals(skill_dir)
    
    # Verify
    verification = verify_improvement(skill_dir, before_results, after_results)
    print(f"Before: {verification['before_rate']:.1%}")
    print(f"After:  {verification['after_rate']:.1%}")
    print(f"Delta:  {verification['delta']:+.1%}")
    print(f"Improved: {verification['improved']}")
    print(f"Regressed: {verification['regressed']}")
    
    if verification['regressed']:
        print("REGRESSION DETECTED - Reverting...")
        revert_patches(skill_dir, results)
        log_improvement(skill_dir, skill_dir.name, patches[0].get("pattern", "unknown"),
                       verification['before_rate'], verification['after_rate'], True)
        return False
    
    if not verification['improved']:
        print("NO IMPROVEMENT - Reverting...")
        revert_patches(skill_dir, results)
        log_improvement(skill_dir, skill_dir.name, patches[0].get("pattern", "unknown"),
                       verification['before_rate'], verification['after_rate'], True)
        return False
    
    print("IMPROVEMENT VERIFIED")
    log_improvement(skill_dir, skill_dir.name, patches[0].get("pattern", "unknown"),
                   verification['before_rate'], verification['after_rate'], False)
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: verify.py <skill_dir> <patches.json>")
        sys.exit(1)
    
    skill_dir = Path(sys.argv[1]).resolve()
    patches_file = Path(sys.argv[2]).resolve()
    
    success = verify(skill_dir, patches_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()