#!/usr/bin/env python3
"""
Skill Usage Analyzer — Analyzes why skills are not used and routes to action systems.
No reports. Direct action routing to Suggestion Applier, Crystal, Knowledge Cube, Proactive Doer.
"""

import os
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SKILLS_DIR = HERMES_HOME / "skills"
FEEDBACK_DB = HERMES_HOME / "cache" / "feedback_store.db"
KC_DB = HERMES_HOME / "cache" / "knowledge_cube.db"
SUGGESTIONS_DB = HERMES_HOME / "cache" / "improvement_suggestions.json"


@dataclass
class SkillUsageData:
    """Collected usage data for a skill."""
    skill_name: str
    skill_path: Path
    last_used: Optional[datetime]
    total_uses: int
    days_unused: int
    has_triggers: bool
    in_claude_md: bool
    in_agents_md: bool
    deps_ok: bool
    dep_issues: List[str]
    duplicates: List[str]
    has_examples: bool
    avg_execution_time: Optional[float]
    context_tags: List[str]


@dataclass
class AnalysisResult:
    """Analysis result with routed action."""
    skill_name: str
    days_unused: int
    root_cause: str
    severity: str  # critical, high, medium, low
    routed_to: str  # suggestion_applier, crystal, knowledge_cube, proactive_doer
    action_payload: Dict[str, Any]


