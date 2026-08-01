# Windows File Search with Everything (voidtools)

## Overview

[Everything](https://www.voidtools.com) is a Windows search engine that
indexes the entire NTFS filesystem instantly. It finds files by name in
milliseconds even across multi-TB drives, unlike `grep -r` or `find` which
scan the filesystem live.

**es.exe** is the command-line interface. It's instant, respects NTFS
permissions, and supports regex and boolean search syntax.

## Installed Locations

Both a service install and a portable copy exist:

| Component | Path |
|-----------|------|
| Service | `D:\Program Files\Everything\Everything.exe` |
| Portable | `D:\Portable_Soft\Everything-1.5.0.1408a.x64\Everything.exe` |
| CLI | `D:\Portable_Soft\Everything-1.5.0.1408a.x64\es.exe` |

The service runs automatically on boot. The portable version can be run
manually for an independent index.

## Basic Usage (es.exe)

```bash
/d/Portable_Soft/Everything-1.5.0.1408a.x64/es.exe "query"
```

### Query Syntax

```bash
# Exact filename match
es.exe "config.yaml"

# Wildcard
es.exe "*.md"
es.exe "*.{py,js,ts}"

# Folder-specific
es.exe "D:\Portable_Soft\hermes *.env"
es.exe "*.py D:\Portable_Soft\hermes\scripts"

# Boolean
es.exe "access_token | refresh_token"
es.exe "error.txt | debug.log"
es.exe "*.md !node_modules"
es.exe "*.py && !test"

# Regex
es.exe "regex:config\.(yaml|yml|json)$"
es.exe "regex:docker-compose\.(yml|yaml)$"

# Content keywords (Everything only indexes filenames + metadata;
# grep the results for content)
es.exe "*.py" | xargs grep -l "def main" 2>/dev/null
```

### Piping for Content Search

Everything only indexes filenames (not file contents). Combine with `grep`:
```bash
# Find config files then grep for a pattern
es.exe "*.{yaml,yml}" | xargs grep -l "custom_providers" 2>/dev/null

# Find Python files containing a function
es.exe "*.py" | xargs grep -l "def init_browser" 2>/dev/null
```

### Excluding Noise

Exclude common noise directories:
```bash
es.exe "*.py !node_modules !.git !cache !venv"
es.exe "*.md !node_modules !.git !__pycache__"
es.exe "config* !node_modules !.git"
```

## When to Use es.exe vs grep/search_files

| Use case | Tool |
|----------|------|
| Find files by **name** or pattern | `es.exe` — instant |
| Search file **contents** | `grep` / `search_files` tool |
| Find AND content-search (narrow) | `es.exe "pattern" \| xargs grep "content"` |
| Find inside **node_modules** etc. | Only es.exe (grep crawls + times out) |
| **Project-local** search (Hermes scripts) | `search_files` tool — faster than global es.exe |
| **System-wide** file find | `es.exe` — grep would take minutes |

## Emacs regex

**es.exe** uses Emacs-style regex by default, not PCRE. Key differences:
- `\( \)` for capture groups, not `( )`
- `\|` for alternation
- Use `regex:` prefix to enable regex mode (without it, wildcard/matching
  syntax applies)

Example for finding proxy configs:
```
es.exe "regex:Free\(Qwen\|Deepseek\)API"
```

## Why Not Plain grep/find

- **`grep -r`** on D:\ or C:\ takes minutes or hours — es.exe returns in
  milliseconds
- **`find`** (Windows `dir /s` / MSYS `find`) is also filesystem-scanning
  and slow
- **Everything indexes:** only new/changed files since last boot are
  scanned, making it near-instant for repeated queries
