#!/usr/bin/env python3
"""
Hermes Hooks Integration — обёртка над инструментами для внедрения
Self-Conscience Gate и Pre-Edit Git Versioning в workflow.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from self_conscience_gate import self_conscience_gate
from pre_edit_git import git_version_before_edit

def pre_action_hook(action: str, target_path: str = None) -> tuple[bool, str]:
    """
    Вызывается ПЕРЕД любым значимым действием:
    - patch / write_file / terminal (write)
    - cronjob create
    - delegate_task
    - skill_manage create/edit
    """
    # 1. Self-Conscience Gate
    allowed, reason = self_conscience_gate(action, target_path)
    if not allowed:
        return False, reason
    
    # 2. Pre-Edit Git Versioning (только для файловых операций)
    if target_path and any(op in action.lower() for op in ["edit", "write", "patch", "modify", "create"]):
        if not git_version_before_edit(target_path):
            return False, f"❌ Git versioning failed for {target_path}"
    
    return True, "✅ Pre-action hooks passed"


def post_action_hook(action: str, target_path: str = None, result: dict = None) -> None:
    """
    Вызывается ПОСЛЕ действия для логирования в Knowledge Cube.
    """
    # Log to Knowledge Cube via hermes_hooks
    try:
        from hermes_hooks import get_hooks
        hooks = get_hooks()
        hooks.on_task_complete(
            f"Action: {action}",
            f"Target: {target_path}, Result: {result}",
            ["action-log", "self-conscience"]
        )
    except Exception:
        pass  # silent fail - hooks are optional


def verify_result_hook(action: str, target_path: str = None, expected_artifact: str = None) -> tuple[bool, str]:
    """
    Проверяет что действие дало РЕАЛЬНЫЙ результат (не просто "файл создан").
    """
    if not expected_artifact:
        return True, "No artifact specified to verify"
    
    artifact_path = Path(expected_artifact)
    if not artifact_path.exists():
        return False, f"❌ Expected artifact not found: {expected_artifact}"
    
    # Additional checks based on artifact type
    if expected_artifact.endswith(".py"):
        # Try to run syntax check
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "py_compile", str(artifact_path)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, f"❌ Syntax error in {expected_artifact}: {result.stderr}"
        except Exception as e:
            return False, f"❌ Verification failed: {e}"
    
    elif expected_artifact.endswith((".html", ".json", ".md")):
        # Check file is not empty
        if artifact_path.stat().st_size == 0:
            return False, f"❌ Artifact is empty: {expected_artifact}"
    
    return True, f"✅ Verified: {expected_artifact}"


def main():
    if len(sys.argv) < 3:
        print("Usage: python hermes_hooks_integration.py <pre|post|verify> <action> [target_path] [expected_artifact]")
        sys.exit(1)
    
    hook_type = sys.argv[1]
    action = sys.argv[2]
    target_path = sys.argv[3] if len(sys.argv) > 3 else None
    expected_artifact = sys.argv[4] if len(sys.argv) > 4 else None
    
    if hook_type == "pre":
        allowed, reason = pre_action_hook(action, target_path)
        print(reason)
        sys.exit(0 if allowed else 1)
    
    elif hook_type == "post":
        post_action_hook(action, target_path)
        print("✅ Post-action hook executed")
        sys.exit(0)
    
    elif hook_type == "verify":
        ok, msg = verify_result_hook(action, target_path, expected_artifact)
        print(msg)
        sys.exit(0 if ok else 1)
    
    else:
        print(f"Unknown hook type: {hook_type}")
        sys.exit(1)


if __name__ == "__main__":
    main()