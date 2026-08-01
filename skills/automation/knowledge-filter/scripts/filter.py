#!/usr/bin/env python3
"""
Knowledge Filter — Three-stage gate between parsers and Knowledge Cube.

Stage 1: Human-Source Filter (personal relevance, constraints, values)
Stage 2: Audience-Analyzer Filter (market relevance, vertical match, geo match)
Stage 3: Skill-Pathfinder Filter (deduplication, novelty check)

Only passes all three → Knowledge Cube. Rejected → cache/unfiltered/
"""

import json
import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# ─── Paths ────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
SKILLS_DIR = HERE.parent.parent
HERMES_ROOT = SKILLS_DIR.parent
# Use absolute path to avoid MSYS path issues
CACHE_DIR = Path("D:/Portable_Soft/hermes/cache")
UNFILTERED_DIR = CACHE_DIR / "unfiltered"
UNFILTERED_DIR.mkdir(parents=True, exist_ok=True)

# ─── Imports ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(SKILLS_DIR / "human-source" / "scripts"))
sys.path.insert(0, str(SKILLS_DIR / "audience-analyzer" / "scripts"))
sys.path.insert(0, str(SKILLS_DIR / "skill-pathfinder" / "scripts"))
sys.path.insert(0, str(HERMES_ROOT / "scripts"))

# Import human-source filter
try:
    sys.path.insert(0, str(SKILLS_DIR / "automation" / "knowledge-filter" / "scripts"))
    from human_source_filter import HumanSourceFilter
    HUMAN_FILTER_AVAILABLE = True
except ImportError as e:
    print(f"  [HumanSource] Import failed: {e}")
    HumanSourceFilter = None
    HUMAN_FILTER_AVAILABLE = False

# Import audience-analyzer filter
try:
    from audience_filter import AudienceFilter
    AUDIENCE_FILTER_AVAILABLE = True
except ImportError as e:
    print(f"  [AudienceAnalyzer] Import failed: {e}")
    AudienceFilter = None
    AUDIENCE_FILTER_AVAILABLE = False

# Import skill-pathfinder filter
try:
    from skill_pathfinder_filter import SkillPathfinderFilter
    PATHFINDER_FILTER_AVAILABLE = True
except ImportError as e:
    print(f"  [SkillPathfinder] Import failed: {e}")
    SkillPathfinderFilter = None
    PATHFINDER_FILTER_AVAILABLE = False

# Import KC RAG for writing to cube
try:
    sys.path.insert(0, str(Path("D:/Portable_Soft/hermes/scripts")))
    from kc_rag import upsert as kc_upsert, search as kc_search
    print("  [KC] kc_rag imported successfully")
except ImportError as e:
    print(f"  [KC] Import failed: {e}")
    kc_upsert = kc_search = None


# ─── Data Classes ────────────────────────────────────────────────────────────
@dataclass
class FilterScore:
    """Score from one filter stage."""
    passed: bool
    score: int  # 0-100
    details: Dict[str, Any]
    reasons: List[str] = None

@dataclass
class FilterResult:
    """Complete filter result for one article."""
    article: Dict[str, Any]
    passed: bool
    failed_at_stage: Optional[int]
    scores: Dict[str, int]
    stage_results: List[FilterScore]
    action: str  # "inserted_into_kc" | "saved_to_unfiltered"
    timestamp: str


# ─── Filter Implementation ──────────────────────────────────────────────────

