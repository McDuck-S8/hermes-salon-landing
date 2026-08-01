#!/usr/bin/env python3
"""
Design Reference Collector — External source scanner for design trends.
Integrates with external_import for semantic search and pattern extraction.

Sources: Awwwards, SiteInspire, Behance, Dribbble, YouTube, Blogs, GitHub
"""

import os
import json
import re
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.autonomy.external_import import ExternalImportProtocol

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache" / "design"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

REFERENCES_FILE = CACHE_DIR / "references.json"
TRENDS_FILE = CACHE_DIR / "trends.json"


@dataclass
class DesignReference:
    """A design reference from external source"""
    id: str
    source: str  # awwwards, behance, youtube, github, blog
    url: str
    title: str
    description: str
    category: str  # landing, dashboard, portfolio, ecommerce, etc.
    tags: List[str]  # glassmorphism, dark-mode, tailwind, etc.
    visual_elements: Dict[str, Any]  # colors, typography, layout, animations
    code_snippets: List[Dict]  # html, css, js snippets
    metadata: Dict
    collected_at: str
    confidence: float = 0.5


@dataclass
class DesignTrend:
    """Extracted trend pattern"""
    id: str
    name: str
    description: str
    category: str  # color, typography, layout, animation, component
    frequency: int  # how many references mention it
    examples: List[str]  # reference IDs
    confidence: float
    detected_at: str


