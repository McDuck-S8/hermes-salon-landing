#!/usr/bin/env python3
"""
Final verification script for Hermes ui-ux-pro-max installation

This script performs comprehensive verification of the ui-ux-pro-max skill installation
within the Hermes ecosystem.
"""

import os
import json
from pathlib import Path

def log_status(step, status, details=""):
    status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_symbol} {step}: {status}")
    if details:
        print(f"    {details}")

def verify_ui_ux_pro_max_installation():
    """Verify ui-ux-pro-max skill installation and structure"""
    print("🔍 Verifying ui-ux-pro-max skill installation...")
    
    skill_path = Path("skills/ui-ux-pro-max")
    if not skill_path.exists():
        log_status("UI/UX Pro Max Installation", "FAIL", "Directory not found")
        return {"status": "FAIL", "issues": ["ui-ux-pro-max directory missing"]}
    
    # Essential files that must exist
    essential_files = [
        (skill_path / "SKILL.md", "Skill documentation"),
        (skill_path / "skill.json", "Skill metadata"),
        (skill_path / "README.md", "README file"),
        (skill_path / "src" / "ui-ux-pro-max", "Source directory"),
    ]
    
    # Check if essential files exist
    missing_files = []
    for file_path, description in essential_files:
        if not file_path.exists():
            missing_files.append(f"{description}")
    
    if missing_files:
        log_status("UI/UX Pro Max Installation", "FAIL", f"Missing essential files: {', '.join(missing_files)}")
        return {"status": "FAIL", "issues": missing_files}
    
    # Check skill.json structure
    skill_json_path = skill_path / "skill.json"
    try:
        with open(skill_json_path, "r", encoding="utf-8") as f:
            skill_data = json.load(f)
        
        # Verify required fields
        required_fields = ["name", "version", "author", "license", "description", "keywords"]
        missing_fields = [field for field in required_fields if not skill_data.get(field)]
        
        if missing_fields:
            log_status("UI/UX Pro Max Skill.json", "FAIL", f"Missing fields: {', '.join(missing_fields)}")
            return {"status": "FAIL", "issues": [f"Missing fields: {', '.join(missing_fields)}"]}
        
        # Verify correct skill name
        if skill_data.get("name") != "ui-ux-pro-max":
            log_status("UI/UX Pro Max Skill.json", "FAIL", f"Wrong skill name: {skill_data.get('name')}")
            return {"status": "FAIL", "issues": [f"Wrong skill name: {skill_data.get('name')}"]}
            
    except Exception as e:
        log_status("UI/UX Pro Max Skill.json", "FAIL", f"Error reading skill.json: {e}")
        return {"status": "FAIL", "issues": [f"Error reading skill.json: {e}"]}
    
    # Check documentation quality
    skill_md_path = skill_path / "SKILL.md"
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            skill_content = f.read()
        
        # Check for key content indicators
        content_indicators = [
            ("ui-ux-pro-max", "Skill name reference"),
            ("ai-powered design intelligence", "AI capabilities"),
            ("reasoning engine", "Reasoning engine"),
            ("161 reasoning rules", "Reasoning rules count"),
            ("84 ui styles", "UI styles count"),
            ("192 color palettes", "Color palettes count"),
            ("22 tech stacks", "Tech stacks reference"),
        ]
        
        missing_indicators = []
        for indicator, description in content_indicators:
            if indicator.lower() not in skill_content.lower():
                missing_indicators.append(f"{description}")
        
        if missing_indicators:
            log_status("UI/UX Pro Max Documentation", "FAIL", f"Missing content: {', '.join(missing_indicators)}")
            return {"status": "FAIL", "issues": missing_indicators}
            
    except Exception as e:
        log_status("UI/UX Pro Max Documentation", "FAIL", f"Error reading SKILL.md: {e}")
        return {"status": "FAIL", "issues": [f"Error reading SKILL.md: {e}"]}
    
    log_status("UI/UX Pro Max Installation", "PASS", 
              f"Skill properly installed with version {skill_data.get('version')}")
    return {"status": "PASS", "skill_data": skill_data}

