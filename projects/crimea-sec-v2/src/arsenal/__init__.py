#!/usr/bin/env python3
"""
Arsenal — Built-in tools and external CLI tool wrappers
Based on T3MP3ST Arsenal (35 built-in + 48 opt-in adapters) + HexStrike AI tools
"""

from __future__ import annotations
import asyncio
import json
import logging
import subprocess
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    OSINT = "osint"
    DNS = "dns"
    PASSIVE = "passive"
    ACTIVE_WEB = "active_web"
    NETWORK = "network"
    VULN_SCAN = "vuln_scan"
    AUTH = "auth"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    CUSTOM = "custom"


class ToolStatus(str, Enum):
    AVAILABLE = "available"
    NOT_INSTALLED = "not_installed"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class ToolResult:
    """Result of tool execution"""
    tool_name: str
    target: str
    success: bool
    output: Any = None
    error: str = ""
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    raw_output: str = ""
    findings: List[Dict] = field(default_factory=list)
    evidence: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "target": self.target,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
            "findings": self.findings,
            "evidence": self.evidence,
        }


@dataclass
class ToolDefinition:
    """Tool metadata"""
    name: str
    category: ToolCategory
    description: str
    version: str = ""
    author: str = ""
    license: str = ""
    homepage: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    opt_in: bool = False  # Requires T3MP3ST_FULL_ARSENAL
    approval_gated: bool = False  # Requires explicit approval per call
    dangerous: bool = False


