# Token Compression — Code Examples

## simple_compress.py — Core

```python
from simple_compress import compress, compress_json, compress_code, compress_log, estimate_tokens

# Auto-detect and compress
result = compress(text)
# result.compressed — compressed text
# result.compression_ratio — e.g., 0.35 (65% saved)
# result.tokens_before / result.tokens_after

# Explicit type
result = compress(json_text, content_type="json")
result = compress(code_text, content_type="code")
result = compress(log_text, content_type="log")
```

## hermes_compress.py — Integration

```python
from hermes_compress import compress_for_llm, compress_tool_output, compress_conversation

# Single output
compressed = compress_for_llm(tool_output)

# Messages
compressed_msgs = compress_conversation([
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "tool", "content": large_output}
])
```

## auto_compress.py — Auto Mode

```python
from auto_compress import auto_compress_output, auto_compress, should_compress

# Only compresses if > 500 tokens
compressed = auto_compress_output(raw_output)

# Compress all tool messages in conversation
messages = auto_compress(messages)

# Check threshold
if should_compress(output):
    compressed = compress(output)
```

## Test Results

| Type | Before | After | Savings |
|------|--------|-------|---------|
| JSON (20 users) | 534 tokens | 66 tokens | 88% |
| Code (function) | 27 tokens | 11 tokens | 59% |
| Logs (50 lines) | 41 tokens | 18 tokens | 56% |
| Small JSON | 5 tokens | 5 tokens | 0% (skipped) |

## Headroom Comparison

| Feature | simple_compress | Headroom (full) |
|---------|-----------------|-----------------|
| Dependencies | None | opentelemetry, magika, kompress |
| JSON compression | 88% | 90-95% |
| Code compression | 59% | 70-80% |
| Log compression | 56% | 60-70% |
| ML detection | No | Yes (Magika) |
| CCR (reversible) | No | Yes |
| Setup time | 0 | 5-10 min |
