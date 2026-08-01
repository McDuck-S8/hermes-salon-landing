#!/usr/bin/env python3
"""
Three-Layer Memory System — Raw → Thematic → Compressed
Implementation from Clarence's "On Becoming" Chapter 1 & 3.
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

@dataclass
class RawEntry:
    """Raw memory entry - append only log."""
    timestamp: str
    type: str          # action, observation, tool_call, error, decision
    content: str
    agent_id: str
    session_id: str
    tags: List[str]
    hash: str

@dataclass
class ThematicEntry:
    """Thematic memory - organized by topic/project."""
    theme: str
    summary: str
    source_hashes: List[str]
    created_at: str
    updated_at: str
    access_count: int
    confidence: float
    domain: str

@dataclass
class CompressedEntry:
    """Compressed memory - distilled patterns/rules."""
    pattern_type: str      # rule, heuristic, principle, anti-pattern
    pattern_text: str
    domains: List[str]
    evidence_count: int
    confidence: float
    created_at: str
    last_validated: str

class ThreeLayerMemory:
    """Three-layer memory: Raw (7d) → Thematic (90d) → Compressed (forever)."""
    
    def __init__(self, agent_id: str, memory_root: Path = None):
        self.agent_id = agent_id
        if memory_root is None:
            memory_root = HERMES_HOME / "memory" / agent_id
        self.root = memory_root
        self.raw_dir = self.root / "raw"
        self.thematic_dir = self.root / "thematic"
        self.compressed_dir = self.root / "compressed"
        self._init_dirs()
    
    def _init_dirs(self):
        for d in [self.raw_dir, self.thematic_dir, self.compressed_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    # ========== RAW LAYER ==========
    
    def log(self, type: str, content: str, session_id: str = None, tags: List[str] = None) -> str:
        """Append to raw log."""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d")
        if tags is None:
            tags = []
        
        entry = RawEntry(
            timestamp=datetime.now().isoformat(),
            type=type,
            content=content,
            agent_id=self.agent_id,
            session_id=session_id,
            tags=tags,
            hash=self._hash_content(content)
        )
        
        # Append to daily raw log
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.raw_dir / f"{date_str}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
        
        return entry.hash
    
    def read_raw(self, days: int = 7) -> List[RawEntry]:
        """Read raw entries from last N days."""
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in sorted(self.raw_dir.glob("*.jsonl")):
            try:
                file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                if file_date < cutoff:
                    continue
            except ValueError:
                continue
            
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            entries.append(RawEntry(**data))
                        except json.JSONDecodeError:
                            continue
        
        return entries
    
    def clean_raw(self, days: int = 7):
        """Delete raw logs older than N days."""
        cutoff = datetime.now() - timedelta(days=days)
        for log_file in self.raw_dir.glob("*.jsonl"):
            try:
                file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                if file_date < cutoff:
                    log_file.unlink()
            except ValueError:
                pass
    
    # ========== THEMATIC LAYER ==========
    
    def compress_to_thematic(self, min_entries: int = 3) -> List[ThematicEntry]:
        """Compress raw logs into thematic summaries."""
        raw_entries = self.read_raw(days=7)
        if len(raw_entries) < min_entries:
            return []
        
        # Group by tags/domain
        groups = defaultdict(list)
        for entry in raw_entries:
            key = entry.tags[0] if entry.tags else entry.type
            groups[key].append(entry)
        
        thematic_entries = []
        for theme, entries in groups.items():
            if len(entries) < min_entries:
                continue
            
            # Create summary
            contents = [e.content[:200] for e in entries[:5]]
            summary = f"[{theme}] {len(entries)} entries. Key: {'; '.join(contents[:3])}..."
            
            thematic = ThematicEntry(
                theme=theme,
                summary=summary,
                source_hashes=[e.hash for e in entries],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                access_count=0,
                confidence=0.8,
                domain=theme
            )
            
            # Save
            theme_file = self.thematic_dir / f"{theme}.json"
            existing = None
            if theme_file.exists():
                existing = json.loads(theme_file.read_text(encoding="utf-8"))
                thematic.access_count = existing.get("access_count", 0)
                thematic.created_at = existing.get("created_at", thematic.created_at)
            
            thematic.updated_at = datetime.now().isoformat()
            theme_file.write_text(json.dumps(asdict(thematic), ensure_ascii=False, indent=2), encoding="utf-8")
            thematic_entries.append(thematic)
        
        return thematic_entries
    
    def read_thematic(self, theme: str = None) -> List[ThematicEntry]:
        """Read thematic entries."""
        entries = []
        for theme_file in self.thematic_dir.glob("*.json"):
            data = json.loads(theme_file.read_text(encoding="utf-8"))
            if theme is None or data.get("theme") == theme:
                entries.append(ThematicEntry(**data))
        return entries
    
    def clean_thematic(self, days: int = 90):
        """Delete thematic entries older than N days."""
        cutoff = datetime.now() - timedelta(days=days)
        for theme_file in self.thematic_dir.glob("*.json"):
            try:
                data = json.loads(theme_file.read_text(encoding="utf-8"))
                updated = datetime.fromisoformat(data.get("updated_at", "2000-01-01"))
                if updated < cutoff:
                    theme_file.unlink()
            except Exception:
                pass
    
    # ========== COMPRESSED LAYER ==========
    
    def compress_to_compressed(self) -> List[CompressedEntry]:
        """Distill thematic entries into compressed patterns."""
        thematics = self.read_thematic()
        if not thematics:
            return []
        
        # Group by domain
        domain_groups = defaultdict(list)
        for t in thematics:
            domain_groups[t.domain].append(t)
        
        compressed = []
        for domain, entries in domain_groups.items():
            if len(entries) < 2:
                continue
            
            # Determine pattern type
            all_text = " ".join([e.summary for e in entries])
            if "error" in all_text.lower() or "fail" in all_text.lower():
                pattern_type = "anti-pattern"
            elif "fix" in all_text.lower() or "guard" in all_text.lower():
                pattern_type = "rule"
            elif "how" in all_text.lower() or "pattern" in all_text.lower():
                pattern_type = "heuristic"
            else:
                pattern_type = "principle"
            
            pattern_text = f"Pattern [{domain}]: Recurring across {len(entries)} themes. {entries[0].summary[:200]}"
            
            compressed = CompressedEntry(
                pattern_type=pattern_type,
                pattern_text=pattern_text,
                domains=[domain],
                evidence_count=sum(len(json.loads(e.source_hashes)) for e in entries if isinstance(e.source_hashes, list)),
                confidence=0.9,
                created_at=datetime.now().isoformat(),
                last_validated=datetime.now().isoformat()
            )
            
            # Save
            pattern_file = self.compressed_dir / f"{domain}_{pattern_type}.json"
            existing = None
            if pattern_file.exists():
                existing = json.loads(pattern_file.read_text(encoding="utf-8"))
                compressed.confidence = max(compressed.confidence, existing.get("confidence", 0))
                compressed.created_at = existing.get("created_at", compressed.created_at)
            
            pattern_file.write_text(json.dumps(asdict(compressed), ensure_ascii=False, indent=2), encoding="utf-8")
            compressed.append(compressed)
        
        return compressed
    
    def read_compressed(self, domain: str = None) -> List[CompressedEntry]:
        """Read compressed patterns."""
        entries = []
        for pattern_file in self.compressed_dir.glob("*.json"):
            data = json.loads(pattern_file.read_text(encoding="utf-8"))
            if domain is None or data.get("domains") and domain in data.get("domains", []):
                entries.append(CompressedEntry(**data))
        return entries
    
    # ========== FULL PIPELINE ==========
    
    def run_full_compression(self) -> Dict[str, int]:
        """Run complete Raw → Thematic → Compressed pipeline."""
        print("Starting three-layer compression...")
        
        # Layer 1: Raw already logged continuously
        # Layer 2: Thematic
        thematic = self.compress_to_thematic()
        print(f"  Thematic created: {len(thematic)}")
        
        # Layer 3: Compressed
        compressed = self.compress_to_compressed()
        print(f"  Compressed created: {len(compressed)}")
        
        return {
            "thematic_created": len(thematic),
            "compressed_created": len(compressed)
        }
    
    def export_memory_md(self, output_path: Path = None) -> str:
        """Export all layers as MEMORY.md"""
        if output_path is None:
            output_path = self.root / "MEMORY.md"
        
        raw_count = len(list(self.raw_dir.glob("*.jsonl")))
        thematic_entries = self.read_thematic()
        compressed_entries = self.read_compressed()
        
        md = f"""# MEMORY.md — {self.agent_id}
