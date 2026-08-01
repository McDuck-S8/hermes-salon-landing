# Self-Improving Skills - Failure Pattern Library

## Pattern Categories

### 1. TOOL_MISUSE
**Symptoms**: Wrong tool name, missing args, invalid arg types
**Root Cause**: Skill docs don't specify exact tool signatures
**Fix Strategy**: Add explicit tool call examples with args
**Example Fix**: 
- Old: "Use the search tool"
- New: "Use `web_search(query=\"your query\", limit=5)`"

### 2. AMBIGUOUS_INSTRUCTION
**Symptoms**: Multiple valid outputs for same input; inconsistent results
**Root Cause**: Decision points not codified
**Fix Strategy**: Add decision tree / explicit rules
**Example Fix**:
```
IF input has field X AND field Y:
  Use strategy A
ELIF input has field X only:
  Use strategy B
ELSE:
  Return error "missing required field"
```

### 3. EDGE_CASE
**Symptoms**: Crashes on empty input, null, unicode, huge input, whitespace
**Root Cause**: No defensive coding in skill
**Fix Strategy**: Add input validation + handling branches
**Example Fix**:
```python
def handle_input(data):
    if not data or not data.strip():
        return {"error": "empty input", "status": "FAIL"}
    if len(data) > MAX_LEN:
        data = data[:MAX_LEN]  # truncate with warning
    # ... process
```

### 4. MISSING_VALIDATION
**Symptoms**: API errors, injection vulnerabilities, garbage in/garbage out
**Root Cause**: Trusts external input without checking
**Fix Strategy**: Add schema validation before external calls
**Example Fix**:
```python
from jsonschema import validate
SCHEMA = {"type": "object", "required": ["url", "method"]}
validate(instance=request, schema=SCHEMA)
```

### 5. CONTEXT_LEAK
**Symptoms**: Test passes alone, fails in suite; state pollution
**Root Cause**: Global state, singleton, module-level cache
**Fix Strategy**: Reset state between tests; use fixtures
**Example Fix**:
```python
@pytest.fixture(autouse=True)
def reset_state():
    global _cache
    _cache = {}
    yield
    _cache = {}
```

### 6. HALLUCINATED_OUTPUT
**Symptoms**: Output format wrong; missing required fields; extra fields
**Root Cause**: No output schema or validation
**Fix Strategy**: Define output schema; validate before return
**Example Fix**:
```python
OUTPUT_SCHEMA = {"type": "object", "required": ["result", "status"]}
def run(input):
    result = do_work(input)
    validate(instance=result, schema=OUTPUT_SCHEMA)
    return result
```

### 7. PERFORMANCE
**Symptoms**: Timeout; slow; memory leak
**Root Cause**: No limits; inefficient algorithm; no caching
**Fix Strategy**: Add timeouts, limits, caching
**Example Fix**:
```python
async def run_with_timeout(coro, timeout=30):
    return await asyncio.wait_for(coro, timeout=timeout)
```

### 8. MISSING_FALLBACK
**Symptoms**: Fails when external service down; no degraded mode
**Root Cause**: Single point of failure
**Fix Strategy**: Add fallback chain
**Example Fix**:
```
try: primary()
except: fallback1()
except: fallback2()
except: return degraded_response()
```

---

## Pattern Detection Rules

### From Eval Results:
- Tool errors → TOOL_MISUSE
- Multiple valid outputs → AMBIGUOUS_INSTRUCTION
- Crashes on boundary inputs → EDGE_CASE
- External API errors → MISSING_VALIDATION / MISSING_FALLBACK
- Sequence-dependent failures → CONTEXT_LEAK
- Wrong output format → HALLUCINATED_OUTPUT
- Timeouts → PERFORMANCE

### From Error Messages:
- "Unknown tool" / "Invalid argument" → TOOL_MISUSE
- "ValidationError" / "SchemaError" → HALLUCINATED_OUTPUT
- "TimeoutError" / "asyncio.TimeoutError" → PERFORMANCE
- "ConnectionError" / "HTTP 5xx" → MISSING_FALLBACK
- "KeyError" / "AttributeError" on input → MISSING_VALIDATION / EDGE_CASE

---

## Fix Templates by Pattern

### TOOL_MISUSE
```markdown
## Tools

### tool_name(arg1: type, arg2: type = default) -> return_type
Description of what it does.
**Example**: `tool_name("value", arg2=5)`
**Returns**: `{ "field": "type" }`
```

### AMBIGUOUS_INSTRUCTION
```markdown
## Decision Rules

When processing X:
1. If condition A: do action 1
2. Else if condition B: do action 2
3. Else: return error with message "specific reason"
```

### EDGE_CASE
```markdown
## Edge Case Handling

| Input | Expected Behavior |
|-------|-------------------|
| empty string | Return error "empty input" |
| null/None | Return error "null input" |
| >10000 chars | Truncate to 10000, log warning |
| unicode/emoji | Process normally |
| whitespace only | Treat as empty |
```

### MISSING_VALIDATION
```markdown
## Input Validation

All external inputs validated against schema before processing:
```python
from jsonschema import validate
INPUT_SCHEMA = {...}
validate(instance=input_data, schema=INPUT_SCHEMA)
```
```

### CONTEXT_LEAK
```markdown
## State Management

No global state. Each invocation is independent.
Tests use fixtures to ensure isolation.
```

### HALLUCINATED_OUTPUT
```markdown
## Output Schema

```json
{
  "type": "object",
  "required": ["result", "status", "metadata"],
  "properties": {
    "result": {"type": "object"},
    "status": {"type": "string", "enum": ["success", "error"]},
    "metadata": {"type": "object"}
  }
}
```
```

### PERFORMANCE
```markdown
## Performance Limits

- Timeout: 30 seconds default
- Max input: 100KB
- Max output: 1MB
- Concurrency: 5 parallel max
```

### MISSING_FALLBACK
```markdown
## Fallback Chain

1. Primary: External API
2. Fallback 1: Cached result (max 1 hour old)
3. Fallback 2: Degraded local computation
4. Fallback 3: Structured error with retry guidance
```