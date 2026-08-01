#!/usr/bin/env python
"""Hermes Token Compressor — integrated from Headroom research.

Usage:
    from hermes_compress import compress_for_llm
    
    # Compress tool output before sending to LLM
    compressed = compress_for_llm(tool_output)
    
    # Compress entire conversation
    compressed_messages = compress_for_llm(messages, mode="messages")
"""

import sys
import json
import re
from pathlib import Path
from typing import Any

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))
from simple_compress import compress, compress_messages, estimate_tokens, CompressResult


def compress_for_llm(
    content: Any,
    mode: str = "text",
    model: str = "qwen3.7-max"
) -> Any:
    """Compress content for LLM consumption.
    
    Args:
        content: Text, dict, or list of messages
        mode: "text" for single text, "messages" for chat messages
        model: Model name (for future model-specific compression)
    
    Returns:
        Compressed content (same type as input)
    """
    if mode == "messages" and isinstance(content, list):
        return compress_messages(content)
    
    if isinstance(content, dict):
        content = json.dumps(content, indent=2)
    
    result = compress(str(content))
    
    # Log compression stats
    savings = result.tokens_before - result.tokens_after
    if savings > 100:
        print(f"[Compress] Saved {savings} tokens ({result.compression_ratio:.0%} ratio)")
    
    return result.compressed


def compress_tool_output(output: str) -> str:
    """Compress tool output (JSON, logs, code)."""
    return compress_for_llm(output)


def compress_conversation(messages: list[dict]) -> list[dict]:
    """Compress entire conversation, preserving system messages."""
    return compress_for_llm(messages, mode="messages")


# Integration with Hermes hooks
def add_compression_to_hooks():
    """Monkey-patch hermes_hooks to add compression."""
    try:
        from hermes_hooks import get_hooks
        hooks = get_hooks()
        
        # Store original method
        original_complete = hooks.on_task_complete
        
        def compressed_complete(task_description, result, tags=None):
            # Compress result before storing
            if isinstance(result, str) and len(result) > 1000:
                result = compress_tool_output(result)
            return original_complete(task_description, result, tags or [])
        
        hooks.on_task_complete = compressed_complete
        print("[Compress] Added compression to hooks")
    except Exception as e:
        print(f"[Compress] Could not patch hooks: {e}")


if __name__ == "__main__":
    # Demo
    test_output = '''{
        "users": [
            {"name": "Alice", "email": "alice@example.com", "bio": "Software engineer with 10 years of experience"},
            {"name": "Bob", "email": "bob@example.com", "bio": "Data scientist passionate about ML"},
            {"name": "Charlie", "email": "charlie@example.com", "bio": "DevOps engineer"}
        ],
        "total": 3,
        "page": 1
    }'''
    
    print("=== Hermes Compressor Demo ===\n")
    
    # Single text
    result = compress_for_llm(test_output)
    print(f"Input: {estimate_tokens(test_output)} tokens")
    print(f"Output: {estimate_tokens(result)} tokens")
    print(f"Saved: {estimate_tokens(test_output) - estimate_tokens(result)} tokens\n")
    
    # Messages
    messages = [
        {"role": "system", "content": "You are Hermes."},
        {"role": "user", "content": "Show users"},
        {"role": "tool", "content": test_output}
    ]
    
    compressed = compress_conversation(messages)
    print(f"Messages: {len(messages)} → {len(compressed)}")
    for i, msg in enumerate(compressed):
        print(f"  [{i}] {msg['role']}: {msg['content'][:50]}...")
