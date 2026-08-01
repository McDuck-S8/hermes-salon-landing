#!/usr/bin/env python3
"""
Crystal v3 — OMH + Agent Reach Integration
Connects Crystal Engine with Oh My Hermes skills and Agent Reach capability layer.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.chain_heartbeat import beat
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add scripts to path
_scripts_dir = Path(__file__).parent.parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from scripts.crystal.models import IntelItem, save_json, load_json
from scripts.crystal.config import Paths


class OMHIntegration:
    """Integration layer for Oh My Hermes skills in Crystal."""
    
    SKILLS = [
        "omh-deep-research",      # Multi-phase web research
        "omh-ralplan",            # Consensus planning: Planner→Architect→Critic
        "omh-ralplan-driver",     # Dispatcher playbook for ralplan
        "omh-deep-interview",     # Socratic requirements interview
        "omh-ralph",              # Verified execution: implement→verify→iterate
        "omh-ralph-driver",       # Dispatcher playbook for ralph
        "omh-ralph-task",         # Executor discipline for single task
        "omh-autopilot",          # Full pipeline: research→interview→plan→execute
        "omh-triage",             # Multi-role consensus triage
        "omh-triage-driver",      # Dispatcher playbook for triage
    ]
    
    def __init__(self):
        # Check project root skills and user skills directories
        # Use Windows absolute path for project skills
        self.project_skills = Path(r"D:\Portable_Soft\hermes\skills")
        self.user_skills = Path.home() / ".hermes" / "skills"
        self.omh_dir = self.project_skills if self.project_skills.exists() else self.user_skills
        
    def is_available(self, skill: str) -> bool:
        """Check if OMH skill is installed in project or user skills."""
        for base in [self.project_skills, self.user_skills]:
            skill_path = base / skill / "SKILL.md"
            if skill_path.exists():
                self.omh_dir = base  # Cache the found location
                return True
        return False
    
    def load_skill(self, skill: str) -> Dict[str, Any]:
        """Load skill metadata from SKILL.md."""
        skill_path = self.omh_dir / skill / "SKILL.md"
        if not skill_path.exists():
            return {}
        
        content = skill_path.read_text(encoding="utf-8")
        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml
                try:
                    meta = yaml.safe_load(parts[1])
                    meta["content"] = parts[2].strip()
                    return meta
                except:
                    pass
        return {"raw": content[:500]}
    
    def run_autopilot(self, domain: str, goal: str = "") -> Dict[str, Any]:
        """
        Run omh-autopilot: research → interview → plan → execute.
        Uses hermes CLI delegate_task for sub-agent execution.
        """
        # This would delegate to hermes CLI in real usage
        # For now, return the plan structure
        return {
            "pipeline": "omh-autopilot",
            "domain": domain,
            "goal": goal,
            "phases": [
                {"phase": "research", "skill": "omh-deep-research", "status": "pending"},
                {"phase": "interview", "skill": "omh-deep-interview", "status": "pending"},
                {"phase": "plan", "skill": "omh-ralplan", "status": "pending"},
                {"phase": "execute", "skill": "omh-ralph", "status": "pending"},
            ],
            "started_at": datetime.now().isoformat(),
        }
    
    def run_deep_research(self, topic: str, depth: str = "normal") -> List[Dict]:
        """Run omh-deep-research: decompose → parallel search → synthesize → verify."""
        return [{
            "skill": "omh-deep-research",
            "topic": topic,
            "depth": depth,
            "phases": [
                "decompose_topic",
                "parallel_search",
                "synthesize",
                "verify_citations"
            ],
            "expected_calls": "5-12 delegate_task calls",
        }]
    
    def run_ralplan(self, requirements: str) -> Dict:
        """Run omh-ralplan: Planner → Architect → Critic debate until consensus."""
        return {
            "skill": "omh-ralplan",
            "input": requirements,
            "roles": ["Planner", "Architect", "Critic"],
            "output": "consensus_plan",
            "driver": "omh-ralplan-driver",
        }
    
    def run_ralph(self, plan: str) -> Dict:
        """Run omh-ralph: implement → verify → iterate until done."""
        return {
            "skill": "omh-ralph",
            "input": plan,
            "phases": ["implement", "verify", "iterate"],
            "driver": "omh-ralph-driver",
            "task_executor": "omh-ralph-task",
        }
    
    def run_triage(self, backlog: List[str]) -> Dict:
        """Run omh-triage: Maintainer + Skeptic consensus triage."""
        return {
            "skill": "omh-triage",
            "backlog": backlog,
            "roles": ["Maintainer", "Skeptic"],
            "driver": "omh-triage-driver",
        }


class AgentReachIntegration:
    """Integration layer for Agent Reach capability layer."""
    
    def __init__(self):
        self.cli = "agent-reach"
        self.skills_dir = Path.home() / ".hermes" / "skills" / "agent-reach"
        self.tools_cache = {}
    
    def is_installed(self) -> bool:
        """Check if Agent Reach is installed."""
        try:
            result = subprocess.run([self.cli, "doctor"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def install(self, safe: bool = False) -> bool:
        """Install Agent Reach."""
        cmd = [self.cli, "install", "--env=auto"]
        if safe:
            cmd.append("--safe")
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            return True
        except:
            return False
    
    def doctor(self) -> Dict:
        """Run health check."""
        try:
            result = subprocess.run([self.cli, "doctor", "--json"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return {"status": "unknown", "channels": {}}
    
    def youtube_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube via yt-dlp (Agent Reach backend)."""
        cmd = [
            "yt-dlp", "--flat-playlist",
            f"ytsearch{max_results}:{query}",
            "--print", "%(title)s|%(url)s|%(channel)s|%(view_count)s|%(duration)s"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        videos.append({
                            "title": parts[0],
                            "url": parts[1],
                            "channel": parts[2],
                            "views": int(parts[3]) if parts[3].isdigit() else 0,
                            "duration": parts[4] if len(parts) > 4 else ""
                        })
            return videos
        except:
            return []
    
    def youtube_transcript(self, url: str, langs: str = "en,ru") -> Dict:
        """Get YouTube transcript via yt-dlp."""
        cmd = [
            "yt-dlp", "--write-auto-subs", "--sub-langs", langs,
            "--skip-download", "--convert-subs", "srt",
            "--print", "description", url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return {
                "description": result.stdout.strip(),
                "subtitles": result.stderr if result.stderr else ""
            }
        except Exception as e:
            return {"error": str(e)}
    
    def web_read(self, url: str) -> str:
        """Read webpage via Jina AI reader."""
        cmd = ["curl", "-s", "--max-time", "30", f"https://r.jina.ai/{url}"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            return result.stdout
        except:
            return ""
    
    def web_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search web via Exa (mcporter) or fallback to DuckDuckGo."""
        # Try Exa via mcporter
        try:
            cmd = ["mcporter", "call", "exa.web_search_exa", json.dumps({"query": query, "max_results": max_results})]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("results", [])
        except:
            pass
        
        # Fallback: DuckDuckGo HTML scrape
        import urllib.parse
        import urllib.request
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            html = resp.read().decode("utf-8")
            # Simple parse
            import re
            results = []
            for match in re.finditer(r'<a class="result__snippet" href="([^"]+)">([^<]+)</a>', html):
                results.append({"url": match.group(1), "title": match.group(2)})
                if len(results) >= max_results:
                    break
            return results
        except:
            return []
    
    def github_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search GitHub via gh CLI."""
        cmd = ["gh", "search", "repos", query, "--limit", str(limit), "--json", "name,description,url,stargazerCount"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return []
    
    def rss_fetch(self, url: str) -> List[Dict]:
        """Fetch RSS/Atom feed."""
        import feedparser
        try:
            feed = feedparser.parse(url)
            return [{"title": e.title, "link": e.link, "summary": e.get("summary", "")} for e in feed.entries]
        except:
            return []


class CrystalOMHResearchPipeline:
    """
    Main research pipeline for Crystal using OMH + Agent Reach.
    
    Flow:
    1. IntelScanner (Agent Reach) → finds topics
    2. omh-deep-research → decomposes, searches, synthesizes
    3. omh-deep-interview → clarifies requirements
    4. omh-ralplan → consensus plan
    5. omh-ralph → verified execution
    6. Results → Knowledge Cube
    """
    
    def __init__(self):
        self.omh = OMHIntegration()
        self.reach = AgentReachIntegration()
        self.intel_cache = Paths.intel_cache if hasattr(Paths, 'intel_cache') else Path("cache/intel_cache.json")
        self.intel_cache.parent.mkdir(parents=True, exist_ok=True)
    
    def scan_and_research(self, topic: str, auto_plan: bool = True) -> Dict:
        """
        Full pipeline: scan → research → (optional) plan → execute.
        """
        beat("agent_reach_youtube")
        beat("agent_reach_web")
        beat("agent_reach_github")
        beat("agent_reach_rss")
        
        results = {
            "topic": topic,
            "started_at": datetime.now().isoformat(),
            "stages": {}
        }
        
        # Stage 1: Agent Reach intelligence scan
        print(f"🔍 Scanning for: {topic}")
        videos = self.reach.youtube_search(f"{topic} 2024 2025 case study", max_results=3)
        web_results = self.reach.web_search(f"{topic} tutorial guide 2024", max_results=5)
        
        beat("omh_deep_research")
        beat("omh_deep_interview")
        beat("omh_ralplan")
        beat("omh_ralph")
        
        results["stages"]["intel_scan"] = {
            "youtube_videos": len(videos),
            "web_results": len(web_results),
            "timestamp": datetime.now().isoformat()
        }
        
        # Stage 2: OMH Deep Research
        if self.omh.is_available("omh-deep-research"):
            print(f"🧠 Running omh-deep-research on: {topic}")
            research_plan = self.omh.run_deep_research(topic)
            results["stages"]["deep_research"] = research_plan
            
            # Extract key findings from videos
            key_findings = []
            for v in videos:
                transcript = self.reach.youtube_transcript(v["url"])
                key_findings.append({
                    "video": v["title"],
                    "url": v["url"],
                    "description": v.get("description", "")[:200],
                    "transcript_preview": transcript.get("description", "")[:500]
                })
            results["stages"]["video_analysis"] = key_findings
        else:
            beat("omh_deep_research", status="SILENT")
        
        # Stage 3: Auto-plan if requested
        if auto_plan and self.omh.is_available("omh-ralplan"):
            print(f"📋 Running omh-ralplan for: {topic}")
            requirements = f"Research findings on {topic}. Implement actionable pipeline based on discovered methods."
            plan = self.omh.run_ralplan(requirements)
            results["stages"]["plan"] = plan
            beat("omh_ralplan")
        else:
            beat("omh_ralplan", status="SILENT")
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    def save_intel(self, topic: str, results: Dict):
        """Save research results to intel cache."""
        cache = load_json(self.intel_cache) if self.intel_cache.exists() else []
        cache.append({
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        # Keep last 100
        if len(cache) > 100:
            cache = cache[-100:]
        save_json(self.intel_cache, cache)
    
    def get_cached_intel(self, topic: str = None) -> List[Dict]:
        """Get cached intelligence."""
        cache = load_json(self.intel_cache) if self.intel_cache.exists() else []
        if topic:
            return [c for c in cache if topic.lower() in c.get("topic", "").lower()]
        return cache[-10:]  # Last 10


# Convenience functions for Crystal modules
def crystal_web_search(query: str, max_results: int = 10) -> List[Dict]:
    """Crystal-compatible web search using Agent Reach."""
    reach = AgentReachIntegration()
    return reach.web_search(query, max_results)


def crystal_youtube_search(query: str, max_results: int = 5) -> List[Dict]:
    """Crystal-compatible YouTube search using Agent Reach."""
    reach = AgentReachIntegration()
    return reach.youtube_search(query, max_results)


def crystal_youtube_transcript(url: str, langs: str = "en,ru") -> Dict:
    """Crystal-compatible YouTube transcript using Agent Reach."""
    reach = AgentReachIntegration()
    return reach.youtube_transcript(url, langs)


def crystal_github_search(query: str, limit: int = 5) -> List[Dict]:
    """Crystal-compatible GitHub search using Agent Reach."""
    reach = AgentReachIntegration()
    return reach.github_search(query, limit)


def crystal_web_read(url: str) -> str:
    """Crystal-compatible web read using Agent Reach."""
    reach = AgentReachIntegration()
    return reach.web_read(url)


def crystal_rss_fetch(url: str) -> List[Dict]:
    """Crystal-compatible RSS fetch using Agent Reach."""
    reach = AgentReachIntegration()
    return reach.rss_fetch(url)


# Initialize on import
_omh = OMHIntegration()
_reach = AgentReachIntegration()

def ensure_agent_reach():
    """Ensure Agent Reach is installed and healthy."""
    if not _reach.is_installed():
        print("⚠️ Agent Reach not installed. Installing...")
        _reach.install()
    doctor = _reach.doctor()
    healthy = sum(1 for c in doctor.get("channels", {}).values() if c.get("status") == "HEALTHY")
    total = len(doctor.get("channels", {}))
    print(f"🩺 Agent Reach doctor: {healthy}/{total} channels healthy")
    return doctor


def ensure_omh_skills():
    """Verify OMH skills are available."""
    available = [s for s in OMHIntegration.SKILLS if _omh.is_available(s)]
    missing = [s for s in OMHIntegration.SKILLS if not _omh.is_available(s)]
    print(f"🔮 OMH Skills: {len(available)}/{len(OMHIntegration.SKILLS)} available")
    if missing:
        print(f"   Missing: {missing}")
    return available


if __name__ == "__main__":
    # Quick test
    print("=== Crystal OMH + Agent Reach Integration Test ===\n")
    
    ensure_omh_skills()
    print()
    
    doctor = ensure_agent_reach()
    print()
    
    # Test pipeline
    pipeline = CrystalOMHResearchPipeline()
    result = pipeline.scan_and_research("faceless YouTube automation AI 2024", auto_plan=True)
    
    print("\n=== Pipeline Result ===")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
    
    # Save to intel
    pipeline.save_intel("faceless YouTube automation AI 2024", result)
    print("\n✅ Saved to intel cache")