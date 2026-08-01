#!/usr/bin/env python3
"""
Crystal v3 — Модуль 16: External Intelligence (Updated with Agent Reach + OMH)
Внешний мир — YouTube, GitHub, Web Search, RSS, Exa, AI новости, инструменты
"""

# Revisit: when external intelligence sources, scanning frequency, or filtering logic changes. Last touched: 2026-07-26.

import os
import json
from datetime import datetime
from pathlib import Path

# Add scripts to path
_scripts_dir = Path(__file__).parent.parent
if str(_scripts_dir) not in __import__('sys').path:
    __import__('sys').path.insert(0, str(_scripts_dir))

from scripts.crystal.models import IntelItem
from scripts.crystal.config import Paths
from scripts.crystal.models import load_json, save_json


# Try to import Agent Reach integration
try:
    from scripts.crystal.omh_integration import (
        AgentReachIntegration,
        crystal_web_search,
        crystal_youtube_search,
        crystal_youtube_transcript,
        crystal_github_search,
        crystal_web_read,
        crystal_rss_fetch,
        ensure_agent_reach,
    )
    AGENT_REACH_AVAILABLE = True
except ImportError:
    AGENT_REACH_AVAILABLE = False
    AgentReachIntegration = None


class IntelScanner:
    """Сканирует внешний мир через Agent Reach (YouTube, GitHub, Web, RSS, Exa)."""
    
    def __init__(self):
        self.cache_path = Paths.intel_cache if hasattr(Paths, 'intel_cache') else None
        self.reach = AgentReachIntegration() if AGENT_REACH_AVAILABLE else None
        self.last_scan = None
        
        # Ensure Agent Reach is ready
        if AGENT_REACH_AVAILABLE and self.reach:
            try:
                ensure_agent_reach()
            except:
                pass
    
    def scan(self) -> list:
        """Сканирует все источники через Agent Reach."""
        items = []
        
        # 1. GitHub trending
        items.extend(self._scan_github())
        
        # 2. AI новости
        items.extend(self._scan_ai_news())
        
        # 3. Новые инструменты
        items.extend(self._scan_tools())
        
        # 4. YouTube research (новое!)
        items.extend(self._scan_youtube())
        
        # 5. RSS feeds (новое!)
        items.extend(self._scan_rss())
        
        self.last_scan = datetime.now().isoformat()
        return items
    
    def _scan_github(self) -> list:
        """Сканировать GitHub trending через Agent Reach."""
        items = []
        if not self.reach:
            return items
            
        try:
            queries = [
                "github trending AI agent framework 2024",
                "github trending LLM tools new",
                "github awesome-ai-agents new entries",
            ]
            for query in queries:
                results = self.reach.github_search(query, limit=3)
                for r in results:
                    items.append(IntelItem(
                        source="github",
                        title=f"Trending: {r.get('name', 'Unknown')}",
                        description=r.get('description', '')[:200],
                        url=r.get('url', ''),
                        relevance=0.7,
                    ))
        except Exception:
            pass
        return items
    
    def _scan_ai_news(self) -> list:
        """Сканировать AI новости через web search."""
        items = []
        if not self.reach:
            return items
            
        try:
            queries = [
                "new AI model release 2024",
                "LLM benchmark breakthrough 2024",
                "AI agent framework new release",
            ]
            for query in queries:
                results = crystal_web_search(query, max_results=3)
                for r in results:
                    items.append(IntelItem(
                        source="ai_news",
                        title=r.get('title', f"Новость: {query[:50]}"),
                        description=r.get('description', r.get('snippet', ''))[:200],
                        url=r.get('url', ''),
                        relevance=0.6,
                    ))
        except Exception:
            pass
        return items
    
    def _scan_tools(self) -> list:
        """Сканировать новые инструменты."""
        items = []
        if not self.reach:
            return items
            
        try:
            queries = [
                "new CLI tools for developers 2024",
                "new Python packages AI automation",
            ]
            for query in queries:
                results = crystal_web_search(query, max_results=3)
                for r in results:
                    items.append(IntelItem(
                        source="tools",
                        title=r.get('title', f"Инструмент: {query[:50]}"),
                        description=r.get('description', r.get('snippet', ''))[:200],
                        url=r.get('url', ''),
                        relevance=0.5,
                    ))
        except Exception:
            pass
        return items
    
    def _scan_youtube(self) -> list:
        """Сканировать YouTube за актуальными кейсами."""
        items = []
        if not self.reach:
            return items
            
        try:
            queries = [
                "AI agent automation case study 2024",
                "faceless YouTube channel automation 2024",
                "n8n workflow automation tutorial 2024",
                "CPA arbitrage case study real numbers 2024",
            ]
            for query in queries:
                videos = crystal_youtube_search(query, max_results=2)
                for v in videos:
                    # Get transcript for deeper analysis
                    transcript = crystal_youtube_transcript(v["url"])
                    items.append(IntelItem(
                        source="youtube",
                        title=v["title"],
                        description=transcript.get("description", "")[:200],
                        url=v["url"],
                        relevance=0.8,
                    ))
        except Exception:
            pass
        return items
    
    def _scan_rss(self) -> list:
        """Сканировать RSS фиды AI/Tech."""
        items = []
        if not self.reach:
            return items
            
        rss_feeds = [
            "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat AI
            "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",  # The Verge AI
            "https://github.com/trending/python?since=daily&format=atom",  # GitHub trending Python
        ]
        
        try:
            for feed_url in rss_feeds:
                entries = crystal_rss_fetch(feed_url)
                for e in entries[:3]:
                    items.append(IntelItem(
                        source="rss",
                        title=e.get('title', 'RSS Entry'),
                        description=e.get('summary', '')[:200],
                        url=e.get('link', ''),
                        relevance=0.6,
                    ))
        except Exception:
            pass
        return items
    
    def research_topic(self, topic: str, max_videos: int = 5, max_web: int = 10) -> dict:
        """Полное исследование темы через Agent Reach + OMH."""
        if not self.reach:
            return {"error": "Agent Reach not available"}
        
        return {
            "topic": topic,
            "youtube": crystal_youtube_search(topic, max_videos),
            "web": crystal_web_search(topic, max_web),
            "github": crystal_github_search(topic, 5),
            "timestamp": datetime.now().isoformat(),
        }
    
    def deep_dive_video(self, url: str) -> dict:
        """Глубокий анализ YouTube видео."""
        return crystal_youtube_transcript(url)
    
    def read_webpage(self, url: str) -> str:
        """Читать веб-страницу."""
        return crystal_web_read(url)


# Backward compatibility
def _web_search(query: str) -> str:
    """Legacy wrapper for old code."""
    if AGENT_REACH_AVAILABLE:
        results = crystal_web_search(query, max_results=1)
        if results:
            return results[0].get('description', results[0].get('snippet', ''))[:200]
    return ""


# Initialize on import
if AGENT_REACH_AVAILABLE:
    try:
        ensure_agent_reach()
        print("🔮 IntelScanner: Agent Reach + OMH integration active")
    except:
        pass
else:
    print("⚠️ IntelScanner: Agent Reach not available, using fallback")