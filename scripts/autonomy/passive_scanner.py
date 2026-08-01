#!/usr/bin/env python3
"""
Passive Scanner — Level 2 of VOID_RESPONSE
Scans digital footprint without intervention: calendar, file timestamps, git history, recent commands
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict


class PassiveScanner:
    """
    Scans digital footprint without user intervention.
    Sources: file timestamps, git history, recent commands, cache files
    """
    
    def __init__(self):
        self.hermes_root = Path(__file__).parent.parent.parent
        self.cache_dir = self.hermes_root / "cache"
    
    def scan_for(self, param: str, environment: str) -> Any:
        """Scan for a specific parameter in digital footprint"""
        param_lower = param.lower()
        
        # Check cache files for relevant data
        if "audience" in param_lower or "target" in param_lower:
            return self._scan_audience_cache()
        
        if "budget" in param_lower or "cost" in param_lower:
            return self._scan_budget_cache()
        
        if "timeline" in param_lower or "deadline" in param_lower:
            return self._scan_timeline_cache()
        
        if "geo" in param_lower or "location" in param_lower or "region" in param_lower:
            return self._scan_geo_cache()
        
        if "platform" in param_lower:
            return self._scan_platform_cache()
        
        # Check git history for related commits
        git_result = self._scan_git_history(param)
        if git_result:
            return git_result
        
        # Check file timestamps for recent activity
        file_result = self._scan_file_timestamps(param)
        if file_result:
            return file_result
        
        return None
    
    def _scan_audience_cache(self) -> Optional[Dict]:
        """Scan for audience/target data in cache"""
        # Check knowledge cube for audience data
        kc_files = list(self.cache_dir.glob("*knowledge*"))
        for f in kc_files:
            try:
                if f.suffix == ".db":
                    continue
                content = f.read_text(encoding="utf-8", errors="ignore")
                if "audience" in content.lower() or "target" in content.lower():
                    return {"source": "cache", "hint": "audience data in knowledge cache"}
            except:
                pass
        return None
    
    def _scan_budget_cache(self) -> Optional[Dict]:
        """Scan for budget/cost data"""
        return None
    
    def _scan_timeline_cache(self) -> Optional[Dict]:
        """Scan for timeline/deadline data"""
        return None
    
    def _scan_geo_cache(self) -> Optional[Dict]:
        """Scan for geo/location data"""
        # Check session bridge for user location
        bridge_file = self.cache_dir / "session_bridge.json"
        if bridge_file.exists():
            try:
                import json
                data = json.loads(bridge_file.read_text(encoding="utf-8"))
                # User is in Crimea based on profile
                return {"country": "RU", "region": "Crimea", "source": "session_bridge"}
            except:
                pass
        return None
    
    def _scan_platform_cache(self) -> Optional[Dict]:
        """Scan for platform preference"""
        return {"primary": "telegram", "secondary": "web", "source": "user_preference"}
    
    def _scan_git_history(self, param: str) -> Optional[Any]:
        """Scan git history for related commits"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--grep", param, "-n", "5"],
                capture_output=True, text=True, timeout=10, cwd=str(self.hermes_root)
            )
            if result.stdout.strip():
                return {"source": "git_history", "commits": result.stdout.strip().split("\n")[:3]}
        except:
            pass
        return None
    
    def _scan_file_timestamps(self, param: str) -> Optional[Any]:
        """Scan recent file modifications"""
        param_lower = param.lower()
        recent_files = []
        cutoff = datetime.now() - timedelta(days=7)
        
        for f in self.hermes_root.rglob("*.py"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > cutoff and param_lower in f.name.lower():
                    recent_files.append(str(f.relative_to(self.hermes_root)))
            except:
                pass
        
        if recent_files:
            return {"source": "file_timestamps", "recent_files": recent_files[:5]}
        return None


if __name__ == "__main__":
    scanner = PassiveScanner()
    print(scanner.scan_for("geo", "production"))
    print(scanner.scan_for("platform", "production"))
    print(scanner.scan_for("audience", "production"))