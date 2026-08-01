#!/usr/bin/env python3
"""
Subagent Verifier — Adversarial verification for created files.
Every file created by a subagent must pass verification before surviving.
"""

import os
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import hashlib

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

class VerificationResult:
    """Result of a single verification check."""
    def __init__(self, check_name: str, passed: bool, message: str, severity: str = "medium"):
        self.check_name = check_name
        self.passed = passed
        self.message = message
        self.severity = severity  # low, medium, high, critical

class FileVerifier:
    """Adversarial verifier for created files."""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.results: List[VerificationResult] = []
    
    def verify_file(self, filepath: Path) -> List[VerificationResult]:
        """Run all verification checks on a file."""
        results = []
        
        if not filepath.exists():
            self.results.append(VerificationResult(
                "file_exists", False, f"File not found: {filepath}", "critical"
            ))
            return self.results
        
        content = filepath.read_text(encoding="utf-8", errors="replace")
        
        # Run all checks
        results.extend(self._check_basic_structure(filepath, content))
        results.extend(self._check_no_placeholders(content))
        results.extend(self._check_no_fabricated_output(content))
        results.extend(self._check_frontmatter(filepath, content))
        results.extend(self._check_skill_format(filepath, content))
        results.extend(self._check_no_hallucinated_commands(content))
        results.extend(self._check_syntax(filepath, content))
        
        self.results.extend(results)
        return results
    
    def _check_basic_structure(self, filepath: Path, content: str) -> List[VerificationResult]:
        """Check basic file structure."""
        results = []
        
        # Not empty
        if not content.strip():
            results.append(VerificationResult(
                "not_empty", False, "File is empty", "critical"
            ))
        else:
            results.append(VerificationResult(
                "not_empty", True, "File has content", "low"
            ))
        
        # Reasonable size
        if len(content) < 50:
            results.append(VerificationResult(
                "reasonable_size", False, f"File too small ({len(content)} chars)", "high"
            ))
        else:
            results.append(VerificationResult(
                "reasonable_size", True, f"File size OK ({len(content)} chars)", "low"
            ))
        
        return results
    
    def _check_no_placeholders(self, content: str) -> List[VerificationResult]:
        """Check for placeholder text that shouldn't survive."""
        results = []
        
        # Only flag as placeholders when used as markers (followed by :, or at start of comment/task)
        placeholder_patterns = [
            (r'\bTODO\s*:', 'TODO marker'),
            (r'\bFIXME\s*:', 'FIXME marker'),
            (r'\bXXX\s*:', 'XXX marker'),
            (r'\bPLACEHOLDER\s*:', 'PLACEHOLDER marker'),
            (r'\bCHANGEME\s*:', 'CHANGEME marker'),
        ]
        
        found = []
        lines = content.split('\n')
        in_code_block = False
        in_table = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Track code block state
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            # Track table state
            if '|' in stripped and stripped.count('|') >= 2:
                in_table = True
            elif in_table and '|' not in stripped:
                in_table = False
            
            # Allow in verification/documentation lists
            is_verification_doc = stripped.startswith(('-', '*')) and any(w in stripped.lower() for w in ['check', 'verify', 'placeholder', 'frontmatter', 'fabricated', 'hallucinated', 'skill section', 'topic index', 'anti-pattern'])
            
            if stripped.startswith('#') or in_code_block or in_table or is_verification_doc:
                continue
                
            for pattern, desc in placeholder_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    found.append(f"{desc} at line {i+1}: {line.strip()[:80]}")
        
        if found:
            results.append(VerificationResult(
                "no_placeholders", False, 
                f"Found {len(found)} placeholder marker(s): {'; '.join(found[:5])}", "high"
            ))
        else:
            results.append(VerificationResult(
                "no_placeholders", True, "No placeholder markers found", "low"
            ))
        
        return results
    
    def _check_no_fabricated_output(self, content: str) -> List[VerificationResult]:
        """Check for fabricated tool output, fake test results, etc."""
        results = []
        
        fabrication_patterns = [
            "tests pass", "tests passed", "all tests pass",
            "build successful", "deployment successful",
            "verified working", "confirmed working",
            "output:", "result:", "success:", "error:",
            "status: ok", "status: success"
        ]
        
        found = []
        for pattern in fabrication_patterns:
            if pattern.lower() in content.lower():
                # Allow in comments, checkboxes, or documentation
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern.lower() in line.lower():
                        stripped = line.strip()
                        # Allow in checkboxes, comments, or documentation
                        if (stripped.startswith('#') or 
                            stripped.startswith('- [') or 
                            stripped.startswith('* [') or
                            stripped.startswith('>') or
                            ('[' in stripped and ']' in stripped and 'x' in stripped.lower())):
                            continue
                        found.append(f"'{pattern}' at line {i+1}: {line.strip()[:80]}")
        
        if found:
            results.append(VerificationResult(
                "no_fabricated_output", False,
                f"Potential fabricated output: {'; '.join(found[:3])}", "high"
            ))
        else:
            results.append(VerificationResult(
                "no_fabricated_output", True, "No fabricated output detected", "low"
            ))
        
        return results
    
    def _check_frontmatter(self, filepath: Path, content: str) -> List[VerificationResult]:
        """Check for proper frontmatter in markdown files."""
        results = []
        
        if filepath.suffix == ".md":
            if content.startswith("---"):
                # Check required fields
                lines = content.split('\n')
                frontmatter_end = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == "---":
                        frontmatter_end = i
                        break
                
                if frontmatter_end > 0:
                    fm_text = "\n".join(lines[1:frontmatter_end])
                    required = ["name:", "description:", "trigger:", "usage:"]
                    missing = [r for r in required if r not in fm_text]
                    
                    if missing:
                        results.append(VerificationResult(
                            "frontmatter_complete", False,
                            f"Missing frontmatter fields: {missing}", "medium"
                        ))
                    else:
                        results.append(VerificationResult(
                            "frontmatter_complete", True, "Frontmatter has required fields", "low"
                        ))
                else:
                    results.append(VerificationResult(
                        "frontmatter_complete", False, "Frontmatter not closed", "medium"
                    ))
            else:
                results.append(VerificationResult(
                    "frontmatter_complete", False, "Missing frontmatter", "medium"
                ))
        
        return results
    
    def _check_skill_format(self, filepath: Path, content: str) -> List[VerificationResult]:
        """Check skill-specific format requirements."""
        results = []
        
        if "skill" in filepath.name.lower() or "skill" in str(filepath.parent).lower():
            required_sections = [
                "Core Mental Models",
                "Key Frameworks",
                "Topic Index",
                "Anti-Patterns"
            ]
            
            missing = [s for s in required_sections if s not in content]
            if missing:
                results.append(VerificationResult(
                    "skill_sections", False,
                    f"Missing skill sections: {missing}", "medium"
                ))
            else:
                results.append(VerificationResult(
                    "skill_sections", True, "Skill has required sections", "low"
                ))
        
        return results
    
    def _check_no_hallucinated_commands(self, content: str) -> List[VerificationResult]:
        """Check for commands that don't exist."""
        results = []
        
        # Look for command patterns
        import re
        cmd_pattern = r'`([a-zA-Z0-9_-]+)\s+[^`]*`'  # backtick commands
        commands = re.findall(cmd_pattern, content)
        
        known_commands = {
            'python', 'pip', 'git', 'ls', 'cd', 'cat', 'grep', 'find',
            'pytest', 'npm', 'yarn', 'docker', 'kubectl', 'terraform',
            'hermes', 'claude', 'ollama', 'curl', 'wget', 'jq',
            'mkdir', 'rm', 'cp', 'mv', 'chmod', 'chown',
            'bash', 'sh', 'zsh', 'npx', 'node', 'tsx', 'tsc', 'ts-node',
            'npx', 'pnpm', 'bun', 'deno', 'vite', 'webpack', 'esbuild',
            'json', 'jsonl', 'yaml', 'yml', 'toml', 'ini', 'cfg',
        }
        
        suspicious = []
        for cmd in commands:
            parts = cmd.split()
            if parts and parts[0] not in known_commands and len(parts[0]) > 2:
                suspicious.append(cmd)
        
        if suspicious:
            results.append(VerificationResult(
                "no_hallucinated_commands", False,
                f"Potentially hallucinated commands: {suspicious[:5]}", "medium"
            ))
        else:
            results.append(VerificationResult(
                "no_hallucinated_commands", True, "No suspicious commands", "low"
            ))
        
        return results
    
    def _check_syntax(self, filepath: Path, content: str) -> List[VerificationResult]:
        """Check syntax for code files."""
        results = []
        
        if filepath.suffix == ".py":
            try:
                import ast
                ast.parse(content)
                results.append(VerificationResult(
                    "python_syntax", True, "Python syntax valid", "low"
                ))
            except SyntaxError as e:
                results.append(VerificationResult(
                    "python_syntax", False, f"Python syntax error: {e}", "high"
                ))
        
        elif filepath.suffix in [".json", ".jsonl"]:
            try:
                json.loads(content)
                results.append(VerificationResult(
                    "json_syntax", True, "JSON syntax valid", "low"
                ))
            except json.JSONDecodeError as e:
                results.append(VerificationResult(
                    "json_syntax", False, f"JSON syntax error: {e}", "high"
                ))
        
        elif filepath.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                yaml.safe_load(content)
                results.append(VerificationResult(
                    "yaml_syntax", True, "YAML syntax valid", "low"
                ))
            except yaml.YAMLError as e:
                results.append(VerificationResult(
                    "yaml_syntax", False, f"YAML syntax error: {e}", "high"
                ))
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get verification summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        
        critical_failures = [r for r in self.results if not r.passed and r.severity == "critical"]
        high_failures = [r for r in self.results if not r.passed and r.severity == "high"]
        
        return {
            "total_checks": len(self.results),
            "passed": passed,
            "failed": failed,
            "critical_failures": len(critical_failures),
            "high_failures": len(high_failures),
            "overall_passed": failed == 0,
            "failures_by_severity": {
                "critical": [r.check_name for r in critical_failures],
                "high": [r.check_name for r in high_failures],
            }
        }


