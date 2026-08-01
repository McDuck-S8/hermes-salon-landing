#!/usr/bin/env python3
"""
Maintenance Scanner — Weekly Anti-Rot Scanner
Scans all 5 layers + substrate against blueprint, reports drift.
Runs as cron: 0 3 * * 0 (Sunday 03:00)
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import subprocess

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
IDENTITY_FILE = HERMES_HOME / "IDENTITY.md"
BLUEPRINT_FILE = HERMES_HOME / "os-blueprint.md"

LAYER_PATHS = {
    "identity": [HERMES_HOME / "CLAUDE.md", HERMES_HOME / "IDENTITY.md"],
    "rules": [HERMES_HOME / ".claude" / "rules" / "always.md", HERMES_HOME / ".claude" / "rules" / "never.md"],
    "skills": [HERMES_HOME / ".claude" / "skills"],
    "agents": [HERMES_HOME / ".claude" / "agents"],
    "tools": [HERMES_HOME / ".claude" / "tools"],
    "substrate": [HERMES_HOME / ".wiki"],
}

LAYER_ROT_RATES = {
    "identity": {"rate": "months", "revisit_months": 6},
    "rules": {"rate": "weeks", "revisit_months": 3},
    "skills": {"rate": "days-weeks", "revisit_months": 1},
    "agents": {"rate": "days", "revisit_months": 0.5},
    "tools": {"rate": "hours", "revisit_months": 0.25},
    "substrate": {"rate": "grows", "revisit_months": None},
}

def get_file_hash(filepath: Path) -> str:
    """Get SHA256 hash of file."""
    try:
        return hashlib.sha256(filepath.read_bytes()).hexdigest()[:16]
    except Exception:
        return "ERROR"

def get_revisit_date(filepath: Path) -> datetime:
    """Extract Revisit date from file frontmatter."""
    try:
        content = filepath.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.strip().startswith("Revisit:"):
                date_str = line.split(":", 1)[1].strip()
                return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        pass
    return None

def scan_layer(layer_name: str, paths: List[Path]) -> Dict[str, Any]:
    """Scan a single layer for drift, expiry, and health."""
    results = {
        "layer": layer_name,
        "files_scanned": 0,
        "files_missing_revisit": 0,
        "files_expired": 0,
        "files_changed": 0,
        "new_files": 0,
        "drift_items": [],
        "errors": [],
    }
    
    rot_info = LAYER_ROT_RATES.get(layer_name, {})
    revisit_months = rot_info.get("revisit_months")
    now = datetime.now()
    
    for base_path in paths:
        if not base_path.exists():
            results["errors"].append(f"Path not found: {base_path}")
            continue
        
        if base_path.is_file():
            files = [base_path]
        else:
            files = list(base_path.rglob("*"))
            files = [f for f in files if f.is_file() and not f.name.startswith(".")]
        
        for filepath in files:
            results["files_scanned"] += 1
            
            # Check Revisit date
            revisit = get_revisit_date(filepath)
            if revisit is None:
                results["files_missing_revisit"] += 1
                results["drift_items"].append({
                    "file": str(filepath.relative_to(HERMES_HOME)),
                    "issue": "missing_revisit",
                    "severity": "medium",
                    "message": "No Revisit date in frontmatter"
                })
            elif revisit_months and revisit < now:
                days_overdue = (now - revisit).days
                results["files_expired"] += 1
                severity = "high" if days_overdue > 30 else "medium"
                results["drift_items"].append({
                    "file": str(filepath.relative_to(HERMES_HOME)),
                    "issue": "expired",
                    "severity": severity,
                    "message": f"Revisit overdue by {days_overdue} days (due {revisit.strftime('%Y-%m-%d')})"
                })
            
            # Track file hash for change detection (could compare with stored hash)
            file_hash = get_file_hash(filepath)
            results["drift_items"].append({
                "file": str(filepath.relative_to(HERMES_HOME)),
                "issue": "hash_tracked",
                "severity": "info",
                "hash": file_hash
            })
    
    return results

def scan_blueprint_compliance() -> Dict[str, Any]:
    """Check if actual structure matches os-blueprint.md if it exists."""
    if not BLUEPRINT_FILE.exists():
        return {"status": "no_blueprint", "message": "os-blueprint.md not found"}
    
    # Could parse blueprint and compare with actual structure
    return {"status": "pending", "message": "Blueprint compliance check not yet implemented"}

def generate_report() -> Dict[str, Any]:
    """Generate full maintenance report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "scan_id": hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()[:12],
        "layers": {},
        "summary": {
            "total_files_scanned": 0,
            "total_missing_revisit": 0,
            "total_expired": 0,
            "total_drift_items": 0,
            "high_severity": 0,
            "medium_severity": 0,
        },
        "blueprint_compliance": scan_blueprint_compliance(),
        "recommendations": []
    }
    
    # Scan each layer
    for layer_name, paths in LAYER_PATHS.items():
        layer_result = scan_layer(layer_name, paths)
        report["layers"][layer_name] = layer_result
        
        # Aggregate
        report["summary"]["total_files_scanned"] += layer_result["files_scanned"]
        report["summary"]["total_missing_revisit"] += layer_result["files_missing_revisit"]
        report["summary"]["total_expired"] += layer_result["files_expired"]
        report["summary"]["total_drift_items"] += len(layer_result["drift_items"])
        for item in layer_result["drift_items"]:
            if item["severity"] == "high":
                report["summary"]["high_severity"] += 1
            elif item["severity"] == "medium":
                report["summary"]["medium_severity"] += 1
    
    # Generate recommendations
    if report["summary"]["total_expired"] > 0:
        report["recommendations"].append(f"URGENT: {report['summary']['total_expired']} files past Revisit date — schedule revisit interviews")
    if report["summary"]["total_missing_revisit"] > 0:
        report["recommendations"].append(f"Add Revisit frontmatter to {report['summary']['total_missing_revisit']} files")
    if report["summary"]["high_severity"] > 0:
        report["recommendations"].append(f"{report['summary']['high_severity']} high-severity drift items need immediate attention")
    
    # Rotation recommendation
    expired_by_layer = {}
    for layer_name, layer_data in report["layers"].items():
        if layer_data["files_expired"] > 0:
            expired_by_layer[layer_name] = layer_data["files_expired"]
    if expired_by_layer:
        report["recommendations"].append(f"Rotation needed: {expired_by_layer}")
    
    return report

