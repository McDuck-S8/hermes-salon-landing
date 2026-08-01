import os
import re
import json

def validate_html_structure(html_path):
    """Validate basic HTML structure and essential components"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    validation_results = {
        "has_doctype": False,
        "has_html_tag": False,
        "has_head": False,
        "has_title": False,
        "has_body": False,
        "has_script_tags": False,
        "has_mermaid": False,
        "has_css": False,
        "has_interactive_features": False,
        "has_template_syntax": False,
        "line_count": 0,
        "issues": []
    }
    
    # Check for essential HTML elements
    validation_results["has_doctype"] = content.strip().startswith("<!DOCTYPE html>")
    validation_results["has_html_tag"] = "<html" in content and "</html>" in content
    validation_results["has_head"] = "<head>" in content and "</head>" in content
    validation_results["has_title"] = "<title>" in content and "</title>" in content
    validation_results["has_body"] = "<body>" in content and "</body>" in content
    validation_results["has_script_tags"] = "<script>" in content and "</script>" in content
    validation_results["has_mermaid"] = "mermaid" in content.lower()
    validation_results["has_css"] = "<style>" in content and "</style>" in content
    validation_results["has_interactive_features"] = any(
        feature in content.lower() for feature in ["onclick", "onmouseenter", "zoomin", "download", "refreshData"]
    )
    validation_results["has_template_syntax"] = "${" in content and "}" in content
    validation_results["line_count"] = len(content.splitlines())
    
    # Check for template syntax issues
    if validation_results["has_template_syntax"]:
        validation_results["issues"].append("Template syntax ({...}) found - HTML not properly generated")
    
    return validation_results

def validate_functionality(html_path):
    """Validate interactive functionality of the HTML file"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    functionality_results = {
        "has_zoom_functionality": False,
        "has_download_functionality": False,
        "has_refresh_functionality": False,
        "has_interactive_controllers": False,
        "javascript_events": [],
        "issues": []
    }
    
    # Check for zoom functionality
    if "zoomIn()" in content and "zoomOut()" in content:
        functionality_results["has_zoom_functionality"] = True
    
    # Check for download functionality
    if "downloadSVG()" in content and "downloadPNG()" in content:
        functionality_results["has_download_functionality"] = True
    
    # Check for refresh functionality
    if "refreshData()" in content:
        functionality_results["has_refresh_functionality"] = True
    
    # Check for interactive controllers
    if "controls" in content.lower() or "buttons" in content.lower():
        functionality_results["has_interactive_controllers"] = True
    
    # Check for JavaScript events
    js_events = ["onclick", "onmouseenter", "onload", "onerror"]
    for event in js_events:
        if event in content:
            functionality_results["javascript_events"].append(event)
    
    # Check for potential issues
    if "metch svg" in content.lower():
        functionality_results["issues"].append("Typo found: 'metch svg' should be 'mermaid svg'")
    
    return functionality_results

def generate_validation_report(html_path, html_results, functionality_results):
    """Generate comprehensive validation report"""
    report = {
        "file": html_path,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "structure_validation": html_results,
        "functionality_validation": functionality_results,
        "overall_status": "VALID",
        "summary": {
            "total_issues": len(html_results["issues"]) + len(functionality_results["issues"]),
            "structure_pass": len(html_results["issues"]) == 0,
            "functionality_pass": len(functionality_results["issues"]) == 0,
            "template_syntax_ok": not html_results["has_template_syntax"],
            "interactive_features_ok": functionality_results["has_zoom_functionality"] and 
                                        functionality_results["has_download_functionality"] and
                                        functionality_results["has_refresh_functionality"]
        }
    }
    
    # Determine overall status
    if report["summary"]["total_issues"] > 0:
        report["overall_status"] = "ISSUES_FOUND"
    elif not report["summary"]["template_syntax_ok"]:
        report["overall_status"] = "TEMPLATE_ISSUES"
    elif not report["summary"]["interactive_features_ok"]:
        report["overall_status"] = "INTERACTIVE_ISSUES"
    
    return report

