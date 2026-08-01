#!/usr/bin/env python
"""Auto-compress tool outputs before LLM calls.

This script can be used as a pre-processor in the Hermes agent loop.
It compresses large tool outputs to save tokens.

Usage in agent loop:
    # Before sending to LLM:
    messages = auto_compress(messages)
    
    # Or compress single output:
    compressed_output = auto_compress_output(raw_output)
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))
from simple_compress import compress, estimate_tokens

# Threshold: compress if output is larger than this
COMPRESS_THRESHOLD = 500  # tokens


def should_compress(content: str) -> bool:
    """Check if content should be compressed."""
    tokens = estimate_tokens(content)
    return tokens > COMPRESS_THRESHOLD


def auto_compress_output(output: str) -> str:
    """Compress tool output if it's large enough."""
    if not should_compress(output):
        return output
    
    result = compress(output)
    savings = result.tokens_before - result.tokens_after
    
    if savings > 100:
        print(f"[AutoCompress] {result.tokens_before} → {result.tokens_after} tokens (saved {savings})")
    
    return result.compressed


def auto_compress(messages: list[dict]) -> list[dict]:
    """Compress all tool messages in conversation."""
    compressed = []
    total_saved = 0
    
    for msg in messages:
        if msg.get('role') == 'tool':
            original = msg.get('content', '')
            if should_compress(original):
                result = compress(original)
                savings = result.tokens_before - result.tokens_after
                total_saved += savings
                compressed.append({
                    **msg,
                    'content': result.compressed
                })
            else:
                compressed.append(msg)
        else:
            compressed.append(msg)
    
    if total_saved > 0:
        print(f"[AutoCompress] Total saved: {total_saved} tokens across {len(messages)} messages")
    
    return compressed


def compress_large_outputs(outputs: list[str], max_tokens: int = 10000) -> list[str]:
    """Compress multiple outputs to fit within token budget."""
    results = []
    total_tokens = 0
    
    for output in outputs:
        tokens = estimate_tokens(output)
        
        if total_tokens + tokens > max_tokens:
            # Need to compress
            target_ratio = (max_tokens - total_tokens) / tokens
            result = compress(output)
            
            # If still too large, truncate
            if estimate_tokens(result.compressed) > max_tokens - total_tokens:
                compressed_tokens = max_tokens - total_tokens
                words = result.compressed.split()
                compressed = ' '.join(words[:int(compressed_tokens / 1.3)])
                results.append(compressed + f"\n[Truncated: {tokens} tokens → {compressed_tokens} tokens]")
            else:
                results.append(result.compressed)
            
            total_tokens = max_tokens
        else:
            results.append(output)
            total_tokens += tokens
    
    return results


if __name__ == "__main__":
    # Demo with realistic tool outputs
    tool_outputs = [
        # Small output - no compression
        '{"status": "ok", "count": 5}',
        
        # Large JSON output - compress
        json.dumps({
            "users": [
                {"id": i, "name": f"User {i}", "email": f"user{i}@example.com", 
                 "bio": f"Software engineer with {i} years of experience in distributed systems"}
                for i in range(20)
            ],
            "total": 20,
            "page": 1,
            "per_page": 20
        }, indent=2),
        
        # Log output - compress
        "\n".join([
            f"2024-01-15T10:30:{i:02d} INFO Processing request {i}"
            for i in range(50)
        ])
    ]
    
    print("=== Auto-Compress Demo ===\n")
    
    for i, output in enumerate(tool_outputs):
        print(f"Output {i+1}:")
        print(f"  Before: {estimate_tokens(output)} tokens")
        compressed = auto_compress_output(output)
        print(f"  After: {estimate_tokens(compressed)} tokens")
        print()
    
    # Demo with messages
    messages = [
        {"role": "system", "content": "You are Hermes."},
        {"role": "user", "content": "Show me all users"},
        {"role": "tool", "content": tool_outputs[1]},  # Large JSON
        {"role": "assistant", "content": "Here are the users..."},
    ]
    
    print("=== Messages Compression ===\n")
    compressed = auto_compress(messages)
    print(f"Messages: {len(messages)} → {len(compressed)}")
