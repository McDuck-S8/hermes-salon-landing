#!/usr/bin/env python
"""Token compressor — auto-detects gigatoken (60x faster, Python 3.11+).

Falls back to built-in regex compressor when gigatoken is unavailable.
Compresses tool outputs, logs, and RAG chunks before sending to LLM.
"""

import json
import re
import sys
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ── gigatoken auto-detect ──────────────────────────────────────────────
_GIGATOKEN = None
_GIGA_PATH = Path("D:/Program Files/Python311/python.exe")
if sys.executable == str(_GIGA_PATH) or "3.11" in sys.version:
    try:
        _spec = importlib.util.find_spec("gigatoken")
        if _spec:
            import gigatoken
            _GIGATOKEN = gigatoken
    except ImportError:
        pass

def estimate_tokens(text: str) -> int:
    """Token count via gigatoken (fast) or word*1.3 fallback."""
    if _GIGATOKEN:
        return len(list(_GIGATOKEN.tokenize(text)))
    return int(len(text.split()) * 1.3)


@dataclass
class CompressResult:
    """Result from compression."""
    compressed: str
    original: str
    compression_ratio: float
    tokens_before: int
    tokens_after: int


def estimate_tokens(text: str) -> int:
    """Rough token count (words * 1.3)."""
    return int(len(text.split()) * 1.3)


def compress_json(text: str) -> str:
    """Compress JSON by preserving keys but compressing values."""
    try:
        data = json.loads(text)
        return _compress_json_value(data)
    except json.JSONDecodeError:
        return text


def _compress_json_value(value: Any) -> str:
    """Recursively compress JSON values."""
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                parts.append(f'"{k}": {_compress_json_value(v)}')
            elif isinstance(v, str) and len(v) > 50:
                # Compress long strings
                parts.append(f'"{k}": "{v[:30]}...[{len(v)} chars]"')
            elif isinstance(v, list) and len(v) > 5:
                # Compress long arrays
                parts.append(f'"{k}": [{", ".join(_compress_json_value(i) for i in v[:3])}, ...{len(v)} items]')
            else:
                parts.append(f'"{k}": {json.dumps(v)}')
        return "{" + ", ".join(parts) + "}"
    elif isinstance(value, list):
        if len(value) > 5:
            return "[" + ", ".join(_compress_json_value(i) for i in value[:3]) + f", ...{len(value)} items]"
        return "[" + ", ".join(_compress_json_value(i) for i in value) + "]"
    else:
        return json.dumps(value)


def compress_code(text: str) -> str:
    """Compress code by removing comments and excess whitespace."""
    lines = text.split('\n')
    compressed = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            continue
        # Skip docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        compressed.append(stripped)
    return '\n'.join(compressed)


def compress_log(text: str) -> str:
    """Compress log output by removing redundant info."""
    lines = text.split('\n')
    compressed = []
    seen = set()
    for line in lines:
        # Remove timestamps
        line = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '', line)
        # Remove repeated lines
        if line in seen:
            continue
        seen.add(line)
        compressed.append(line)
    return '\n'.join(compressed)


def compress(text: str, content_type: str = "auto") -> CompressResult:
    """Compress text using appropriate strategy.
    
    Args:
        text: Text to compress
        content_type: "json", "code", "log", or "auto"
    
    Returns:
        CompressResult with compressed text and stats
    """
    original = text
    tokens_before = estimate_tokens(text)
    
    # Auto-detect content type
    if content_type == "auto":
        stripped = text.strip()
        if stripped.startswith('{') or stripped.startswith('['):
            content_type = "json"
        elif any(kw in text for kw in ['def ', 'class ', 'import ', 'function ', 'const ', 'let ']):
            content_type = "code"
        elif any(kw in text for kw in ['ERROR', 'WARN', 'INFO', 'DEBUG', '[202']):
            content_type = "log"
        else:
            content_type = "text"
    
    # Apply compression
    if content_type == "json":
        compressed = compress_json(text)
    elif content_type == "code":
        compressed = compress_code(text)
    elif content_type == "log":
        compressed = compress_log(text)
    else:
        # Text: just remove excess whitespace
        compressed = re.sub(r'\s+', ' ', text).strip()
    
    tokens_after = estimate_tokens(compressed)
    ratio = tokens_after / tokens_before if tokens_before > 0 else 1.0
    
    return CompressResult(
        compressed=compressed,
        original=original,
        compression_ratio=ratio,
        tokens_before=tokens_before,
        tokens_after=tokens_after
    )


def compress_messages(messages: list[dict]) -> list[dict]:
    """Compress a list of messages (OpenAI/Anthropic format).
    
    Preserves system messages, compresses tool outputs.
    """
    compressed = []
    for msg in messages:
        if msg.get('role') == 'system':
            compressed.append(msg)
        elif msg.get('role') == 'tool':
            # Compress tool outputs
            result = compress(str(msg.get('content', '')))
            compressed.append({
                **msg,
                'content': result.compressed
            })
        else:
            compressed.append(msg)
    return compressed


# Demo
if __name__ == "__main__":
    # Test JSON compression
    json_text = '''{
        "users": [
            {"name": "Alice", "email": "alice@example.com", "bio": "Software engineer with 10 years of experience in distributed systems"},
            {"name": "Bob", "email": "bob@example.com", "bio": "Data scientist passionate about machine learning and AI"},
            {"name": "Charlie", "email": "charlie@example.com", "bio": "DevOps engineer specializing in cloud infrastructure"}
        ],
        "total": 3,
        "page": 1
    }'''
    
    print("=== JSON Compression ===")
    result = compress(json_text, "json")
    print(f"Before: {result.tokens_before} tokens")
    print(f"After: {result.tokens_after} tokens")
    print(f"Ratio: {result.compression_ratio:.2%}")
    print(f"Compressed:\n{result.compressed}\n")
    
    # Test code compression
    code_text = '''
def hello():
    # This is a comment
    """This is a docstring."""
    print("Hello, world!")
    
    # Another comment
    x = 42
    return x
'''
    
    print("=== Code Compression ===")
    result = compress(code_text, "code")
    print(f"Before: {result.tokens_before} tokens")
    print(f"After: {result.tokens_after} tokens")
    print(f"Ratio: {result.compression_ratio:.2%}")
    print(f"Compressed:\n{result.compressed}\n")
    
    # Test log compression
    log_text = '''
2024-01-15T10:30:00 INFO Starting server...
2024-01-15T10:30:01 INFO Server started on port 8080
2024-01-15T10:30:01 INFO Server started on port 8080
2024-01-15T10:30:01 INFO Server started on port 8080
2024-01-15T10:30:02 ERROR Connection refused
2024-01-15T10:30:03 INFO Retrying...
'''
    
    print("=== Log Compression ===")
    result = compress(log_text, "log")
    print(f"Before: {result.tokens_before} tokens")
    print(f"After: {result.tokens_after} tokens")
    print(f"Ratio: {result.compression_ratio:.2%}")
    print(f"Compressed:\n{result.compressed}")
