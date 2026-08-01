#!/usr/bin/env python3
"""
KnowledgeBase — CVE, MITRE ATT&CK, Attack Patterns
Based on T3MP3ST KnowledgeBase with Crimea-specific additions
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class CVESeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class MITRETactic(str, Enum):
    RECONNAISSANCE = "TA0043"
    RESOURCE_DEVELOPMENT = "TA0042"
    INITIAL_ACCESS = "TA0001"
    EXECUTION = "TA0002"
    PERSISTENCE = "TA0003"
    PRIVILEGE_ESCALATION = "TA0004"
    DEFENSE_EVASION = "TA0005"
    CREDENTIAL_ACCESS = "TA0006"
    DISCOVERY = "TA0007"
    LATERAL_MOVEMENT = "TA0008"
    COLLECTION = "TA0009"
    COMMAND_AND_CONTROL = "TA0011"
    EXFILTRATION = "TA0010"
    IMPACT = "TA0040"


@dataclass
class CVEEntry:
    cve_id: str
    description: str
    cvss31_score: Optional[float] = None
    cvss31_vector: Optional[str] = None
    cwe_ids: List[str] = field(default_factory=list)
    affected_products: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    published_date: Optional[str] = None
    last_modified: Optional[str] = None
    exploit_available: bool = False
    exploit_maturity: str = "unproven"  # unproven, poc, functional, high, weaponized
    epss_score: Optional[float] = None  # Exploit Prediction Scoring System
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "cve_id": self.cve_id,
            "description": self.description,
            "cvss31_score": self.cvss31_score,
            "cvss31_vector": self.cvss31_vector,
            "cwe_ids": self.cwe_ids,
            "affected_products": self.affected_products,
            "references": self.references,
            "published_date": self.published_date,
            "last_modified": self.last_modified,
            "exploit_available": self.exploit_available,
            "exploit_maturity": self.exploit_maturity,
            "epss_score": self.epss_score,
            "tags": self.tags,
        }


@dataclass
class MITRETechnique:
    technique_id: str
    name: str
    description: str
    tactic: MITRETactic
    platforms: List[str] = field(default_factory=list)
    permissions_required: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    defenses_bypassed: List[str] = field(default_factory=list)
    sub_techniques: List[str] = field(default_factory=list)
    detection: str = ""
    mitigation: str = ""
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "technique_id": self.technique_id,
            "name": self.name,
            "description": self.description,
            "tactic": self.tactic.value,
            "platforms": self.platforms,
            "permissions_required": self.permissions_required,
            "data_sources": self.data_sources,
            "defenses_bypassed": self.defenses_bypassed,
            "sub_techniques": self.sub_techniques,
            "detection": self.detection,
            "mitigation": self.mitigation,
            "references": self.references,
        }


@dataclass
class AttackPattern:
    pattern_id: str
    name: str
    description: str
    category: str  # web, network, auth, crypto, logic, etc.
    mitre_techniques: List[str] = field(default_factory=list)
    cve_references: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    severity: str = "medium"
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "mitre_techniques": self.mitre_techniques,
            "cve_references": self.cve_references,
            "prerequisites": self.prerequisites,
            "indicators": self.indicators,
            "mitigations": self.mitigations,
            "severity": self.severity,
            "references": self.references,
        }


class KnowledgeBase:
    """
    Local knowledge base with CVE, MITRE ATT&CK, and attack patterns.
    Supports offline operation with periodic updates.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.cves: Dict[str, CVEEntry] = {}
        self.mitre: Dict[str, MITRETechnique] = {}
        self.patterns: Dict[str, AttackPattern] = {}

        self._load_all()

    def _load_all(self) -> None:
        """Load all knowledge bases from disk"""
        self._load_cves()
        self._load_mitre()
        self._load_patterns()

    def _load_cves(self) -> None:
        cve_file = self.data_dir / "cve.json"
        if cve_file.exists():
            try:
                with open(cve_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry in data:
                        cve = CVEEntry(**entry)
                        self.cves[cve.cve_id] = cve
                logger.info(f"Loaded {len(self.cves)} CVE entries")
            except Exception as e:
                logger.error(f"Failed to load CVEs: {e}")
                self._init_default_cves()
        else:
            self._init_default_cves()

    def _init_default_cves(self) -> None:
        """Initialize with critical CVEs relevant to web/infra testing"""
        default_cves = [
            CVEEntry(
                cve_id="CVE-2021-44228",
                description="Apache Log4j2 JNDI injection (Log4Shell)",
                cvss31_score=10.0,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                cwe_ids=["CWE-502"],
                affected_products=["Apache Log4j 2.0-beta9 to 2.14.1"],
                exploit_available=True,
                exploit_maturity="weaponized",
                epss_score=0.97,
                tags=["rce", "log4j", "java", "critical"]
            ),
            CVEEntry(
                cve_id="CVE-2022-22965",
                description="Spring Framework RCE via Data Binding (Spring4Shell)",
                cvss31_score=9.8,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cwe_ids=["CWE-502"],
                affected_products=["Spring Framework 5.3.0-5.3.17, 5.2.0-5.2.19"],
                exploit_available=True,
                exploit_maturity="functional",
                epss_score=0.93,
                tags=["rce", "spring", "java"]
            ),
            CVEEntry(
                cve_id="CVE-2023-34362",
                description="Progress MOVEit Transfer SQL Injection",
                cvss31_score=9.8,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cwe_ids=["CWE-89"],
                affected_products=["MOVEit Transfer 2023.0.0-2023.0.6"],
                exploit_available=True,
                exploit_maturity="weaponized",
                epss_score=0.95,
                tags=["sqli", "moveit", "file_transfer"]
            ),
            CVEEntry(
                cve_id="CVE-2024-21762",
                description="Fortinet FortiOS SSL-VPN Heap-based Buffer Overflow",
                cvss31_score=9.8,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cwe_ids=["CWE-122"],
                affected_products=["FortiOS 7.4.0-7.4.2, 7.2.0-7.2.6, 7.0.0-7.0.13"],
                exploit_available=True,
                exploit_maturity="poc",
                epss_score=0.88,
                tags=["rce", "fortinet", "vpn", "heap_overflow"]
            ),
            CVEEntry(
                cve_id="CVE-2024-3400",
                description="Palo Alto Networks PAN-OS Command Injection",
                cvss31_score=10.0,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                cwe_ids=["CWE-78"],
                affected_products=["PAN-OS 10.2, 11.0, 11.1"],
                exploit_available=True,
                exploit_maturity="functional",
                epss_score=0.94,
                tags=["rce", "paloalto", "firewall", "cmd_injection"]
            ),
            CVEEntry(
                cve_id="CVE-2024-24919",
                description="Check Point Security Gateway Information Disclosure",
                cvss31_score=8.6,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                cwe_ids=["CWE-200"],
                affected_products=["Check Point Quantum Security Gateway"],
                exploit_available=True,
                exploit_maturity="functional",
                epss_score=0.85,
                tags=["info_disclosure", "checkpoint", "vpn"]
            ),
            CVEEntry(
                cve_id="CVE-2024-4577",
                description="PHP CGI Argument Injection (Windows)",
                cvss31_score=9.8,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cwe_ids=["CWE-78"],
                affected_products=["PHP 8.3.*, 8.2.*, 8.1.* on Windows"],
                exploit_available=True,
                exploit_maturity="functional",
                epss_score=0.91,
                tags=["rce", "php", "windows", "cgi"]
            ),
            CVEEntry(
                cve_id="CVE-2024-51567",
                description="CyberPanel v2.3.6 RCE via Securing Status",
                cvss31_score=9.8,
                cvss31_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                cwe_ids=["CWE-78"],
                affected_products=["CyberPanel <= 2.3.6"],
                exploit_available=True,
                exploit_maturity="functional",
                epss_score=0.89,
                tags=["rce", "cyberpanel", "panel"]
            ),
        ]

        for cve in default_cves:
            self.cves[cve.cve_id] = cve
        self._save_cves()
        logger.info(f"Initialized {len(default_cves)} default CVEs")

    def _load_mitre(self) -> None:
        mitre_file = self.data_dir / "mitre.json"
        if mitre_file.exists():
            try:
                with open(mitre_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry in data:
                        entry["tactic"] = MITRETactic(entry["tactic"])
                        tech = MITRETechnique(**entry)
                        self.mitre[tech.technique_id] = tech
                logger.info(f"Loaded {len(self.mitre)} MITRE techniques")
            except Exception as e:
                logger.error(f"Failed to load MITRE: {e}")
                self._init_default_mitre()
        else:
            self._init_default_mitre()

    def _init_default_mitre(self) -> None:
        """Initialize with core MITRE ATT&CK techniques"""
        default_techniques = [
            MITRETechnique(
                technique_id="T1190",
                name="Exploit Public-Facing Application",
                description="Adversaries may attempt to exploit a weakness in an Internet-facing host or system.",
                tactic=MITRETactic.INITIAL_ACCESS,
                platforms=["Linux", "Windows", "Network"],
                permissions_required=["User"],
                data_sources=["Application Log", "Web Application Firewall", "Network Traffic"],
                detection="Monitor for anomalous traffic to public applications. Look for exploitation behavior patterns.",
                mitigation="Keep applications updated. Use WAF. Implement least privilege.",
                references=["https://attack.mitre.org/techniques/T1190/"]
            ),
            MITRETechnique(
                technique_id="T1190.001",
                name="Exploit Public-Facing Application: Web Application",
                description="Exploitation of web application vulnerabilities such as SQLi, XSS, RCE.",
                tactic=MITRETactic.INITIAL_ACCESS,
                platforms=["Linux", "Windows"],
                permissions_required=["User"],
                sub_techniques=["T1190"],
                references=["https://attack.mitre.org/techniques/T1190/001/"]
            ),
            MITRETechnique(
                technique_id="T1059",
                name="Command and Scripting Interpreter",
                description="Adversaries may abuse command and script interpreters to execute commands.",
                tactic=MITRETactic.EXECUTION,
                platforms=["Linux", "Windows", "macOS"],
                permissions_required=["User"],
                references=["https://attack.mitre.org/techniques/T1059/"]
            ),
            MITRETechnique(
                technique_id="T1068",
                name="Exploitation for Privilege Escalation",
                description="Adversaries may exploit software vulnerabilities to escalate privileges.",
                tactic=MITRETactic.PRIVILEGE_ESCALATION,
                platforms=["Linux", "Windows"],
                permissions_required=["User"],
                references=["https://attack.mitre.org/techniques/T1068/"]
            ),
            MITRETechnique(
                technique_id="T1021",
                name="Remote Services",
                description="Adversaries may use remote services to access internal systems.",
                tactic=MITRETactic.LATERAL_MOVEMENT,
                platforms=["Linux", "Windows"],
                permissions_required=["User", "Administrator"],
                references=["https://attack.mitre.org/techniques/T1021/"]
            ),
            MITRETechnique(
                technique_id="T1005",
                name="Data from Local System",
                description="Adversaries may search local system sources for files of interest.",
                tactic=MITRETactic.COLLECTION,
                platforms=["Linux", "Windows", "macOS"],
                permissions_required=["User"],
                references=["https://attack.mitre.org/techniques/T1005/"]
            ),
            MITRETechnique(
                technique_id="T1041",
                name="Exfiltration Over Web Service",
                description="Adversaries may exfiltrate data over web services.",
                tactic=MITRETactic.EXFILTRATION,
                platforms=["Linux", "Windows"],
                permissions_required=["User"],
                references=["https://attack.mitre.org/techniques/T1041/"]
            ),
            MITRETechnique(
                technique_id="T1505",
                name="Server Software Component",
                description="Adversaries may deploy server software components to maintain access.",
                tactic=MITRETactic.PERSISTENCE,
                platforms=["Linux", "Windows"],
                permissions_required=["Administrator", "SYSTEM"],
                references=["https://attack.mitre.org/techniques/T1505/"]
            ),
            MITRETechnique(
                technique_id="T1546",
                name="Event Triggered Execution",
                description="Adversaries may establish persistence by executing malicious content triggered by events.",
                tactic=MITRETactic.PERSISTENCE,
                platforms=["Linux", "Windows"],
                permissions_required=["User", "Administrator"],
                references=["https://attack.mitre.org/techniques/T1546/"]
            ),
            MITRETechnique(
                technique_id="T1083",
                name="File and Directory Discovery",
                description="Adversaries may enumerate files and directories.",
                tactic=MITRETactic.DISCOVERY,
                platforms=["Linux", "Windows", "macOS"],
                permissions_required=["User"],
                references=["https://attack.mitre.org/techniques/T1083/"]
            ),
            MITRETechnique(
                technique_id="T1046",
                name="Network Service Scanning",
                description="Adversaries may scan for open ports and services.",
                tactic=MITRETactic.DISCOVERY,
                platforms=["Linux", "Windows"],
                permissions_required=["User"],
                references=["https://attack.mitre.org/techniques/T1046/"]
            ),
            MITRETechnique(
                technique_id="T1590",
                name="Active Scanning",
                description="Adversaries may execute active scans to gather information.",
                tactic=MITRETactic.RECONNAISSANCE,
                platforms=["PRE"],
                permissions_required=["None"],
                references=["https://attack.mitre.org/techniques/T1590/"]
            ),
            MITRETechnique(
                technique_id="T1590.005",
                name="Active Scanning: Vulnerability Scanning",
                description="Adversaries may scan for vulnerabilities.",
                tactic=MITRETactic.RECONNAISSANCE,
                platforms=["PRE"],
                sub_techniques=["T1590"],
                references=["https://attack.mitre.org/techniques/T1590/005/"]
            ),
        ]

        for tech in default_techniques:
            self.mitre[tech.technique_id] = tech
        self._save_mitre()
        logger.info(f"Initialized {len(default_techniques)} default MITRE techniques")

    def _load_patterns(self) -> None:
        patterns_file = self.data_dir / "patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry in data:
                        pattern = AttackPattern(**entry)
                        self.patterns[pattern.pattern_id] = pattern
                logger.info(f"Loaded {len(self.patterns)} attack patterns")
            except Exception as e:
                logger.error(f"Failed to load patterns: {e}")
                self._init_default_patterns()
        else:
            self._init_default_patterns()

    def _init_default_patterns(self) -> None:
        """Initialize with common attack patterns"""
        default_patterns = [
            AttackPattern(
                pattern_id="PATTERN-001",
                name="SQL Injection",
                category="web",
                description="Injection of malicious SQL via user input",
                mitre_techniques=["T1190", "T1059"],
                cve_references=["CVE-2023-34362", "CVE-2022-22965"],
                prerequisites=["User input in SQL query", "No parameterized queries"],
                indicators=["SQL errors in response", "Time-based delays", "Union select results"],
                mitigations=["Parameterized queries", "Input validation", "WAF", "Least privilege DB user"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-002",
                name="Cross-Site Scripting (XSS)",
                category="web",
                description="Injection of malicious scripts into web pages",
                mitre_techniques=["T1189", "T1059"],
                cve_references=[],
                prerequisites=["User input reflected in response", "No output encoding"],
                indicators=["Script tags in response", "Alert dialogs", "Event handlers"],
                mitigations=["Output encoding", "CSP", "HttpOnly cookies", "Input validation"],
                severity="medium"
            ),
            AttackPattern(
                pattern_id="PATTERN-003",
                name="Server-Side Request Forgery (SSRF)",
                category="web",
                description="Force server to make requests to internal/external resources",
                mitre_techniques=["T1190", "T1590"],
                cve_references=["CVE-2021-44228"],
                prerequisites=["User-controlled URL parameter", "No URL validation"],
                indicators=["Internal IP access", "Cloud metadata access", "Localhost access"],
                mitigations=["Allowlist URLs", "Block private IPs", "No redirects", "Network segmentation"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-004",
                name="Path Traversal",
                category="web",
                description="Access files outside intended directory",
                mitre_techniques=["T1005", "T1083"],
                cve_references=[],
                prerequisites=["User-controlled file path", "No path validation"],
                indicators=["../ sequences", "Absolute paths", "URL encoding"],
                mitigations=["Path normalization", "Allowlist directories", "Chroot/jail"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-005",
                name="Authentication Bypass",
                category="auth",
                description="Bypass authentication mechanisms",
                mitre_techniques=["T1078", "T1556"],
                cve_references=[],
                prerequisites=["Weak auth logic", "Default credentials", "JWT flaws"],
                indicators=["Admin access without login", "Token manipulation", "Session fixation"],
                mitigations=["MFA", "Strong password policy", "JWT validation", "Rate limiting"],
                severity="critical"
            ),
            AttackPattern(
                pattern_id="PATTERN-006",
                name="Remote Code Execution",
                category="web",
                description="Execute arbitrary code on target system",
                mitre_techniques=["T1190", "T1059", "T1068"],
                cve_references=["CVE-2021-44228", "CVE-2022-22965", "CVE-2024-3400"],
                prerequisites=["Deserialization flaw", "Command injection", "Template injection"],
                indicators=["Command output in response", "Reverse shell", "File creation"],
                mitigations=["Input validation", "Disable dangerous functions", "Sandboxing", "WAF"],
                severity="critical"
            ),
            AttackPattern(
                pattern_id="PATTERN-007",
                name="Security Misconfiguration",
                category="config",
                description="Insecure default configurations",
                mitre_techniques=["T1069", "T1578"],
                cve_references=[],
                prerequisites=["Default credentials", "Exposed admin interfaces", "Debug enabled"],
                indicators=["Default login works", "Directory listing", "Stack traces", "Version disclosure"],
                mitigations=["Hardening guides", "Change defaults", "Disable debug", "Regular audits"],
                severity="medium"
            ),
            AttackPattern(
                pattern_id="PATTERN-008",
                name="Broken Access Control",
                category="web",
                description="Users can access unauthorized resources",
                mitre_techniques=["T1078", "T1080"],
                cve_references=[],
                prerequisites=["Missing authorization checks", "IDOR", "Forceful browsing"],
                indicators=["Access to other user data", "Admin functions accessible", "Horizontal/vertical privilege escalation"],
                mitigations=["Deny by default", "Role-based access", "Object-level authorization", "Audit trails"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-009",
                name="Insecure Deserialization",
                category="web",
                description="Deserialization of untrusted data leading to RCE",
                mitre_techniques=["T1190", "T1059"],
                cve_references=["CVE-2021-44228"],
                prerequisites=["User-controlled serialized data", "Gadget chains available"],
                indicators=["Serialized objects in params", "Base64 encoded objects", "Magic bytes"],
                mitigations=["Avoid serialization", "Integrity checks", "Allowlist classes", "Sandboxing"],
                severity="critical"
            ),
            AttackPattern(
                pattern_id="PATTERN-010",
                name="API Security Issues",
                category="api",
                description="Broken Object Level Authorization, Excessive Data Exposure, etc.",
                mitre_techniques=["T1080", "T1005"],
                cve_references=[],
                prerequisites=["Exposed API endpoints", "Missing rate limiting", "No object-level auth"],
                indicators=["Access to other users' objects", "Mass assignment", "API versioning issues"],
                mitigations=["Object-level authorization", "Rate limiting", "Schema validation", "API gateway"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-011",
                name="Supply Chain Attack",
                category="supply_chain",
                description="Compromise via third-party dependencies",
                mitre_techniques=["T1195.001", "T1195.002"],
                cve_references=["CVE-2021-44228"],
                prerequisites=["Vulnerable dependency", "Unpinned versions", "No SBOM"],
                indicators=["Unexpected behavior", "Unknown network connections", "File modifications"],
                mitigations=["Dependency scanning", "SBOM", "Pinned versions", "Private registry", "Signed packages"],
                severity="critical"
            ),
            AttackPattern(
                pattern_id="PATTERN-012",
                name="Cloud Misconfiguration",
                category="cloud",
                description="Insecure cloud resource configurations",
                mitre_techniques=["T1578", "T1613"],
                cve_references=[],
                prerequisites=["Public S3 buckets", "Overly permissive IAM", "Exposed management ports"],
                indicators=["Public data access", "Anonymous access", "Default security groups"],
                mitigations=["IaC scanning", "CSPM", "Least privilege IAM", "GuardDuty", "Config rules"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-013",
                name="Container Escape",
                category="container",
                description="Break out of container to host",
                mitre_techniques=["T1611", "T1068"],
                cve_references=["CVE-2022-0811", "CVE-2021-22555"],
                prerequisites=["Privileged container", "Host path mounts", "Kernel vulnerabilities"],
                indicators=["Host filesystem access", "Docker socket access", "Capability escalation"],
                mitigations=["Drop capabilities", "Read-only rootfs", "User namespaces", "gVisor/Kata", "No privileged"],
                severity="critical"
            ),
            AttackPattern(
                pattern_id="PATTERN-014",
                name="Kubernetes RBAC Misconfiguration",
                category="kubernetes",
                description="Overly permissive RBAC policies",
                mitre_techniques=["T1609", "T1078"],
                cve_references=[],
                prerequisites=["Cluster-admin binding", "Default service accounts", "No PSP/OPA"],
                indicators=["Anonymous access", "Excessive permissions", "Privilege escalation paths"],
                mitigations=["RBAC least privilege", "OPA/Gatekeeper", "Pod Security Standards", "Audit logging"],
                severity="high"
            ),
            AttackPattern(
                pattern_id="PATTERN-015",
                name="Client-Side Vulnerabilities",
                category="client",
                description="XSS, CSRF, Clickjacking, DOM-based issues",
                mitre_techniques=["T1189", "T1204"],
                cve_references=[],
                prerequisites=["User interaction", "Missing CSP", "No CSRF tokens", "Framable pages"],
                indicators=["Script execution", "Unauthorized actions", "UI redressing"],
                mitigations=["CSP", "CSRF tokens", "X-Frame-Options", "SameSite cookies", "HTTPS only"],
                severity="medium"
            ),
        ]

        for pattern in default_patterns:
            self.patterns[pattern.pattern_id] = pattern
        self._save_patterns()
        logger.info(f"Initialized {len(default_patterns)} default attack patterns")

    # === Persistence ===

    def _save_cves(self) -> None:
        cve_file = self.data_dir / "cve.json"
        with open(cve_file, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.cves.values()], f, indent=2, ensure_ascii=False)

    def _save_mitre(self) -> None:
        mitre_file = self.data_dir / "mitre.json"
        with open(mitre_file, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.mitre.values()], f, indent=2, ensure_ascii=False)

    def _save_patterns(self) -> None:
        patterns_file = self.data_dir / "patterns.json"
        with open(patterns_file, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.patterns.values()], f, indent=2, ensure_ascii=False)

    # === Query Methods ===

    def get_cve(self, cve_id: str) -> Optional[CVEEntry]:
        return self.cves.get(cve_id.upper())

    def get_cves_by_product(self, product: str) -> List[CVEEntry]:
        product_lower = product.lower()
        return [c for c in self.cves.values() if any(product_lower in p.lower() for p in c.affected_products)]

    def get_cves_by_tag(self, tag: str) -> List[CVEEntry]:
        tag_lower = tag.lower()
        return [c for c in self.cves.values() if any(tag_lower in t.lower() for t in c.tags)]

    def get_critical_cves(self, min_score: float = 9.0) -> List[CVEEntry]:
        return [c for c in self.cves.values() if c.cvss31_score and c.cvss31_score >= min_score]

    def get_exploitable_cves(self) -> List[CVEEntry]:
        return [c for c in self.cves.values() if c.exploit_available and c.exploit_maturity in ["functional", "high", "weaponized"]]

    def get_technique(self, technique_id: str) -> Optional[MITRETechnique]:
        return self.mitre.get(technique_id.upper())

    def get_techniques_by_tactic(self, tactic: MITRETactic) -> List[MITRETechnique]:
        return [t for t in self.mitre.values() if t.tactic == tactic]

    def get_pattern(self, pattern_id: str) -> Optional[AttackPattern]:
        return self.patterns.get(pattern_id.upper())

    def get_patterns_by_category(self, category: str) -> List[AttackPattern]:
        return [p for p in self.patterns.values() if p.category.lower() == category.lower()]

    def get_patterns_by_mitre(self, technique_id: str) -> List[AttackPattern]:
        tech_id = technique_id.upper()
        return [p for p in self.patterns.values() if tech_id in p.mitre_techniques]

    def match_patterns(self, findings: List[Dict]) -> List[AttackPattern]:
        """Match findings to attack patterns"""
        matched = set()
        for finding in findings:
            # Match by type
            ftype = finding.get("type", "").lower()
            for pattern in self.patterns.values():
                if pattern.category in ftype or any(t in ftype for t in pattern.mitre_techniques):
                    matched.add(pattern.pattern_id)
        return [self.patterns[pid] for pid in matched if pid in self.patterns]

    # === Update Methods ===

    async def update_cves_from_nvd(self, days_back: int = 30) -> int:
        """Update CVEs from NVD API (requires API key for full access)"""
        # Simplified - in production use NVD API with key
        logger.info("CVE update from NVD not implemented (requires API key)")
        return 0

    async def update_mitre_from_github(self) -> int:
        """Update MITRE ATT&CK from official GitHub"""
        try:
            url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Parse STIX bundle
                        count = 0
                        for obj in data.get("objects", []):
                            if obj.get("type") == "attack-pattern":
                                technique_id = None
                                for ref in obj.get("external_references", []):
                                    if ref.get("source_name") == "mitre-attack":
                                        technique_id = ref.get("external_id")
                                        break
                                if technique_id and technique_id.startswith("T"):
                                    # Create technique entry
                                    tech = MITRETechnique(
                                        technique_id=technique_id,
                                        name=obj.get("name", ""),
                                        description=obj.get("description", ""),
                                        tactic=MITRETactic(obj.get("kill_chain_phases", [{}])[0].get("phase_name", "").upper().replace("-", "_")),
                                        platforms=obj.get("x_mitre_platforms", []),
                                        permissions_required=obj.get("x_mitre_permissions_required", []),
                                        data_sources=obj.get("x_mitre_data_sources", []),
                                        detection=obj.get("x_mitre_detection", ""),
                                        references=[r.get("url", "") for r in obj.get("external_references", []) if r.get("url")]
                                    )
                                    self.mitre[technique_id] = tech
                                    count += 1
                        self._save_mitre()
                        logger.info(f"Updated {count} MITRE techniques from GitHub")
                        return count
        except Exception as e:
            logger.error(f"Failed to update MITRE from GitHub: {e}")
        return 0

    async def auto_update(self) -> Dict[str, int]:
        """Run all updates"""
        results = {}
        results["mitre"] = await self.update_mitre_from_github()
        # CVE update would need NVD API key
        return results


# === Factory ===

async def create_kb(data_dir: str = None) -> KnowledgeBase:
    """Create KnowledgeBase instance"""
    if data_dir is None:
        data_dir = Path(__file__).parent.parent.parent / "data" / "kb"
    return KnowledgeBase(Path(data_dir))


__all__ = [
    "KnowledgeBase",
    "CVEEntry",
    "MITRETechnique",
    "AttackPattern",
    "CVESeverity",
    "MITRETactic",
    "create_kb",
]