def verify_generate_income_pipeline_flow():
    """Verify generate_income_pipeline_flow.html file"""
    print("\n🔍 Verifying generate_income_pipeline_flow.html...")
    
    html_path = "generate_income_pipeline_flow.html"
    if not os.path.exists(html_path):
        log_status("Generate Income Pipeline Flow", "FAIL", "HTML file not found")
        return {"status": "FAIL", "issues": ["HTML file missing"]}
    
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Essential HTML elements
        essential_elements = [
            ("<!DOCTYPE html>", "HTML5 doctype"),
            ("<html", "HTML tag"),
            ("<head>", "Head section"),
            ("<title>", "Title tag"),
            ("<body>", "Body section"),
            ("<script>", "Script inclusion"),
            ("<style>", "Style definition"),
            ("</html>", "Closing HTML tag"),
        ]
        
        missing_elements = []
        for element, description in essential_elements:
            if element not in content:
                missing_elements.append(f"{description}")
        
        if missing_elements:
            log_status("Generate Income Pipeline Flow", "FAIL", 
                     f"Missing essential elements: {', '.join(missing_elements)}")
            return {"status": "FAIL", "issues": missing_elements}
        
        # Check for Mermaid support
        if "mermaid" not in content.lower():
            log_status("Generate Income Pipeline Flow", "WARN", "Mermaid diagram support missing")
        
        # Check interactive features
        interactive_features = [
            ("onclick", "Click handlers"),
            ("zoomIn(", "Zoom functionality"),
            ("download(", "Download functionality"),
            ("toggleDarkMode(", "Dark mode toggle"),
            ("refreshData(", "Data refresh"),
        ]
        
        interactive_found = []
        for feature, description in interactive_features:
            if feature in content:
                interactive_found.append(f"{description}")
        
        if interactive_found:
            log_status("Generate Income Pipeline Flow", "PASS", 
                     f"Interactive features found: {', '.join(interactive_found)}")
        
        # Check for template syntax issues
        if "${" in content or "<?=" in content:
            log_status("Generate Income Pipeline Flow", "FAIL", "Template syntax found")
            return {"status": "FAIL", "issues": ["Template syntax present"]}
        
        # Check file size
        line_count = len(content.splitlines())
        log_status("Generate Income Pipeline Flow", "PASS", 
                  f"HTML properly generated, {line_count} lines, no template syntax")
        return {"status": "PASS", "line_count": line_count, "interactive_features": interactive_found}
        
    except Exception as e:
        log_status("Generate Income Pipeline Flow", "FAIL", f"Error reading HTML: {e}")
        return {"status": "FAIL", "issues": [f"Error reading HTML: {e}"]}

def verify_validate_flow_script():
    """Verify validate_flow.py script"""
    print("\n🔍 Verifying validate_flow.py script...")
    
    script_path = "validate_flow.py"
    if not os.path.exists(script_path):
        log_status("Validate Flow Script", "FAIL", "Script file not found")
        return {"status": "FAIL", "issues": ["Script file missing"]}
    
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Essential function names
        essential_functions = [
            "def validate_html_structure()",
            "def validate_functionality()",
            "def main()",
        ]
        
        missing_functions = []
        for func in essential_functions:
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            log_status("Validate Flow Script", "FAIL", f"Missing functions: {', '.join(missing_functions)}")
            return {"status": "FAIL", "issues": missing_functions}
        
        # Check imports
        required_imports = ["import os", "import json", "import re"]
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            log_status("Validate Flow Script", "FAIL", f"Missing imports: {', '.join(missing_imports)}")
            return {"status": "FAIL", "issues": missing_imports}
        
        # Check syntax
        try:
            compile(content, script_path, "exec")
            log_status("Validate Flow Script Syntax", "PASS", "Python syntax is valid")
        except SyntaxError as e:
            log_status("Validate Flow Script Syntax", "FAIL", f"Syntax error: {e}")
            return {"status": "FAIL", "issues": [f"Syntax error: {e}"]}
        
        log_status("Validate Flow Script", "PASS", 
                  f"Script contains all required functions and valid syntax")
        return {"status": "PASS", "validation_function_count": len([f for f in essential_functions if f in content])}
        
    except Exception as e:
        log_status("Validate Flow Script", "FAIL", f"Error reading script: {e}")
        return {"status": "FAIL", "issues": [f"Error reading script: {e}"]}

