#!/usr/bin/env python3
"""
LLM Filter — analyzes skill scan findings and removes false positives.

Reads skill_scan_report.json, checks each finding's context,
and determines if it's a real threat or documentation/example code.
"""
import json
import re
from pathlib import Path

REPORT = Path("D:/Portable_Soft/hermes/cache/skill_scan_report.json")
OUTPUT = Path("D:/Portable_Soft/hermes/cache/skill_scan_filtered.json")

# False positive indicators
FALSE_POSITIVE_PATTERNS = {
    "P2_hidden_instructions": [
        r"^#{1,6}\s",           # markdown headers
        r"^\|",                 # markdown tables
        r"^\*\*",               # bold text
        r"ASSISTANT:",          # prompt template markers
        r"SYSTEM:",             # prompt template markers
        r"USER:",               # prompt template markers
        r"Human:",              # conversation markers
        r"Assistant:",          # conversation markers
        r"^```",                # code blocks
        r"example",             # example sections
        r"sample",              # sample sections
        r"template",            # template sections
        r"reference",           # reference docs
    ],
    "AST4_subprocess": [
        r"#\s*(example|sample|demo|test|usage)",  # comments indicating example
        r'""".*?subprocess',   # docstring with subprocess
        r"Usage:",             # usage instructions
        r"How to use",         # usage instructions
    ],
    "AST1_exec_call": [
        r"#\s*(example|demo|test)",
        r'""".*?exec\(',
        r"red.?teaming",
        r"godmode",
        r"jailbreak",
    ],
    "AST2_eval_call": [
        r"#\s*(example|demo|test)",
        r'""".*?eval\(',
    ],
    "E2_env_harvesting": [
        r"os\.environ\.get\s*\(\s*[\"'](API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)",  # legitimate API key usage
        r"api_key\s*=\s*os\.environ",
        r"token\s*=\s*os\.environ",
    ],
    "PE3_credential_access": [
        r"#\s*(configure|setup|install|auth)",  # setup instructions
        r"chmod\s+600",  # secure file permissions
        r"ssh-keygen",  # key generation
    ],
    "PE2_sudo_root": [
        r"docker",  # docker commands often use sudo
        r"systemctl",  # service management
        r"apt|yum|brew",  # package managers
    ],
    "P3_exfiltration_commands": [
        r"#\s*(send|transmit|upload|post)",  # comments
        r"webhook",  # webhook URLs
        r"notification",  # notification systems
    ],
    "SC2_external_script": [
        r"curl.*?github\.com",  # downloading from GitHub
        r"pip install",  # package installation
        r"npm install",  # package installation
        r"brew install",  # package installation
    ],
    "P1_instruction_override": [
        r"#\s*(ignore|override|bypass)",  # comments about ignoring
        r"security.*?test",
        r"penetration.*?test",
    ],
    "E1_external_transmission": [
        r"api\.openai\.com",  # legitimate API calls
        r"api\.anthropic\.com",
        r"webhook",
        r"notification",
    ],
    "P6_direct_leakage": [
        r"#\s*(print|output|return|display)",  # comments
        r"logging",
        r"debug",
    ],
    "MP1_persistent_injection": [
        r"memory.*?system",
        r"knowledge.*?base",
        r"session.*?context",
    ],
    "OH1_unvalidated_output": [
        r"innerHTML",  # web development patterns
        r"template",
        r"render",
    ],
    "SC3_obfuscated_code": [
        r"base64.*?encode",
        r"encoding",
        r"decode.*?example",
    ],
}


