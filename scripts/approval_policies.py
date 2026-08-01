#!/usr/bin/env python3
"""
Approval Policies — Pre-deployment content scanning for private data leaks.
Run before ANY deploy/publish action. Blocks if private patterns detected.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# ─── PRIVATE DATA PATTERNS (NEVER DEPLOY) ───
PRIVATE_PATTERNS = [
    # Geographic constraints
    (r"(?i)\bcrimea\b", "Crimea geographic constraint"),
    (r"(?i)\bworks? in crimea\b", "Crimea operational claim"),
    
    # KYC / Documents
    (r"(?i)\bno\s*kyc\b", "No KYC claim"),
    (r"(?i)\bkyc\s*free\b", "KYC-free claim"),
    (r"(?i)\bno\s*documents?\b", "No documents claim"),
    (r"(?i)\bwithout\s*documents?\b", "Without documents claim"),
    (r"(?i)\bno\s*verification\b", "No verification claim"),
    
    # Payout methods
    (r"(?i)\busdt\s*payout\b", "USDT payout method"),
    (r"(?i)\busdt\s*withdraw\b", "USDT withdraw method"),
    (r"(?i)\bp2p\s*offramp\b", "P2P offramp method"),
    (r"(?i)\bp2p\s*withdraw\b", "P2P withdraw method"),
    (r"(?i)\bcard\s*withdraw\b", "Card withdraw method"),
    (r"(?i)\bтбанк\b", "T-Bank reference"),
    (r"(?i)\btinkoff\b", "Tinkoff reference"),
    
    # Personal circumstances
    (r"(?i)\bmy\s+circumstances\b", "Personal circumstances"),
    (r"(?i)\bpersonal\s+constraint\b", "Personal constraint"),
    (r"(?i)\binternal\s+only\b", "Internal only marking"),
]

# ─── SAFE PATTERNS (ALLOWED IN PUBLIC) ───
SAFE_PATTERNS = [
    (r"(?i)\binstant\s+approval\b", "Instant approval"),
    (r"(?i)\bfast\s+onboarding\b", "Fast onboarding"),
    (r"(?i)\bcompetitive\s+rates?\b", "Competitive rates"),
    (r"(?i)\breliable\s+payouts?\b", "Reliable payouts"),
    (r"(?i)\bexclusive\s+offer\b", "Exclusive offer"),
]


def scan_content(content: str, filepath: str) -> List[Tuple[str, str, int]]:
    """
    Scan content for private patterns.
    Returns: List of (pattern_name, matched_text, line_number)
    """
    violations = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern, name in PRIVATE_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Check if it's in a comment/string that's clearly internal
                context = line[max(0, match.start()-20):match.end()+20]
                violations.append((name, match.group(), i, context.strip()))
    
    return violations


def scan_file(filepath: Path) -> List[Tuple[str, str, int]]:
    """Scan a single file for private data."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        return scan_content(content, str(filepath))
    except Exception as e:
        return [("SCAN_ERROR", str(e), 0, str(filepath))]


def scan_directory(root: Path, extensions: List[str] = None) -> dict:
    """Scan directory for private data leaks."""
    if extensions is None:
        extensions = ['.py', '.html', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']
    
    results = {"clean": [], "violations": {}}
    
    for ext in extensions:
        for file in root.rglob(f"*{ext}"):
            if file.is_file():
                violations = scan_file(file)
                if violations:
                    results["violations"][str(file)] = violations
                else:
                    results["clean"].append(str(file))
    
    return results


def check_and_report(root: Path = None) -> int:
    """
    Main entry point. Returns exit code:
    0 = clean
    1 = violations found
    2 = error
    """
    if root is None:
        root = Path(__file__).parent.parent
    
    print(f"🔍 Scanning for private data leaks in: {root}")
    print("=" * 60)
    
    results = scan_directory(root)
    
    if results["violations"]:
        print(f"\n❌ VIOLATIONS FOUND: {len(results['violations'])} files")
        print("-" * 60)
        
        for filepath, violations in results["violations"].items():
            print(f"\n📁 {filepath}")
            for name, matched, line_no, context in violations:
                print(f"  Line {line_no}: [{name}] '{matched}'")
                print(f"    Context: ...{context}...")
        
        print("\n" + "=" * 60)
        print("🛑 DEPLOY BLOCKED — Private data detected")
        print("Fix all violations before deploying.")
        return 1
    else:
        print(f"\n✅ CLEAN — {len(results['clean'])} files scanned, 0 violations")
        return 0


if __name__ == "__main__":
    # Allow scanning specific path
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    exit(check_and_report(target))