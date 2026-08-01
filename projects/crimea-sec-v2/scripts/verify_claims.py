#!/usr/bin/env python3
"""
verify-claims.py — Verify Crimea Security Framework v2 claims
Based on T3MP3ST verify-claims pattern
"""

import asyncio
import sys
from pathlib import Path

# This script is at: crimea-sec-v2/scripts/verify_claims.py
# Project root is: crimea-sec-v2/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.arsenal import create_arsenal
from src.kb import create_kb
from src.core import ConfigLoader
from src.opsec import OPSECProfile
from src.mission import MissionControl
from src.core import Phase, OperatorArchetype, FindingSeverity, MissionStatus


async def main():
    print("=" * 60)
    print("Crimea Security Framework v2 - Verify Claims")
    print("=" * 60)
    print()

    config_dir = PROJECT_ROOT / "config"
    config = ConfigLoader(config_dir)

    all_ok = True
    errors = []
    warnings = []

    # 1. Verify Arsenal
    print("📦 Verifying Arsenal...")
    arsenal = create_arsenal({"full_arsenal": True})

    builtin_tools = []
    optin_tools = []
    cli_tools = []
    approval_gated = []
    dangerous_tools = []

    for name, tool in arsenal.tools.items():
        if tool.definition.opt_in:
            optin_tools.append(name)
        elif "CLI" in tool.__class__.__name__.upper() or "CLI" in str(type(tool)):
            cli_tools.append(name)
        else:
            builtin_tools.append(name)

        if tool.definition.approval_gated:
            approval_gated.append(name)
        if tool.definition.dangerous:
            dangerous_tools.append(name)

    print(f"  ✅ Built-in tools: {len(builtin_tools)}")
    for t in sorted(builtin_tools):
        print(f"     - {t}")

    print(f"  ✅ Opt-in adapters: {len(optin_tools)}")
    for t in sorted(optin_tools):
        print(f"     - {t}")

    print(f"  ✅ CLI tool wrappers: {len(cli_tools)}")
    for t in sorted(cli_tools):
        print(f"     - {t}")

    print(f"  ⚠️  Approval-gated: {len(approval_gated)}")
    for t in sorted(approval_gated):
        print(f"     - {t}")

    print(f"  🔴 Dangerous: {len(dangerous_tools)}")
    for t in sorted(dangerous_tools):
        print(f"     - {t}")

    total_tools = len(builtin_tools) + len(optin_tools) + len(cli_tools)
    print(f"  📊 Total cataloged: {total_tools} tools")

    if total_tools < 80:
        warnings.append(f"Expected ~83 tools, found {total_tools}")

    # 2. Verify Knowledge Base
    print("\n📚 Verifying Knowledge Base...")
    kb = await create_kb(PROJECT_ROOT / "data" / "kb")

    cve_count = len(kb.cves)
    mitre_count = len(kb.mitre)
    pattern_count = len(kb.patterns)

    print(f"  ✅ CVEs: {cve_count}")
    print(f"  ✅ MITRE techniques: {mitre_count}")
    print(f"  ✅ Attack patterns: {pattern_count}")

    if cve_count < 20:
        warnings.append(f"Expected 20+ CVEs, found {cve_count}")
    if mitre_count < 15:
        warnings.append(f"Expected 15+ MITRE techniques, found {mitre_count}")
    if pattern_count < 10:
        warnings.append(f"Expected 10+ patterns, found {pattern_count}")

    # 3. Verify OPSEC Profiles
    print("\n🛡️  Verifying OPSEC Profiles...")
    opsec_data = config.load_opsec_profiles()
    profiles = opsec_data.get("profiles", [])
    print(f"  ✅ Profiles: {len(profiles)}")
    for p in profiles:
        print(f"     - {p['id']}: {p['name']} (threshold: {p['detection_risk_threshold']})")

    if len(profiles) != 5:
        warnings.append(f"Expected 5 OPSEC profiles, found {len(profiles)}")

    # 4. Verify RoE Templates
    print("\n📋 Verifying Rules of Engagement...")
    roe_data = config.load_roe_templates()
    templates = roe_data.get("templates", [])
    print(f"  ✅ Templates: {len(templates)}")
    for t in templates:
        allowed = len(t.get("allowed_phases", []))
        forbidden = len(t.get("forbidden_phases", []))
        print(f"     - {t['id']}: {t['name']} (allowed: {allowed}, forbidden: {forbidden})")

    if len(templates) < 3:
        errors.append(f"Expected 3+ RoE templates, found {len(templates)}")
        all_ok = False

    # 5. Verify Crimea Targets
    print("\n🎯 Verifying Crimea Targets...")
    targets_data = config.load_crimea_targets()
    scopes = targets_data.get("scopes", [])
    authorized = [s for s in scopes if s.get("authorized", False)]
    print(f"  ✅ Total scopes: {len(scopes)}")
    print(f"  ✅ Authorized: {len(authorized)}")
    print(f"  ⚠️  Not authorized: {len(scopes) - len(authorized)}")

    for s in scopes:
        status = "✅" if s.get("authorized") else "⚠️ "
        print(f"     {status} {s['id']}: {s['name']} ({s.get('category', 'unknown')})")

    if len(authorized) == 0:
        warnings.append("No authorized scopes configured - add authorization_refs")

    # 6. Verify Configuration
    print("\n⚙️  Verifying Default Configuration...")
    default_config = config.load_default_config()

    required_sections = ["app", "paths", "llm", "opsec", "roe", "mission", "arsenal", "kb", "evidence", "reporting", "mcp", "api", "crimea_targets", "legal"]
    for section in required_sections:
        if section in default_config:
            print(f"  ✅ {section}")
        else:
            errors.append(f"Missing config section: {section}")
            all_ok = False

    # 7. Verify MCP Server
    print("\n🔌 Verifying MCP Server...")
    mcp_server_path = PROJECT_ROOT / "src" / "mcp" / "server.py"
    if mcp_server_path.exists():
        print(f"  ✅ MCP server: {mcp_server_path}")
    else:
        errors.append("MCP server not found")
        all_ok = False

    # 8. Verify CLI
    print("\n💻 Verifying CLI...")
    cli_path = PROJECT_ROOT / "src" / "cli" / "main.py"
    if cli_path.exists():
        print(f"  ✅ CLI: {cli_path}")
    else:
        errors.append("CLI not found")
        all_ok = False

    # 9. Verify Legal Config
    print("\n⚖️  Verifying Legal Compliance...")
    legal = default_config.get("legal", {})
    laws = legal.get("applicable_laws", [])
    print(f"  ✅ Applicable laws: {len(laws)}")
    for law in laws:
        print(f"     - {law}")

    mandatory = legal.get("mandatory_controls", {})
    print(f"  ✅ Mandatory controls: {len(mandatory)}")
    for k, v in mandatory.items():
        print(f"     - {k}: {v}")

    if "152-FZ" not in laws or "187-FZ" not in laws:
        warnings.append("Missing core Russian legal references (152-FZ, 187-FZ)")

    # Summary
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    if all_ok and len(errors) == 0:
        print("✅ ALL CHECKS PASSED")
    else:
        print("❌ SOME CHECKS FAILED")

    print(f"\n📊 Statistics:")
    print(f"  Tools cataloged: {total_tools}")
    print(f"  CVEs: {cve_count}")
    print(f"  MITRE techniques: {mitre_count}")
    print(f"  Attack patterns: {pattern_count}")
    print(f"  OPSEC profiles: {len(profiles)}")
    print(f"  RoE templates: {len(templates)}")
    print(f"  Crimea scopes: {len(scopes)} ({len(authorized)} authorized)")

    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    print()
    print("=" * 60)

    return 0 if all_ok and len(errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))