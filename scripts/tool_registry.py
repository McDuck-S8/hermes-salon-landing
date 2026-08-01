#!/usr/bin/env python3
"""
Tool Registry — External tool detection, validation, and execution.
Implements: tool discovery, version checking, fallback chains, timeout management.
"""

import os
import json
import subprocess
import shutil
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Callable
import platform

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache" / "tools"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

TOOL_CACHE_FILE = CACHE_DIR / "tool_registry.json"


class ToolStatus(Enum):
    AVAILABLE = "available"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ToolSpec:
    """Specification for an external tool."""
    name: str
    command: str                          # Command to run (e.g., "yt-dlp", "npx lighthouse")
    version_cmd: str = "--version"        # Command to get version
    version_regex: str = r"(\d+\.\d+\.\d+)"  # Regex to extract version
    min_version: Optional[str] = None     # Minimum required version
    install_hint: str = ""                # Installation hint
    required: bool = True                 # If True, missing = error
    category: str = "general"             # Category for grouping
    aliases: List[str] = None             # Alternative names
    env_vars: Dict[str, str] = None       # Required env vars
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.env_vars is None:
            self.env_vars = {}


@dataclass
class ToolInfo:
    """Runtime information about a tool."""
    name: str
    status: ToolStatus
    path: Optional[str] = None            # Full path to executable
    version: Optional[str] = None         # Detected version
    raw_output: str = ""                  # Raw version output
    error: str = ""                       # Error message if any
    checked_at: float = 0                 # Timestamp of check
    available: bool = False               # Quick access
    metadata: Dict = None                 # Extra info
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ToolRegistry:
    """Manages external tool discovery, validation, and execution."""
    
    def __init__(self, cache_file: Path = TOOL_CACHE_FILE):
        self.cache_file = cache_file
        self.tools: Dict[str, ToolSpec] = {}
        self.cache: Dict[str, ToolInfo] = {}
        self._lock = threading.RLock()
        self._register_default_tools()
        self._load_cache()
    
    def _register_default_tools(self):
        """Register commonly used tools."""
        defaults = [
            ToolSpec(
                name="yt-dlp",
                command="yt-dlp",
                version_cmd="--version",
                version_regex=r"(\d{4}\.\d{2}\.\d{2})",
                min_version="2023.01.01",
                install_hint="pip install yt-dlp",
                category="media",
            ),
            ToolSpec(
                name="npx",
                command="npx",
                version_cmd="--version",
                version_regex=r"(\d+\.\d+\.\d+)",
                min_version="8.0.0",
                install_hint="npm install -g npx",
                category="node",
            ),
            ToolSpec(
                name="lighthouse",
                command="npx lighthouse",
                version_cmd="--version",
                version_regex=r"(\d+\.\d+\.\d+)",
                min_version="10.0.0",
                install_hint="npm install -g lighthouse",
                category="audit",
            ),
            ToolSpec(
                name="html-validate",
                command="npx html-validate",
                version_cmd="--version",
                version_regex=r"(\d+\.\d+\.\d+)",
                min_version="8.0.0",
                install_hint="npm install -g html-validate",
                category="audit",
            ),
            ToolSpec(
                name="eslint",
                command="npx eslint",
                version_cmd="--version",
                version_regex=r"(\d+\.\d+\.\d+)",
                min_version="8.0.0",
                install_hint="npm install -g eslint",
                category="code",
            ),
            ToolSpec(
                name="node",
                command="node",
                version_cmd="--version",
                version_regex=r"v?(\d+\.\d+\.\d+)",
                min_version="18.0.0",
                install_hint="Install from nodejs.org",
                category="runtime",
            ),
            ToolSpec(
                name="python",
                command="python",
                version_cmd="--version",
                version_regex=r"Python (\d+\.\d+\.\d+)",
                min_version="3.10.0",
                install_hint="Install from python.org",
                category="runtime",
            ),
            ToolSpec(
                name="git",
                command="git",
                version_cmd="--version",
                version_regex=r"git version (\d+\.\d+\.\d+)",
                min_version="2.30.0",
                install_hint="Install from git-scm.com",
                category="vcs",
            ),
            ToolSpec(
                name="curl",
                command="curl",
                version_cmd="--version",
                version_regex=r"curl (\d+\.\d+\.\d+)",
                min_version="7.68.0",
                install_hint="Built-in on Windows 10+",
                category="network",
            ),
            ToolSpec(
                name="taskkill",
                command="taskkill",
                version_cmd="/?",
                version_regex=r"(\d+\.\d+\.\d+)",
                min_version="1.0.0",
                install_hint="Built-in Windows",
                category="system",
                required=False,
            ),
            ToolSpec(
                name="python-venv",
                command="python",
                version_cmd="-m venv --help",
                version_regex=r"Python (\d+\.\d+\.\d+)",
                min_version="3.10.0",
                install_hint="Built-in Python",
                category="runtime",
                required=False,
            ),
        ]
        
        for tool in defaults:
            self.register(tool)
    
    def register(self, spec: ToolSpec) -> 'ToolRegistry':
        """Register a tool specification."""
        with self._lock:
            self.tools[spec.name] = spec
            for alias in spec.aliases:
                self.tools[alias] = spec
        return self
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        with self._lock:
            if name in self.tools:
                del self.tools[name]
                return True
        return False
    
    def get_spec(self, name: str) -> Optional[ToolSpec]:
        """Get tool specification by name."""
        return self.tools.get(name)
    
    def check_tool(self, name: str, force: bool = False) -> ToolInfo:
        """
        Check if a tool is available and get its version.
        Returns ToolInfo with status and version info.
        """
        with self._lock:
            spec = self.tools.get(name)
            if not spec:
                return ToolInfo(
                    name=name,
                    status=ToolStatus.UNKNOWN,
                    error=f"Tool '{name}' not registered",
                    checked_at=time.time()
                )
            
            # Return cached if not forced and recent (< 1 hour)
            if not force and name in self.cache:
                cached = self.cache[name]
                if time.time() - cached.checked_at < 3600:
                    return cached
            
            # Check tool
            info = self._check_tool_impl(spec)
            info.checked_at = time.time()
            self.cache[name] = info
            self._save_cache()
            return info
    
    def _check_tool_impl(self, spec: ToolSpec) -> ToolInfo:
        """Actually check tool availability and version."""
        # Find executable
        paths_to_try = []
        
        # Try direct command
        path = shutil.which(spec.command.split()[0])
        if path:
            paths_to_try.append(path)
        
        # Try aliases
        for alias in spec.aliases:
            path = shutil.which(alias.split()[0])
            if path:
                paths_to_try.append(path)
        
        # Try common locations on Windows
        if platform.system() == "Windows":
            for ext in [".exe", ".cmd", ".bat"]:
                for p in [
                    os.environ.get("PROGRAMFILES", ""),
                    os.environ.get("PROGRAMFILES(X86)", ""),
                    os.environ.get("LOCALAPPDATA", ""),
                ]:
                    if p:
                        candidate = Path(p) / f"{spec.command.split()[0]}{ext}"
                        if candidate.exists():
                            paths_to_try.append(str(candidate))
        
        # Try each path
        for path in paths_to_try:
            try:
                # Test if executable runs
                test_cmd = [path]
                if spec.version_cmd:
                    test_cmd.append(spec.version_cmd)
                
                result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                )
                
                if result.returncode == 0 or result.stdout:
                    # Extract version
                    version = None
                    output = result.stdout or result.stderr
                    if spec.version_regex:
                        import re
                        match = re.search(spec.version_regex, output)
                        if match:
                            version = match.group(1)
                    
                    # Check minimum version
                    status = ToolStatus.AVAILABLE
                    if spec.min_version and version:
                        if not self._version_meets_min(version, spec.min_version):
                            status = ToolStatus.VERSION_MISMATCH
                    
                    return ToolInfo(
                        name=spec.name,
                        status=status,
                        path=path,
                        version=version,
                        raw_output=output.strip(),
                        available=True,
                        checked_at=time.time()
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError, OSError):
                continue
        
        # Not found
        return ToolInfo(
            name=spec.name,
            status=ToolStatus.MISSING,
            error=f"Tool not found: {spec.command}",
            available=False,
            checked_at=time.time()
        )
    
    def _version_meets_min(self, version: str, min_version: str) -> bool:
        """Check if version meets minimum."""
        try:
            v_parts = [int(x) for x in version.split('.')]
            min_parts = [int(x) for x in min_version.split('.')]
            
            # Pad shorter with zeros
            max_len = max(len(v_parts), len(min_parts))
            v_parts += [0] * (max_len - len(v_parts))
            min_parts += [0] * (max_len - len(min_parts))
            
            return v_parts >= min_parts
        except:
            return True  # Assume ok if can't parse
    
    def require_tool(self, name: str) -> ToolInfo:
        """Get tool info, raise if not available."""
        info = self.check_tool(name)
        if not info.available:
            spec = self.tools.get(name)
            hint = spec.install_hint if spec else ""
            raise RuntimeError(
                f"Required tool '{name}' not available. {hint}"
            )
        return info
    
    def check_all(self, force: bool = False) -> Dict[str, ToolInfo]:
        """Check all registered tools."""
        results = {}
        for name in self.tools:
            results[name] = self.check_tool(name, force=force)
        return results
    
    def get_available(self, category: str = None) -> List[ToolInfo]:
        """Get list of available tools, optionally filtered by category."""
        results = []
        for name, spec in self.tools.items():
            if category and spec.category != category:
                continue
            info = self.check_tool(name)
            if info.available:
                results.append(info)
        return results
    
    def run_tool(
        self,
        name: str,
        args: List[str],
        timeout: int = 60,
        cwd: Optional[Path] = None,
        env: Dict[str, str] = None,
        capture: bool = True,
        stdin: str = None
    ) -> Tuple[int, str, str]:
        """
        Run a tool with arguments.
        Returns: (returncode, stdout, stderr)
        """
        info = self.require_tool(name)
        
        cmd = [info.path] + args
        
        env_vars = os.environ.copy()
        if env:
            env_vars.update(env)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=timeout,
                cwd=str(cwd) if cwd else None,
                env=env_vars,
                input=stdin,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout after {timeout}s"
        except FileNotFoundError:
            return -1, "", f"Executable not found: {name}"
        except Exception as e:
            return -1, "", str(e)
    
    def run_with_fallback(
        self,
        primary: str,
        fallback: str,
        args: List[str],
        timeout: int = 60,
        **kwargs
    ) -> Tuple[int, str, str]:
        """Try primary tool, fall back to alternative."""
        try:
            return self.run_tool(primary, args, timeout=timeout)
        except Exception as e:
            print(f"[TOOL] Primary {primary} failed: {e}, trying fallback {fallback}")
            return self.run_tool(fallback, args, timeout=timeout)
    
    def _load_cache(self):
        """Load tool cache from disk."""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text())
                for name, info in data.items():
                    self.cache[name] = ToolInfo(**info)
            except Exception:
                pass
    
    def _save_cache(self):
        """Save tool cache to disk."""
        try:
            data = {name: asdict(info) for name, info in self.cache.items()}
            self.cache_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
    
    def list_tools(self, category: str = None) -> List[Dict]:
        """List all registered tools with their status."""
        results = []
        for name, spec in self.tools.items():
            if category and spec.category != category:
                continue
            info = self.check_tool(name)
            results.append({
                "name": name,
                "category": spec.category,
                "status": info.status.value,
                "version": info.version,
                "path": info.path,
                "required": spec.required,
                "install_hint": spec.install_hint,
            })
        return results
    
    def get_missing_required(self) -> List[str]:
        """Get list of required tools that are missing."""
        missing = []
        for name, spec in self.tools.items():
            if spec.required:
                info = self.check_tool(name)
                if not info.available:
                    missing.append(name)
        return missing


