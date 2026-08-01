#!/usr/bin/env python3
"""
External Import Protocol — Agent Reach Integration
Uses AgentReach for YouTube, web, GitHub, RSS, search capabilities.
"""

import subprocess, json, os, sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Import AgentReach
sys.path.insert(0, str(Path(__file__).parent))
from agent_reach_integration import AgentReach

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

class ExternalImporter:
    """
    External Import Protocol using AgentReach.
    Provides: YouTube, Web Search, GitHub, RSS, Web Read.
    """
    
    def __init__(self):
        self.agent_reach = AgentReach()
        self._ensure_installed()
    
    def _ensure_installed(self):
        """Ensure AgentReach is installed"""
        if not self.agent_reach.bin.exists():
            print("[EXTERNAL_IMPORT] Installing AgentReach...")
            self.agent_reach.install()
    
    # === YouTube ===
    
    def youtube_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube videos via AgentReach (uses yt-dlp + proxy)"""
        try:
            return self.agent_reach.youtube_search(query, max_results)
        except Exception as e:
            return [{"error": f"youtube_search failed: {e}"}]
    
    def youtube_transcript(self, url: str) -> Optional[str]:
        """Get YouTube transcript via AgentReach (yt-dlp + proxy)"""
        try:
            return self.agent_reach.youtube_transcript(url)
        except Exception as e:
            return f"Error: {e}"
    
    def youtube_metadata(self, url: str) -> Optional[Dict]:
        """Get video metadata via yt-dlp --dump-json"""
        try:
            result = subprocess.run([
                "yt-dlp", "--proxy", "socks5://127.0.0.1:10806",
                "--dump-json", "--no-download", url
            ], capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
        except Exception as e:
            pass
        return None
    
    # === Web ===
    
    def web_search(self, query: str, max_results: int = 10) -> Any:
        """Web search via Exa (via mcporter) or Jina fallback"""
        try:
            return self.agent_reach.web_search(query, max_results)
        except Exception as e:
            return {"error": f"web_search failed: {e}"}
    
    def web_read(self, url: str) -> str:
        """Read webpage via Jina AI"""
        try:
            return self.agent_reach.web_read(url)
        except Exception as e:
            return f"Error: {e}"
    
    # === GitHub ===
    
    def github_read(self, repo: str, path: str = "") -> str:
        """Read GitHub file/repo via Jina AI"""
        try:
            return self.agent_reach.github_read(repo, path)
        except Exception as e:
            return f"Error: {e}"
    
    # === RSS ===
    
    def rss_fetch(self, url: str) -> str:
        """Fetch RSS feed"""
        try:
            return self.agent_reach.rss_fetch(url)
        except Exception as e:
            return f"Error: {e}"
    
    # === High-level workflows ===
    
    def research_youtube_topic(self, topic: str, max_videos: int = 5) -> Dict:
        """
        Full YouTube research workflow:
        1. Search for topic
        2. Get metadata for top videos
        3. Extract transcripts for top videos
        4. Return structured data
        """
        results = {
            "topic": topic,
            "videos": []
        }
        
        # Search
        videos = self.youtube_search(topic, max_results=max_results)
        if not videos or (isinstance(videos, list) and len(videos) > 0 and "error" in videos[0]):
            return {"error": "Search failed", "topic": topic}
        
        # Process each video
        for video in videos[:max_results]:
            url = video.get("url") or video.get("url", "")
            if not url and "id" in video:
                url = f"https://www.youtube.com/watch?v={video['id']}"
            
            video_data = {
                "title": video.get("title", ""),
                "url": url,
                "channel": video.get("channel", ""),
                "views": video.get("views", 0)
            }
            
            # Get metadata
            meta = self.youtube_metadata(url)
            if meta:
                video_data["duration"] = meta.get("duration")
                video_data["description"] = meta.get("description", "")[:1000]
                video_data["subtitles"] = list(meta.get("subtitles", {}).keys())
                video_data["auto_captions"] = list(meta.get("automatic_captions", {}).keys())
            
            # Get transcript if available
            if meta and meta.get("automatic_captions"):
                transcript = self.youtube_transcript(url)
                video_data["transcript"] = transcript[:5000] if transcript else None
            
            results["videos"].append(video_data)
        
        return results
    
    def research_web_topic(self, topic: str, max_sources: int = 10) -> Dict:
        """Full web research workflow"""
        search_results = self.web_search(topic, max_results=max_sources)
        results = {"topic": topic, "sources": []}
        
        if isinstance(search_results, list):
            for item in search_results[:max_sources]:
                url = item.get("url") or item.get("link") or item.get("href")
                if not url:
                    continue
                content = self.web_read(url)
                results["sources"].append({
                    "url": url,
                    "title": item.get("title", ""),
                    "content": content[:3000]
                })
        
        return results
    
    def fetch_rss_feeds(self, urls: List[str]) -> List[Dict]:
        """Fetch multiple RSS feeds"""
        results = []
        for url in urls:
            content = self.rss_fetch(url)
            results.append({"url": url, "content": content[:5000]})
        return results
    
    # === Integration with Tactical Buffer ===
    
    def import_youtube_to_tactical(self, topic: str, max_videos: List[Dict], 
                                    source: str = "youtube_research") -> int:
        """Import YouTube research results to Tactical Buffer"""
        from autonomy.tactical_buffer import TacticalBuffer
        tb = TacticalBuffer()
        
        count = 0
        for video in topic_videos:
            vid = video.get("id") or video.get("video_id") or ""
            if not vid:
                continue
            
            concepts = []
            if "concepts" in video:
                concepts = video["concepts"]
            elif "description" in video:
                # Extract concepts from description (simple keyword extraction)
                desc = video.get("description", "")
                concepts = self._extract_concepts(desc)
            
            tb.add(
                param=f"video_{video.get('id', '')}",
                value={
                    "video_id": video.get("id", ""),
                    "title": video.get("title", ""),
                    "concepts": concepts,
                    "source": source
                },
                source=source,
                context_tags={
                    "task_type": "video_research",
                    "video_id": video.get("id", ""),
                    "topic": video.get("title", "")
                }
            )
            count += 1
        
        return count
    
    def _extract_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Simple concept extraction from text"""
        # Simple keyword extraction - in production use LLM
        import re
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        from collections import Counter
        freq = Counter(words)
        # Filter common words
        stopwords = {"the", "and", "for", "with", "from", "this", "that", "have", "are", "not", "but", "you", "your", "can", "will", "use", "how", "what", "when", "why", "who", "where", "their", "there", "here", "then", "than", "also", "such", "more", "some", "very", "into", "only", "over", "after", "before", "under", "above", "between", "through", "during", "without", "within", "about", "these", "those", "each", "other", "such", "same", "many", "few", "most", "least", "must", "should", "could", "would", "might", "shall", "will", "need", "may", "can"}
        filtered = [(w, c) for w, c in freq.most_common(50) if w not in stopwords]
        return [w for w, c in filtered[:max_concepts]]


def test_external_import():
    """Quick test"""
    importer = ExternalImporter()
    
    # Test YouTube search
    print("Testing YouTube search...")
    videos = importer.youtube_search("faceless YouTube automation AI 2024", 3)
    print(json.dumps(videos, indent=2, ensure_ascii=False))
    
    # Test web search
    print("\nTesting web search...")
    results = importer.web_search("AI agent workflow automation 2024", 3)
    print(json.dumps(results, indent=2, ensure_ascii=False)[:1000])


if __name__ == "__main__":
    test_external_import()