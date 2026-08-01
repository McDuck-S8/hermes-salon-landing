#!/usr/bin/env python3
"""
CLI for Crimea Security Framework v2
"""

from __future__ import annotations
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ConfigLoader
from src.mission import MissionControl, create_mission_from_scope
from src.core import Phase, FindingSeverity, MissionStatus
from src.kb import create_kb
from src.arsenal import create_arsenal
from src.opsec import OPSECProfile, OPSECController

console = Console()


@click.group()
@click.version_option(version="2.0.0", prog_name="crimea-sec")
@click.option("--config-dir", type=click.Path(exists=True), help="Config directory")
@click.pass_context
def cli(ctx, config_dir):
    """Crimea Security Framework v2 - Legal penetration testing for Crimea/Russia"""
    ctx.ensure_object(dict)
    ctx.obj["config_dir"] = Path(config_dir) if config_dir else PROJECT_ROOT / "config"


# ==================== MISSION COMMANDS ====================

@cli.group()
def mission():
    """Mission management"""
    pass


@mission.command("create")
@click.option("--name", required=True, help="Mission name")
@click.option("--description", required=True, help="Mission description")
@click.option("--scope", "scope_id", required=True, help="Scope ID from config/crimea-targets.yaml")
@click.option("--roe", "roe_template", default="strict", help="RoE template: strict, permissive, bugbounty, crimea_gov")
@click.option("--opsec", "opsec_profile", default="balanced", help="OPSEC profile: silent, balanced, aggressive, apt, redteam")
@click.pass_context
def mission_create(ctx, name, description, scope_id, roe_template, opsec_profile):
    """Create a new mission from predefined scope"""

    async def _create():
        config = ConfigLoader(ctx.obj["config_dir"])
        scope = config.get_scope_by_id(scope_id)

        if not scope:
            console.print(f"[red]Scope not found: {scope_id}[/red]")
            return

        if not scope.get("authorized", False):
            console.print(f"[yellow]Warning: Scope {scope_id} is not authorized![/yellow]")
            console.print(f"Authorization required: {scope.get('authorization_ref', 'Unknown')}")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Creating mission...", total=None)
            mission = await create_mission_from_scope(
                scope_id=scope_id,
                name=name,
                description=description,
                roe_template=roe_template,
                opsec_profile=opsec_profile,
                config_dir=ctx.obj["config_dir"]
            )
            progress.update(task, completed=True)

        console.print(Panel.fit(
            f"[green]Mission created successfully![/green]\n\n"
            f"Mission ID: {mission.mission_id}\n"
            f"Name: {mission.name}\n"
            f"Scope: {scope_id} ({scope['name']})\n"
            f"RoE: {roe_template}\n"
            f"OPSEC: {opsec_profile}\n"
            f"Status: {mission.status.value}",
            title="Mission Created",
            border_style="green"
        ))

    asyncio.run(_create())


@mission.command("start")
@click.argument("mission_id")
@click.pass_context
def mission_start(ctx, mission_id):
    """Start a mission"""

    async def _start():
        mc = MissionControl(ctx.obj["config_dir"])
        mission = mc.get_mission(mission_id)

        if not mission:
            console.print(f"[red]Mission not found: {mission_id}[/red]")
            return

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Starting mission...", total=None)
            await mc.start_mission(mission_id)
            progress.update(task, completed=True)

        console.print(f"[green]Mission started: {mission_id}[/green]")
        console.print(f"Current phase: {mission.current_phase.value if mission.current_phase else 'N/A'}")

    asyncio.run(_start())