def verify_file(filepath: str, strict: bool = True) -> Tuple[bool, Dict]:
    """Main entry point for verifying a single file."""
    verifier = FileVerifier(strict_mode=strict)
    verifier.verify_file(Path(filepath))
    summary = verifier.get_summary()
    return summary["overall_passed"], summary


def verify_directory(directory: str, pattern: str = "*", strict: bool = True) -> Dict[str, Any]:
    """Verify all matching files in a directory."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return {"error": "Directory not found"}
    
    files = list(dir_path.rglob(pattern))
    results = {}
    
    for filepath in files:
        if filepath.is_file():
            passed, summary = verify_file(str(filepath), strict)
            results[str(filepath)] = {"passed": passed, "summary": summary}
    
    total = len(results)
    passed = sum(1 for r in results.values() if r["passed"])
    
    return {
        "total_files": total,
        "passed": passed,
        "failed": total - passed,
        "files": results
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Subagent Verifier - Adversarial file verification")
    parser.add_argument("path", help="File or directory to verify")
    parser.add_argument("--pattern", default="*", help="Glob pattern for directory scan")
    parser.add_argument("--strict", action="store_true", default=True, help="Strict mode")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        passed, summary = verify_file(str(path), args.strict)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{status} — {path}")
            print(f"  Checks: {summary['total_checks']}, Passed: {summary['passed']}, Failed: {summary['failed']}")
            if summary['critical_failures'] > 0:
                print(f"  🔴 Critical: {summary['failures_by_severity']['critical']}")
            if summary['high_failures'] > 0:
                print(f"  🟠 High: {summary['failures_by_severity']['high']}")
        
        sys.exit(0 if passed else 1)
    
    elif path.is_dir():
        results = verify_directory(str(path), args.pattern, args.strict)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Directory: {path}")
            print(f"  Total: {results['total_files']}, Passed: {results['passed']}, Failed: {results['failed']}")
            for filepath, result in results["files"].items():
                status = "✅" if result["passed"] else "❌"
                print(f"  {status} {filepath}")
        
        sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()