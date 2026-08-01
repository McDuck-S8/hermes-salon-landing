#!/usr/bin/env python3
"""
Skill-Pathfinder Filter — Stage 3 of Knowledge Filter.
Checks for duplicates in Knowledge Cube, skills/, and reports/.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
SKILLS_DIR = HERE.parent.parent.parent
HERMES_ROOT = SKILLS_DIR.parent
CACHE_DIR = HERMES_ROOT / "cache"
DB_PATH = CACHE_DIR / "knowledge_cube.db"

class SkillPathfinderFilter:
    """Checks for duplicates and novelty."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.threshold = self.config.get("threshold", 50)  # novelty threshold - lowered from 70
        
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "can", "this", "that", "these",
            "those", "it", "its", "we", "our", "you", "your", "he", "him", "his",
            "she", "her", "they", "them", "their", "what", "which", "who", "when",
            "where", "why", "how", "all", "each", "every", "both", "few", "more",
            "most", "other", "some", "such", "no", "not", "only", "own", "same",
            "so", "than", "too", "very", "just", "i", "me", "my", "we", "us",
            # Russian
            "и", "в", "на", "с", "по", "для", "от", "до", "из", "о", "об", "о",
            "что", "как", "где", "когда", "почему", "зачем", "какой", "какая",
            "какое", "какие", "тот", "та", "то", "те", "этот", "эта", "это",
            "эти", "мой", "моя", "моё", "мои", "твой", "твоя", "твоё", "твои",
            "свой", "своя", "своё", "свои", "наш", "наша", "наше", "наши",
            "ваш", "ваша", "ваше", "ваши", "их", "он", "она", "оно", "они",
            "был", "была", "было", "были", "будет", "будет", "есть", "нет",
            "да", "нет", "не", "ни", "или", "но", "а", "да", "же", "ли", "бы",
            "то", "тоже", "также", "уже", "ещё", "все", "всё", "всего", "всю",
        }
        
        # Extract words (alphanumeric + underscore, 3+ chars)
        words = re.findall(r'\b\w{3,}\b', text.lower())
        return [w for w in words if w not in stopwords and not w.isdigit()]
    
    def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """Simple TF-IDF-like similarity."""
        words1 = set(self._extract_keywords(text1))
        words2 = set(self._extract_keywords(text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0
    
    def _search_knowledge_cube(self, article: Dict) -> List[Dict]:
        """Search KC for similar entries."""
        results = []
        try:
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search in kc_entries
            query = f"%{article.get('title', '')[:50]}%"
            cursor.execute(
                "SELECT id, content, tags, source, category FROM kc_entries "
                "WHERE content LIKE ? OR tags LIKE ? ORDER BY importance DESC LIMIT 20",
                (query, query)
            )
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "content": row["content"][:200],
                    "tags": row["tags"],
                    "source": row["source"],
                    "category": row["category"],
                })
            
            # Also search experiences table
            cursor.execute(
                "SELECT id, raw_text, axis_domain, axis_outcome FROM experiences "
                "WHERE raw_text LIKE ? ORDER BY ts DESC LIMIT 20",
                (query,)
            )
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "content": row["raw_text"][:200],
                    "domain": row["axis_domain"],
                    "outcome": row["axis_outcome"],
                    "source": "experiences"
                })
            
            conn.close()
        except Exception as e:
            print(f"  [Pathfinder] KC search error: {e}", file=sys.stderr)
        
        return results
    
    def _scan_skills(self, article: Dict) -> List[Dict]:
        """Scan skills/ directory for relevant implementations."""
        results = []
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        
        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            try:
                text = skill_md.read_text(encoding="utf-8", errors="ignore")
                # Quick check: does skill mention similar topics?
                score = self._tfidf_similarity(text, title + " " + content)
                if score > 0.15:  # threshold
                    results.append({
                        "skill": skill_dir.name,
                        "similarity": round(score, 3),
                        "path": str(skill_dir.relative_to(HERMES_ROOT))
                    })
            except Exception:
                pass
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:10]
    
    def _scan_reports(self, article: Dict) -> List[Dict]:
        """Scan reports/ for prior analysis."""
        results = []
        reports_dir = HERMES_ROOT / "reports"
        if not reports_dir.exists():
            return results
        
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        
        for report_file in reports_dir.glob("*.md"):
            try:
                text = report_file.read_text(encoding="utf-8", errors="ignore")
                score = self._tfidf_similarity(text, title + " " + content)
                if score > 0.1:
                    results.append({
                        "report": report_file.name,
                        "similarity": round(score, 3),
                        "path": str(report_file.relative_to(HERMES_ROOT))
                    })
            except Exception:
                pass
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:5]
    
    def evaluate(self, article: Dict) -> Dict[str, Any]:
        """Evaluate novelty against existing knowledge."""
        text = f"{article.get('title', '')} {article.get('content', '')}"
        
        # Search all sources
        kc_matches = self._search_knowledge_cube(article)
        skill_matches = self._scan_skills(article)
        report_matches = self._scan_reports(article)
        
        # Compute max similarity
        max_similarity = 0.0
        similar_entries = []
        
        # Check KC entries
        for match in kc_matches:
            content = match.get("content", "")
            sim = self._tfidf_similarity(text, content)
            if sim > max_similarity:
                max_similarity = sim
            if sim > 0.2:
                similar_entries.append({
                    "source": match.get("source", "kc"),
                    "similarity": round(sim, 3),
                    "preview": content[:100]
                })
        
        # Check skills
        for match in skill_matches:
            if match["similarity"] > max_similarity:
                max_similarity = match["similarity"]
            if match["similarity"] > 0.2:
                similar_entries.append({
                    "source": f"skill:{match['skill']}",
                    "similarity": match["similarity"],
                    "preview": match["path"]
                })
        
        # Check reports
        for match in report_matches:
            if match["similarity"] > max_similarity:
                max_similarity = match["similarity"]
            if match["similarity"] > 0.2:
                similar_entries.append({
                    "source": f"report:{match['report']}",
                    "similarity": match["similarity"],
                    "preview": match["path"]
                })
        
        # Novelty score
        novelty = max(0, 100 - int(max_similarity * 100))
        passed = novelty >= self.threshold
        
        reasons = []
        if passed:
            reasons.append(f"Novelty {novelty}% (max similarity: {max_similarity:.0%})")
        else:
            reasons.append(f"Novelty {novelty}% < threshold {self.threshold}%")
            if similar_entries:
                top = similar_entries[0]
                reasons.append(f"Most similar: {top['source']} ({top['similarity']:.0%})")
        
        return {
            "score": novelty,
            "passed": passed,
            "novelty": novelty,
            "max_similarity": round(max_similarity, 3),
            "similar_count": len(similar_entries),
            "similar_entries": similar_entries[:5],
            "reasons": reasons,
            "details": {
                "kc_matches": len(kc_matches),
                "skill_matches": len(skill_matches),
                "report_matches": len(report_matches),
                "threshold": self.threshold,
            }
        }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--source", default="test")
    parser.add_argument("--url", default="")
    args = parser.parse_args()
    
    filter = SkillPathfinderFilter()
    result = filter.evaluate({
        "title": args.title,
        "content": args.content,
        "source": args.source,
        "url": args.url
    })
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()