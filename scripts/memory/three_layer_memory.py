#!/usr/bin/env python3
"""
Three-Layer Memory Compression for Knowledge Cube
Implements: raw → thematic → compressed pipeline
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"


class ThreeLayerMemory:
    """Three-layer memory: raw (experiences) → thematic (MEMORY.md) → compressed (patterns)."""
    
    def __init__(self, db_path: Path = KC_DB):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Add thematic and compressed tables to KC."""
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        try:
            # Thematic layer: organized by domain/topic
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_thematic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    source_experiences TEXT NOT NULL,  -- JSON array of experience IDs
                    confidence REAL DEFAULT 0.8,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Compressed layer: distilled patterns/rules
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_compressed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,  -- rule, heuristic, principle, anti-pattern
                    pattern_text TEXT NOT NULL,
                    domains TEXT NOT NULL,  -- JSON array
                    confidence REAL DEFAULT 0.9,
                    evidence_count INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_validated TEXT
                )
            """)
            
            # Compression log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compression_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    compression_type TEXT NOT NULL,  -- raw_to_thematic, thematic_to_compressed
                    source_ids TEXT NOT NULL,
                    target_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def compress_raw_to_thematic(self, domain: str = None, days_back: int = 7, min_experiences: int = 3) -> List[Dict]:
        """
        Layer 1: Raw experiences → Thematic summaries.
        Groups experiences by domain/theme, creates summaries.
        """
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            # Get raw experiences
            since = (datetime.now() - timedelta(days=days_back)).isoformat()
            query = """
                SELECT id, raw_text, axis_domain, axis_outcome, tags, source, ts
                FROM experiences
                WHERE ts > ? AND is_white_spot = 0
            """
            params = [since]
            if domain:
                query += " AND axis_domain = ?"
                params.append(domain)
            query += " ORDER BY ts DESC"
            
            experiences = conn.execute(query, params).fetchall()
            
            if len(experiences) < min_experiences:
                return []
            
            # Group by domain + outcome
            groups = {}
            for exp in experiences:
                key = (exp["axis_domain"], exp["axis_outcome"])
                if key not in groups:
                    groups[key] = []
                groups[key].append(exp)
            
            thematic_entries = []
            for (dom, outcome), exps in groups.items():
                if len(exps) < min_experiences:
                    continue
                
                # Create thematic summary
                combined_text = " ".join([e["raw_text"] for e in exps])
                tags = set()
                for e in exps:
                    try:
                        tags.update(json.loads(e["tags"]) if e["tags"] else [])
                    except:
                        pass
                
                summary = self._generate_thematic_summary(dom, outcome, exps)
                exp_ids = [e["id"] for e in exps]
                
                # Insert thematic entry
                cursor = conn.execute("""
                    INSERT INTO memory_thematic (domain, theme, summary, source_experiences, confidence, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (dom, outcome, summary, json.dumps(exp_ids), 0.8, datetime.now().isoformat(), datetime.now().isoformat()))
                
                thematic_id = cursor.lastrowid
                conn.commit()
                
                # Log compression
                conn.execute("""
                    INSERT INTO compression_log (compression_type, source_ids, target_id, created_at)
                    VALUES (?, ?, ?, ?)
                """, ("raw_to_thematic", json.dumps(exp_ids), thematic_id, datetime.now().isoformat()))
                conn.commit()
                
                thematic_entries.append({
                    "id": thematic_id,
                    "domain": dom,
                    "theme": outcome,
                    "summary": summary,
                    "source_count": len(exps)
                })
            
            return thematic_entries
            
        finally:
            conn.close()
    
    def _generate_thematic_summary(self, domain: str, outcome: str, experiences: List) -> str:
        """Generate a concise thematic summary from experiences."""
        # Extract key actions/patterns
        actions = []
        for exp in experiences[:10]:  # Sample first 10
            text = exp["raw_text"][:200]
            actions.append(text)
        
        return f"[{domain}/{outcome}] {len(experiences)} experiences. Key patterns: {'; '.join(actions[:3])}..."
    
    def compress_thematic_to_compressed(self, domain: str = None, min_confidence: float = 0.7) -> List[Dict]:
        """Layer 2: Thematic summaries → Compressed patterns/rules."""
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            query = """
                SELECT id, domain, theme, summary, source_experiences, confidence
                FROM memory_thematic
                WHERE confidence >= ?
            """
            params = [min_confidence]
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            
            thematics = conn.execute(query, params).fetchall()
            
            if not thematics:
                return []
            
            compressed_entries = []
            
            # Group by theme across domains
            theme_groups = {}
            for th in thematics:
                theme = th["theme"]
                if theme not in theme_groups:
                    theme_groups[theme] = []
                theme_groups[theme].append(th)
            
            for theme, entries in theme_groups.items():
                # Need at least 2 unique domains OR 1 domain with multiple entries
                domains = list(set(e["domain"] for e in entries))
                if len(domains) < 2 and len(entries) < 2:
                    continue
                
                # Extract pattern
                pattern_text = self._extract_pattern(theme, entries)
                total_evidence = sum(len(json.loads(e["source_experiences"])) for e in entries)
                
                # Determine pattern type
                if "error" in theme.lower() or "fail" in theme.lower():
                    pattern_type = "anti-pattern"
                elif "fix" in theme.lower() or "guard" in theme.lower():
                    pattern_type = "rule"
                elif "how" in theme.lower() or "pattern" in theme.lower():
                    pattern_type = "heuristic"
                else:
                    pattern_type = "principle"
                
                cursor = conn.execute("""
                    INSERT INTO memory_compressed (pattern_type, pattern_text, domains, confidence, evidence_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (pattern_type, pattern_text, json.dumps(domains), 0.9, total_evidence, datetime.now().isoformat()))
                
                compressed_id = cursor.lastrowid
                conn.commit()
                
                # Log compression
                source_ids = []
                for e in entries:
                    source_ids.extend(json.loads(e["source_experiences"]))
                conn.execute("""
                    INSERT INTO compression_log (compression_type, source_ids, target_id, created_at)
                    VALUES (?, ?, ?, ?)
                """, ("thematic_to_compressed", json.dumps(source_ids), compressed_id, datetime.now().isoformat()))
                conn.commit()
                
                compressed_entries.append({
                    "id": compressed_id,
                    "pattern_type": pattern_type,
                    "pattern_text": pattern_text,
                    "domains": domains,
                    "evidence_count": total_evidence
                })
            
            return compressed_entries
            
        finally:
            conn.close()
    
    def _extract_pattern(self, theme: str, entries: List) -> str:
        """Extract a reusable pattern from thematic entries."""
        summaries = [e["summary"] for e in entries]
        return f"Pattern [{theme}]: Recurring across {len(entries)} domains. {summaries[0]}"
    
    def run_full_compression(self, domain: str = None) -> Dict:
        """Run complete raw → thematic → compressed pipeline."""
        print("Starting three-layer compression...")
        
        # Layer 1: Raw → Thematic
        thematic = self.compress_raw_to_thematic(domain)
        print(f"Created {len(thematic)} thematic summaries")
        
        # Layer 2: Thematic → Compressed
        compressed = self.compress_thematic_to_compressed(domain)
        print(f"Created {len(compressed)} compressed patterns")
        
        return {
            "thematic_created": len(thematic),
            "compressed_created": len(compressed),
            "thematic": thematic,
            "compressed": compressed
        }
    
    def get_compressed_patterns(self, domain: str = None, pattern_type: str = None) -> List[Dict]:
        """Retrieve compressed patterns for use."""
        conn = sqlite3.connect(str(self.db_path), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            query = "SELECT * FROM memory_compressed WHERE 1=1"
            params = []
            if domain:
                query += " AND domains LIKE ?"
                params.append(f"%{domain}%")
            if pattern_type:
                query += " AND pattern_type = ?"
                params.append(pattern_type)
            query += " ORDER BY evidence_count DESC"
            
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def compress_memory(domain: str = None) -> Dict:
    """Main entry point for memory compression."""
    memory = ThreeLayerMemory()
    return memory.run_full_compression(domain)


if __name__ == "__main__":
    import sys
    domain = sys.argv[1] if len(sys.argv) > 1 else None
    result = compress_memory(domain)
    print(json.dumps(result, ensure_ascii=False, indent=2))