class BaseTool(ABC):
    """Abstract base tool"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.definition = self._get_definition()

    @abstractmethod
    def _get_definition(self) -> ToolDefinition:
        pass

    @abstractmethod
    async def execute(self, target: str, parameters: Dict = None) -> ToolResult:
        pass

    async def validate_target(self, target: str) -> bool:
        return True

    async def check_installation(self) -> ToolStatus:
        return ToolStatus.AVAILABLE


class BuiltinTool(BaseTool):
    """Pure Python built-in tool (no external dependencies)"""

    @abstractmethod
    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        pass

    async def execute(self, target: str, parameters: Dict = None) -> ToolResult:
        import time
        start = time.time()
        try:
            result = await self._execute_impl(target, parameters or {})
            result.execution_time = time.time() - start
            return result
        except Exception as e:
            logger.error(f"Tool {self.definition.name} failed: {e}")
            return ToolResult(
                tool_name=self.definition.name,
                target=target,
                success=False,
                error=str(e),
                execution_time=time.time() - start
            )


class CLITOOL(BaseTool):
    """Wrapper for external CLI tools"""

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.binary_path = config.get("binary_path") if config else None
        self.default_args = config.get("default_args", []) if config else []
        self.timeout = config.get("timeout", 300) if config else 300

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import time
        start = time.time()

        # Build command
        cmd = await self.build_command(target, parameters)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout
            )

            execution_time = time.time() - start
            success = proc.returncode == 0

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            result = ToolResult(
                tool_name=self.definition.name,
                target=target,
                success=success,
                output=output,
                error=error if not success else "",
                execution_time=execution_time,
                raw_output=output
            )

            # Parse findings
            result.findings = await self.parse_findings(output, target)

            return result

        except asyncio.TimeoutError:
            return ToolResult(
                tool_name=self.definition.name,
                target=target,
                success=False,
                error=f"Timeout after {self.timeout}s",
                execution_time=time.time() - start
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.definition.name,
                target=target,
                success=False,
                error=str(e),
                execution_time=time.time() - start
            )

    @abstractmethod
    async def build_command(self, target: str, parameters: Dict) -> List[str]:
        pass

    async def parse_findings(self, output: str, target: str) -> List[Dict]:
        return []

    async def check_installation(self) -> ToolStatus:
        if not self.binary_path:
            return ToolStatus.NOT_INSTALLED
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return ToolStatus.AVAILABLE if proc.returncode == 0 else ToolStatus.ERROR
        except FileNotFoundError:
            return ToolStatus.NOT_INSTALLED
        except Exception:
            return ToolStatus.ERROR


# ======================== BUILT-IN TOOLS (35) ========================

class DNSLookupTool(BuiltinTool):
    """DNS lookup using system resolver"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="dns_lookup",
            category=ToolCategory.DNS,
            description="DNS record lookup (A, AAAA, MX, TXT, NS, CNAME)",
            version="1.0",
            tags=["dns", "recon", "passive"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import dns.resolver
        import dns.exception

        record_types = parameters.get("record_types", ["A", "AAAA", "MX", "TXT", "NS", "CNAME"])
        results = {}

        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(target, rtype)
                results[rtype] = [str(r) for r in answers]
            except dns.exception.DNSException:
                results[rtype] = []

        findings = []
        if results.get("A"):
            findings.append({"type": "dns_record", "target": target, "record_type": "A", "values": results["A"]})

        return ToolResult(
            tool_name=self.definition.name,
            target=target,
            success=True,
            output=results,
            findings=findings
        )


class PortScanTool(BuiltinTool):
    """TCP port scanner (async, no nmap required)"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="port_scan",
            category=ToolCategory.NETWORK,
            description="Async TCP port scanner",
            version="1.0",
            tags=["port_scan", "recon", "network"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import socket

        ports = parameters.get("ports", list(range(1, 1025)))
        if isinstance(ports, str):
            if ports == "top-100":
                ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080]
            elif ports == "top-1000":
                ports = list(range(1, 1025))

        timeout = parameters.get("timeout", 2)
        concurrency = parameters.get("concurrency", 100)

        open_ports = []

        async def scan_port(port: int):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port),
                    timeout=timeout
                )
                writer.close()
                await writer.wait_closed()
                open_ports.append(port)
            except Exception:
                pass

        # Batch scan
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_scan(port):
            async with semaphore:
                await scan_port(port)

        await asyncio.gather(*[bounded_scan(p) for p in ports])

        findings = []
        for port in sorted(open_ports):
            findings.append({
                "type": "open_port",
                "target": target,
                "port": port,
                "service": self._get_service_name(port)
            })

        return ToolResult(
            tool_name=self.definition.name,
            target=target,
            success=True,
            output={"open_ports": sorted(open_ports), "scanned_ports": len(ports)},
            findings=findings
        )

    def _get_service_name(self, port: int) -> str:
        services = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
            80: "http", 110: "pop3", 111: "rpcbind", 135: "msrpc",
            139: "netbios", 143: "imap", 443: "https", 445: "smb",
            993: "imaps", 995: "pop3s", 1723: "pptp", 3306: "mysql",
            3389: "rdp", 5432: "postgresql", 5900: "vnc", 8080: "http-proxy"
        }
        return services.get(port, "unknown")


class HTTPRequestTool(BuiltinTool):
    """HTTP client with full control"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="http_request",
            category=ToolCategory.ACTIVE_WEB,
            description="Full-featured HTTP client",
            version="1.0",
            tags=["http", "web", "api", "active"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import aiohttp

        method = parameters.get("method", "GET")
        headers = parameters.get("headers", {})
        data = parameters.get("data")
        json_data = parameters.get("json")
        params = parameters.get("params")
        timeout = parameters.get("timeout", 30)
        follow_redirects = parameters.get("follow_redirects", True)
        ssl_verify = parameters.get("ssl_verify", False)

        # Ensure target is a URL
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method, target,
                    headers=headers,
                    data=data,
                    json=json_data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    allow_redirects=follow_redirects,
                    ssl=ssl_verify
                ) as resp:
                    text = await resp.text()
                    response_headers = dict(resp.headers)

                    findings = []
                    # Check for security headers
                    sec_headers = {
                        "X-Frame-Options": "Missing X-Frame-Options",
                        "X-Content-Type-Options": "Missing X-Content-Type-Options",
                        "Strict-Transport-Security": "Missing HSTS",
                        "Content-Security-Policy": "Missing CSP",
                        "X-XSS-Protection": "Missing XSS Protection"
                    }
                    for header, msg in sec_headers.items():
                        if header not in response_headers:
                            findings.append({
                                "type": "missing_security_header",
                                "target": target,
                                "header": header,
                                "description": msg,
                                "severity": "low"
                            })

                    # Check server header
                    if "Server" in response_headers:
                        findings.append({
                            "type": "server_disclosure",
                            "target": target,
                            "server": response_headers["Server"],
                            "severity": "info"
                        })

                    return ToolResult(
                        tool_name=self.definition.name,
                        target=target,
                        success=True,
                        output={
                            "status": resp.status,
                            "headers": response_headers,
                            "body_length": len(text),
                            "url": str(resp.url)
                        },
                        findings=findings,
                        evidence=[{"type": "http_response", "status": resp.status, "headers": response_headers, "body_preview": text[:2000]}]
                    )
            except Exception as e:
                return ToolResult(
                    tool_name=self.definition.name,
                    target=target,
                    success=False,
                    error=str(e)
                )


class SubdomainEnumTool(BuiltinTool):
    """Passive subdomain enumeration"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="subdomain_enum",
            category=ToolCategory.OSINT,
            description="Passive subdomain enumeration via CT logs, search engines",
            version="1.0",
            tags=["subdomain", "recon", "passive", "osint"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import aiohttp

        sources = parameters.get("sources", ["crtsh", "wayback", "threatcrowd"])
        subdomains = set()

        async with aiohttp.ClientSession() as session:
            for source in sources:
                if source == "crtsh":
                    subdomains.update(await self._crtsh(session, target))
                elif source == "wayback":
                    subdomains.update(await self._wayback(session, target))
                elif source == "threatcrowd":
                    subdomains.update(await self._threatcrowd(session, target))

        findings = [{"type": "subdomain", "target": target, "subdomain": s} for s in sorted(subdomains)]

        return ToolResult(
            tool_name=self.definition.name,
            target=target,
            success=True,
            output={"subdomains": sorted(subdomains), "count": len(subdomains)},
            findings=findings
        )

    async def _crtsh(self, session, domain: str) -> Set[str]:
        subdomains = set()
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data:
                        name = entry.get("name_value", "")
                        for n in name.split("\n"):
                            n = n.strip().lower()
                            if n.endswith(f".{domain}") or n == domain:
                                subdomains.add(n)
        except Exception:
            pass
        return subdomains

    async def _wayback(self, session, domain: str) -> Set[str]:
        subdomains = set()
        try:
            url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data[1:]:  # Skip header
                        url = entry[0]
                        # Extract subdomain
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        host = parsed.netloc.lower()
                        if host.endswith(f".{domain}") or host == domain:
                            subdomains.add(host)
        except Exception:
            pass
        return subdomains

    async def _threatcrowd(self, session, domain: str) -> Set[str]:
        subdomains = set()
        try:
            url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for sub in data.get("subdomains", []):
                        subdomains.add(sub.lower())
        except Exception:
            pass
        return subdomains


class DirBruteforceTool(BuiltinTool):
    """Directory/file brute force"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="dir_bruteforce",
            category=ToolCategory.ACTIVE_WEB,
            description="Directory and file enumeration",
            version="1.0",
            tags=["dirbust", "enum", "web", "active"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import aiohttp

        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        wordlist = parameters.get("wordlist", "common")
        extensions = parameters.get("extensions", ["", ".php", ".html", ".js", ".txt", ".bak", ".old"])
        threads = parameters.get("threads", 20)
        status_codes = parameters.get("status_codes", [200, 301, 302, 403])

        words = self._get_wordlist(wordlist)
        paths = [w + ext for w in words for ext in extensions]

        found = []

        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(threads)

            async def check_path(path):
                async with semaphore:
                    url = target.rstrip("/") + "/" + path
                    try:
                        async with session.get(url, timeout=10, allow_redirects=False) as resp:
                            if resp.status in status_codes:
                                found.append({
                                    "path": path,
                                    "url": url,
                                    "status": resp.status,
                                    "size": resp.content_length
                                })
                    except Exception:
                        pass

            await asyncio.gather(*[check_path(p) for p in paths])

        findings = [{"type": "path_found", "target": target, "path": f["path"], "status": f["status"]} for f in found]

        return ToolResult(
            tool_name=self.definition.name,
            target=target,
            success=True,
            output={"found": found, "total_checked": len(paths)},
            findings=findings
        )

    def _get_wordlist(self, name: str) -> List[str]:
        wordlists = {
            "common": ["admin", "login", "wp-admin", "administrator", "dashboard", "panel", "api", "v1", "v2", "test", "dev", "staging", "backup", "config", "settings", "setup", "install", "phpinfo", "server-status", "robots.txt", "sitemap.xml", ".git", ".env", "web.config"],
            "raft-small": ["admin", "login", "dashboard", "api", "test", "dev", "backup", "config", "admin.php", "login.php", "index.php", "wp-login.php"],
            "quick": ["admin", "login", "wp-admin", "administrator", "api", "test", "backup"]
        }
        return wordlists.get(name, wordlists["common"])


class SSLScanTool(BuiltinTool):
    """SSL/TLS configuration scanner"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="ssl_scan",
            category=ToolCategory.PASSIVE,
            description="SSL/TLS certificate and configuration analysis",
            version="1.0",
            tags=["ssl", "tls", "certificate", "passive"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import ssl
        import socket
        from datetime import datetime

        port = parameters.get("port", 443)
        hostname = target.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

        findings = []
        cert_info = {}

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert)
                    x509 = ssl._ssl._test_decode_cert(cert_pem)

                    cert_info = {
                        "subject": dict(x509.get("subject", [])),
                        "issuer": dict(x509.get("issuer", [])),
                        "version": x509.get("version"),
                        "serial_number": x509.get("serialNumber"),
                        "not_before": x509.get("notBefore"),
                        "not_after": x509.get("notAfter"),
                        "subject_alt_names": x509.get("subjectAltName", []),
                        "signature_algorithm": x509.get("signatureAlgorithm"),
                        "public_key_algorithm": x509.get("subjectPublicKeyAlgorithm"),
                    }

                    # Check expiry
                    not_after = datetime.strptime(x509["notAfter"], "%b %d %H:%M:%S %Y %Z")
                    days_until_expiry = (not_after - datetime.now()).days
                    if days_until_expiry < 30:
                        findings.append({
                            "type": "cert_expiring_soon",
                            "target": target,
                            "days_remaining": days_until_expiry,
                            "severity": "high" if days_until_expiry < 7 else "medium"
                        })

                    # Check SAN
                    if not cert_info["subject_alt_names"]:
                        findings.append({
                            "type": "missing_san",
                            "target": target,
                            "severity": "medium"
                        })

                    # Check cipher
                    cipher = ssock.cipher()
                    if cipher:
                        cert_info["cipher"] = {"name": cipher[0], "version": cipher[1], "bits": cipher[2]}
                        if cipher[2] < 128:
                            findings.append({
                                "type": "weak_cipher",
                                "target": target,
                                "cipher": cipher[0],
                                "bits": cipher[2],
                                "severity": "high"
                            })

        except Exception as e:
            return ToolResult(
                tool_name=self.definition.name,
                target=target,
                success=False,
                error=str(e)
            )

        return ToolResult(
            tool_name=self.definition.name,
            target=target,
            success=True,
            output=cert_info,
            findings=findings,
            evidence=[{"type": "certificate", "pem": cert_pem}]
        )


class TechnologyDetectTool(BuiltinTool):
    """Technology fingerprinting"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="technology_detect",
            category=ToolCategory.PASSIVE,
            description="Web technology fingerprinting (headers, cookies, HTML patterns)",
            version="1.0",
            tags=["tech", "fingerprint", "wappalyzer", "passive"]
        )

    async def _execute_impl(self, target: str, parameters: Dict) -> ToolResult:
        import aiohttp
        import re

        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        technologies = {}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(target, timeout=15, ssl=False) as resp:
                    text = await resp.text()
                    headers = dict(resp.headers)
                    cookies = resp.cookies

                    # Server header
                    if "Server" in headers:
                        technologies["server"] = headers["Server"]

                    # X-Powered-By
                    if "X-Powered-By" in headers:
                        technologies["x_powered_by"] = headers["X-Powered-By"]

                    # Cookies
                    for name, cookie in cookies.items():
                        if name.startswith("PHPSESSID"):
                            technologies["php"] = True
                        elif name.startswith("JSESSIONID"):
                            technologies["java"] = True
                        elif name.startswith("ASP.NET"):
                            technologies["aspnet"] = True
                        elif "laravel" in name.lower():
                            technologies["laravel"] = True
                        elif "django" in name.lower():
                            technologies["django"] = True

                    # HTML patterns
                    patterns = {
                        "wordpress": [r"wp-content", r"wp-includes", r"WordPress"],
                        "drupal": [r"Drupal", r"drupal", r"/sites/default/"],
                        "joomla": [r"Joomla", r"joomla", r"/media/system/"],
                        "react": [r"react", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"],
                        "vue": [r"vue\.js", r"Vue\.js", r"__VUE__"],
                        "angular": [r"angular", r"ng-", r"ngVersion"],
                        "jquery": [r"jquery", r"jQuery"],
                        "bootstrap": [r"bootstrap", r"Bootstrap"],
                        "nginx": [r"nginx"],
                        "apache": [r"apache"],
                        "iis": [r"IIS", r"Microsoft-IIS"],
                        "cloudflare": [r"cloudflare", r"__cfduid"],
                    }

                    for tech, pats in patterns.items():
                        for pat in pats:
                            if re.search(pat, text, re.IGNORECASE):
                                technologies[tech] = True
                                break

        findings = [{"type": "technology", "target": target, "technology": k, "version": v if isinstance(v, str) else "detected"} for k, v in technologies.items()]

        return ToolResult(
            tool_name=self.definition.name,
            target=target,
            success=True,
            output={"technologies": technologies},
            findings=findings
        )


# ======================== EXTERNAL CLI TOOL WRAPPERS ========================

class NmapTool(CLITOOL):
    """Nmap wrapper"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="nmap",
            category=ToolCategory.NETWORK,
            description="Network exploration and security auditing",
            version="7.94",
            homepage="https://nmap.org",
            tags=["port_scan", "service_detect", "os_detect", "vuln_scan", "network"],
            opt_in=False,
            parameters={
                "scan_type": {"type": "string", "enum": ["syn", "connect", "udp", "ack"], "default": "syn"},
                "ports": {"type": "string", "default": "top-1000"},
                "scripts": {"type": "string", "default": "vuln"},
                "timing": {"type": "string", "enum": ["T0", "T1", "T2", "T3", "T4", "T5"], "default": "T3"},
                "os_detection": {"type": "boolean", "default": True},
                "version_detection": {"type": "boolean", "default": True},
            }
        )

    async def build_command(self, target: str, parameters: Dict) -> List[str]:
        scan_type = parameters.get("scan_type", "syn")
        ports = parameters.get("ports", "top-1000")
        scripts = parameters.get("scripts", "vuln")
        timing = parameters.get("timing", "T3")
        os_detection = parameters.get("os_detection", True)
        version_detection = parameters.get("version_detection", True)

        scan_flags = {
            "syn": "-sS",
            "connect": "-sT",
            "udp": "-sU",
            "ack": "-sA"
        }

        cmd = [
            self.binary_path or "nmap",
            scan_flags.get(scan_type, "-sS"),
            f"-{timing}",
            "-p", ports,
        ]

        if version_detection:
            cmd.append("-sV")
        if os_detection:
            cmd.append("-O")
        if scripts:
            cmd.extend(["--script", scripts])
        if parameters.get("output_format"):
            cmd.extend(["-oX", "-"])  # XML to stdout

        cmd.append(target)
        return cmd

    async def parse_findings(self, output: str, target: str) -> List[Dict]:
        # Parse XML output
        import xml.etree.ElementTree as ET
        findings = []
        try:
            root = ET.fromstring(output)
            for host in root.findall("host"):
                for port in host.findall(".//port"):
                    port_id = port.get("portid")
                    protocol = port.get("protocol")
                    state = port.find("state").get("state") if port.find("state") is not None else "unknown"
                    service = port.find("service")
                    service_name = service.get("name") if service is not None else "unknown"
                    service_version = service.get("version") if service is not None else ""

                    if state == "open":
                        findings.append({
                            "type": "open_port",
                            "target": target,
                            "port": int(port_id),
                            "protocol": protocol,
                            "service": service_name,
                            "version": service_version
                        })
        except Exception:
            pass
        return findings


class NucleiTool(CLITOOL):
    """Nuclei vulnerability scanner wrapper"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="nuclei",
            category=ToolCategory.VULN_SCAN,
            description="Fast vulnerability scanner with template-based detection",
            version="3.0",
            homepage="https://nuclei.projectdiscovery.io",
            tags=["vuln_scan", "cve", "cwe", "misconfig", "exposed_panels"],
            opt_in=False,
            parameters={
                "severity": {"type": "string", "default": "high,critical"},
                "tags": {"type": "string", "default": ""},
                "exclude_tags": {"type": "string", "default": "dos,fuzz,intrusive"},
                "rate_limit": {"type": "integer", "default": 10},
                "timeout": {"type": "integer", "default": 10},
                "retries": {"type": "integer", "default": 1},
                "templates": {"type": "string", "default": ""},  # custom template path
            }
        )

    async def build_command(self, target: str, parameters: Dict) -> List[str]:
        severity = parameters.get("severity", "high,critical")
        tags = parameters.get("tags", "")
        exclude_tags = parameters.get("exclude_tags", "dos,fuzz,intrusive")
        rate_limit = parameters.get("rate_limit", 10)
        timeout = parameters.get("timeout", 10)
        retries = parameters.get("retries", 1)
        templates = parameters.get("templates", "")

        cmd = [
            self.binary_path or "nuclei",
            "-target", target,
            "-severity", severity,
            "-rate-limit", str(rate_limit),
            "-timeout", str(timeout),
            "-retries", str(retries),
            "-json",
            "-silent",
        ]

        if tags:
            cmd.extend(["-tags", tags])
        if exclude_tags:
            cmd.extend(["-exclude-tags", exclude_tags])
        if templates:
            cmd.extend(["-t", templates])

        return cmd

    async def parse_findings(self, output: str, target: str) -> List[Dict]:
        findings = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            try:
                result = json.loads(line)
                info = result.get("info", {})
                findings.append({
                    "type": "vulnerability",
                    "target": target,
                    "template_id": result.get("template-id"),
                    "name": info.get("name"),
                    "severity": info.get("severity"),
                    "description": info.get("description"),
                    "cve": info.get("cve", []),
                    "cwe": info.get("cwe", []),
                    "tags": info.get("tags", []),
                    "reference": info.get("reference", []),
                    "matched_at": result.get("matched-at"),
                    "extracted_results": result.get("extracted-results", [])
                })
            except json.JSONDecodeError:
                pass
        return findings


class FFUFTool(CLITOOL):
    """FFUF fast web fuzzer wrapper"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="ffuf",
            category=ToolCategory.ACTIVE_WEB,
            description="Fast web fuzzer for directory/file/virtual host discovery",
            version="2.1",
            homepage="https://github.com/ffuf/ffuf",
            tags=["fuzzing", "dirbust", "vhost", "parameter_fuzz"],
            opt_in=False,
            parameters={
                "wordlist": {"type": "string", "default": "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt"},
                "extensions": {"type": "string", "default": "php,html,js,txt,bak,old,zip,tar.gz"},
                "threads": {"type": "integer", "default": 40},
                "rate": {"type": "integer", "default": 0},
                "match_codes": {"type": "string", "default": "200,301,302,307,403,401,500"},
                "filter_codes": {"type": "string", "default": "404"},
                "filter_size": {"type": "string", "default": "0"},
                "recursion": {"type": "boolean", "default": False},
                "recursion_depth": {"type": "integer", "default": 2},
            }
        )

    async def build_command(self, target: str, parameters: Dict) -> List[str]:
        wordlist = parameters.get("wordlist", "raft-medium")
        extensions = parameters.get("extensions", "php,html,js,txt,bak,old")
        threads = parameters.get("threads", 40)
        rate = parameters.get("rate", 0)
        match_codes = parameters.get("match_codes", "200,301,302,307,403,401,500")
        filter_codes = parameters.get("filter_codes", "404")
        filter_size = parameters.get("filter_size", "0")
        recursion = parameters.get("recursion", False)
        recursion_depth = parameters.get("recursion_depth", 2)

        # Resolve wordlist path
        wordlist_paths = {
            "raft-small": "/usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt",
            "raft-medium": "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt",
            "raft-large": "/usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt",
            "common": "/usr/share/wordlists/dirb/common.txt",
            "big": "/usr/share/seclists/Discovery/Web-Content/big.txt",
        }
        wl_path = wordlist_paths.get(wordlist, wordlist)

        cmd = [
            self.binary_path or "ffuf",
            "-u", target.rstrip("/") + "/FUZZ",
            "-w", wl_path,
            "-e", extensions,
            "-t", str(threads),
            "-mc", match_codes,
            "-fc", filter_codes,
            "-fs", filter_size,
            "-json",
            "-s",  # silent
        ]

        if rate > 0:
            cmd.extend(["-rate", str(rate)])
        if recursion:
            cmd.extend(["-recursion", "-recursion-depth", str(recursion_depth)])

        return cmd

    async def parse_findings(self, output: str, target: str) -> List[Dict]:
        findings = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            try:
                result = json.loads(line)
                if result.get("status") in [200, 301, 302, 307, 403, 401, 500]:
                    findings.append({
                        "type": "path_found",
                        "target": target,
                        "url": result.get("url"),
                        "status": result.get("status"),
                        "length": result.get("length"),
                        "words": result.get("words"),
                        "lines": result.get("lines"),
                    })
            except json.JSONDecodeError:
                pass
        return findings


class SQLMapTool(CLITOOL):
    """SQLMap wrapper (approval-gated)"""

    def _get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="sqlmap",
            category=ToolCategory.VULN_SCAN,
            description="Automatic SQL injection and database takeover tool",
            version="1.7",
            homepage="http://sqlmap.org",
            tags=["sqli", "injection", "database", "exploitation"],
            opt_in=True,
            approval_gated=True,
            dangerous=True,
            parameters={
                "level": {"type": "integer", "default": 1, "max": 5},
                "risk": {"type": "integer", "default": 1, "max": 3},
                "technique": {"type": "string", "default": "BEUSTQ"},
                "threads": {"type": "integer", "default": 1},
                "batch": {"type": "boolean", "default": True},
                "crawl_depth": {"type": "integer", "default": 0},
            }
        )

    async def build_command(self, target: str, parameters: Dict) -> List[str]:
        level = parameters.get("level", 1)
        risk = parameters.get("risk", 1)
        technique = parameters.get("technique", "BEUSTQ")
        threads = parameters.get("threads", 1)
        batch = parameters.get("batch", True)
        crawl = parameters.get("crawl_depth", 0)

        cmd = [
            self.binary_path or "sqlmap",
            "-u", target,
            "--level", str(level),
            "--risk", str(risk),
            "--technique", technique,
            "--threads", str(threads),
            "--batch" if batch else "",
            "--output-dir", "/tmp/sqlmap",
            "--flush-session",
            "--fresh-queries",
        ]

        if crawl > 0:
            cmd.extend(["--crawl", str(crawl)])

        if parameters.get("data"):  # POST data
            cmd.extend(["--data", parameters["data"]])

        return [c for c in cmd if c]

    async def parse_findings(self, output: str, target: str) -> List[Dict]:
        findings = []
        if "sqlmap identified the following injection point" in output.lower():
            findings.append({
                "type": "sqli",
                "target": target,
                "description": "SQL injection vulnerability detected",
                "severity": "high",
                "details": output[:2000]
            })
        return findings


# ======================== ARSENAL REGISTRY ========================

class Arsenal:
    """Central tool registry and execution engine"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {c: [] for c in ToolCategory}
        self._load_builtin_tools()
        self._load_cli_tools()

    def _load_builtin_tools(self) -> None:
        """Load all built-in tools"""
        builtins = [
            DNSLookupTool,
            PortScanTool,
            HTTPRequestTool,
            SubdomainEnumTool,
            DirBruteforceTool,
            SSLScanTool,
            TechnologyDetectTool,
        ]

        for tool_class in builtins:
            tool = tool_class(self.config.get(tool_class.__name__.lower(), {}))
            self.register_tool(tool)

    def _load_cli_tools(self) -> None:
        """Load CLI tool wrappers"""
        cli_tools = {
            "nmap": NmapTool,
            "nuclei": NucleiTool,
            "ffuf": FFUFTool,
            "sqlmap": SQLMapTool,
        }

        for name, tool_class in cli_tools.items():
            tool_config = self.config.get(name, {})
            # Check if opt-in tools are enabled
            if name in ["sqlmap"] and not self.config.get("full_arsenal", False):
                logger.info(f"Tool {name} is opt-in, skipping (set full_arsenal=true to enable)")
                continue
            try:
                tool = tool_class(tool_config)
                self.register_tool(tool)
            except Exception as e:
                logger.warning(f"Failed to load CLI tool {name}: {e}")

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool"""
        self.tools[tool.definition.name] = tool
        self.categories[tool.definition.category].append(tool.definition.name)
        logger.debug(f"Registered tool: {tool.definition.name} ({tool.definition.category.value})")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        return [self.tools[name] for name in self.categories.get(category, []) if name in self.tools]

    def list_tools(self) -> List[Dict]:
        return [tool.definition.__dict__ for tool in self.tools.values()]

    async def execute_tool(self, name: str, target: str, parameters: Dict = None) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                tool_name=name,
                target=target,
                success=False,
                error=f"Tool not found: {name}"
            )

        # Check installation
        status = await tool.check_installation()
        if status != ToolStatus.AVAILABLE:
            return ToolResult(
                tool_name=name,
                target=target,
                success=False,
                error=f"Tool not available: {status.value}"
            )

        # Check approval for gated tools
        if tool.definition.approval_gated:
            if not parameters or not parameters.get("_approved", False):
                return ToolResult(
                    tool_name=name,
                    target=target,
                    success=False,
                    error="Tool requires explicit approval (add '_approved': true to parameters)"
                )

        return await tool.execute(target, parameters or {})

    async def execute_category(self, category: ToolCategory, target: str, parameters: Dict = None) -> List[ToolResult]:
        """Execute all tools in a category"""
        results = []
        tools = self.get_tools_by_category(category)
        for tool in tools:
            result = await self.execute_tool(tool.definition.name, target, parameters)
            results.append(result)
        return results


# ======================== FACTORY ========================

def create_arsenal(config: Dict = None) -> Arsenal:
    """Factory function"""
    return Arsenal(config)


# Export
__all__ = [
    "ToolCategory",
    "ToolStatus",
    "ToolResult",
    "ToolDefinition",
    "BaseTool",
    "BuiltinTool",
    "CLITOOL",
    "DNSLookupTool",
    "PortScanTool",
    "HTTPRequestTool",
    "SubdomainEnumTool",
    "DirBruteforceTool",
    "SSLScanTool",
    "TechnologyDetectTool",
    "NmapTool",
    "NucleiTool",
    "FFUFTool",
    "SQLMapTool",
    "Arsenal",
    "create_arsenal",
]