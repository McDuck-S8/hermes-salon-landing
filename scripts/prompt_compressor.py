#!/usr/bin/env python3
"""
Lightweight Prompt Compressor — no sklearn, no torch, no heavy deps.
Uses tiktoken + heuristics for prompt compression.

> Revisit: when prompt compression logic, token reduction, or compression quality changes. Last touched: 2026-07-02.
"""

import re
import sys
from pathlib import Path

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


class PromptCompressor:
    """Lightweight prompt compressor using token counting + heuristics."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.encoding = None
        if HAS_TIKTOKEN:
            try:
                self.encoding = tiktoken.encoding_for_model(model)
            except Exception:
                self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        if self.encoding:
            return len(self.encoding.encode(text))
        # Rough fallback: ~4 chars per token
        return len(text) // 4
    
    def compress(self, prompt: str, target_tokens: int = 2000, rate: float = 0.5) -> str:
        """
        Compress prompt to target token count.
        
        Strategies (in order):
        1. Remove excessive whitespace
        2. Deduplicate repeated lines/blocks
        3. Truncate long examples/logs (keep first/last N lines)
        4. Remove low-importance sections (verbose logs, stack traces)
        5. Hard truncate if still over limit
        """
        if self.count_tokens(prompt) <= target_tokens:
            return prompt
        
        lines = prompt.split('\n')
        
        # 1. Remove excessive whitespace
        lines = [re.sub(r' {2,}', ' ', line) for line in lines]
        lines = [line for line in lines if line.strip() or len(lines) < 100]
        
        if self.count_tokens('\n'.join(lines)) <= target_tokens:
            return '\n'.join(lines)
        
        # 2. Deduplicate consecutive identical lines
        deduped = []
        prev = None
        for line in lines:
            if line != prev:
                deduped.append(line)
                prev = line
        lines = deduped
        
        if self.count_tokens('\n'.join(lines)) <= target_tokens:
            return '\n'.join(lines)
        
        # 3. Truncate long repetitive blocks (logs, stack traces, JSON)
        # Detect repetitive patterns
        compressed = self._truncate_repetitive_blocks(lines, target_tokens)
        
        if self.count_tokens('\n'.join(compressed)) <= target_tokens:
            return '\n'.join(compressed)
        
        # 4. Keep first/last N lines of long sections, summarize middle
        final = self._smart_truncate(compressed, target_tokens)
        
        return '\n'.join(final)
    
    def _truncate_repetitive_blocks(self, lines: list, target_tokens: int) -> list:
        """Find and compress repetitive blocks (logs, stack traces, repeated patterns)."""
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect stack traces
            if 'Traceback' in line or 'File "' in line or 'line ' in line and 'in ' in line:
                # Keep first 5 lines, then skip to end
                stack_start = i
                while i < len(lines) and (lines[i].startswith(' ') or lines[i].startswith('\t') or 'Traceback' in lines[i] or 'File "' in lines[i]):
                    i += 1
                stack_end = i
                if stack_end - stack_start > 10:
                    result.extend(lines[stack_start:stack_start+5])
                    result.append(f"  ... [{stack_end - stack_start - 10} stack frames omitted] ...")
                    result.extend(lines[stack_end-5:stack_end])
                else:
                    result.extend(lines[stack_start:stack_end])
                continue
            
            # Detect long JSON blocks
            if line.strip().startswith('{') and line.strip().endswith('}') and len(line) > 200:
                # Try to parse and summarize
                try:
                    import json
                    obj = json.loads(line)
                    summary = f"  {{... JSON object with keys: {', '.join(list(obj.keys())[:5])} ...}}"
                    result.append(summary)
                except:
                    result.append(line[:200] + "... [truncated]")
                i += 1
                continue
            
            # Detect repeated log patterns
            if i + 3 < len(lines) and lines[i:i+3] == lines[i+3:i+6]:
                pattern = lines[i:i+3]
                count = 1
                j = i + 3
                while j + 2 < len(lines) and lines[j:j+3] == pattern:
                    count += 1
                    j += 3
                result.extend(pattern)
                result.append(f"  ... [repeated {count} times] ...")
                i = j
                continue
            
            result.append(line)
            i += 1
        
        return result
    
    def _smart_truncate(self, lines: list, target_tokens: int) -> list:
        """Keep important parts (beginning, end, key markers), truncate middle."""
        current = '\n'.join(lines)
        if self.count_tokens(current) <= target_tokens:
            return lines
        
        # Priority markers - keep these lines
        priority_markers = [
            'ERROR', 'FAILED', 'SUCCESS', 'FIXED', 'VERIFIED',
            'Phase', 'Phase 1', 'Phase 2', 'Phase 2.5', 'Phase 3', 'Phase 4',
            'SUMMARY', 'GAP', 'FIX', 'PATCH', 'COMMAND',
            'architecture', 'bugfix', 'learning', 'uncategorized'
        ]
        
        priority_indices = set()
        for i, line in enumerate(lines):
            if any(marker.lower() in line.lower() for marker in priority_markers):
                priority_indices.add(i)
                # Also keep context around
                priority_indices.add(max(0, i-1))
                priority_indices.add(min(len(lines)-1, i+1))
        
        # Always keep first 20 and last 20 lines
        for i in range(min(20, len(lines))):
            priority_indices.add(i)
        for i in range(max(0, len(lines)-20), len(lines)):
            priority_indices.add(i)
        
        # Build result
        result = []
        last_kept = -2
        for i in range(len(lines)):
            if i in priority_indices:
                if i > last_kept + 1:
                    result.append(f"  ... [{i - last_kept - 1} lines omitted] ...")
                result.append(lines[i])
                last_kept = i
        
        # Check token count
        result_text = '\n'.join(result)
        if self.count_tokens(result_text) <= target_tokens:
            return result
        
        # Hard truncate
        return self._hard_truncate(lines, target_tokens)
    
    def _hard_truncate(self, lines: list, target_tokens: int) -> list:
        """Hard truncate keeping first/last portions."""
        total_tokens = self.count_tokens('\n'.join(lines))
        if total_tokens <= target_tokens:
            return lines
        
        # Binary search for how many lines to keep
        keep_ratio = target_tokens / total_tokens
        keep_count = max(10, int(len(lines) * keep_ratio))
        half = keep_count // 2
        
        if len(lines) <= keep_count:
            return lines
        
        result = lines[:half]
        result.append(f"\n  ... [{len(lines) - keep_count} lines omitted] ...\n")
        result.extend(lines[-half:])
        return result


def compress_prompt(prompt: str, target_tokens: int = 2000, rate: float = 0.5) -> str:
    """Convenience function."""
    compressor = PromptCompressor()
    return compressor.compress(prompt, target_tokens, rate)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--target", "-t", type=int, default=2000, help="Target tokens")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    args = parser.parse_args()
    
    if args.stdin:
        text = sys.stdin.read()
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print("No input provided")
        sys.exit(1)
    
    compressed = compress_prompt(text, args.target)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(compressed)
    else:
        print(compressed)