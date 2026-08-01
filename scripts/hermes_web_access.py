#!/usr/bin/env python3
"""
Hermes Web Access Tools - Agent Reach capability layer integration.
Provides: YouTube search/transcript, web search/read, GitHub read, RSS fetch.
Uses Agent Reach capability layer for backend auto-routing and health checks.
"""
import subprocess, json, sys, os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add scripts to path for Agent Reach integration
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from scripts.crystal.omh_integration import AgentReachIntegration
    AGENT_REACH_AVAILABLE = True
except ImportError:
    AGENT_REACH_AVAILABLE = False

PROXY = "socks5://127.0.0.1:10806"


class HermesWebAccess:
    """Web access tools for Hermes autonomous research via Agent Reach."""

    def __init__(self):
        self.reach = AgentReachIntegration() if AGENT_REACH_AVAILABLE else None

    def youtube_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search YouTube via Agent Reach (yt-dlp backend)."""
        if self.reach:
            return self.reach.youtube_search(query, max_results)

        # Fallback to direct yt-dlp
        try:
            result = subprocess.run([
                "yt-dlp", "--proxy", PROXY,
                f"ytsearch{max_results}:{query}",
                "--print", "%(title)s|%(url)s|%(channel)s|%(view_count)s|%(duration)s|%(upload_date)s",
                "--flat-playlist"
            ], capture_output=True, text=True, timeout=60)

            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line and line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        videos.append({
                            "title": parts[0],
                            "url": parts[1],
                            "channel": parts[2],
                            "views": int(parts[3]) if parts[3].isdigit() else 0,
                            "duration": parts[4] if len(parts) > 4 else "",
                            "upload_date": parts[5] if len(parts) > 5 else ""
                        })
            return videos
        except Exception as e:
            return [{"error": str(e)}]

    def youtube_transcript(self, url: str, langs: str = "en,ru") -> Dict[str, Any]:
        """Get YouTube video description and auto-generated subtitles via Agent Reach."""
        if self.reach:
            return self.reach.youtube_transcript(url, langs)

        # Fallback to direct yt-dlp
        try:
            desc_result = subprocess.run([
                "yt-dlp", "--proxy", PROXY, "--print", "description", url
            ], capture_output=True, text=True, timeout=60)

            sub_result = subprocess.run([
                "yt-dlp", "--proxy", PROXY,
                "--write-auto-subs", "--sub-langs", langs,
                "--skip-download", "--convert-subs", "srt",
                "-o", "-", url
            ], capture_output=True, text=True, timeout=60)

            return {
                "description": desc_result.stdout.strip(),
                "subtitles": sub_result.stdout.strip() if sub_result.stdout else "",
                "error": desc_result.stderr if desc_result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}

    def web_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search web via Exa (mcporter) - proxy-dependent backends skipped for speed."""
        # Try Exa via mcporter if available
        try:
            result = subprocess.run([
                "mcporter", "call", "exa.web_search_exa",
                json.dumps({"query": query, "max_results": max_results})
            ], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("results", [])
        except:
            pass

        # Proxy-dependent search backends are unreliable - return empty
        # Use web_read() + manual search instead
        return []

    def web_read(self, url: str) -> str:
        """Read webpage content via Jina AI reader (free, no API key). Uses proxy."""
        if self.reach:
            return self.reach.web_read(url)

        try:
            # Use proxy for Jina AI
            result = subprocess.run([
                "curl", "-s", "--max-time", "30", "--proxy", PROXY,
                f"https://r.jina.ai/{url}"
            ], capture_output=True, text=True, timeout=35)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"

    def github_read(self, repo: str, path: str = "") -> str:
        """Read file from GitHub raw."""
        url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
        return self.web_read(url)

    def github_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search GitHub via gh CLI."""
        if self.reach:
            return self.reach.github_search(query, limit)

        try:
            # Use correct field name: stargazersCount (plural)
            result = subprocess.run([
                "gh", "search", "repos", query, "--limit", str(limit),
                "--json", "name,description,url,stargazersCount"
            ], capture_output=True, text=True, timeout=20)
            # Handle field name change
            if result.returncode != 0 and "stargazersCount" in result.stderr:
                result = subprocess.run([
                    "gh", "search", "repos", query, "--limit", str(limit),
                    "--json", "name,description,url"
                ], capture_output=True, text=True, timeout=20)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return []

    def rss_fetch(self, url: str) -> List[Dict]:
        """Fetch RSS/Atom feed."""
        if self.reach:
            return self.reach.rss_fetch(url)

        import feedparser
        try:
            feed = feedparser.parse(url)
            return [{"title": e.title, "link": e.link, "summary": e.get("summary", "")} for e in feed.entries]
        except:
            return []


# Convenience functions for Crystal modules
def crystal_web_search(query: str, max_results: int = 10) -> List[Dict]:
    """Crystal-compatible web search using Agent Reach."""
    hwa = HermesWebAccess()
    return hwa.web_search(query, max_results)


def crystal_youtube_search(query: str, max_results: int = 5) -> List[Dict]:
    """Crystal-compatible YouTube search using Agent Reach."""
    hwa = HermesWebAccess()
    return hwa.youtube_search(query, max_results)


def crystal_youtube_transcript(url: str, langs: str = "en,ru") -> Dict:
    """Crystal-compatible YouTube transcript using Agent Reach."""
    hwa = HermesWebAccess()
    return hwa.youtube_transcript(url, langs)


def crystal_github_search(query: str, limit: int = 5) -> List[Dict]:
    """Crystal-compatible GitHub search using Agent Reach."""
    hwa = HermesWebAccess()
    return hwa.github_search(query, limit)


def crystal_web_read(url: str) -> str:
    """Crystal-compatible web read using Agent Reach."""
    hwa = HermesWebAccess()
    return hwa.web_read(url)


def crystal_rss_fetch(url: str) -> List[Dict]:
    """Crystal-compatible RSS fetch using Agent Reach."""
    hwa = HermesWebAccess()
    return hwa.rss_fetch(url)


# Initialize on import
_reach = None
if AGENT_REACH_AVAILABLE:
    try:
        from scripts.crystal.omh_integration import ensure_agent_reach
        ensure_agent_reach()
        print("🔮 HermesWebAccess: Agent Reach integration active")
    except:
        pass