class KnowledgeFilter:
    """Three-stage knowledge filter."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        
        # Initialize sub-filters
        self.human_filter = HumanSourceFilter() if HumanSourceFilter else None
        self.audience_filter = AudienceFilter() if AudienceFilter else None
        self.pathfinder_filter = SkillPathfinderFilter() if SkillPathfinderFilter else None

        if not any([self.human_filter, self.audience_filter, self.pathfinder_filter]):
            print("WARNING: No sub-filters available. Using fallback logic.")

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load filter configuration."""
        default_config = {
            "filters": {
                "human_source": {"threshold": 60},
                "audience_analyzer": {"threshold": 50},
                "skill_pathfinder": {"threshold": 70},
            },
            "output": {
                "unfiltered_dir": str(UNFILTERED_DIR),
                "keep_unfiltered_days": 30,
                "log_all_decisions": True,
            }
        }
        
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                # Deep merge
                for k, v in user_config.items():
                    if isinstance(v, dict) and k in default_config:
                        default_config[k].update(v)
                    else:
                        default_config[k] = v
            except Exception:
                pass
        
        return default_config

    def filter_article(self, title: str, url: str, source: str, content: str,
                       extra: Dict = None) -> FilterResult:
        """Filter a single article through all three stages."""
        
        article = {
            "title": title,
            "url": url,
            "source": source,
            "content": content,
            "extra": extra or {}
        }
        
        result = FilterResult(
            article=article,
            passed=False,
            failed_at_stage=None,
            scores={},
            stage_results=[],
            action="",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # ─── STAGE 1: Human-Source Filter ────────────────────────────────────
        hs_result = self._run_human_source_filter(article)
        result.scores["human_source"] = hs_result.score
        result.stage_results.append(hs_result)
        
        if not hs_result.passed:
            result.passed = False
            result.failed_at_stage = 1
            result.action = "saved_to_unfiltered"
            self._save_rejection(result, 1)
            return result
        
        # ─── Audience-Analyzer Filter ────────────────────────────────────────────────
        aa_result = self._run_audience_filter(article)
        result.scores["audience"] = aa_result.score
        result.stage_results.append(aa_result)
        
        if not aa_result.passed:
            result.passed = False
            result.failed_at_stage = 2
            result.action = "saved_to_unfiltered"
            self._save_rejection(result, 2)
            # Still continue to stage 3 for logging purposes
            # return result
        
        # ─── STAGE 3: Skill-Pathfinder Filter ─────────────────────────────────
        sp_result = self._run_pathfinder_filter(article)
        result.scores["pathfinder"] = sp_result.score
        result.stage_results.append(sp_result)
        
        # Final decision: pass if HS passed AND (AA passed OR SP passed)
        hs_passed = result.stage_results[0].passed
        aa_passed = aa_result.passed if len(result.stage_results) > 1 else False
        sp_passed = sp_result.passed
        
        # Need human-source + at least one of audience/pathfinder
        result.passed = hs_passed and (aa_passed or sp_passed)
        
        if not result.passed:
            result.failed_at_stage = 2 if not aa_passed else 3
            result.action = "saved_to_unfiltered"
            self._save_rejection(result, result.failed_at_stage)
            return result
        
        # ─── ALL PASSED → Insert into Knowledge Cube ──────────────────────────
        result.passed = True
        result.action = "inserted_into_kc"
        self._insert_into_kc(article, result)
        
        return result

    def _run_human_source_filter(self, article: Dict) -> FilterScore:
        """Stage 1: Check personal relevance and constraints."""
        
        if self.human_filter:
            try:
                hs_result = self.human_filter.evaluate(article)
                return FilterScore(
                    passed=hs_result["score"] >= self.config["filters"]["human_source"]["threshold"],
                    score=hs_result["score"],
                    details=hs_result,
                    reasons=hs_result.get("conflicts", [])
                )
            except Exception as e:
                print(f"  [HumanSource] Error: {e}, using fallback")
        
        # Fallback logic
        return self._fallback_human_source(article)

    def _fallback_human_source(self, article: Dict) -> FilterScore:
        """Fallback human-source evaluation."""
        text = f"{article['title']} {article['content']}".lower()
        
        score = 50  # base
        conflicts = []
        
        # Hard blocks
        hard_blocks = [
            ("google gemini", "Google Gemini API required"),
            ("playwright", "Playwright required (blocked)"),
            ("chrome.*headless", "Chrome headless required"),
            ("kyc", "KYC required"),
            ("passport", "Passport required"),
            ("selfie", "Selfie verification required"),
            ("document", "Documents required"),
            ("paid api", "Paid API required"),
            ("budget", "Requires budget"),
        ]
        
        for kw, reason in hard_blocks:
            if kw in text:
                return FilterScore(False, 0, {}, [f"HARD BLOCK: {reason}"])
        
        # Boost keywords
        boost_keywords = {
            "crimea": 15, "simferopol": 15, "hh.ru": 10, "job": 10,
            "p2p": 20, "usdt": 20, "rub": 15, "offramp": 20, "crypto": 10,
            "shorts": 15, "tiktok": 15, "content": 10, "pipeline": 10,
            "arbitrage": 25, "matrix": 10, "betting": 15, "cricket": 15,
            "autonomous": 20, "cron": 10, "daemon": 10, "self-heal": 15,
            "telegram": 10, "bot": 10, "channel": 10,
            "no kyc": 20, "no kyc": 20, "whitebird": 15, "p2p": 15,
        }
        
        for kw, boost in boost_keywords.items():
            if kw in text:
                score += boost
        
        # Penalty keywords
        penalty_keywords = {
            "google ads": -20, "facebook ads": -15, "tiktok ads": -15,
            "agency": -10, "manager": -10, "manual": -5, "routine": -5,
        }
        
        for kw, penalty in penalty_keywords.items():
            if kw in text:
                score += penalty
        
        score = max(0, min(100, score))
        threshold = self.config["filters"]["human_source"]["threshold"]
        
        return FilterScore(
            passed=score >= threshold,
            score=score,
            details={"method": "fallback", "text_length": len(text)},
            reasons=conflicts if score < threshold else []
        )

    def _run_audience_filter(self, article: Dict) -> FilterScore:
        """Stage 2: Check market relevance."""
        
        if self.audience_filter:
            try:
                aa_result = self.audience_filter.evaluate(article)
                return FilterScore(
                    passed=aa_result["score"] >= self.config["filters"]["audience_analyzer"]["threshold"],
                    score=aa_result["score"],
                    details=aa_result,
                    reasons=aa_result.get("reasons", [])
                )
            except Exception as e:
                print(f"  [AudienceAnalyzer] Error: {e}, using fallback")
        
        # Fallback logic
        return self._fallback_audience(article)

    def _fallback_audience(self, article: Dict) -> FilterScore:
        """Fallback audience relevance evaluation."""
        text = f"{article['title']} {article['content']}".lower()
        
        score = 30  # base
        matched_verticals = []
        geo_match = []
        
        # Vertical keywords
        verticals = {
            "gambling": {
                "keywords": ["betting", "casino", "slots", "cricket", "1xbet", "1win", "gambling", "bet", "wager", "sportsbook"],
                "geos": ["in", "br", "mx", "latam", "id", "bd", "india", "brazil", "mexico"],
                "weight": 30
            },
            "fintech": {
                "keywords": ["card", "payout", "leadgen", "loan", "crypto", "p2p", "offramp", "onramp", "whitebird", "usdt", "rub"],
                "geos": ["ru", "cis", "latam", "in", "ua", "kz"],
                "weight": 25
            },
            "content": {
                "keywords": ["shorts", "tiktok", "reels", "viral", "organic", "youtube", "instagram", "creators"],
                "geos": ["global", "us", "in", "br"],
                "weight": 20
            },
        }
        
        for vertical, config in verticals.items():
            kw_hits = sum(1 for kw in config["keywords"] if kw in text)
            if kw_hits >= 2:
                matched_verticals.append(vertical)
                score += config["weight"]
            
            geo_hits = [g for g in config["geos"] if g in text]
            if geo_hits:
                geo_match.extend(geo_hits)
                score += 10
        
        # Source-specific boost
        source_boosts = {
            "affiliatefix": 15, "partnerkin": 15, "reddit": 10,
            "youtube": 10, "telegram": 10, "partnerkin_youtube": 15,
        }
        score += source_boosts.get(article["source"], 0)
        
        score = max(0, min(100, score))
        threshold = self.config["filters"]["audience_analyzer"]["threshold"]
        
        return FilterScore(
            passed=score >= threshold,
            score=score,
            details={"matched_verticals": matched_verticals, "geo_match": geo_match},
            reasons=[] if score >= threshold else [f"Score {score} < threshold {threshold}"]
        )

    def _run_pathfinder_filter(self, article: Dict) -> FilterScore:
        """Stage 3: Check for duplicates/novelty."""
        
        if self.pathfinder_filter:
            try:
                sp_result = self.pathfinder_filter.evaluate(article)
                return FilterScore(
                    passed=sp_result["novelty"] >= self.config["filters"]["skill_pathfinder"]["threshold"],
                    score=sp_result["novelty"],
                    details=sp_result,
                    reasons=sp_result.get("reasons", [])
                )
            except Exception as e:
                print(f"  [SkillPathfinder] Error: {e}, using fallback")
        
        return self._fallback_pathfinder(article)

    def _fallback_pathfinder(self, article: Dict) -> FilterScore:
        """Fallback novelty check using KC search."""
        if not kc_search:
            return FilterScore(True, 100, {"method": "no_kc", "note": "KC search unavailable"})
        
        try:
            query = f"{article['title']} {article['content'][:200]}"
            results = kc_search(query, limit=5)
            
            if not results:
                return FilterScore(True, 100, {"similar_count": 0, "method": "kc_search"})
            
            # Calculate max similarity from results
            max_similarity = 0
            similar = []
            for r in results:
                sim = r.get("score", 0) * 100  # assume 0-1 score
                if sim > max_similarity:
                    max_similarity = sim
                similar.append({
                    "id": r.get("id"),
                    "title": r.get("content", "")[:80],
                    "similarity": round(sim, 1)
                })
            
            novelty = max(0, 100 - max_similarity)
            threshold = self.config["filters"]["skill_pathfinder"]["threshold"]
            
            return FilterScore(
                passed=novelty >= threshold,
                score=int(novelty),
                details={"similar_count": len(similar), "similar": similar, "max_similarity": round(max_similarity, 1)},
                reasons=[f"Too similar to existing (max {max_similarity:.1f}%)"] if novelty < threshold else []
            )
        except Exception as e:
            return FilterScore(True, 90, {"error": str(e)}, [])

    def _insert_into_kc(self, article: Dict, result: FilterResult):
        """Insert filtered article into Knowledge Cube."""
        if not kc_upsert:
            print("  [KC] kc_upsert unavailable, skipping insert")
            return
        
        # Build KC entry
        scores = result.scores
        content = (
            f"[{article['source'].upper()}] {article['title']}\n"
            f"URL: {article['url']}\n"
            f"Source: {article['source']}\n\n"
            f"KEY INSIGHTS:\n{article['content'][:1500]}"
        )
        
        tags = [
            f"source:{article['source']}",
            f"filter:passed",
            f"personal_importance:{scores.get('human_source', 0)}",
            f"audience_relevance:{scores.get('audience', 0)}",
            f"novelty:{scores.get('pathfinder', 0)}",
        ]
        
        # Add vertical/geo tags from stage 2 details
        if len(result.stage_results) >= 2:
            aa_details = result.stage_results[1].details
            for v in aa_details.get("matched_verticals", []):
                tags.append(f"vertical:{v}")
            for g in aa_details.get("geo_match", []):
                tags.append(f"geo:{g}")
        
        # Determine category
        category = "actionable"
        if "gambling" in tags or "betting" in " ".join(tags).lower():
            category = "arbitrage"
        elif "fintech" in " ".join(tags).lower() or "crypto" in " ".join(tags).lower():
            category = "finance"
        elif "content" in " ".join(tags).lower():
            category = "content"
        
        try:
            entry_id = kc_upsert(
                content=content,
                tags=",".join(tags),
                source="knowledge_filter",
                category=category,
                importance=max(5, min(9, scores.get('human_source', 50) // 10 + 3)),
                confidence=min(0.95, (scores.get('human_source', 50) + scores.get('audience', 50) + scores.get('pathfinder', 50)) / 300),
                verification_method="auto_filtered",
                expiration_date=(datetime.now(timezone.utc).replace(month=datetime.now().month + 3)).strftime("%Y-%m-%d") if datetime.now().month <= 9 else (datetime.now(timezone.utc).replace(year=datetime.now().year+1, month=datetime.now().month-9)).strftime("%Y-%m-%d")
            )
            print(f"  [KC] Inserted: {entry_id}")
        except Exception as e:
            print(f"  [KC] Insert failed: {e}")

    def _save_rejection(self, result: FilterResult, stage: int):
        """Save rejected article to unfiltered cache."""
        date_dir = UNFILTERED_DIR / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)
        
        reject_file = date_dir / f"rejected_stage{stage}_{result.article['source']}_{datetime.now().strftime('%H%M%S')}.json"
        
        reject_data = {
            "timestamp": result.timestamp,
            "title": result.article["title"],
            "url": result.article["url"],
            "source": result.article["source"],
            "failed_at_stage": stage,
            "scores": result.scores,
            "stage_details": [asdict(s) for s in result.stage_results],
        }
        
        reject_file.write_text(json.dumps(reject_data, indent=2, ensure_ascii=False))
        
        # Update index
        index_file = UNFILTERED_DIR / "index.json"
        index = []
        if index_file.exists():
            try:
                index = json.loads(index_file.read_text())
            except:
                index = []
        
        index.append({
            "file": str(reject_file.relative_to(UNFILTERED_DIR)),
            "timestamp": result.timestamp,
            "title": result.article["title"][:80],
            "source": result.article["source"],
            "stage": stage,
        })
        
        # Keep only last 1000
        index = index[-1000:]
        index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    def filter_batch(self, articles: List[Dict]) -> List[FilterResult]:
        """Filter multiple articles."""
        results = []
        for art in articles:
            print(f"\n🔍 Filtering: {art['title'][:60]}... ({art['source']})")
            result = self.filter_article(
                title=art.get("title", ""),
                url=art.get("url", ""),
                source=art.get("source", ""),
                content=art.get("content", art.get("summary", "")),
                extra=art.get("extra")
            )
            results.append(result)
            
            if result.passed:
                print(f"  ✅ PASSED (HS:{result.scores.get('human_source',0)} AA:{result.scores.get('audience',0)} SP:{result.scores.get('pathfinder',0)})")
            else:
                print(f"  ❌ REJECTED at stage {result.failed_at_stage} (HS:{result.scores.get('human_source',0)} AA:{result.scores.get('audience',0)} SP:{result.scores.get('pathfinder',0)})")
                for sr in result.stage_results:
                    if sr.reasons:
                        for r in sr.reasons:
                            print(f"    - {r}")
        
        return results


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Knowledge Filter — three-stage gate to KC")
    parser.add_argument("--title", help="Article title")
    parser.add_argument("--url", help="Article URL")
    parser.add_argument("--source", help="Source name (affiliatefix, partnerkin, reddit, youtube, telegram)")
    parser.add_argument("--content", help="Article content/summary")
    parser.add_argument("--batch", type=Path, help="JSON file with articles array")
    parser.add_argument("--test-rss", action="store_true", help="Test on latest RSS cache")
    parser.add_argument("--limit", type=int, default=10, help="Limit for test-rss")
    parser.add_argument("--config", type=Path, help="Config file path")
    parser.add_argument("--output", type=Path, help="Output report file")
    
    args = parser.parse_args()
    
    filter = KnowledgeFilter(args.config)
    
    if args.test_rss:
        # Load RSS cache
        rss_cache = CACHE_DIR / "rss_monitor" / "latest.json"
        if not rss_cache.exists():
            print("RSS cache not found. Run rss_monitor.py first.")
            sys.exit(1)
        
        with open(rss_cache) as f:
            data = json.load(f)
        
        articles = []
        for feed_id, entries in data.get("feeds", {}).items():
            for e in entries[:args.limit]:
                articles.append({
                    "title": e.get("title", ""),
                    "url": e.get("url", ""),
                    "source": feed_id,
                    "content": e.get("summary", "")[:2000],
                    "extra": {"tags": e.get("tags", []), "topic": e.get("topic", "")}
                })
        
        print(f"=== KNOWLEDGE FILTER TEST ({len(articles)} articles) ===")
        results = filter.filter_batch(articles)
        
        passed = sum(1 for r in results if r.passed)
        rejected = len(results) - passed
        
        print(f"\n=== SUMMARY ===")
        print(f"Total: {len(results)} | Passed: {passed} | Rejected: {rejected}")
        
        if args.output:
            report = generate_report(results)
            args.output.write_text(report)
            print(f"Report saved to {args.output}")
        
        return
    
    if args.batch:
        with open(args.batch) as f:
            articles = json.load(f)
        results = filter.filter_batch(articles)
        if args.output:
            args.output.write_text(generate_report(results))
        return
    
    if not all([args.title, args.url, args.source, args.content]):
        parser.error("Need --title, --url, --source, --content for single article")
    
    result = filter.filter_article(args.title, args.url, args.source, args.content)
    print(json.dumps({
        "passed": result.passed,
        "scores": result.scores,
        "failed_at_stage": result.failed_at_stage,
        "action": result.action,
        "stage_details": [asdict(s) for s in result.stage_results]
    }, indent=2, ensure_ascii=False))


def generate_report(results: List[FilterResult]) -> str:
    """Generate markdown report."""
    lines = [
        "# Knowledge Filter Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total: {len(results)} | Passed: {sum(1 for r in results if r.passed)} | Rejected: {sum(1 for r in results if not r.passed)}",
        "",
        "## Passed Articles",
    ]
    
    for r in results:
        if r.passed:
            lines.append(f"### ✅ {r.article['title']}")
            lines.append(f"- Source: {r.article['source']}")
            lines.append(f"- URL: {r.article['url']}")
            lines.append(f"- Scores: HS={r.scores.get('human_source',0)} AA={r.scores.get('audience',0)} SP={r.scores.get('pathfinder',0)}")
            lines.append("")
    
    lines.append("## Rejected Articles")
    
    for r in results:
        if not r.passed:
            lines.append(f"### ❌ {r.article['title']} (Stage {r.failed_at_stage})")
            lines.append(f"- Source: {r.article['source']}")
            lines.append(f"- URL: {r.article['url']}")
            lines.append(f"- Scores: HS={r.scores.get('human_source',0)} AA={r.scores.get('audience',0)} SP={r.scores.get('pathfinder',0)}")
            for sr in r.stage_results:
                if sr.reasons:
                    lines.append(f"- Reasons: {', '.join(sr.reasons)}")
            lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()