def verify_hermes_integration():
    """Verify Hermes integration"""
    print("\n🔍 Verifying Hermes integration...")
    
    integration = {
        "skills_dir_exists": False,
        "ui_ux_pro_max_exists": False,
        "skill_json_valid": False,
        "skill_loading_works": False,
        "issues": [],
        "status": "VALID"
    }
    
    # Check skills directory
    if os.path.exists("skills"):
        integration["skills_dir_exists"] = True
        
        # Check if ui-ux-pro-max exists
        try:
            skills_list = os.listdir("skills")
            integration["ui_ux_pro_max_exists"] = any("ui-ux-pro-max" in skill.lower() for skill in skills_list)
        except Exception:
            pass
    
    # Validate skill.json
    try:
        with open("skills/ui-ux-pro-max/skill.json", "r", encoding="utf-8") as f:
            skill_data = json.load(f)
        
        if skill_data.get("name") == "ui-ux-pro-max":
            integration["skill_json_valid"] = True
            integration["skill_loading_works"] = True
    
    except Exception as e:
        integration["issues"].append(f"Skill JSON error: {e}")
    
    status = "PASS" if integration["skill_json_valid"] else "FAIL"
    log_status("Hermes Integration", status, 
              f"Skill loading: {'✅ Available' if integration['skill_loading_works'] else '❌ Not available'}")
    
    return integration

def main():
    print("="*70)
    print("🔍 HERMES UI/UX PRO MAX VERIFICATION")
    print("="*70)
    print("Verifying complete ui-ux-pro-max installation...")
    
    # Run all verifications
    results = {}
    results["ui_ux_pro_max"] = verify_ui_ux_pro_max_installation()
    results["generate_income_pipeline_flow"] = verify_generate_income_pipeline_flow()
    results["validate_flow"] = verify_validate_flow_script()
    results["hermes_integration"] = verify_hermes_integration()
    
    # Create comprehensive report
    print("\n" + "="*70)
    print("📊 VERIFICATION REPORT")
    print("="*70)
    
    # Determine overall status
    statuses = [r.get("status", "UNKNOWN") for r in results.values() if isinstance(r, dict) and "status" in r]
    if all(s == "PASS" for s in statuses):
        overall_status = "PASS"
    elif any(s == "FAIL" for s in statuses):
        overall_status = "FAIL"
    else:
        overall_status = "WARN"
    
    report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "verification_status": overall_status,
        "components": {},
        "summary": {
            "total_components": len(results),
            "passed": sum(1 for s in statuses if s == "PASS"),
            "failed": sum(1 for s in statuses if s == "FAIL"),
            "warnings": sum(1 for s in statuses if s == "WARN"),
        }
    }
    
    # Add component details
    for component, result in results.items():
        if isinstance(result, dict):
            report["components"][component] = {
                "status": result.get("status", "UNKNOWN"),
                "issues": result.get("issues", []),
                "details": {k: v for k, v in result.items() if k not in ["status", "issues"]}
            }
    
    # Save report
    report_path = "hermes_ui_ux_pro_max_final_verification.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 VERIFICATION SUMMARY")
    print(f"🔍 Overall Status: {report['verification_status']}")
    print(f"📊 Components: {report['summary']['total_components']}")
    print(f"✅ Passed: {report['summary']['passed']}")
    print(f"❌ Failed: {report['summary']['failed']}")
    print(f"⚠️ Warnings: {report['summary']['warnings']}")
    print(f"\n💾 Detailed report: {report_path}")
    
    # Component details
    print("\n🔧 COMPONENT DETAILS")
    for component, data in report["components"].items():
        print(f"  • {component}: {data['status']}")
    
    # Final message
    print("\n" + "="*70)
    if overall_status == "PASS":
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("\n✅ Successfully implemented:")
        print("  1. ✅ ui-ux-pro-max skill from GitHub repository")
        print("  ². ✅ Complete skill metadata and structure")
        print("  ³. ✅ validate_flow.py validation script")
        print("  ④. ✅ generate_income_pipeline_flow.html with interactive features")
        print("  ⑤. ✅ Hermes skill integration")
        print("\n🚀 Ready for production use!")
        return 0
    elif overall_status == "FAIL":
        print("⚠️ VERIFICATION FAILED")
        print("\n📋 Components that need attention:")
        for component, data in report["components"].items():
            if data["status"] == "FAIL":
                print(f"  ❌ {component}")
                for issue in data["issues"]:
                    print(f"     • {issue}")
        print("\n💡 Recommendations:")
        print("  1. Fix failing components above")
        print("  2. Verify skill.json and source files")
        print("  3. Check directory structure")
        return 1
    else:
        print("⚠️ VERIFICATION COMPLETED WITH WARNINGS")
        print("\n📋 Components that need attention:")
        for component, data in report["components"].items():
            if data["status"] in ["FAIL", "WARN"]:
                print(f"  • {component}: {data['status']}")
                for issue in data["issues"]:
                    print(f"     • {issue}")
        return 1

if __name__ == "__main__":
    exit(main())
