#!/usr/bin/env python3
"""
MCP Server for Crimea Security Framework v2
Integrates with Hermes, Claude Code, VS Code Copilot, Cursor, etc.
Based on T3MP3ST MCP Server + HexStrike AI patterns
"""

from __future__ import annotations
import asyncio
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
    InitializeResult,
)

from src.config import ConfigLoader
from src.mission import MissionControl, create_mission_from_scope
from src.core import Phase, OperatorArchetype, FindingSeverity
from src.opsec import OPSECProfile, DetectionType
from src.kb import KnowledgeBase, create_kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrimeaSecMCPServer:
    """MCP Server for Crimea Security Framework"""

    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir) if config_dir else PROJECT_ROOT / "config"
        self.config = ConfigLoader(self.config_dir)
        self.mission_control = MissionControl(self.config_dir)
        self.kb = None
        self.server = Server("crimea-sec-v2")
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="security_recon",
                        description="Passive reconnaissance: DNS, subdomains, certificates, WHOIS, tech detection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "target": {"type": "string", "description": "Target domain or IP"},
                                "modules": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Recon modules: dns, subdomain, cert, whois, tech, wayback"
                                },
                                "opsec_profile": {"type": "string", "description": "OPSEC profile: silent, balanced, aggressive"},
                            },
                            "required": ["target"]
                        }
                    ),
                    Tool(
                        name="security_scan",
                        description="Active security scanning: ports, services, vulnerabilities, directories",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "target": {"type": "string", "description": "Target URL or IP"},
                                "scan_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Scan types: port, service, vuln, dir, ssl, nuclei"
                                },
                                "opsec_profile": {"type": "string", "description": "OPSEC profile"},
                                "roe_template": {"type": "string", "description": "RoE template: strict, permissive, bugbounty"},
                            },
                            "required": ["target"]
                        }
                    ),
                    Tool(
                        name="security_analyze",
                        description="Analyze findings: CVSS scoring, MITRE mapping, pattern matching, remediation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "findings": {"type": "array", "items": {"type": "object"}},
                                "target": {"type": "string"},
                            },
                            "required": ["findings", "target"]
                        }
                    ),
                    Tool(
                        name="mission_start",
                        description="Start a new security assessment mission",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "scope_id": {"type": "string", "description": "Predefined scope from config/crimea-targets.yaml"},
                                "roe_template": {"type": "string", "default": "strict"},
                                "opsec_profile": {"type": "string", "default": "balanced"},
                            },
                            "required": ["name", "scope_id"]
                        }
                    ),
                    Tool(
                        name="mission_status",
                        description="Get mission status and progress",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "mission_id": {"type": "string"}
                            },
                            "required": ["mission_id"]
                        }
                    ),
                    Tool(
                        name="evidence_get",
                        description="Retrieve evidence for a finding",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "mission_id": {"type": "string"},
                                "finding_id": {"type": "string"}
                            },
                            "required": ["mission_id", "finding_id"]
                        }
                    ),
                    Tool(
                        name="report_generate",
                        description="Generate mission report",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "mission_id": {"type": "string"},
                                "formats": {"type": "array", "items": {"type": "string"}, "default": ["html", "json"]}
                            },
                            "required": ["mission_id"]
                        }
                    ),
                    Tool(
                        name="kb_query",
                        description="Query knowledge base: CVEs, MITRE techniques, attack patterns",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query_type": {"type": "string", "enum": ["cve", "mitre", "pattern", "product", "tag"]},
                                "value": {"type": "string"},
                                "limit": {"type": "integer", "default": 10}
                            },
                            "required": ["query_type", "value"]
                        }
                    ),
                    Tool(
                        name="roe_validate",
                        description="Validate target against RoE and scope",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "target": {"type": "string"},
                                "roe_template": {"type": "string"},
                                "scope_id": {"type": "string"}
                            },
                            "required": ["target", "scope_id"]
                        }
                    ),
                    Tool(
                        name="scope_verify",
                        description="Verify target is within authorized scope",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "target": {"type": "string"},
                                "scope_receipt": {"type": "object"}
                            },
                            "required": ["target", "scope_receipt"]
                        }
                    ),
                ]
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                result = await self._execute_tool(name, arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
                )
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))],
                    isError=True
                )

    async def _execute_tool(self, name: str, args: Dict) -> Dict:
        """Execute tool by name"""

        if name == "security_recon":
            return await self._tool_recon(args)
        elif name == "security_scan":
            return await self._tool_scan(args)
        elif name == "security_analyze":
            return await self._tool_analyze(args)
        elif name == "mission_start":
            return await self._tool_mission_start(args)
        elif name == "mission_status":
            return await self._tool_mission_status(args)
        elif name == "evidence_get":
            return await self._tool_evidence_get(args)
        elif name == "report_generate":
            return await self._tool_report_generate(args)
        elif name == "kb_query":
            return await self._tool_kb_query(args)
        elif name == "roe_validate":
            return await self._tool_roe_validate(args)
        elif name == "scope_verify":
            return await self._tool_scope_verify(args)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _tool_recon(self, args: Dict) -> Dict:
        """Passive reconnaissance"""
        target = args["target"]
        modules = args.get("modules", ["dns", "subdomain", "cert", "whois", "tech"])
        opsec = "wayback" in modules

        findings = []
        evidence = []

        # Initialize KB if needed
        if self.kb is None:
            self.kb = await create_kb(self.config_dir.parent / "data" / "kb")

        # DNS lookup
        if "dns" in modules:
            from src.arsenal import DNSLookupTool
            tool = DNSLookupTool()
            result = await tool.execute(target, {"record_types": ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]})
            findings.extend(result.findings)
            evidence.append({"type": "dns", "output": result.output})

        # Subdomain enumeration
        if "subdomain" in modules:
            from src.arsenal import SubdomainEnumTool
            tool = SubdomainEnumTool()
            result = await tool.execute(target)
            findings.extend(result.findings)
            evidence.append({"type": "subdomain", "output": result.output})

        # Certificate transparency
        if "cert" in modules:
            from src.arsenal import SSLScanTool
            tool = SSLScanTool()
            result = await tool.execute(target)
            findings.extend(result.findings)
            evidence.append({"type": "certificate", "output": result.output})

        # WHOIS
        if "whois" in modules:
            from src.arsenal import HTTPRequestTool
            tool = HTTPRequestTool()
            result = await tool.execute(f"https://rdap.org/domain/{target}")
            if result.success:
                evidence.append({"type": "whois", "output": result.output})

        # Technology detection
        if "tech" in modules:
            from src.arsenal import TechnologyDetectTool
            tool = TechnologyDetectTool()
            result = await tool.execute(target)
            findings.extend(result.findings)
            evidence.append({"type": "technology", "output": result.output})

        # Wayback Machine
        if "wayback" in modules:
            from src.arsenal import HTTPRequestTool
            tool = HTTPRequestTool()
            result = await tool.execute(f"http://web.archive.org/cdx/search/cdx?url=*.{target}/*&output=json&fl=original&collapse=urlkey")
            if result.success:
                evidence.append({"type": "wayback", "output": result.output})

        return {
            "target": target,
            "modules_run": modules,
            "findings_count": len(findings),
            "findings": findings,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat()
        }

    async def _tool_scan(self, args: Dict) -> Dict:
        """Active security scanning"""
        target = args["target"]
        scan_types = args.get("scan_types", ["port", "service", "vuln", "dir"])
        opsec_profile = args.get("opsec_profile", "balanced")

        findings = []
        evidence = []

        # Port scan
        if "port" in scan_types:
            from src.arsenal import PortScanTool
            tool = PortScanTool()
            result = await tool.execute(target, {"ports": "top-1000"})
            findings.extend(result.findings)
            evidence.append({"type": "port_scan", "output": result.output})

        # Service detection
        if "service" in scan_types:
            from src.arsenal import PortScanTool
            tool = PortScanTool()
            result = await tool.execute(target, {"ports": "top-100", "version_detection": True})
            findings.extend(result.findings)
            evidence.append({"type": "service_detection", "output": result.output})

        # Vulnerability scan (nuclei)
        if "vuln" in scan_types:
            from src.arsenal import NmapTool
            tool = NmapTool({"binary_path": "nmap"})
            result = await tool.execute(target, {"scripts": "vuln", "ports": "top-1000"})
            if result.success:
                findings.extend(result.findings)
                evidence.append({"type": "nuclei_vuln", "output": result.output})

        # Directory enumeration
        if "dir" in scan_types:
            from src.arsenal import DirBruteforceTool
            tool = DirBruteforceTool()
            result = await tool.execute(target, {"wordlist": "common", "threads": 20})
            findings.extend(result.findings)
            evidence.append({"type": "dir_enum", "output": result.output})

        # SSL scan
        if "ssl" in scan_types:
            from src.arsenal import SSLScanTool
            tool = SSLScanTool()
            result = await tool.execute(target)
            findings.extend(result.findings)
            evidence.append({"type": "ssl_scan", "output": result.output})

        return {
            "target": target,
            "scan_types": scan_types,
            "opsec_profile": opsec_profile,
            "findings_count": len(findings),
            "findings": findings,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat()
        }

    async def _tool_analyze(self, args: Dict) -> Dict:
        """Analyze findings with KB"""
        findings = args["findings"]
        target = args["target"]

        if self.kb is None:
            self.kb = await create_kb(self.config_dir.parent / "data" / "kb")

        # Match patterns
        matched_patterns = self.kb.match_patterns(findings)

        # Enrich with CVEs
        enriched_findings = []
        for finding in findings:
            ftype = finding.get("type", "")
            cves = []
            techniques = []

            # Find relevant CVEs
            if "sqli" in ftype.lower():
                cves = self.kb.get_cves_by_tag("sqli")[:5]
            elif "xss" in ftype.lower():
                cves = self.kb.get_cves_by_tag("xss")[:5]
            elif "rce" in ftype.lower():
                cves = self.kb.get_cves_by_tag("rce")[:5]

            # Find relevant MITRE techniques
            for pattern in matched_patterns:
                for tech_id in pattern.mitre_techniques:
                    tech = self.kb.get_technique(tech_id)
                    if tech:
                        techniques.append(tech.to_dict())

            enriched_findings.append({
                **finding,
                "related_cves": [c.to_dict() for c in cves],
                "mitre_techniques": techniques,
                "matched_patterns": [p.pattern_id for p in matched_patterns],
                "remediation": self._get_remediation(finding, matched_patterns)
            })

        return {
            "target": target,
            "findings_analyzed": len(findings),
            "matched_patterns": [p.to_dict() for p in matched_patterns],
            "enriched_findings": enriched_findings,
            "summary": {
                "critical": len([f for f in enriched_findings if self._get_severity(f) == "critical"]),
                "high": len([f for f in enriched_findings if self._get_severity(f) == "high"]),
                "medium": len([f for f in enriched_findings if self._get_severity(f) == "medium"]),
                "low": len([f for f in enriched_findings if self._get_severity(f) == "low"]),
            }
        }

    def _get_severity(self, finding: Dict) -> str:
        """Calculate severity from finding"""
        cves = finding.get("related_cves", [])
        if cves:
            max_score = max(c.get("cvss31_score", 0) for c in cves)
            if max_score >= 9.0:
                return "critical"
            elif max_score >= 7.0:
                return "high"
            elif max_score >= 4.0:
                return "medium"
            else:
                return "low"
        return finding.get("severity", "medium")

    def _get_remediation(self, finding: Dict, patterns: List) -> str:
        """Get remediation guidance"""
        for pattern in patterns:
            if pattern.category in finding.get("type", "").lower():
                return "; ".join(pattern.mitigations[:3])
        return "Apply security best practices and patch management"

    async def _tool_mission_start(self, args: Dict) -> Dict:
        """Start a new mission"""
        scope = self.config.get_scope_by_id(args["scope_id"])
        if not scope:
            return {"error": f"Scope not found: {args['scope_id']}"}

        mission = await create_mission_from_scope(
            scope_id=args["scope_id"],
            name=args["name"],
            description=args["description"],
            roe_template=args.get("roe_template", "strict"),
            opsec_profile=args.get("opsec_profile", "balanced"),
            config_dir=self.config_dir
        )

        # Start mission
        await self.mission_control.start_mission(mission.mission_id)

        return {
            "mission_id": mission.mission_id,
            "name": mission.name,
            "status": mission.status.value,
            "current_phase": mission.current_phase.value if mission.current_phase else None,
            "targets": [t.identifier for t in mission.targets.values()],
        }

    async def _tool_mission_status(self, args: Dict) -> Dict:
        """Get mission status"""
        mission = self.mission_control.get_mission(args["mission_id"])
        if not mission:
            return {"error": f"Mission not found: {args['mission_id']}"}

        return {
            "mission_id": mission.mission_id,
            "name": mission.name,
            "status": mission.status.value,
            "current_phase": mission.current_phase.value if mission.current_phase else None,
            "phases_completed": [p.value for p in mission.phases_completed],
            "targets": len(mission.targets),
            "findings": len(mission.findings),
            "evidence_count": len(mission.evidence),
            "operators": len(mission.operators),
            "detection_risk": mission.detection_risk,
            "started_at": mission.started_at.isoformat() if mission.started_at else None,
            "completed_at": mission.completed_at.isoformat() if mission.completed_at else None,
        }

    async def _tool_evidence_get(self, args: Dict) -> Dict:
        """Get evidence for finding"""
        mission = self.mission_control.get_mission(args["mission_id"])
        if not mission:
            return {"error": "Mission not found"}

        finding = mission.findings.get(args["finding_id"])
        if not finding:
            return {"error": "Finding not found"}

        evidence = [e for e in mission.evidence.values() if e.finding_id == args["finding_id"]]

        return {
            "finding": finding.to_dict(),
            "evidence": [e.to_dict() for e in evidence],
        }

    async def _tool_report_generate(self, args: Dict) -> Dict:
        """Generate mission report"""
        mission = self.mission_control.get_mission(args["mission_id"])
        if not mission:
            return {"error": "Mission not found"}

        formats = args.get("formats", ["html", "json"])
        reports = await self.mission_control.generate_report(mission.mission_id, formats)

        return {
            "mission_id": mission.mission_id,
            "reports": reports,
            "generated_at": datetime.now().isoformat()
        }

    async def _tool_kb_query(self, args: Dict) -> Dict:
        """Query knowledge base"""
        if self.kb is None:
            self.kb = await create_kb(self.config_dir.parent / "data" / "kb")

        query_type = args["query_type"]
        value = args["value"]
        limit = args.get("limit", 10)

        if query_type == "cve":
            cve = self.kb.get_cve(value)
            return {"results": [cve.to_dict()] if cve else []}

        elif query_type == "mitre":
            tech = self.kb.get_technique(value)
            return {"results": [tech.to_dict()] if tech else []}

        elif query_type == "pattern":
            pattern = self.kb.get_pattern(value)
            return {"results": [pattern.to_dict()] if pattern else []}

        elif query_type == "product":
            cves = self.kb.get_cves_by_product(value)[:limit]
            return {"results": [c.to_dict() for c in cves]}

        elif query_type == "tag":
            cves = self.kb.get_cves_by_tag(value)[:limit]
            return {"results": [c.to_dict() for c in cves]}

        return {"error": f"Unknown query type: {query_type}"}

    async def _tool_roe_validate(self, args: Dict) -> Dict:
        """Validate target against RoE"""
        target = args["target"]
        roe_template = args.get("roe_template", "strict")
        scope_id = args["scope_id"]

        scope = self.config.get_scope_by_id(scope_id)
        if not scope:
            return {"error": "Scope not found", "valid": False}

        roe = self.config.get_roe_template(roe_template)

        # Check if target in scope
        in_scope = self._check_scope(target, scope)

        # Check if phase allowed
        phase_allowed = True  # Would check based on current phase

        # Check tool gates
        allowed_tools = self._get_allowed_tools(roe)

        return {
            "target": target,
            "in_scope": in_scope,
            "phase_allowed": phase_allowed,
            "allowed_tools": allowed_tools,
            "valid": in_scope and phase_allowed,
            "scope_id": scope_id,
            "roe_template": roe_template
        }

    def _check_scope(self, target: str, scope: Dict) -> bool:
        """Check if target is within scope"""
        # Check domains
        for domain in scope.get("domains", []):
            if domain in target or target.endswith("." + domain):
                return True

        # Check IPs/CIDRs
        import ipaddress
        try:
            target_ip = ipaddress.ip_address(target.split(":")[0].split("/")[0])
            for cidr in scope.get("cidrs", []):
                if target_ip in ipaddress.ip_network(cidr):
                    return True
        except:
            pass

        # Check excluded
        for excluded in scope.get("scope_details", {}).get("out_of_scope", []):
            if excluded in target:
                return False

        return False

    def _get_allowed_tools(self, roe: Dict) -> List[str]:
        """Get allowed tools from RoE"""
        allowed = []
        for tool, config in roe.get("tool_gates", {}).items():
            if config.get("allowed", False):
                allowed.append(tool)
        return allowed

    async def _tool_scope_verify(self, args: Dict) -> Dict:
        """Verify target against scope receipt"""
        target = args["target"]
        scope_receipt = args["scope_receipt"]

        from src.core import validate_scope
        valid = validate_scope(target, scope_receipt)

        return {
            "target": target,
            "valid": valid,
            "scope_receipt_id": scope_receipt.get("receipt_id", "unknown")
        }

    async def initialize(self) -> InitializeResult:
        """Initialize MCP server"""
        # Initialize KB
        self.kb = await create_kb(self.config_dir.parent / "data" / "kb")

        return InitializeResult(
            protocolVersion="2024-11-05",
            capabilities={
                "tools": {},
            },
            serverInfo={
                "name": "crimea-sec-v2",
                "version": "2.0.0",
            }
        )

    async def run(self) -> None:
        """Run MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.initialize()
            )


async def main():
    """Main entry point"""
    config_dir = None
    if len(sys.argv) > 1:
        config_dir = sys.argv[1]

    server = CrimeaSecMCPServer(config_dir)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())