@mission.command("status")
@click.argument("mission_id")
@click.pass_context
def mission_status(ctx, mission_id):
    """Show mission status"""

    async def _status():
        mc = MissionControl(ctx.obj["config_dir"])
        mission = mc.get_mission(mission_id)

        if not mission:
            console.print(f"[red]Mission not found: {mission_id}[/red]")
            return

        table = Table(title=f"Mission Status: {mission.name} ({mission_id})")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Mission ID", mission.mission_id)
        table.add_row("Name", mission.name)
        table.add_row("Status", mission.status.value)
        table.add_row("Current Phase", mission.current_phase.value if mission.current_phase else "N/A")
        table.add_row("Phases Completed", ", ".join([p.value for p in mission.phases_completed]) or "None")
        table.add_row("Targets", str(len(mission.targets)))
        table.add_row("Findings", str(len(mission.findings)))
        table.add_row("Evidence Items", str(len(mission.evidence)))
        table.add_row("Operators", str(len(mission.operators)))
        table.add_row("Detection Risk", f"{mission.detection_risk:.1%}")
        table.add_row("Started", mission.started_at.isoformat() if mission.started_at else "N/A")
        table.add_row("Completed", mission.completed_at.isoformat() if mission.completed_at else "N/A")

        console.print(table)

        # Show targets
        if mission.targets:
            targets_table = Table(title="Targets")
            targets_table.add_column("Target ID")
            targets_table.add_column("Identifier")
            targets_table.add_column("Type")
            targets_table.add_column("Status")
            for t in mission.targets.values():
                targets_table.add_row(t.target_id, t.identifier, t.target_type, t.status)
            console.print(targets_table)

        # Show findings by severity
        if mission.findings:
            findings_table = Table(title="Findings by Severity")
            findings_table.add_column("Severity")
            findings_table.add_column("Count")
            for sev in FindingSeverity:
                count = len(mission.get_findings_by_severity(sev))
                if count > 0:
                    findings_table.add_row(sev.value.upper(), str(count))
            console.print(findings_table)

    asyncio.run(_status())


@mission.command("list")
@click.pass_context
def mission_list(ctx):
    """List all missions"""
    mc = MissionControl(ctx.obj["config_dir"])
    missions = mc.list_missions()

    if not missions:
        console.print("[yellow]No missions found[/yellow]")
        return

    table = Table(title="Missions")
    table.add_column("Mission ID")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Phase")
    table.add_column("Targets")
    table.add_column("Findings")
    table.add_column("Created")

    for m in missions:
        table.add_row(
            m.mission_id,
            m.name,
            m.status.value,
            m.current_phase.value if m.current_phase else "N/A",
            str(len(m.targets)),
            str(len(m.findings)),
            m.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)


@mission.command("report")
@click.argument("mission_id")
@click.option("--format", "formats", multiple=True, default=["html", "json"], help="Report formats")
@click.pass_context
def mission_report(ctx, mission_id, formats):
    """Generate mission report"""

    async def _report():
        mc = MissionControl(ctx.obj["config_dir"])
        mission = mc.get_mission(mission_id)

        if not mission:
            console.print(f"[red]Mission not found: {mission_id}[/red]")
            return

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Generating report...", total=None)
            reports = await mc.generate_report(mission_id, list(formats))
            progress.update(task, completed=True)

        console.print(f"[green]Reports generated for mission {mission_id}[/green]")
        for fmt, content in reports.items():
            console.print(f"  {fmt}: {len(content)} chars")

    asyncio.run(_report())


# ==================== RECON COMMANDS ====================

@cli.group()
def recon():
    """Reconnaissance operations"""
    pass


@recon.command("run")
@click.argument("target")
@click.option("--modules", default="dns,subdomain,cert,whois,tech,wayback", help="Comma-separated modules")
@click.option("--opsec", default="balanced", help="OPSEC profile")
@click.pass_context
def recon_run(ctx, target, modules, opsec):
    """Run passive reconnaissance on target"""

    async def _recon():
        config = ConfigLoader(ctx.obj["config_dir"])
        kb = await create_kb(config.load_default_config().get("kb", {}).get("cve_db_path", "data/kb"))

        module_list = [m.strip() for m in modules.split(",")]

        console.print(f"[cyan]Running reconnaissance on {target}[/cyan]")
        console.print(f"Modules: {', '.join(module_list)}")
        console.print(f"OPSEC: {opsec}")

        # TODO: Implement actual recon using arsenal tools
        console.print("[yellow]Recon module not yet fully implemented[/yellow]")
        console.print("Use 'crimea-sec mission create' + 'mission start' for full workflow")

    asyncio.run(_recon())


# ==================== SCAN COMMANDS ====================

@cli.group()
def scan():
    """Active security scanning"""
    pass


@scan.command("run")
@click.argument("target")
@click.option("--types", default="port,service,vuln,dir,ssl", help="Scan types")
@click.option("--opsec", default="balanced", help="OPSEC profile")
@click.option("--roe", default="strict", help="RoE template")
@click.pass_context
def scan_run(ctx, target, types, opsec, roe):
    """Run active security scan on target"""

    async def _scan():
        console.print(f"[cyan]Running scan on {target}[/cyan]")
        console.print(f"Types: {types}")
        console.print(f"OPSEC: {opsec}")
        console.print(f"RoE: {roe}")
        console.print("[yellow]Scan module not yet fully implemented[/yellow]")

    asyncio.run(_scan())


