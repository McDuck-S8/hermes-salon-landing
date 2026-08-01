#!/usr/bin/env python3
"""Clean VTT subtitle files → plain text for LLM consumption.

Includes ASR deduplication — YouTube auto-generated captions often
repeat each segment 3x (word, phrase, sentence). This script detects
and removes those repetitions.

Usage:
    python clean_vtt.py input.vtt [output.txt]
    python clean_vtt.py dir/          # batch: cleans all *.vtt in dir
If output omitted, writes to <input>.txt next to the vtt.
"""

import re, sys
from pathlib import Path


def deduplicate(text: str) -> str:
    """Remove sequential triplicate repetitions from ASR captions.
    
    YouTube auto-captions often produce patterns like:
    "This is the only this is the only this is the only tutorial"
    → "This is the only tutorial"
    """
    # Pattern: 3+ consecutive identical chunks of 2-6 words each
    # This catches the triple-repeat pattern
    while True:
        # Try removing 3x repeats of word/phrase sequences
        new_text = re.sub(
            r'(\b(?:\w+(?:[ ,.!?;:-]+|$)){2,6}\s*)\1{2,}',
            r'\1',
            text,
            flags=re.IGNORECASE
        )
        if new_text == text:
            break
        text = new_text
    
    # Also handle simple word triplicates: "the the the"
    text = re.sub(r'\b(\w+)\s+\1\s+\1\b', r'\1', text)
    
    # Handle "in in" duplicates
    text = re.sub(r'\b(\w{1,4})\s+\1\b', r'\1', text)
    
    return text


def clean_vtt(text: str) -> str:
    """Strip all VTT markup: headers, timing, <c> tags, then deduplicate."""
    lines = text.split("\n")
    clean = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or \
           line.startswith("Language:") or "-->" in line or line.startswith("NOTE") or \
           re.match(r'^\d+$', line):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        clean.append(line)
    text = " ".join(clean)
    text = re.sub(r'\s+', ' ', text).strip()
    text = deduplicate(text)
    return text


def process_file(vtt_path: Path):
    text = clean_vtt(vtt_path.read_text(encoding="utf-8", errors="replace"))
    out = vtt_path.with_suffix(".txt")
    out.write_text(text, encoding="utf-8")
    print(f"{vtt_path.name} → {out.name} ({len(text)} chars)")


if __name__ == "__main__":
    path = Path(sys.argv[1])
    if path.is_dir():
        for vtt in sorted(path.glob("*.vtt")):
            process_file(vtt)
    else:
        process_file(path)
