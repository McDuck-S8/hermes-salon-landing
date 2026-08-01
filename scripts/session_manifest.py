"""
Session Manifest Verification Module
=====================================
Records SHA256 hashes for key system files at session start.

> Revisit: when manifest verification logic, hash algorithms, or cross-session persistence changes. Last touched: 2026-07-02.
Verifies them at next session start to detect changes.

Usage:
    python session_manifest.py record    # Record current hashes
    python session_manifest.py verify    # Verify against stored manifest (default)
"""

import hashlib
import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

# Resolve HERMES_HOME relative to this script
HERMES_HOME = Path(__file__).resolve().parent.parent

# Cache directory for manifest storage
CACHE_DIR = HERMES_HOME / "cache"
MANIFEST_FILE = CACHE_DIR / "session_manifest.json"

# Key system files to track (relative to HERMES_HOME)
KEY_SYSTEM_FILES = [
    # Core configuration
    "config.yaml",
    "config.json",

    # Main entry points
    "main.py",
    "cli.py",

    # Core scripts
    "scripts/self_system.py",
    "scripts/session_recall.py",
    "scripts/proactive_engine.py",
    "scripts/autonomous_agent.py",
    "scripts/event_bus.py",
    "scripts/event_daemon.py",
    "scripts/procedural_executor.py",
    "scripts/action_executor.py",
    "scripts/session_manifest.py",

    # Critical skills
    "skills/hermes-agent/SKILL.md",
    "skills/PROCEDURAL_SKILLS.md",

    # Core constants if exists
    "hermes_constants.py",
]


def _calculate_hash(file_path: Path) -> str:
    """Calculate SHA256 hash for a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (FileNotFoundError, PermissionError) as e:
        return f"ERROR: {str(e)}"


def _file_exists(file_path: Path) -> tuple[bool, str]:
    """Check if file exists and return status."""
    if file_path.exists():
        return True, "exists"
    return False, "file not found"


def _check_syntax(file_path: Path) -> tuple[bool, str]:
    """Check Python syntax using py_compile."""
    if not file_path.suffix == ".py":
        return True, "not Python"
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, "syntax ok"
    except py_compile.PyCompileError as e:
        return False, f"syntax error: {e}"


def record_changes() -> dict:
    """
    Record current SHA256 hashes for all key system files.
    
    Returns:
        dict with 'recorded' (list of file hashes), 'timestamp', and 'status'
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    recorded_files = {}
    for rel_path in KEY_SYSTEM_FILES:
        full_path = HERMES_HOME / rel_path
        if full_path.exists():
            recorded_files[rel_path] = {
                "hash": _calculate_hash(full_path),
                "size": full_path.stat().st_size,
                "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
            }
    
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "files": recorded_files,
        "total_files": len(recorded_files),
        "hermes_home": str(HERMES_HOME)
    }
    
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    return {
        "recorded": recorded_files,
        "timestamp": manifest["timestamp"],
        "status": "success",
        "manifest_file": str(MANIFEST_FILE)
    }


def verify_manifest() -> dict:
    """
    Verify current files against stored manifest.
    
    Returns:
        dict with 'verified' (list of unchanged files) and 'broken' (list of changed files with reason)
    """
    if not MANIFEST_FILE.exists():
        return {
            "verified": [],
            "broken": [],
            "error": "No manifest found. Run 'python session_manifest.py record' first.",
            "status": "no_manifest"
        }
    
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    verified = []
    broken = []
    
    for rel_path, stored_info in manifest.get("files", {}).items():
        full_path = HERMES_HOME / rel_path
        exists, existence_reason = _file_exists(full_path)
        
        if not exists:
            broken.append({
                "file": rel_path,
                "reason": f"File missing: {existence_reason}"
            })
            continue
        
        current_hash = _calculate_hash(full_path)
        
        if current_hash == stored_info["hash"]:
            verified.append({
                "file": rel_path,
                "hash": current_hash
            })
        else:
            broken.append({
                "file": rel_path,
                "reason": f"Hash mismatch (content changed)",
                "old_hash": stored_info["hash"][:16] + "...",
                "new_hash": current_hash[:16] + "..."
            })
    
    # Check for new files not in manifest
    for rel_path in KEY_SYSTEM_FILES:
        if rel_path not in manifest.get("files", {}):
            full_path = HERMES_HOME / rel_path
            if full_path.exists():
                verified.append({
                    "file": rel_path,
                    "hash": _calculate_hash(full_path),
                    "note": "new file (not in previous manifest)"
                })
    
    # Check syntax of Python files
    syntax_issues = []
    for item in verified:
        full_path = HERMES_HOME / item["file"]
        syntax_ok, syntax_msg = _check_syntax(full_path)
        if not syntax_ok:
            syntax_issues.append({
                "file": item["file"],
                "reason": syntax_msg
            })
    
    for item in broken:
        full_path = HERMES_HOME / item["file"]
        if full_path.exists():
            syntax_ok, syntax_msg = _check_syntax(full_path)
            if not syntax_ok:
                syntax_issues.append({
                    "file": item["file"],
                    "reason": syntax_msg
                })
    
    status = "ok" if not broken and not syntax_issues else "changes_detected"
    
    return {
        "verified": verified,
        "broken": broken,
        "syntax_issues": syntax_issues,
        "manifest_timestamp": manifest.get("timestamp", "unknown"),
        "current_timestamp": datetime.now().isoformat(),
        "status": status
    }


def _print_result(result: dict, mode: str):
    """Pretty print verification results."""
    if mode == "record":
        print(f"[OK] Recorded {len(result['recorded'])} files")
        print(f"[MANIFEST] Saved to: {result['manifest_file']}")
        for rel_path, info in result['recorded'].items():
            print(f"   [FILE] {rel_path}: {info['hash'][:16]}...")
        print(f"[MANIFEST] Timestamp: {result.get('manifest_timestamp', 'unknown')}")
    else:
        print(f"[ERROR] {result['error']}")
elif action == "verify":
    if result.get("success"):
        print(f"[OK] Verified: {len(result['verified'])} files")
        for item in result['verified']:
            note = f" ({item['note']})" if item.get('note') else ""
            print(f"   [FILE] {item['file']}{note}")
        if result.get("broken"):
            print(f"[WARN] Changed/Missing: {len(result['broken'])} files")
            for item in result['broken']:
                print(f"   [FAIL] {item['file']}: {item['reason']}")
        if result.get("syntax_issues"):
            print(f"[WARN] Syntax issues: {len(result['syntax_issues'])} files")
            for item in result['syntax_issues']:
                print(f"   [WARN] {item['file']}: {item['reason']}")
    else:
        if result.get('verified'):
            print("[OK] All files verified successfully!")
        else:
            print("[WARN] Changes detected since last recording")


def main():
    """Main entry point for CLI."""
    mode = "verify" if len(sys.argv) < 2 else sys.argv[1].lower()
    
    if mode == "record":
        result = record_changes()
        _print_result(result, "record")
    elif mode == "verify":
        result = verify_manifest()
        _print_result(result, "verify")
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python session_manifest.py [record|verify]")
        sys.exit(1)


if __name__ == "__main__":
    main()