Generated: {datetime.now().isoformat()}

## Raw Layer (last 7 days)
Files: {raw_count}
"""
        
        md += "\n## Thematic Layer\n"
        for t in thematic_entries:
            md += f"- **{t.theme}** ({t.domain}): {t.summary[:100]}... [accessed: {t.access_count}]\n"
        
        md += "\n## Compressed Layer\n"
        for c in compressed_entries:
            md += f"- **{c.pattern_type}** [{', '.join(c.domains)}]: {c.pattern_text[:120]}... (evidence: {c.evidence_count})\n"
        
        output_path.write_text(md, encoding="utf-8")
        return md


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Three-Layer Memory System")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--log", action="store_true", help="Log an entry")
    parser.add_argument("--type", help="Entry type for --log")
    parser.add_argument("--content", help="Content for --log")
    parser.add_argument("--tags", nargs="+", help="Tags for --log")
    parser.add_argument("--compress", action="store_true", help="Run full compression")
    parser.add_argument("--export", action="store_true", help="Export MEMORY.md")
    args = parser.parse_args()
    
    memory = ThreeLayerMemory(args.agent_id)
    
    if args.log and args.content:
        h = memory.log(args.type, args.content, tags=args.tags or [])
        print(f"Logged: {h}")
    
    if args.compress:
        result = memory.run_full_compression()
        print(f"Result: {result}")
    
    if args.export:
        md = memory.export_memory_md()
        print("Exported MEMORY.md")


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()