def save_report(report: Dict[str, Any], output_dir: Path = None):
    """Save report to file."""
    if output_dir is None:
        output_dir = HERMES_HOME / "maintenance_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"maintenance_{timestamp}.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Also save as markdown for readability
    md_file = output_dir / f"maintenance_{timestamp}.md"
    md_content = format_report_markdown(report)
    md_file.write_text(md_content, encoding="utf-8")
    
    return report_file, md_file

def format_report_markdown(report: Dict[str, Any]) -> str:
    """Format report as readable markdown."""
    lines = [
        f"# Maintenance Report — {report['timestamp']}",
        f"**Scan ID**: {report['scan_id']}",
        "",
        "## Summary",
        f"- **Files Scanned**: {report['summary']['total_files_scanned']}",
        f"- **Missing Revisit**: {report['summary']['total_missing_revisit']}",
        f"- **Expired**: {report['summary']['total_expired']}",
        f"- **Drift Items**: {report['summary']['total_drift_items']}",
        f"- **High Severity**: {report['summary']['high_severity']}",
        f"- **Medium Severity**: {report['summary']['medium_severity']}",
        "",
        "## Layer Details"
    ]
    
    for layer_name, layer_data in report["layers"].items():
        lines.append(f"### {layer_name.capitalize()}")
        lines.append(f"- Files Scanned: {layer_data['files_scanned']}")
        lines.append(f"- Missing Revisit: {layer_data['files_missing_revisit']}")
        lines.append(f"- Expired: {layer_data['files_expired']}")
        if layer_data["drift_items"]:
            lines.append("- Drift Items:")
            for item in layer_data["drift_items"][:10]:  # Limit to 10
                lines.append(f"  - `{item['file']}`: {item['issue']} ({item['severity']})")
        lines.append("")
    
    if report["recommendations"]:
        lines.append("## Recommendations")
        for rec in report["recommendations"]:
            lines.append(f"- {rec}")
    
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Maintenance Scanner - Anti-Rot Weekly Scan")
    parser.add_argument("--output", help="Output directory", default=None)
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    print("🔍 Starting maintenance scan...")
    report = generate_report()
    
    output_dir = Path(args.output) if args.output else None
    json_file, md_file = save_report(report, output_dir)
    
    print(f"\n📊 Scan Complete")
    print(f"  Files Scanned: {report['summary']['total_files_scanned']}")
    print(f"  Missing Revisit: {report['summary']['total_missing_revisit']}")
    print(f"  Expired: {report['summary']['total_expired']}")
    print(f"  High Severity: {report['summary']['high_severity']}")
    print(f"  Medium Severity: {report['summary']['medium_severity']}")
    print(f"\n📁 Reports saved:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")
    
    if report["recommendations"]:
        print("\n🎯 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    # Exit code based on severity
    if report["summary"]["high_severity"] > 0:
        return 2
    elif report["summary"]["medium_severity"] > 0 or report["summary"]["total_expired"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())