class DesignReferenceCollector:
    """Collects design references from multiple external sources"""
    
    def __init__(self):
        self.external_import = ExternalImportProtocol()
        self.references: Dict[str, DesignReference] = {}
        self.trends: Dict[str, DesignTrend] = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cached references and trends"""
        if REFERENCES_FILE.exists():
            try:
                data = json.loads(REFERENCES_FILE.read_text())
                for ref_data in data.get("references", []):
                    self.references[ref_data["id"]] = DesignReference(**ref_data)
            except Exception:
                pass
        
        if TRENDS_FILE.exists():
            try:
                data = json.loads(TRENDS_FILE.read_text())
                for trend_data in data.get("trends", []):
                    self.trends[trend_data["id"]] = DesignTrend(**trend_data)
            except Exception:
                pass
    
    def _save_cache(self):
        """Save references and trends to cache"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        ref_data = {"references": [asdict(r) for r in self.references.values()]}
        REFERENCES_FILE.write_text(json.dumps(ref_data, indent=2, ensure_ascii=False))
        
        trend_data = {"trends": [asdict(t) for t in self.trends.values()]}
        TRENDS_FILE.write_text(json.dumps(trend_data, indent=2, ensure_ascii=False))
    
    def collect_from_awwwards(self, limit: int = 10) -> List[DesignReference]:
        """Collect from Awwwards via search"""
        # Use external import for semantic search
        query = "site:awwwards.com best websites 2024 2025"
        results = self.external_import.semantic_search(query, top_k=limit)
        
        refs = []
        for r in results:
            ref_id = f"awwwards_{hashlib.md5(r.get('url', '').encode()).hexdigest()[:8]}"
            if ref_id in self.references:
                continue
            
            ref = DesignReference(
                id=ref_id,
                source="awwwards",
                url=r.get("url", ""),
                title=r.get("title", ""),
                description=r.get("snippet", ""),
                category="inspiration",
                tags=self._extract_tags(r.get("snippet", "") + " " + r.get("title", "")),
                visual_elements={},
                code_snippets=[],
                metadata={"search_rank": len(refs)},
                collected_at=datetime.now().isoformat(),
                confidence=0.6
            )
            self.references[ref_id] = ref
            refs.append(ref)
        
        self._save_cache()
        return refs
    
    def collect_from_youtube(self, channels: List[str] = None) -> List[DesignReference]:
        """Collect from YouTube design channels"""
        if channels is None:
            channels = [
                "designcourse", "fluxacademy", "joshwcomeau", 
                "kevinpowell", "traversymedia", "webdevsimplified"
            ]
        
        refs = []
        for channel in channels[:3]:  # Limit for speed
            query = f"site:youtube.com {channel} design ui ux 2024"
            results = self.external_import.semantic_search(query, top_k=2)
            
            for r in results:
                ref_id = f"youtube_{hashlib.md5(r.get('url', '').encode()).hexdigest()[:8]}"
                if ref_id in self.references:
                    continue
                
                ref = DesignReference(
                    id=ref_id,
                    source="youtube",
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    description=r.get("snippet", ""),
                    category="tutorial",
                    tags=self._extract_tags(r.get("snippet", "") + " " + r.get("title", "")),
                    visual_elements={},
                    code_snippets=[],
                    metadata={"channel": channel},
                    collected_at=datetime.now().isoformat(),
                    confidence=0.5
                )
                self.references[ref_id] = ref
                refs.append(ref)
        
        self._save_cache()
        return refs
    
    def collect_from_github(self, query: str = "tailwind components", limit: int = 5) -> List[DesignReference]:
        """Collect from GitHub repositories"""
        search_query = f"site:github.com {query} stars:>100"
        results = self.external_import.semantic_search(search_query, top_k=limit)
        
        refs = []
        for r in results:
            ref_id = f"github_{hashlib.md5(r.get('url', '').encode()).hexdigest()[:8]}"
            if ref_id in self.references:
                continue
            
            ref = DesignReference(
                id=ref_id,
                source="github",
                url=r.get("url", ""),
                title=r.get("title", ""),
                description=r.get("snippet", ""),
                category="code",
                tags=self._extract_tags(r.get("snippet", "") + " " + r.get("title", "")),
                visual_elements={},
                code_snippets=[],
                metadata={},
                collected_at=datetime.now().isoformat(),
                confidence=0.7
            )
            self.references[ref_id] = ref
            refs.append(ref)
        
        self._save_cache()
        return refs
    
    def collect_from_blogs(self, limit: int = 5) -> List[DesignReference]:
        """Collect from design blogs"""
        blogs = [
            "smashingmagazine.com", "css-tricks.com", "uxdesign.cc",
            "uxcollective.com", "web.dev", "developer.mozilla.org"
        ]
        
        refs = []
        for blog in blogs[:3]:
            query = f"site:{blog} css design trends 2024"
            results = self.external_import.semantic_search(query, top_k=2)
            
            for r in results:
                ref_id = f"blog_{hashlib.md5(r.get('url', '').encode()).hexdigest()[:8]}"
                if ref_id in self.references:
                    continue
                
                ref = DesignReference(
                    id=ref_id,
                    source="blog",
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    description=r.get("snippet", ""),
                    category="article",
                    tags=self._extract_tags(r.get("snippet", "") + " " + r.get("title", "")),
                    visual_elements={},
                    code_snippets=[],
                    metadata={"blog": blog},
                    collected_at=datetime.now().isoformat(),
                    confidence=0.6
                )
                self.references[ref_id] = ref
                refs.append(ref)
        
        self._save_cache()
        return refs
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract design-relevant tags from text"""
        tag_keywords = [
            "glassmorphism", "neumorphism", "dark mode", "dark-mode",
            "tailwind", "bootstrap", "css grid", "flexbox", "container queries",
            "micro-animations", "microanimations", "framer motion", "gsap",
            "3d", "webgl", "three.js", "shaders", "glass", "blur",
            "typography", "variable fonts", "fluid typography",
            "mobile first", "responsive", "container",
            "landing page", "dashboard", "portfolio", "ecommerce",
            "design system", "component library", "storybook",
            "accessibility", "a11y", "wcag", "semantic html",
            "performance", "lighthouse", "core web vitals",
            "seo", "schema", "structured data"
        ]
        
        text_lower = text.lower()
        found = [kw for kw in tag_keywords if kw in text_lower]
        return list(set(found))
    
    def run_full_collection(self, max_per_source: int = 5) -> Dict[str, List]:
        """Run collection from all sources"""
        print("[DESIGN_COLLECTOR] Starting full collection...")
        
        results = {
            "awwwards": self.collect_from_awwwards(max_per_source),
            "youtube": self.collect_from_youtube(),
            "github": self.collect_from_github(limit=max_per_source),
            "blogs": self.collect_from_blogs(max_per_source)
        }
        
        total = sum(len(v) for v in results.values())
        print(f"[DESIGN_COLLECTOR] Collected {total} new references")
        
        # Analyze trends
        self._analyze_trends()
        
        return results
    
    def _analyze_trends(self):
        """Analyze collected references for trends"""
        tag_counts = {}
        category_counts = {}
        
        for ref in self.references.values():
            for tag in ref.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            category_counts[ref.category] = category_counts.get(ref.category, 0) + 1
        
        # Create trend entries for top tags
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:20]:
            if count >= 2:  # Only trends mentioned 2+ times
                trend_id = f"trend_{hashlib.md5(tag.encode()).hexdigest()[:8]}"
                if trend_id not in self.trends:
                    examples = [ref.id for ref in self.references.values() if tag in ref.tags]
                    self.trends[trend_id] = DesignTrend(
                        id=trend_id,
                        name=tag,
                        description=f"Trend detected in {count} references",
                        category="style" if tag not in ["landing page", "dashboard", "portfolio", "ecommerce"] else "layout",
                        frequency=count,
                        examples=examples[:5],
                        confidence=min(0.5 + count * 0.1, 0.9),
                        detected_at=datetime.now().isoformat()
                    )
        
        self._save_cache()
        print(f"[DESIGN_COLLECTOR] Updated {len(self.trends)} trends")


import hashlib

# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_reference_collector.py <command>")
        print("Commands: collect, list, trends, stats")
        sys.exit(1)
    
    collector = DesignReferenceCollector()
    cmd = sys.argv[1]
    
    if cmd == "collect":
        results = collector.run_full_collection()
        print(json.dumps({k: len(v) for k, v in results.items()}, indent=2))
    
    elif cmd == "list":
        for ref in collector.references.values():
            print(f"{ref.id}: {ref.title[:60]} | {ref.source} | {ref.tags}")
    
    elif cmd == "trends":
        for trend in collector.trends.values():
            print(f"{trend.name}: freq={trend.frequency}, conf={trend.confidence:.2f}")
    
    elif cmd == "stats":
        print(f"References: {len(collector.references)}")
        print(f"Trends: {len(collector.trends)}")
        by_source = {}
        for ref in collector.references.values():
            by_source[ref.source] = by_source.get(ref.source, 0) + 1
        print(f"By source: {by_source}")


if __name__ == "__main__":
    main()