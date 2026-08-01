# tool_registry.py — Reference

## Purpose
External tool discovery, validation, version checking, and fallback chains. Eliminates "command not found", version mismatches, and blocked pipelines.

## Key Classes

### ToolSpec
```python
@dataclass
class ToolSpec:
    name: str
    command: str                    # e.g., "yt-dlp", "npx lighthouse"
    version_cmd: str = "--version"  # Command to get version
    version_regex: str = r"(\d+\.\d+\.\d+)"
    min_version: Optional[str] = None
    install_hint: str = ""
    required: bool = True
    category: str = "general"
    aliases: List[str] = None
    env_vars: Dict[str, str] = None
```

### ToolInfo
```python
@dataclass
class ToolInfo:
    name: str
    status: ToolStatus  # AVAILABLE, MISSING, VERSION_MISMATCH, ERROR, UNKNOWN
    path: Optional[str] = None
    version: Optional[str] = None
    raw_output: str = ""
    error: str = ""
    checked_at: float = 0
    available: bool = False
    metadata: Dict = None
```

### ToolRegistry
```python
registry = ToolRegistry()  # Singleton via get_tool_registry()

# Registration
registry.register(ToolSpec(...))
registry.unregister(name)

# Checking
info = registry.check_tool(name, force=False)  # Cached 1hr
info = registry.require_tool(name)              # Raises if unavailable
results = registry.check_all(force=True)        # Pre-flight

# Execution
code, stdout, stderr = registry.run_tool(name, args, timeout=60, cwd=..., env=...)
code, stdout, stderr = registry.run_with_fallback(primary, fallback, args, ...)

# Listing
tools = registry.list_tools(category="node")    # Filter by category
missing = registry.get_missing_required()
```

## Default Registered Tools
| Tool | Command | Category | Required |
|------|---------|----------|----------|
| yt-dlp | yt-dlp | media | ✅ |
| npx | npx | node | ✅ |
| lighthouse | npx lighthouse | audit | ✅ |
| html-validate | npx html-validate | audit | ✅ |
| eslint | npx eslint | code | ✅ |
| node | node | runtime | ✅ |
| python | python | runtime | ✅ |
| git | git | vcs | ✅ |
| curl | curl | network | ✅ |
| taskkill | taskkill | system | ❌ |
| python-venv | python -m venv | runtime | ❌ |

## Version Checking
- Extracts version via regex from `stdout`/`stderr`
- Compares semantic version (pads with zeros)
- Returns `VERSION_MISMATCH` if below `min_version`

## Windows Path Resolution
- Checks `shutil.which()` first
- Falls back to `PROGRAMFILES`, `PROGRAMFILES(X86)`, `LOCALAPPDATA`
- Adds `.exe`, `.cmd`, `.bat` extensions

## Cache
- `cache/tools/tool_registry.json` — persists ToolInfo
- TTL: 1 hour (configurable)
- `force=True` bypasses cache

## Test Results (2026-07-29)
```
✅ python: 3.13.2
✅ git: 2.40.0
✅ curl: 7.88.1
✅ node: 24.16.0
✅ npx: 11.13.0
✅ lighthouse: 11.13.0 (via npx)
✅ html-validate: 11.13.0 (via npx)
✅ eslint: 11.13.0 (via npx)
✅ taskkill: available (via /?)
❌ yt-dlp: missing (installed as python module)
❌ python-venv: missing (checks python -m venv --help)
```

## Integration
```python
# In any script needing external tools
from scripts.tool_registry import get_tool_registry, require_tool, run_tool

registry = get_tool_registry()
registry.check_all(force=True)  # Pre-flight at session start

# Use
code, out, err = run_tool("yt-dlp", ["--dump-json", url])

# With fallback
code, out, err = registry.run_with_fallback("yt-dlp", "curl", args)
```