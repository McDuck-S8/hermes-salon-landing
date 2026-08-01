# Context7 MCP — Up-to-Date Library Documentation

**Server:** `context7`
**Config location:** `~/.hermes/config.yaml`
**Type:** HTTP MCP server

## Config

```yaml
mcp_servers:
  context7:
    url: "http://mcp.context7.com/sse"
```

Restart Hermes after adding. Tools appear as `mcp_context7_*`.

## Workflow Rule

Before writing code using any library/framework/API, check Context7 for up-to-date docs:

1. Resolve the library: `mcp__context7__resolve_library_id(query, libraryName)`
2. Query docs: `mcp__context7__query_docs(libraryId, query)`

This prevents relying on stale training data knowledge.

## Available Tools

- `resolve_library_id(query, libraryName)` — get the Context7 library ID string
- `query_docs(libraryId, query)` — retrieve docs for a specific question
- `list_prompts`, `get_prompt`, `list_resources`, `read_resource` — secondary

## Example

```python
# Before coding with browser-harness:
# 1. Resolve
ctx_id = "..."  # from resolve_library_id
# 2. Get docs
docs = mcp__context7__query_docs(libraryId=ctx_id, query="helpers API functions")
```

## Notes

- Max 3 query_docs calls per question
- Some libraries may not have Context7 coverage — fall back to web_search