# ==================== KNOWLEDGE BASE COMMANDS ====================

@cli.group()
def kb():
    """Knowledge base queries"""
    pass


@kb.command("cve")
@click.argument("cve_id")
@click.pass_context
def kb_cve(ctx, cve_id):
    """Query CVE details"""

    async def _cve():
        kb = await create_kb()
        cve = kb.get_cve(cve_id)
        if cve:
            console.print_json(json.dumps(cve.to_dict(), indent=2))
        else:
            console.print(f"[red]CVE not found: {cve_id}[/red]")

    asyncio.run(_cve())


@kb.command("mitre")
@click.argument("technique_id")
@click.pass_context
def kb_mitre(ctx, technique_id):
    """Query MITRE ATT&CK technique"""

    async def _mitre():
        kb = await create_kb()
        tech = kb.get_technique(technique_id)
        if tech:
            console.print_json(json.dumps(tech.to_dict(), indent=2))
        else:
            console.print(f"[red]Technique not found: {technique_id}[/red]")

    asyncio.run(_mitre())


@kb.command("pattern")
@click.argument("pattern_id")
@click.pass_context
def kb_pattern(ctx, pattern_id):
    """Query attack pattern"""

    async def _pattern():
        kb = await create_kb()
        pattern = kb.get_pattern(pattern_id)
        if pattern:
            console.print_json(json.dumps(pattern.to_dict(), indent=2))
        else:
            console.print(f"[red]Pattern not found: {pattern_id}[/red]")

    asyncio.run(_pattern())


@kb.command("search")
@click.option("--product", help="Search CVEs by product")
@click.option("--tag", help="Search CVEs by tag")
@click.option("--tactic", help="Search MITRE techniques by tactic")
@click.option("--category", help="Search patterns by category")
@click.pass_context
def kb_search(ctx, product, tag, tactic, category):
    """Search knowledge base"""

    async def _search():
        kb = await create_kb()

        if product:
            cves = kb.get_cves_by_product(product)
            console.print(f"[cyan]CVEs for {product}:[/cyan]")
            for c in cves:
                console.print(f"  {c.cve_id}: {c.description[:80]}... (CVSS: {c.cvss31_score})")

        if tag:
            cves = kb.get_cves_by_tag(tag)
            console.print(f"[cyan]CVEs with tag '{tag}':[/cyan]")
            for c in cves:
                console.print(f"  {c.cve_id}: {c.description[:80]}... (CVSS: {c.cvss31_score})")

        if tactic:
            techs = kb.get_techniques_by_tactic(tactic)
            console.print(f"[cyan]MITRE techniques for {tactic}:[/cyan]")
            for t in techs:
                console.print(f"  {t.technique_id}: {t.name}")

        if category:
            patterns = kb.get_patterns_by_category(category)
            console.print(f"[cyan]Patterns for {category}:[/cyan]")
            for p in patterns:
                console.print(f"  {p.pattern_id}: {p.name} ({p.severity})")

    asyncio.run(_search())


# ==================== TOOLS COMMANDS ====================

@cli.group()
def tools():
    """Tool management"""
    pass


@tools.command("list")
@click.pass_context
def tools_list(ctx):
    """List available tools"""
    config = ConfigLoader(ctx.obj["config_dir"])
    arsenal = create_arsenal(config.load_default_config().get("arsenal", {}))

    table = Table(title="Available Tools")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Description")
    table.add_column("Opt-in")
    table.add_column("Approval")
    table.add_column("Dangerous")

    for name, tool in sorted(arsenal.tools.items()):
        d = tool.definition
        table.add_row(
            name,
            d.category.value,
            d.description[:60] + "..." if len(d.description) > 60 else d.description,
            "✅" if d.opt_in else "❌",
            "✅" if d.approval_gated else "❌",
            "🔴" if d.dangerous else "❌"
        )

    console.print(table)


