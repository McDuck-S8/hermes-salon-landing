#!/usr/bin/env python3
"""
Skill Scanner — security audit for agent skills based on SkillSpector rules.

Scans SKILL.md files and associated scripts for:
- Prompt injection patterns
- Data exfiltration
- Dangerous code execution
- Privilege escalation
- Supply chain risks

Usage:
    python scripts/skill_scanner.py                    # scan all skills
    python scripts/skill_scanner.py --skill ponytail   # scan one skill
    python scripts/skill_scanner.py --format json      # JSON output
"""
import re
import sys
import json
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
SKILLS_DIRS = [
    HERMES_HOME / "skills",
    Path.home() / ".claude" / "skills",
]

# SkillSpector rule patterns (simplified from 64 rules)
RULES = {
    # Prompt Injection
    "P1_instruction_override": {
        "severity": "HIGH",
        "category": "Prompt Injection",
        "patterns": [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+(all\s+)?prior",
            r"forget\s+(everything|all|prior)",
            r"override\s+safety",
            r"bypass\s+(safety|security|filter)",
        ],
    },
    "P2_hidden_instructions": {
        "severity": "HIGH",
        "category": "Prompt Injection",
        "patterns": [
            r"<!--.*?-->",
            r"\[HIDDEN\]",
            r"system\s*:\s*you\s+are",
            r"ASSISTANT:\s*",
        ],
    },
    "P3_exfiltration_commands": {
        "severity": "HIGH",
        "category": "Data Exfiltration",
        "patterns": [
            r"send\s+(all|every|the)\s+(data|info|context|conversation)",
            r"transmit\s+to\s+external",
            r"upload\s+(all|everything)\s+to",
            r"curl.*?(POST|PUT).*?(https?://(?!localhost|127\.0\.0\.1))",
        ],
    },
    # Data Exfiltration
    "E1_external_transmission": {
        "severity": "MEDIUM",
        "category": "Data Exfiltration",
        "patterns": [
            r"requests\.(post|put|patch)\s*\(\s*[\"']https?://(?!localhost|127\.0\.0\.1)",
            r"urllib\.request\.urlopen\s*\(\s*[\"']https?://(?!localhost|127\.0\.0\.1)",
            r"fetch\s*\(\s*[\"']https?://(?!localhost|127\.0\.0\.1)",
        ],
    },
    "E2_env_harvesting": {
        "severity": "HIGH",
        "category": "Data Exfiltration",
        "patterns": [
            r"os\.environ\.items\s*\(\s*\)",
            r"os\.environ\.get\s*\(\s*[\"'].*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)",
            r"process\.env\.(API_KEY|SECRET|TOKEN|PASSWORD)",
        ],
    },
    "E3_file_enumeration": {
        "severity": "MEDIUM",
        "category": "Data Exfiltration",
        "patterns": [
            r"os\.listdir\s*\(\s*[\"']/etc",
            r"os\.listdir\s*\(\s*[\"']/root",
            r"glob\.glob\s*\(\s*[\"']~\/\.(ssh|gnupg|aws|config)",
            r"Path\s*\(\s*[\"']~\/\.(ssh|gnupg|aws)",
        ],
    },
    # Privilege Escalation
    "PE2_sudo_root": {
        "severity": "MEDIUM",
        "category": "Privilege Escalation",
        "patterns": [
            r"sudo\s+",
            r"subprocess\.run\s*\(\s*\[?\s*[\"']sudo",
            r"os\.system\s*\(\s*[\"']sudo",
        ],
    },
    "PE3_credential_access": {
        "severity": "HIGH",
        "category": "Privilege Escalation",
        "patterns": [
            r"open\s*\(\s*[\"']~\/\.ssh\/",
            r"open\s*\(\s*[\"']~\/\.aws\/",
            r"cat\s+[\"']~\/\.ssh\/",
            r"\.env\b.*?(read|open|load)",
        ],
    },
    # Supply Chain
    "SC2_external_script": {
        "severity": "HIGH",
        "category": "Supply Chain",
        "patterns": [
            r"curl\s+.*?\|\s*(bash|sh|python|node)",
            r"wget\s+.*?\|\s*(bash|sh|python|node)",
            r"eval\s*\(\s*.*?(request|fetch|download)",
        ],
    },
    "SC3_obfuscated_code": {
        "severity": "HIGH",
        "category": "Supply Chain",
        "patterns": [
            r"base64\.b64decode\s*\(.*?\)\s*\)",
            r"exec\s*\(\s*.*?base64",
            r"eval\s*\(\s*.*?atob\s*\(",
            r"\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}",
        ],
    },
    # Dangerous Code Execution
    "AST1_exec_call": {
        "severity": "CRITICAL",
        "category": "Code Execution",
        "patterns": [
            r"\bexec\s*\(",
            r"\bexec\s*\[",
        ],
    },
    "AST2_eval_call": {
        "severity": "HIGH",
        "category": "Code Execution",
        "patterns": [
            r"\beval\s*\(",
        ],
    },
    "AST4_subprocess": {
        "severity": "HIGH",
        "category": "Code Execution",
        "patterns": [
            r"subprocess\.(run|call|Popen|check_output)\s*\(",
            r"os\.system\s*\(",
            r"os\.popen\s*\(",
        ],
    },
    # Output Handling
    "OH1_unvalidated_output": {
        "severity": "HIGH",
        "category": "Output Handling",
        "patterns": [
            r"innerHTML\s*=",
            r"document\.write\s*\(",
            r"dangerouslySetInnerHTML",
        ],
    },
    # System Prompt Leakage
    "P6_direct_leakage": {
        "severity": "HIGH",
        "category": "Prompt Leakage",
        "patterns": [
            r"print\s*\(\s*.*?(system|prompt|instructions)",
            r"echo\s+.*?(system|prompt|instructions)",
            r"return\s+.*?(system_prompt|instructions)",
        ],
    },
    # Memory Poisoning
    "MP1_persistent_injection": {
        "severity": "HIGH",
        "category": "Memory Poisoning",
        "patterns": [
            r"write.*?MEMORY\.md",
            r"append.*?MEMORY\.md",
            r"overwrite.*?memory",
            r"always\s+(remember|recall|use)\s+this",
        ],
    },
}


