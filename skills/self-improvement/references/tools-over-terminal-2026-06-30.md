# Tools Over Terminal — Use Right Tools

## Problem
Agent uses terminal cat/grep/sed instead of proper tools. User: "ты снова сам!!!!"

## Tool Mapping

| Instead of terminal | Use this |
|---------------------|----------|
| `cat file` | `read_file(path)` |
| `grep pattern file` | `search_files(pattern, target="content")` |
| `find / -name "*.py"` | `search_files("*.py", target="files")` |
| `sed 's/old/new/'` | `patch(path, old_string, new_string)` |
| `echo "content" > file` | `write_file(path, content)` |
| `python -c "..."` | `execute_code(code)` |
| `curl url` | `web_search(query)` or `web_extract(urls)` |

## Why
- read_file has line numbers, pagination, error handling
- search_files is ripgrep-backed, faster than shell grep
- patch has fuzzy matching, won't break on whitespace
- write_file creates parent dirs automatically
- execute_code runs in-session, no subprocess overhead

## When terminal IS correct
- Running scripts: `python scripts/foo.py`
- Git operations: `git status`, `git diff`
- Package management: `pip install`, `uv add`
- Process management: `ps`, `kill`
- Network checks: `netstat`, `curl` for APIs