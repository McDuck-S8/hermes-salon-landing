#!/usr/bin/env python3
"""
Nocturnal Cognition — Nightly consolidation for Crystal.
Runs as cron job (02:00) to consolidate daily experiences into thematic memory.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
CRYSTAL_DB = HERMES_HOME / "cache" / "crystal.db"


class NocturnalCognition:
    """Nightly memory consolidation for Crystal."""
    
    def __init__(self):
        self.kc_db = KC_DB
        self.crystal_db = CRYSTAL_DB
        self._init_crystal_db()
    
    def _init_crystal_db(self):
        """Initialize Crystal-specific tables."""
        self.crystal_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.crystal_db), timeout=5)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crystal_consolidation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    experiences_processed INTEGER DEFAULT 0,
                    thematic_created INTEGER DEFAULT 0,
                    compressed_created INTEGER DEFAULT 0,
                    patterns_extracted INTEGER DEFAULT 0,
                    insights_generated INTEGER DEFAULT 0,
                    duration_ms INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crystal_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,  -- pattern, recommendation, warning, hypothesis
                    insight_text TEXT NOT NULL,
                    domains TEXT NOT NULL,  -- JSON array
                    confidence REAL DEFAULT 0.8,
                    evidence_ids TEXT,  -- JSON array
                    created_at TEXT NOT NULL,
                    applied BOOLEAN DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crystal_dreams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dream_type TEXT NOT NULL,  -- simulation, prediction, synthesis
                    dream_content TEXT NOT NULL,
                    domains TEXT NOT NULL,
                    trigger TEXT,
                    created_at TEXT NOT NULL,
                    evaluated BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()
        finally:
            conn.close()
    
    def consolidate_daily(self, days_back: int = 1) -> Dict[str, Any]:
        """Run nightly consolidation of daily experiences."""
        start_time = datetime.now()
        
        # Import three-layer memory
        sys.path.insert(0, str(HERMES_HOME / "scripts"))
        from memory.three_layer_memory import ThreeLayerMemory
        
        memory = ThreeLayerMemory()
        
        # Run compression for recent days
        result = memory.run_full_compression()
        
        # Generate insights from compressed patterns
        insights = self._generate_insights()
        
        # Simulate "dreams" - cross-domain predictions
        dreams = self._generate_dreams()
        
        # Log consolidation
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        self._log_consolidation(
            date=datetime.now().date().isoformat(),
            experiences_processed=0,  # Would need to query KC
            thematic_created=result["thematic_created"],
            compressed_created=result["compressed_created"],
            patterns_extracted=len(insights),
            insights_generated=len(insights),
            duration_ms=duration_ms
        )
        
        return {
            "consolidation_date": datetime.now().date().isoformat(),
            "thematic_created": result["thematic_created"],
            "compressed_created": result["compressed_created"],
            "insights_generated": len(insights),
            "dreams_generated": len(dreams),
            "duration_ms": duration_ms,
            "insights": insights,
            "dreams": dreams
        }
    
    def _generate_insights(self) -> List[Dict]:
        """Generate actionable insights from compressed patterns."""
        conn = sqlite3.connect(str(self.kc_db), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            patterns = conn.execute("""
                SELECT * FROM memory_compressed
                WHERE evidence_count > 10
                ORDER BY evidence_count DESC
                LIMIT 20
            """).fetchall()
            
            insights = []
            for p in patterns:
                if p["pattern_type"] == "anti-pattern":
                    insight = {
                        "type": "warning",
                        "text": f"High-confidence anti-pattern detected: {p['pattern_text'][:200]}",
                        "domains": json.loads(p["domains"]),
                        "confidence": min(0.95, p["confidence"]),
                        "evidence_count": p["evidence_count"]
                    }
                elif p["pattern_type"] == "rule":
                    insight = {
                        "type": "recommendation",
                        "text": f"Rule to apply: {p['pattern_text'][:200]}",
                        "domains": json.loads(p["domains"]),
                        "confidence": p["confidence"],
                        "evidence_count": p["evidence_count"]
                    }
                else:
                    insight = {
                        "type": "pattern",
                        "text": f"Cross-domain principle: {p['pattern_text'][:200]}",
                        "domains": json.loads(p["domains"]),
                        "confidence": p["confidence"],
                        "evidence_count": p["evidence_count"]
                    }
                
                # Save to crystal insights
                conn2 = sqlite3.connect(str(self.crystal_db), timeout=5)
                conn2.execute("""
                    INSERT INTO crystal_insights (insight_type, insight_text, domains, confidence, evidence_ids, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (insight["type"], insight["text"], json.dumps(insight["domains"]), 
                      insight["confidence"], json.dumps([]), datetime.now().isoformat()))
                conn2.commit()
                conn2.close()
                
                insights.append(insight)
            
            return insights
        finally:
            conn.close()
    
    def _generate_dreams(self) -> List[Dict]:
        """Generate 'dreams' - cross-domain synthesis predictions."""
        conn = sqlite3.connect(str(self.kc_db), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            # Find themes that appear in multiple domains
            cross_domain = conn.execute("""
                SELECT theme, COUNT(DISTINCT domain) as domain_count, GROUP_CONCAT(DISTINCT domain) as domains
                FROM memory_thematic
                GROUP BY theme
                HAVING domain_count >= 3
                ORDER BY domain_count DESC
                LIMIT 10
            """).fetchall()
            
            dreams = []
            for row in cross_domain:
                domains = row["domains"].split(",")
                dream = {
                    "type": "synthesis",
                    "content": f"Theme '{row['theme']}' connects {len(domains)} domains: {', '.join(domains)}. Possible unified mechanism?",
                    "domains": domains,
                    "trigger": f"cross_domain_theme_{row['theme']}",
                    "created_at": datetime.now().isoformat()
                }
                
                # Save dream
                conn2 = sqlite3.connect(str(self.crystal_db), timeout=5)
                conn2.execute("""
                    INSERT INTO crystal_dreams (dream_type, dream_content, domains, trigger, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (dream["type"], dream["content"], json.dumps(domains), 
                      dream["trigger"], datetime.now().isoformat()))
                conn2.commit()
                conn2.close()
                
                dreams.append(dream)
            
            return dreams
        finally:
            conn.close()
    
    def _log_consolidation(self, date: str, experiences_processed: int, thematic_created: int,
                          compressed_created: int, patterns_extracted: int, insights_generated: int,
                          duration_ms: int):
        """Log consolidation run."""
        conn = sqlite3.connect(str(self.crystal_db), timeout=5)
        try:
            conn.execute("""
                INSERT INTO crystal_consolidation (date, experiences_processed, thematic_created, compressed_created,
                                                  patterns_extracted, insights_generated, duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (date, experiences_processed, thematic_created, compressed_created,
                  patterns_extracted, insights_generated, duration_ms, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def get_recent_consolidations(self, limit: int = 7) -> List[Dict]:
        """Get recent consolidation runs."""
        conn = sqlite3.connect(str(self.crystal_db), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute("""
                SELECT * FROM crystal_consolidation
                ORDER BY date DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    
    def get_pending_insights(self) -> List[Dict]:
        """Get insights not yet applied."""
        conn = sqlite3.connect(str(self.crystal_db), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute("""
                SELECT * FROM crystal_insights
                WHERE applied = 0
                ORDER BY created_at DESC
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    
    def mark_insight_applied(self, insight_id: int):
        """Mark insight as applied."""
        conn = sqlite3.connect(str(self.crystal_db), timeout=5)
        try:
            conn.execute("UPDATE crystal_insights SET applied = 1 WHERE id = ?", (insight_id,))
            conn.commit()
        finally:
            conn.close()


def run_nocturnal_cognition() -> Dict[str, Any]:
    """Main entry point for cron job."""
    nc = NocturnalCognition()
    return nc.consolidate_daily()


if __name__ == "__main__":
    result = run_nocturnal_cognition()
    print(json.dumps(result, ensure_ascii=False, indent=2))