def is_false_positive(finding: dict, file_content: str) -> tuple[bool, str]:
    """Determine if a finding is a false positive."""
    rule = finding["rule"]
    line_num = finding["line"]
    code = finding["code"]

    # Get context (5 lines around)
    lines = file_content.split("\n")
    start = max(0, line_num - 6)
    end = min(len(lines), line_num + 5)
    context = "\n".join(lines[start:end])

    # Check if this is documentation/example code
    fp_patterns = FALSE_POSITIVE_PATTERNS.get(rule, [])

    for pattern in fp_patterns:
        if re.search(pattern, context, re.IGNORECASE):
            return True, f"Documentation/example context"

    # Check if the finding is in a comment or docstring
    stripped = code.strip()
    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
        return True, "In comment"

    # Check if it's in a markdown code block
    if stripped.startswith("```") or stripped.startswith("    "):
        return True, "In code block"

    # Specific rule checks
    if rule == "P2_hidden_instructions":
        # HTML comments in markdown are normal
        if "<!--" in code and "-->" in code:
            return True, "HTML comment in markdown"
        # ASSISTANT:/SYSTEM: in prompt templates is normal
        if re.match(r"^(ASSISTANT|SYSTEM|USER|Human|Assistant):", stripped):
            return True, "Prompt template marker"

    if rule.startswith("AST") and "subprocess" in rule.lower():
        # subprocess in documentation examples
        if "example" in context.lower() or "usage" in context.lower():
            return True, "Example code"

    if rule == "E2_env_harvesting":
        # os.environ.get("API_KEY") is legitimate
        if re.search(r"os\.environ\.get\s*\(\s*[\"']\w+", code):
            return True, "Legitimate env var access"

    return False, "Real finding"


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    filtered_results = []
    total_filtered = 0
    total_real = 0

    for result in report["results"]:
        skill_name = result["skill"]
        filtered_findings = []

        for finding in result["findings"]:
            filepath = Path(finding["file"])
            if not filepath.exists():
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            is_fp, reason = is_false_positive(finding, content)

            if is_fp:
                total_filtered += 1
                finding["filtered"] = True
                finding["filter_reason"] = reason
            else:
                total_real += 1
                finding["filtered"] = False

            filtered_findings.append(finding)

        filtered_results.append({
            "skill": skill_name,
            "files": result["files"],
            "total_findings": len(filtered_findings),
            "real_findings": sum(1 for f in filtered_findings if not f.get("filtered")),
            "filtered_findings": sum(1 for f in filtered_findings if f.get("filtered")),
            "findings": filtered_findings,
        })

    # Calculate real risk
    real_findings = []
    for r in filtered_results:
        for f in r["findings"]:
            if not f.get("filtered"):
                real_findings.append(f)

    # Risk scoring for real findings only
    score = 0
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in real_findings:
        sev = f["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        if sev == "CRITICAL": score += 50
        elif sev == "HIGH": score += 25
        elif sev == "MEDIUM": score += 10
        elif sev == "LOW": score += 5
    score = min(100, score)

    print("=" * 60)
    print("LLM FILTER RESULTS")
    print("=" * 60)
    print(f"Total findings:     {report['total_findings']}")
    print(f"False positives:    {total_filtered}")
    print(f"Real findings:      {total_real}")
    print(f"Filter rate:        {total_filtered/report['total_findings']*100:.0f}%")
    print()
    print(f"Real risk score:    {score}/100")
    print(f"Real severity:      {'LOW' if score<=20 else 'MEDIUM' if score<=50 else 'HIGH' if score<=80 else 'CRITICAL'}")
    print(f"  CRITICAL: {severity_counts['CRITICAL']}")
    print(f"  HIGH:     {severity_counts['HIGH']}")
    print(f"  MEDIUM:   {severity_counts['MEDIUM']}")
    print(f"  LOW:      {severity_counts['LOW']}")
    print()

    # Show real findings
    if real_findings:
        print("REAL FINDINGS:")
        for f in real_findings:
            skill = Path(f["file"]).parts[-3] if len(Path(f["file"]).parts) > 3 else "unknown"
            fname = Path(f["file"]).name
            code_safe = f['code'][:100].encode('ascii', 'replace').decode('ascii')
            print(f"  {f['severity']:8s} {f['rule']:30s} {skill}/{fname}:{f['line']}")
            print(f"           {code_safe}")
    else:
        print("NO REAL FINDINGS — all were false positives")

    print("=" * 60)

    # Save filtered report
    output = {
        "timestamp": report["timestamp"],
        "original_findings": report["total_findings"],
        "filtered_out": total_filtered,
        "real_findings": total_real,
        "filter_rate": f"{total_filtered/report['total_findings']*100:.0f}%",
        "real_risk_score": score,
        "results": filtered_results,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFiltered report: {OUTPUT}")


if __name__ == "__main__":
    main()