class SkillUsageAnalyzer:
    """Analyzes skill usage and routes to action systems."""
    
    def __init__(self):
        self.skills_dir = SKILLS_DIR
        self.feedback_db = FEEDBACK_DB
        self.kc_db = KC_DB
        
    def collect_skill_data(self) -> List[SkillUsageData]:
        """Collect usage data for all skills."""
        skills = []
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            skill_name = skill_dir.name
            skill_data = self._analyze_skill(skill_dir, skill_name)
            if skill_data:
                skills.append(skill_data)
                
        return skills
    
    def _analyze_skill(self, skill_dir: Path, skill_name: str) -> Optional[SkillUsageData]:
        """Analyze a single skill's usage data."""
        skill_json = skill_dir / "skill.json"
        skill_md = skill_dir / "SKILL.md"
        
        # Load skill metadata
        metadata = {}
        if skill_json.exists():
            try:
                metadata = json.loads(skill_json.read_text(encoding="utf-8"))
            except:
                pass
        elif skill_md.exists():
            # Parse from SKILL.md frontmatter
            content = skill_md.read_text(encoding="utf-8")
            if content.startswith("---"):
                fm_end = content.find("\n---", 3)
                if fm_end > 0:
                    try:
                        import yaml
                        metadata = yaml.safe_load(content[3:fm_end])
                        if metadata:
                            metadata = {k.lower().replace("-", "_"): v for k, v in metadata.items()}
                    except:
                        pass
        
        # Get usage from feedback store
        usage_data = self._get_usage_from_feedback(skill_name)
        
        # Check triggers
        has_triggers = self._check_triggers(skill_dir, metadata)
        
        # Check presence in CLAUDE.md and AGENTS.md
        in_claude = self._check_in_file("CLAUDE.md", skill_name)
        in_agents = self._check_in_file(".claude/rules/always.md", skill_name) or \
                    self._check_in_file(".claude/rules/never.md", skill_name)
        
        # Check dependencies
        deps_ok, dep_issues = self._check_dependencies(skill_dir, metadata)
        
        # Check for duplication
        duplicates = self._find_duplicates(skill_name, metadata)
        
        # Check examples
        has_examples = self._check_examples(skill_dir)
        
        # Get execution time
        exec_time = self._get_avg_exec_time(skill_name)
        
        # Calculate days unused - consider skill "unused" if no feedback in last 14 days
        last_used = usage_data.get("last_used")
        now = datetime.now()
        if last_used:
            days_unused = (now - last_used).days
            # If last used > 14 days ago, consider it unused
            if days_unused > 14:
                days_unused = days_unused
            else:
                days_unused = 0  # Recently used
        else:
            # No record in feedback_store = never used / unused > 14 days
            days_unused = 999  # Mark as completely unused
            
        return SkillUsageData(
            skill_name=skill_name,
            skill_path=skill_dir,
            last_used=last_used,
            total_uses=usage_data.get("total_uses", 0),
            days_unused=days_unused,
            has_triggers=has_triggers,
            in_claude_md=in_claude,
            in_agents_md=in_agents,
            deps_ok=deps_ok,
            dep_issues=dep_issues,
            duplicates=duplicates,
            has_examples=has_examples,
            avg_execution_time=exec_time,
            context_tags=metadata.get("tags", [])
        )
    
    def _get_usage_from_feedback(self, skill_name: str) -> Dict:
        """Get usage data from feedback store."""
        if not self.feedback_db.exists():
            return {"total_uses": 0, "last_used": None}
            
        conn = sqlite3.connect(str(self.feedback_db), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute("""
                SELECT COUNT(*) as total, MAX(timestamp) as last_used
                FROM feedback WHERE skill = ?
            """, (skill_name,)).fetchone()
            if row:
                last_used = None
                if row["last_used"]:
                    try:
                        last_used = datetime.fromisoformat(row["last_used"])
                    except:
                        pass
                return {"total_uses": row["total"] or 0, "last_used": last_used}
        finally:
            conn.close()
        return {"total_uses": 0, "last_used": None}
    
    def _check_triggers(self, skill_dir: Path, metadata: Dict) -> bool:
        """Check if skill has triggers defined."""
        # Check SKILL.md for trigger field
        trigger = metadata.get("trigger", "") or metadata.get("triggers", "")
        if trigger:
            return True
            
        # Check for hooks directory
        hooks_dir = skill_dir / "hooks"
        if hooks_dir.exists() and any(hooks_dir.iterdir()):
            return True
            
        # Check SKILL.md content for trigger
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            if "trigger" in content.lower():
                return True
                
        return False
    
    def _check_in_file(self, filepath: str, skill_name: str) -> bool:
        """Check if skill is mentioned in a file."""
        fpath = Path(filepath)
        if not fpath.exists():
            return False
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        return skill_name.lower() in content.lower()
    
    def _check_dependencies(self, skill_dir: Path, metadata: Dict) -> tuple:
        """Check if skill dependencies are satisfied."""
        deps = metadata.get("dependencies", []) or metadata.get("requires", [])
        issues = []
        
        for dep in deps:
            if dep.startswith("pip:"):
                pkg = dep[4:]
                try:
                    __import__(pkg.replace("-", "_"))
                except ImportError:
                    issues.append(f"Missing pip dependency: {pkg}")
            elif dep.startswith("cmd:"):
                cmd = dep[4:]
                if not self._command_exists(cmd):
                    issues.append(f"Missing command: {cmd}")
            elif dep.startswith("skill:"):
                skill = dep[6:]
                if not (SKILLS_DIR / skill).exists():
                    issues.append(f"Missing skill dependency: {skill}")
                    
        return len(issues) == 0, issues
    
    def _command_exists(self, cmd: str) -> bool:
        try:
            subprocess.run(["which", cmd] if os.name != "nt" else ["where", cmd], 
                          capture_output=True, check=True)
            return True
        except:
            return False
    
    def _find_duplicates(self, skill_name: str, metadata: Dict) -> List[str]:
        """Find skills with similar functionality."""
        duplicates = []
        desc = metadata.get("description", "").lower()
        tags = metadata.get("tags", [])
        
        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir() or skill_dir.name == skill_name:
                continue
                
            other_md = skill_dir / "SKILL.md"
            if not other_md.exists():
                continue
                
            try:
                content = other_md.read_text(encoding="utf-8")
                if content.startswith("---"):
                    fm_end = content.find("\n---", 3)
                    if fm_end > 0:
                        import yaml
                        other_meta = yaml.safe_load(content[3:fm_end])
                        if other_meta:
                            other_desc = other_meta.get("description", "").lower()
                            other_tags = other_meta.get("tags", [])
                            
                            # Check tag overlap
                            tag_overlap = len(set(tags) & set(other_tags))
                            # Check description similarity (simple word overlap)
                            desc_words = set(desc.split())
                            other_words = set(other_desc.split())
                            desc_overlap = len(desc_words & other_words) / max(len(desc_words), 1)
                            
                            if tag_overlap >= 2 or desc_overlap > 0.5:
                                duplicates.append(skill_dir.name)
            except:
                pass
                
        return duplicates
    
    def _check_examples(self, skill_dir: Path) -> bool:
        """Check if skill has usage examples."""
        # Check for examples directory
        examples_dir = skill_dir / "examples"
        if examples_dir.exists() and any(examples_dir.iterdir()):
            return True
            
        # Check SKILL.md for examples section
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            if "example" in content.lower() or "usage" in content.lower():
                return True
                
        # Check for test files
        test_dir = skill_dir / "tests"
        if test_dir.exists() and any(test_dir.iterdir()):
            return True
            
        return False
    
    def _get_avg_exec_time(self, skill_name: str) -> Optional[float]:
        """Get average execution time from logs."""
        # Would need log parsing - placeholder
        return None
    
    def analyze_all_skills(self) -> List[AnalysisResult]:
        """Analyze all skills and return routed actions."""
        skills = self.collect_skill_data()
        results = []
        
        for skill in skills:
            if skill.days_unused < 14:
                continue  # Skip recently used skills
                
            result = self._analyze_root_cause(skill)
            if result:
                results.append(result)
                
        return results
    
    def _analyze_root_cause(self, skill: SkillUsageData) -> Optional[AnalysisResult]:
        """Determine root cause and route to appropriate system."""
        
        # Priority 1: Broken dependencies (Proactive Doer)
        if not skill.deps_ok and skill.dep_issues:
            return AnalysisResult(
                skill_name=skill.skill_name,
                days_unused=skill.days_unused,
                root_cause=f"Broken dependencies: {', '.join(skill.dep_issues)}",
                severity="critical",
                routed_to="proactive_doer",
                action_payload={
                    "action": "fix_dependencies",
                    "skill": skill.skill_name,
                    "issues": skill.dep_issues,
                    "skill_path": str(skill.skill_path)
                }
            )
        
        # Priority 2: No triggers (Suggestion Applier)
        if not skill.has_triggers:
            return AnalysisResult(
                skill_name=skill.skill_name,
                days_unused=skill.days_unused,
                root_cause="No triggers defined - skill never auto-activates",
                severity="high",
                routed_to="suggestion_applier",
                action_payload={
                    "action": "add_trigger",
                    "skill": skill.skill_name,
                    "trigger_type": "event_based",
                    "suggested_events": self._suggest_triggers(skill),
                    "skill_path": str(skill.skill_path)
                }
            )
        
        # Priority 3: Not in agent config (Suggestion Applier)
        if not skill.in_claude_md and not skill.in_agents_md:
            return AnalysisResult(
                skill_name=skill.skill_name,
                days_unused=skill.days_unused,
                root_cause="Skill not registered in CLAUDE.md or AGENTS.md - agent doesn't know it exists",
                severity="high",
                routed_to="suggestion_applier",
                action_payload={
                    "action": "register_skill",
                    "skill": skill.skill_name,
                    "skill_path": str(skill.skill_path),
                    "target_files": ["CLAUDE.md", ".claude/rules/always.md"]
                }
            )
        
        # Priority 4: Duplicates another skill (Crystal)
        if skill.duplicates:
            return AnalysisResult(
                skill_name=skill.skill_name,
                days_unused=skill.days_unused,
                root_cause=f"Duplicates functionality of: {', '.join(skill.duplicates)}",
                severity="medium",
                routed_to="crystal",
                action_payload={
                    "action": "resolve_duplication",
                    "skill": skill.skill_name,
                    "duplicates": skill.duplicates,
                    "recommendation": "merge" if len(skill.duplicates) == 1 else "consolidate"
                }
            )
        
        # Priority 5: No examples (Suggestion Applier)
        if not skill.has_examples:
            return AnalysisResult(
                skill_name=skill.skill_name,
                days_unused=skill.days_unused,
                root_cause="No usage examples - skill not discoverable/usable",
                severity="medium",
                routed_to="suggestion_applier",
                action_payload={
                    "action": "add_examples",
                    "skill": skill.skill_name,
                    "skill_path": str(skill.skill_path)
                }
            )
        
        # Priority 6: Task model shifted (Knowledge Cube)
        return AnalysisResult(
            skill_name=skill.skill_name,
            days_unused=skill.days_unused,
            root_cause="Skill not aligned with current task patterns",
            severity="low",
            routed_to="knowledge_cube",
            action_payload={
                "action": "reassess_relevance",
                "skill": skill.skill_name,
                "context_tags": skill.context_tags,
                "signal": "skill_unused_since_context_shift"
            }
        )
    
    def _suggest_triggers(self, skill: SkillUsageData) -> List[str]:
        """Suggest appropriate triggers based on skill context."""
        triggers = []
        tags = [t.lower() for t in skill.context_tags]
        
        if any(t in tags for t in ["pdf", "document", "ingestion"]):
            triggers.append("new_document_uploaded")
        if any(t in tags for t in ["monitor", "watch", "scan"]):
            triggers.append("file_changed")
        if any(t in tags for t in ["cron", "schedule", "periodic"]):
            triggers.append("schedule_fired")
        if any(t in tags for t in ["web", "scrape", "fetch"]):
            triggers.append("new_url_discovered")
        if any(t in tags for t in ["deploy", "build", "test"]):
            triggers.append("build_completed")
            
        return triggers or ["manual_trigger"]
    
    def execute_actions(self, results: List[AnalysisResult]) -> Dict[str, int]:
        """Execute routed actions. Returns count per system."""
        counts = defaultdict(int)
        
        for result in results:
            success = self._route_action(result)
            if success:
                counts[result.routed_to] += 1
                
        return dict(counts)
    
    def _route_action(self, result: AnalysisResult) -> bool:
        """Route action to appropriate system."""
        try:
            if result.routed_to == "suggestion_applier":
                return self._call_suggestion_applier(result)
            elif result.routed_to == "crystal":
                return self._call_crystal(result)
            elif result.routed_to == "knowledge_cube":
                return self._call_knowledge_cube(result)
            elif result.routed_to == "proactive_doer":
                return self._call_proactive_doer(result)
        except Exception as e:
            print(f"Failed to route {result.skill_name} to {result.routed_to}: {e}")
            return False
        return False
    
    def _call_suggestion_applier(self, result: AnalysisResult) -> bool:
        """Call Suggestion Applier to apply fix."""
        payload = {
            "source": "skill_usage_analyzer",
            "skill": result.skill_name,
            "action": result.action_payload.get("action"),
            "payload": result.action_payload
        }
        
        # Write to suggestion queue for Suggestion Applier to pick up
        queue_file = HERMES_HOME / "cache" / "suggestion_queue.json"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        queue = []
        if queue_file.exists():
            queue = json.loads(queue_file.read_text(encoding="utf-8"))
        
        queue.append({
            "timestamp": datetime.now().isoformat(),
            "priority": result.severity,
            "payload": payload
        })
        
        queue_file.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    
    def _call_crystal(self, result: AnalysisResult) -> bool:
        """Write task for Crystal to process."""
        task_file = HERMES_HOME / "cache" / "crystal_tasks.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        if task_file.exists():
            tasks = json.loads(task_file.read_text(encoding="utf-8"))
            
        tasks.append({
            "timestamp": datetime.now().isoformat(),
            "type": "skill_analysis",
            "skill": result.skill_name,
            "action": result.action_payload.get("action"),
            "payload": result.action_payload,
            "priority": result.severity
        })
        
        task_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    
    def _call_knowledge_cube(self, result: AnalysisResult) -> bool:
        """Write signal to Knowledge Cube."""
        if not KC_DB.exists():
            return False
            
        import hashlib
        content = f"Skill {result.skill_name} unused for {result.days_unused} days. Root cause: {result.root_cause}. Context tags: {', '.join(result.action_payload.get('context_tags', []))}. This indicates a shift in task patterns - the skill is no longer relevant to current workflows."
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
        conn = sqlite3.connect(str(KC_DB), timeout=5)
        try:
            conn.execute("""
                INSERT INTO experiences (raw_text, content, hash, axis_domain, axis_outcome, tags, source, ts, is_white_spot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                content,
                content,
                content_hash,
                "skill_analysis",
                "context_shift",
                json.dumps(["skill_unused", "context_shift", "relevance_check"]),
                "skill_usage_analyzer",
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"KC write failed: {e}")
            return False
        finally:
            conn.close()
    
    def _call_proactive_doer(self, result: AnalysisResult) -> bool:
        """Write task for Proactive Doer to fix dependencies."""
        task_file = HERMES_HOME / "cache" / "proactive_doer_tasks.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        
        tasks = []
        if task_file.exists():
            tasks = json.loads(task_file.read_text(encoding="utf-8"))
            
        tasks.append({
            "timestamp": datetime.now().isoformat(),
            "type": "fix_skill_dependencies",
            "skill": result.skill_name,
            "issues": result.action_payload.get("issues", []),
            "skill_path": result.action_payload.get("skill_path"),
            "priority": result.severity
        })
        
        task_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Usage Analyzer - Routes to action systems")
    parser.add_argument("--analyze", action="store_true", help="Analyze all skills")
    parser.add_argument("--execute", action="store_true", help="Execute routed actions")
    parser.add_argument("--skill", help="Analyze specific skill")
    parser.add_argument("--threshold", type=int, default=14, help="Days unused threshold")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    analyzer = SkillUsageAnalyzer()
    
    if args.analyze:
        results = analyzer.analyze_all_skills()
        if args.json:
            print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2, default=str))
        else:
            for r in results:
                print(f"[{r.severity.upper()}] {r.skill_name} ({r.days_unused}d) -> {r.routed_to}: {r.root_cause}")
        
    if args.execute:
        results = analyzer.analyze_all_skills()
        counts = analyzer.execute_actions(results)
        print(f"Executed actions: {counts}")


if __name__ == "__main__":
    main()