def scan_file(filepath: Path) -> list[dict]:
    """Scan a single file for vulnerability patterns."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    lines = content.split("\n")
    for rule_id, rule in RULES.items():
        for pattern in rule["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "rule": rule_id,
                        "severity": rule["severity"],
                        "category": rule["category"],
                        "file": str(filepath),
                        "line": i,
                        "code": line.strip()[:120],
                    })
    return findings


def scan_skill(skill_dir: Path) -> dict:
    """Scan a complete skill directory."""
    findings = []
    files_scanned = 0

    if skill_dir.is_file():
        findings = scan_file(skill_dir)
        return {"skill": skill_dir.name, "files": 1, "findings": findings}

    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".py", ".js", ".ts", ".sh", ".yaml", ".yml", ".json", ".toml"):
            findings.extend(scan_file(f))
            files_scanned += 1

    return {"skill": skill_dir.name, "files": files_scanned, "findings": findings}


def calculate_risk(findings: list[dict]) -> dict:
    """Calculate risk score from findings."""
    score = 0
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for f in findings:
        sev = f["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        if sev == "CRITICAL":
            score += 50
        elif sev == "HIGH":
            score += 25
        elif sev == "MEDIUM":
            score += 10
        elif sev == "LOW":
            score += 5

    score = min(100, score)

    if score <= 20:
        recommendation = "SAFE"
    elif score <= 50:
        recommendation = "CAUTION"
    elif score <= 80:
        recommendation = "DO NOT INSTALL"
    else:
        recommendation = "DANGEROUS"

    return {
        "score": score,
        "severity": "LOW" if score <= 20 else "MEDIUM" if score <= 50 else "HIGH" if score <= 80 else "CRITICAL",
        "recommendation": recommendation,
        "critical": severity_counts["CRITICAL"],
        "high": severity_counts["HIGH"],
        "medium": severity_counts["MEDIUM"],
        "low": severity_counts["LOW"],
    }


def main():
    args = sys.argv[1:]
    fmt = "terminal"
    target_skill = None
    output_file = None

    for i, a in enumerate(args):
        if a == "--format" and i + 1 < len(args):
            fmt = args[i + 1]
        elif a == "--skill" and i + 1 < len(args):
            target_skill = args[i + 1]
        elif a == "--output" and i + 1 < len(args):
            output_file = args[i + 1]

    # Collect skills to scan
    skills_to_scan = []
    if target_skill:
        for d in SKILLS_DIRS:
            p = d / target_skill
            if p.exists():
                skills_to_scan.append(p)
                break
        if not skills_to_scan:
            print(f"Skill not found: {target_skill}")
            sys.exit(1)
    else:
        for d in SKILLS_DIRS:
            if d.exists():
                for p in d.iterdir():
                    if p.is_dir() and not p.name.startswith("."):
                        skills_to_scan.append(p)

    print(f"Scanning {len(skills_to_scan)} skills...\n")

    all_results = []
    total_findings = 0
    total_files = 0

    for skill_dir in sorted(skills_to_scan):
        result = scan_skill(skill_dir)
        all_results.append(result)
        total_findings += len(result["findings"])
        total_files += result["files"]

        if result["findings"]:
            risk = calculate_risk(result["findings"])
            icon = "CRITICAL" if risk["score"] > 80 else "WARNING" if risk["score"] > 20 else "OK"
            print(f"  [{icon}] {result['skill']}: {len(result['findings'])} findings (risk: {risk['score']}/100)")
            for f in result["findings"][:5]:
                print(f"    {f['severity']:8s} {f['rule']:30s} {f['file'].split('/')[-1]}:{f['line']}")
            if len(result["findings"]) > 5:
                print(f"    ... and {len(result['findings']) - 5} more")
        else:
            print(f"  [OK] {result['skill']}: clean")

    # Summary
    all_findings = []
    for r in all_results:
        all_findings.extend(r["findings"])

    overall_risk = calculate_risk(all_findings)

    print(f"\n{'='*60}")
    print(f"SCAN COMPLETE")
    print(f"  Skills scanned: {len(skills_to_scan)}")
    print(f"  Files scanned:  {total_files}")
    print(f"  Findings:       {total_findings}")
    print(f"  Risk Score:     {overall_risk['score']}/100")
    print(f"  Severity:       {overall_risk['severity']}")
    print(f"  Recommendation: {overall_risk['recommendation']}")
    print(f"  Critical: {overall_risk['critical']} | High: {overall_risk['high']} | Medium: {overall_risk['medium']} | Low: {overall_risk['low']}")
    print(f"{'='*60}")

    # Save report
    if fmt == "json" or output_file:
        report = {
            "timestamp": datetime.now().isoformat(),
            "skills_scanned": len(skills_to_scan),
            "files_scanned": total_files,
            "total_findings": total_findings,
            "risk": overall_risk,
            "results": all_results,
        }
        out = output_file or "skill_scan_report.json"
        Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nReport saved: {out}")


if __name__ == "__main__":
    main()
