#!/usr/bin/env python3
"""
Agent Reach integration for Hermes.
Provides internet access tools: YouTube, Twitter, GitHub, Reddit, RSS, web search, web read.
"""
import subprocess, json, os, sys
from pathlib import Path

class AgentReach:
    def __init__(self):
        self.home = Path.home() / ".agent-reach"
        self.venv = self.home / "venv"
        self.bin = self.venv / "bin" / "agent-reach" if os.name != "nt" else self.venv / "Scripts" / "agent-reach.exe"
        
    def install(self):
        """Install Agent Reach via pipx or venv"""
        if self.bin.exists():
            return True
        try:
            # Try pipx first
            subprocess.run(["pipx", "install", "https://github.com/Panniantong/agent-reach/archive/main.zip"], check=True, capture_output=True)
            return True
        except:
            # Fallback to venv
            self.venv.mkdir(parents=True, exist_ok=True)
            subprocess.run([sys.executable, "-m", "venv", str(self.venv)], check=True)
            pip = self.venv / "bin" / "pip" if os.name != "nt" else self.venv / "Scripts" / "pip.exe"
            subprocess.run([str(pip), "install", "https://github.com/Panniantong/agent-reach/archive/main.zip"], check=True)
            return True
    
    def doctor(self):
        """Run health check"""
        result = subprocess.run([str(self.bin), "doctor"], capture_output=True, text=True)
        return result.stdout, result.returncode == 0
    
    def youtube_transcript(self, url):
        """Get YouTube transcript via yt-dlp"""
        result = subprocess.run(
            ["yt-dlp", "--proxy", "socks5://127.0.0.1:10806", "--write-auto-subs", "--sub-langs", "en,ru", "--skip-download", "--print", "description", url],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout
    
    def youtube_search(self, query, max_results=5):
        """Search YouTube"""
        result = subprocess.run(
            ["yt-dlp", "--proxy", "socks5://127.0.0.1:10806", f"ytsearch{max_results}:{query}", "--print", "%(title)s|%(url)s|%(channel)s|%(view_count)s", "--flat-playlist"],
            capture_output=True, text=True, timeout=60
        )
        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    videos.append({"title": parts[0], "url": parts[1], "channel": parts[2], "views": parts[3]})
        return videos
    
    def web_search(self, query, max_results=10):
        """Search via Exa (via mcporter) or fallback to curl+Jina"""
        try:
            result = subprocess.run(["mcporter", "call", "exa.web_search_exa", json.dumps({"query": query, "max_results": max_results})], capture_output=True, text=True, timeout=30)
            return json.loads(result.stdout)
        except:
            # Fallback: Jina AI reader
            result = subprocess.run(["curl", "-s", f"https://r.jina.ai/http://cc.bingj.com/cache.aspx?d=503-3189-2229&w=5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a&u={query}"], capture_output=True, text=True, timeout=30)
            return result.stdout
    
    def web_read(self, url):
        """Read webpage via Jina AI"""
        result = subprocess.run(["curl", "-s", f"https://r.jina.ai/{url}"], capture_output=True, text=True, timeout=30)
        return result.stdout
    
    def github_read(self, repo, path=""):
        """Read GitHub repo/file"""
        url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
        return self.web_read(url)
    
    def rss_fetch(self, url):
        """Fetch RSS feed"""
        result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
        return result.stdout

# Quick test functions
def test_youtube_search():
    ar = AgentReach()
    videos = ar.youtube_search("faceless YouTube automation AI 2024", 3)
    print(json.dumps(videos, indent=2, ensure_ascii=False))

def test_web_read():
    ar = AgentReach()
    content = ar.web_read("https://github.com/Panniantong/Agent-Reach")
    print(content[:2000])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["install", "doctor", "youtube-search", "youtube-transcript", "web-search", "web-read", "github-read", "rss-fetch"])
    parser.add_argument("--query", "-q")
    parser.add_argument("--url", "-u")
    parser.add_argument("--repo", "-r")
    parser.add_argument("--max", "-m", type=int, default=5)
    args = parser.parse_args()
    
    ar = AgentReach()
    
    if args.command == "install":
        print("Installing..."); ar.install(); print("Done")
    elif args.command == "doctor":
        out, ok = ar.doctor(); print(out); sys.exit(0 if ok else 1)
    elif args.command == "youtube-search":
        print(json.dumps(ar.youtube_search(args.query, args.max), indent=2, ensure_ascii=False))
    elif args.command == "youtube-transcript":
        print(ar.youtube_transcript(args.url))
    elif args.command == "web-search":
        print(json.dumps(ar.web_search(args.query, args.max), indent=2, ensure_ascii=False))
    elif args.command == "web-read":
        print(ar.web_read(args.url))
    elif args.command == "github-read":
        print(ar.github_read(args.repo, args.url))
    elif args.command == "rss-fetch":
        print(ar.rss_fetch(args.url))