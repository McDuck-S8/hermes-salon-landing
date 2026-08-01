# System-Wide File Search on Windows

## Why Not search_files

`search_files` (ripgrep-based) searches within `D:/Portable_Soft/hermes/` project directory.
For files ANYWHERE on the PC, it won't find them.

## es.exe (Everything Search CLI)

**Path:** `D:\Portable_Soft\Everything-1.5.0.1408a.x64\es.exe`
**Status:** Installed and running (3 Everything.exe processes active)

### Usage

```bash
# Find files by name
/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe "filename"

# Limit results, show date-modified
/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe -n 20 -dm "pattern"

# Search in specific path
/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe -path "D:\\my_openclaude" kanban

# Files only (no folders)
/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe /a-d "*.html"

# Full syntax: es.exe [options] search text
#   -n <num>       limit results
#   -dm            show date-modified column
#   -path <path>   search in specific path
#   /a-d           files only
#   /ad            folders only
```

### When to Use es.exe vs search_files

| Tool | Scope | Use for |
|------|-------|---------|
| `search_files` | Project directory only | Code search, grep within project |
| `es.exe` | Whole PC (indexed by Everything) | Finding ANY file anywhere: configs, apps, templates, system files |

### Note

Everything service runs on this machine (3 processes: 1 service + 2 user instances).
The index is real-time — no need to wait for indexing.