# Global registry instance
_registry: Optional[ToolRegistry] = None
_registry_lock = threading.Lock()


def get_tool_registry() -> ToolRegistry:
    """Get global tool registry instance."""
    global _registry
    with _registry_lock:
        if _registry is None:
            _registry = ToolRegistry()
        return _registry


def check_tool(name: str, force: bool = False) -> ToolInfo:
    """Convenience function to check a tool."""
    return get_tool_registry().check_tool(name, force=force)


def require_tool(name: str) -> ToolInfo:
    """Require a tool, raise if not available."""
    return get_tool_registry().require_tool(name)


def run_tool(name: str, args: List[str], **kwargs) -> Tuple[int, str, str]:
    """Run a tool with arguments."""
    return get_tool_registry().run_tool(name, args, **kwargs)


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tool_registry.py <command> [args]")
        print("Commands: list, check <name>, check-all, missing")
        sys.exit(1)
    
    registry = get_tool_registry()
    cmd = sys.argv[1]
    
    if cmd == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        tools = registry.list_tools(category)
        for t in tools:
            status_icon = "✓" if t["status"] == "available" else "✗"
            print(f"  {status_icon} {t['name']} ({t['category']}) - v{t['version'] or 'unknown'} {t['path'] or ''}")
    
    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: check <tool_name>")
            sys.exit(1)
        info = registry.check_tool(sys.argv[2], force=True)
        print(json.dumps(asdict(info), indent=2))
    
    elif cmd == "check-all":
        results = registry.check_all(force=True)
        for name, info in results.items():
            status = "✓" if info.available else "✗"
            print(f"  {status} {name}: {info.version or 'N/A'} ({info.status.value})")
    
    elif cmd == "missing":
        missing = registry.get_missing_required()
        if missing:
            print("Missing required tools:")
            for m in missing:
                print(f"  - {m}")
        else:
            print("All required tools available")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()