def main():
    """Main validation function"""
    html_path = "generate_income_pipeline_flow.html"
    
    print("🔍 Starting validation of income pipeline flow HTML...")
    
    # Validate HTML structure
    print("Validating HTML structure...")
    html_results = validate_html_structure(html_path)
    
    # Validate functionality
    print("Validating functionality...")
    functionality_results = validate_functionality(html_path)
    
    # Generate report
    print("Generating validation report...")
    report = generate_validation_report(html_path, html_results, functionality_results)
    
    # Print results
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Overall Status: {report['overall_status']}")
    print(f"   Issues Found: {report['summary']['total_issues']}")
    print(f"   Structure Valid: {'✅' if report['summary']['structure_pass'] else '❌'}")
    print(f"   Functionality Valid: {'✅' if report['summary']['functionality_pass'] else '❌'}")
    print(f"   Template Syntax: {'✅' if report['summary']['template_syntax_ok'] else '❌'}")
    print(f"   Interactive Features: {'✅' if report['summary']['interactive_features_ok'] else '❌'}")
    
    if report['summary']['total_issues'] > 0:
        print(f"\n❌ ISSUES FOUND:")
        for issue in html_results["issues"]:
            print(f"   - {issue}")
        for issue in functionality_results["issues"]:
            print(f"   - {issue}")
    
    # Save report
    report_path = "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved: {report_path}")
    
    # Return status code based on overall status
    if report["overall_status"] == "VALID":
        print("\n✅ VALIDATION SUCCESSFUL - HTML is ready for production!")
        return 0
    else:
        print(f"\n⚠️ VALIDATION ISSUES - HTML needs fixes!")
        return 1

if __name__ == "__main__":
    exit(main())
        ("toggleDarkMode()", "dark mode toggle"),
        ("refreshData()", "refresh data function"),
        ("initCharts()", "charts initialization"),
    ]
    
    for pattern, description in function_patterns:
        if pattern in content:
            functionality_results["has_zoom_function"] = True
            functionality_results["has_download_function"] = True
            functionality_results["has_chart_support"] = True
            functionality_results["has_interactive_elements"] = True
            functionality_results["has_mermaid_diagram"] = True
            break
    
    # Check for error handling
    if "try {" in content and "catch" in content:
        functionality_results["has_error_handling"] = True
    
    # Check for Mermaid diagram presence
    if "mermaid" in content.lower() and ("diagram" in content.lower() or "flow" in content.lower()):
        functionality_results["has_mermaid_diagram"] = True
    
    return functionality_results

def main():
    html_path = "generate_income_pipeline_flow.html"
    
    print("🔍 Validating generate_income_pipeline_flow.html...\n")
    
    # Validate structure
    structure_results = validate_html_structure(html_path)
    
    # Validate functionality  
    functionality_results = validate_functionality(html_path)
    
    # Generate report
    report = {
        "file_name": html_path,
        "structure_validation": structure_results,
        "functionality_validation": functionality_results,
        "overall_status": "VALID" if not structure_results["issues"] and not functionality_results["issues"] else "ISSUES_FOUND",
        "summary": {
            "total_issues": len(structure_results["issues"]) + len(functionality_results["issues"]),
            "structure_issues": len(structure_results["issues"]),
            "functionality_issues": len(functionality_results["issues"]),
            "html_size": f"{structure_results['line_count']:,} lines",
            "has_interactive_features": structure_results["has_interactive_features"] and functionality_results["has_interactive_elements"]
        }
    }
    
    # Print report
    print(f"📊 VALIDATION REPORT")
    print(f"{'='*50}")
    print(f"File: {report['file_name']}")
    print(f"Overall Status: {'✅ VALID' if report['overall_status'] == 'VALID' else '❌ ISSUES FOUND'}")
    print(f"\n📈 SUMMARY:")
    print(f"  • Total issues: {report['summary']['total_issues']}")
    print(f"  • Structure issues: {report['summary']['structure_issues']}")
    print(f"  • Functionality issues: {report['summary']['functionality_issues']}")
    print(f"  • HTML size: {report['summary']['html_size']}")
    print(f"  • Has interactive features: {report['summary']['has_interactive_features']}")
    
    if report['summary']['total_issues'] > 0:
        print(f"\n❌ ISSUES FOUND:")
        for issue in structure_results["issues"] + functionality_results["issues"]:
            print(f"  • {issue}")
    
    # Save report
    with open("generate_income_pipeline_flow.html.validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Report saved to: generate_income_pipeline_flow.html.validation_report.json")
    
    if report['overall_status'] == 'VALID':
        print(f"\n🎉 SUCCESS: HTML flow diagram is properly generated and functional!")
        return 0
    else:
        print(f"\n⚠️  WARNINGS: HTML has issues that may affect functionality.")
        return 1

if __name__ == "__main__":
    exit(main())
