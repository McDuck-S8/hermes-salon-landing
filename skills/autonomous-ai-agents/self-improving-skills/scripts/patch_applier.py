#!/usr/bin/env python3
"""
Patch applier for self-improving skills.
Applies patches, verifies improvement, reverts on regression.
"""
import json
import sys
import subprocess
from pathlib import Path


def apply_patch(skill_dir: Path, patch: dict) -> dict:
    """Apply a single patch"""
    file_path = skill_dir / patch.get("file", "")
    action = patch.get("action", "patch")
    change_type = patch.get("change_type", "replace")
    
    try:
        if action == "create":
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(patch.get("new_text", ""), encoding='utf-8')
            return {"file": str(file_path), "success": True, "action": "created"}
        
        elif action == "replace" or change_type == "replace":
            if not file_path.exists():
                return {"file": str(file_path), "success": False, "error": "File not found"}
            content = file_path.read_text(encoding='utf-8')
            old_text = patch.get("old_text", "")
            new_text = patch.get("new_text", "")
            if old_text not in content:
                return {"file": str(file_path), "success": False, "error": "old_text not found"}
            content = content.replace(old_text, new_text, 1)
            file_path.write_text(content, encoding='utf-8')
            return {"file": str(file_path), "success": True, "action": "replaced"}
        
        elif action == "insert" or change_type == "insert":
            if not file_path.exists():
                return {"file": str(file_path), "success": False, "error": "File not found"}
            content = file_path.read_text(encoding='utf-8')
            anchor = patch.get("old_text", "") or patch.get("anchor", "")
            new_text = patch.get("new_text", "")
            if anchor not in content:
                return {"file": str(file_path), "success": False, "error": "anchor not found"}
            content = content.replace(anchor, anchor + new_text, 1)
            file_path.write_text(content, encoding='utf-8')
            return {"file": str(file_path), "success": True, "action": "inserted"}
        
        elif action == "delete" or change_type == "delete":
            if not file_path.exists():
                return {"file": str(file_path), "success": False, "error": "File not found"}
            content = file_path.read_text(encoding='utf-8')
            old_text = patch.get("old_text", "")
            if old_text not in content:
                return {"file": str(file_path), "success": False, "error": "old_text not found"}
            content = content.replace(old_text, "", 1)
            file_path.write_text(content, encoding='utf-8')
            return {"file": str(file_path), "success": True, "action": "deleted"}
        
        elif action == "patch":
            # Apply unified diff
            diff = patch.get("patch", "") or patch.get("diff", "")
            if not diff:
                return {"file": str(file_path), "success": False, "error": "No diff content"}
            
            # Check if patch applies cleanly
            result = subprocess.run(
                ["git", "apply", "--check", "-"],
                input=diff.encode(),
                capture_output=True,
                cwd=skill_dir
            )
            if result.returncode != 0:
                return {"file": str(file_path), "success": False, "error": f"Patch check failed: {result.stderr.decode()}"}
            
            # Apply
            result = subprocess.run(
                ["git", "apply", "-"],
                input=diff.encode(),
                capture_output=True,
                cwd=skill_dir
            )
            if result.returncode == 0:
                return {"file": str(file_path), "success": True, "action": "patched"}
            return {"file": str(file_path), "success": False, "error": f"Patch apply failed: {result.stderr.decode()}"}
        
        else:
            return {"file": str(file_path), "success": False, "error": f"Unknown action: {action}"}
    
    except Exception as e:
        return {"file": str(file_path), "success": False, "error": str(e)}


def apply_patches(skill_dir: Path, patches: list) -> list:
    """Apply multiple patches"""
    return [apply_patch(skill_dir, p) for p in patches]


def re_run_evals(skill_dir: Path) -> dict:
    """Re-run evals for a skill"""
    eval_script = skill_dir / "evals" / "run_eval.py"
    if not eval_script.exists():
        return {}
    
    result = subprocess.run(
        [sys.executable, str(eval_script), str(skill_dir)],
        capture_output=True, text=True
    )
    
    results_file = skill_dir / "evals" / "last_results.json"
    if results_file.exists():
        return json.loads(results_file.read_text(encoding='utf-8'))
    return {}


def verify_improvement(skill_dir: Path, before_results: dict, after_results: dict) -> dict:
    """Compare before/after pass rates"""
    before_rate = before_results.get("pass_rate", before_results.get("overall_score", 0))
    after_rate = after_results.get("pass_rate", after_results.get("overall_score", 0))
    
    improved = after_rate > before_rate
    regressed = after_rate < before_rate - 0.05
    
    return {
        "before_rate": before_rate,
        "after_rate": after_rate,
        "improved": improved,
        "regressed": regressed,
        "delta": after_rate - before_rate
    }


def revert_patches(skill_dir: Path) -> bool:
    """Revert all changes in skill directory using git"""
    try:
        repo_root = skill_dir.parent.parent.parent
        result = subprocess.run(
            ["git", "checkout", "HEAD", "--", str(skill_dir.relative_to(repo_root))],
            cwd=repo_root, capture_output=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Revert failed: {e}")
        return False


def log_improvement(skill_dir: Path, skill_name: str, pattern: str, 
                   before_rate: float, after_rate: float, reverted: bool):
    """Log improvement to .improvement-log.json"""
    log_file = skill_dir / ".improvement-log.json"
    entries = []
    if log_file.exists():
        entries = json.loads(log_file.read_text(encoding='utf-8'))
    
    entries.append({
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "skill": skill_name,
        "pattern": pattern,
        "pass_rate_before": before_rate,
        "pass_rate_after": after_rate,
        "reverted": reverted
    })
    
    log_file.write_text(json.dumps(entries, indent=2), encoding='utf-8')


def verify(skill_dir: Path, patches_file: Path) -> bool:
    """Main verification flow"""
    # Load patches
    patches = json.loads(patches_file.read_text(encoding='utf-8'))
    
    # Load before state
    before_file = skill_dir / "evals" / "last_results.json"
    before_results = {}
    if before_file.exists():
        before_results = json.loads(before_file.read_text(encoding='utf-8'))
    
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
    
    pattern = patches[0].get("pattern", "unknown") if patches else "unknown"
    
    if verification['regressed']:
        print("REGRESSION DETECTED - Reverting...")
        # Revert using git
        subprocess.run(["git", "checkout", "HEAD", "--", str(skill_dir)], 
                      cwd=skill_dir.parent.parent.parent, capture_output=True)
        log_improvement(skill_dir, skill_dir.name, pattern,
                       verification['before_rate'], verification['after_rate'], True)
        return False
    
    if not verification['improved']:
        print("NO IMPROVEMENT - Reverting...")
        subprocess.run(["git", "checkout", "HEAD", "--", str(skill_dir)], 
                      cwd=skill_dir.parent.parent.parent, capture_output=True)
        log_improvement(skill_dir, skill_dir.name, pattern,
                       verification['before_rate'], verification['after_rate'], True)
        return False
    
    print("IMPROVEMENT VERIFIED")
    log_improvement(skill_dir, skill_dir.name, pattern,
                   verification['before_rate'], verification['after_rate'], False)
    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: patch_applier.py <skill_dir> <patches.json>")
        sys.exit(1)
    
    skill_dir = Path(sys.argv[1]).resolve()
    patches_file = Path(sys.argv[2]).resolve()
    
    success = verify(skill_dir, patches_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()