@tools.command("info")
@click.argument("tool_name")
@click.pass_context
def tools_info(ctx, tool_name):
    """Show tool details"""
    config = ConfigLoader(ctx.obj["config_dir"])
    arsenal = create_arsenal(config.load_default_config().get("arsenal", {}))
    tool = arsenal.get_tool(tool_name)

    if not tool:
        console.print(f"[red]Tool not found: {tool_name}[/red]")
        return

    d = tool.definition
    console.print(Panel.fit(
        f"[bold]{d.name}[/bold]\n\n"
        f"Category: {d.category.value}\n"
        f"Description: {d.description}\n"
        f"Version: {d.version or 'N/A'}\n"
        f"Author: {d.author or 'N/A'}\n"
        f"License: {d.license or 'N/A'}\n"
        f"Homepage: {d.homepage or 'N/A'}\n"
        f"Tags: {', '.join(d.tags) if d.tags else 'None'}\n"
        f"Opt-in: {'Yes' if d.opt_in else 'No'}\n"
        f"Approval Gated: {'Yes' if d.approval_gated else 'No'}\n"
        f"Dangerous: {'Yes' if d.dangerous else 'No'}\n",
        title=f"Tool: {tool_name}",
        border_style="cyan"
    ))


# ==================== SCOPE COMMANDS ====================

@cli.group()
def scope():
    """Scope management"""
    pass


@scope.command("list")
@click.pass_context
def scope_list(ctx):
    """List all scopes"""
    config = ConfigLoader(ctx.obj["config_dir"])
    scopes = config.load_crimea_targets().get("scopes", [])

    table = Table(title="Crimea Scopes")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Type")
    table.add_column("Authorized")
    table.add_column("RoE")
    table.add_column("OPSEC")

    for s in scopes:
        table.add_row(
            s["id"],
            s["name"][:40] + "..." if len(s["name"]) > 40 else s["name"],
            s.get("category", "N/A"),
            s.get("type", "N/A"),
            "✅" if s.get("authorized") else "❌",
            s.get("roe_template", "N/A"),
            s.get("opsec_preset", "N/A")
        )

    console.print(table)


@scope.command("verify")
@click.argument("target")
@click.argument("scope_id")
@click.pass_context
def scope_verify(ctx, target, scope_id):
    """Verify target is within scope"""

    async def _verify():
        config = ConfigLoader(ctx.obj["config_dir"])
        scope = config.get_scope_by_id(scope_id)

        if not scope:
            console.print(f"[red]Scope not found: {scope_id}[/red]")
            return

        from src.core import validate_scope
        from src.core import ScopeReceipt

        receipt = ScopeReceipt(
            receipt_id="test",
            customer_legal_entity=scope.get("organization", ""),
            customer_authorized_representative=scope.get("contacts", [{}])[0].get("email", ""),
            target_systems=scope.get("urls", []) + scope.get("cidrs", []),
            ip_ranges=scope.get("cidrs", []),
            domains=[u.replace("https://", "").replace("http://", "").split("/")[0] for u in scope.get("urls", [])],
            excluded_paths=scope.get("scope_details", {}).get("out_of_scope", []),
            testing_window_start=datetime.now(),
            testing_window_end=datetime.now(),
            emergency_contact=scope.get("contacts", [{}])[0].get("email", ""),
            authorized_signature="test",
            signature_date=datetime.now(),
            roe_template_id=scope.get("roe_template", "strict")
        )

        valid = validate_scope(target, receipt)

        if valid:
            console.print(f"[green]✅ Target '{target}' is IN SCOPE for {scope_id}[/green]")
        else:
            console.print(f"[red]❌ Target '{target}' is OUT OF SCOPE for {scope_id}[/red]")

    asyncio.run(_verify())


# ==================== VERIFY COMMAND ====================

@cli.command("verify")
@click.pass_context
def verify(ctx):
    """Run verification checks (verify-claims)"""
    import subprocess
    result = subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "verify_claims.py")])
    sys.exit(result.returncode)


# ==================== MCP COMMAND ====================

@cli.command("mcp")
@click.option("--config", help="Config file path")
@click.pass_context
def mcp(ctx, config):
    """Run MCP server"""
    config_path = config or str(ctx.obj["config_dir"] / "default.yaml")
    console.print(f"[cyan]Starting MCP server with config: {config_path}[/cyan]")
    console.print("[yellow]MCP server not yet fully implemented[/yellow]")


# ==================== CONFIG COMMAND ====================

@cli.command("config")
@click.option("--show", is_flag=True, help="Show current config")
@click.pass_context
def config_cmd(ctx, show):
    """Configuration management"""
    config = ConfigLoader(ctx.obj["config_dir"])
    default = config.load_default_config()

    if show:
        console.print(Syntax(json.dumps(default, indent=2, ensure_ascii=False), "json"))
    else:
        console.print("[cyan]Config directory:[/cyan]", ctx.obj["config_dir"])
        console.print("[cyan]Sections:[/cyan]")
        for section in default.keys():
            console.print(f"  - {section}")


if __name__ == "__main__":
    cli()