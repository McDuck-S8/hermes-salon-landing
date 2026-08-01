#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Pathfinder --- Поисковик Пути.
Самоориентация в пространстве навыков: граф зависимостей, оценка уровней, точка входа, маршрут обучения.
Протокол 3 шагов: Research → Select/Synthesize → Execute.
"""

import argparse
import sys
import yaml
import json
import subprocess
import re
import asyncio
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
import sqlite3

# Add skills to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR))

try:
    import networkx as nx
except ImportError:
    nx = None
    print("Warning: networkx not installed. Graph features limited.", file=sys.stderr)


@dataclass
class SkillInfo:
    """Information about a skill."""
    name: str
    path: Path
    category: str
    description: str
    version: str
    tags: List[str]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    level: int = 0
    demand: int = 0
    artifacts: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None
    usage_count: int = 0
    error_count: int = 0
    has_tests: bool = False
    test_coverage: float = 0.0


@dataclass
class GapAnalysis:
    """Analysis of a skill gap."""
    skill_name: str
    current_level: int
    demand: int
    gap_score: float
    missing_artifacts: List[str]
    missing_tests: List[str]
    dependency_gaps: List[str]


@dataclass
class ResearchResult:
    """Result of best-practices research (Step 1)."""
    skill_name: str
    examples: List[Dict]
    selected_approach: str
    selected_sources: List[str]
    synthesis_notes: str
    decision_rationale: str


@dataclass
class RouteStep:
    """One step in the learning route."""
    skill_name: str
    reason: str
    prerequisite_skills: List[str]
    estimated_effort: str
    research_required: bool


class SkillInventory:
    """Scans and catalogs all skills."""

    def __init__(self, skills_root: Path):
        self.skills_root = skills_root
        self.knowledge_cube_db = skills_root.parent.parent / "cache" / "knowledge_cube.db"

    def scan_all_skills(self) -> Dict[str, SkillInfo]:
        """Scan skills/ directory and build inventory."""
        skills = {}

        for skill_dir in self.skills_root.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            skill_info = self._parse_skill_md(skill_md, skill_dir)
            if skill_info:
                skills[skill_info.name] = skill_info

        # Enrich with runtime data
        self._enrich_with_runtime_data(skills)
        self._enrich_with_git_history(skills)
        self._enrich_with_knowledge_cube(skills)

        return skills

    def _parse_skill_md(self, skill_md: Path, skill_dir: Path) -> Optional[SkillInfo]:
        """Parse SKILL.md frontmatter - handles various YAML formats."""
        try:
            content = skill_md.read_text(encoding='utf-8')

            # Extract frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1]
                    # Try to parse directly first
                    try:
                        frontmatter = yaml.safe_load(frontmatter_text)
                    except yaml.YAMLError:
                        # Fix common issues and retry
                        frontmatter_text = self._fix_yaml_issues(frontmatter_text)
                        try:
                            frontmatter = yaml.safe_load(frontmatter_text)
                        except yaml.YAMLError:
                            return None
                else:
                    frontmatter = {}
            else:
                frontmatter = {}

            name = frontmatter.get('name', skill_dir.name)
            category = frontmatter.get('category', 'uncategorized')
            description = frontmatter.get('description', '')
            version = frontmatter.get('version', '1.0.0')
            tags = frontmatter.get('tags', [])
            deps = frontmatter.get('dependencies', {})

            # Find artifacts (scripts, templates, etc.)
            artifacts = []
            for pattern in ['scripts/**/*.py', 'scripts/**/*.sh', 'templates/**/*', 'references/**/*']:
                artifacts.extend([str(p.relative_to(skill_dir)) for p in skill_dir.glob(pattern)])

            return SkillInfo(
                name=name,
                path=skill_dir,
                category=category,
                description=description,
                version=version,
                tags=tags,
                dependencies=deps,
                artifacts=artifacts
            )
        except Exception as e:
            print(f"  Skipping {skill_md}: {e}", file=sys.stderr)
            return None

    def _fix_yaml_issues(self, text: str) -> str:
        """Fix common YAML parsing issues."""
        # Fix unquoted colons in values (description: text with : colon)
        text = re.sub(r'^(\s*\w+:\s*)(.+:\s*.+)$', r'\1"\2"', text, flags=re.MULTILINE)
        # Fix description with | or >-
        text = re.sub(r'^(\s*description:\s*)[\|>\-].*$', r'\1 ""', text, flags=re.MULTILINE)
        # Fix unquoted strings with colons anywhere
        text = re.sub(r'^(\s*\w+:\s*)([^"]*:\s*[^"]*)$', r'\1"\2"', text, flags=re.MULTILINE)
        return text

    def _enrich_with_runtime_data(self, skills: Dict[str, SkillInfo]):
        """Add usage/error counts from cron/logs."""
        cron_file = self.skills_root.parent.parent / "cron" / "jobs.json"
        if cron_file.exists():
            try:
                with open(cron_file) as f:
                    cron_jobs = json.load(f)
                for job in cron_jobs.get('jobs', []):
                    for skill in job.get('skills', []):
                        if skill in skills:
                            skills[skill].usage_count += job.get('run_count', 0)
            except Exception:
                pass

        logs_dir = self.skills_root.parent.parent / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                try:
                    content = log_file.read_text(encoding='utf-8', errors='ignore')
                    for skill_name in skills:
                        if skill_name in content.lower():
                            skills[skill_name].error_count += content.lower().count('error')
                            skills[skill_name].error_count += content.lower().count('traceback')
                except Exception:
                    pass

    def _enrich_with_git_history(self, skills: Dict[str, SkillInfo]):
        """Add last_updated from git log - DISABLED for performance."""
        pass

    def _enrich_with_knowledge_cube(self, skills: Dict[str, SkillInfo]):
        """Add demand signals from Knowledge Cube - DISABLED for performance."""
        pass


class SkillGraph:
    """Builds and analyzes skill dependency graph."""

    def __init__(self, skills: Dict[str, SkillInfo]):
        self.skills = skills
        self.graph = nx.DiGraph() if nx else None
        self._build_graph()

    def _build_graph(self):
        if not self.graph:
            return

        for name, skill in self.skills.items():
            self.graph.add_node(name, **asdict(skill))

        for name, skill in self.skills.items():
            for dep_type, deps in skill.dependencies.items():
                for dep in deps:
                    if dep in self.skills:
                        if dep_type == 'requires':
                            self.graph.add_edge(dep, name, type='requires', weight=1.0)
                        elif dep_type == 'enhances':
                            self.graph.add_edge(dep, name, type='enhances', weight=0.5)
                        elif dep_type == 'conflicts':
                            self.graph.add_edge(name, dep, type='conflicts', weight=-1.0)
                        elif dep_type == 'subsumes':
                            self.graph.add_edge(name, dep, type='subsumes', weight=0.0)

        self._infer_implicit_dependencies()

    def _infer_implicit_dependencies(self):
        skill_list = list(self.skills.values())
        for i, skill_a in enumerate(skill_list):
            for skill_b in skill_list[i+1:]:
                common_tags = set(skill_a.tags) & set(skill_b.tags)
                if skill_a.category == skill_b.category and len(common_tags) >= 2:
                    if not self.graph.has_edge(skill_a.name, skill_b.name):
                        self.graph.add_edge(skill_a.name, skill_b.name, type='enhances', weight=0.3)

    def get_dependencies(self, skill_name: str) -> Dict[str, List[str]]:
        if not self.graph or skill_name not in self.graph:
            return {'requires': [], 'enhances': [], 'conflicts': [], 'subsumes': []}

        result = {'requires': [], 'enhances': [], 'conflicts': [], 'subsumes': []}

        for pred in self.graph.predecessors(skill_name):
            edge_data = self.graph[pred][skill_name]
            dep_type = edge_data.get('type', 'enhances')
            if dep_type in result:
                result[dep_type].append(pred)

        for succ in self.graph.successors(skill_name):
            edge_data = self.graph[skill_name][succ]
            dep_type = edge_data.get('type', 'enhances')
            if dep_type == 'requires':
                result.setdefault('required_by', []).append(succ)

        return result

    def topological_order(self) -> List[str]:
        if not self.graph:
            return list(self.skills.keys())

        try:
            req_graph = nx.DiGraph()
            req_graph.add_nodes_from(self.graph.nodes())
            for u, v, data in self.graph.edges(data=True):
                if data.get('type') == 'requires':
                    req_graph.add_edge(u, v)
            return list(nx.topological_sort(req_graph))
        except Exception:
            return list(self.skills.keys())

    def find_strongly_connected(self) -> List[List[str]]:
        if not self.graph:
            return []
        try:
            return [list(c) for c in nx.strongly_connected_components(self.graph) if len(c) > 1]
        except Exception:
            return []


class SkillAssessor:
    """Assesses skill levels (0-100)."""

    def __init__(self, skills: Dict[str, SkillInfo]):
        self.skills = skills

    def assess_all(self) -> Dict[str, int]:
        levels = {}
        for name, skill in self.skills.items():
            levels[name] = self._assess_skill(skill)
            skill.level = levels[name]
        return levels

    def _assess_skill(self, skill: SkillInfo) -> int:
        score = 0

        # Artifacts (30%)
        score += min(30, len(skill.artifacts) * 3)

        # Tests (20%)
        test_score = 0
        scripts_dir = skill.path / "scripts"
        if scripts_dir.exists():
            test_files = list(scripts_dir.glob("**/test*.py")) + list(scripts_dir.glob("**/*_test.py"))
            if test_files:
                test_score = 10
                for tf in test_files[:3]:
                    try:
                        result = subprocess.run(
                            [sys.executable, '-m', 'py_compile', str(tf)],
                            capture_output=True, timeout=10
                        )
                        if result.returncode == 0:
                            test_score += 3
                    except Exception:
                        pass
        score += min(20, test_score)

        # Usage (20%)
        score += min(20, skill.usage_count // 5)

        # Freshness (15%)
        freshness = 15
        if skill.last_updated:
            try:
                last = datetime.fromisoformat(skill.last_updated.replace('Z', '+00:00'))
                days = (datetime.now() - last.replace(tzinfo=None)).days
                if days > 90:
                    freshness = max(0, 15 - days // 30)
            except Exception:
                pass
        score += freshness

        # Completeness (15%)
        complete = 15
        if skill.description and len(skill.artifacts) == 0:
            complete = 5
        elif 'create' in skill.description.lower() and not any('create' in a for a in skill.artifacts):
            complete = 10
        score += complete

        return min(100, max(0, score))

    def get_gaps(self, skill: SkillInfo) -> Tuple[List[str], List[str], List[str]]:
        missing_artifacts = []
        missing_tests = []

        scripts_dir = skill.path / "scripts"
        if scripts_dir.exists():
            py_files = list(scripts_dir.glob("**/*.py"))
            test_files = [f for f in py_files if 'test' in f.name.lower()]
            if py_files and not test_files:
                missing_tests.append("No test files found")

        desc = skill.description.lower()
        if 'cli' in desc or 'command' in desc:
            if not any('cli' in a or 'main' in a or '__main__' in a for a in skill.artifacts):
                missing_artifacts.append("CLI entry point")

        if 'api' in desc or 'server' in desc:
            if not any('api' in a or 'server' in a or 'app' in a for a in skill.artifacts):
                missing_artifacts.append("API/Server implementation")

        return missing_artifacts, missing_tests, []


class DemandEstimator:
    """Estimates demand for each skill (0-100)."""

    def __init__(self, skills: Dict[str, SkillInfo]):
        self.skills = skills
        self.sessions_db = SKILLS_DIR.parent / "sessions" / "hermes.db"

    def estimate_all(self) -> Dict[str, int]:
        demands = {}
        for name, skill in self.skills.items():
            demands[name] = self._estimate_demand(skill)
            skill.demand = demands[name]
        return demands

    def _estimate_demand(self, skill: SkillInfo) -> int:
        score = 0

        # User requests (35%) - disabled
        # score += min(35, self._count_user_requests(skill.name) * 5)

        # Error patterns (25%)
        score += min(25, skill.error_count // 2)

        # Cron frequency (20%)
        score += min(20, skill.usage_count // 3)

        # Cross-skill refs (20%)
        score += min(20, self._count_cross_refs(skill.name) * 3)

        # Category boost for this user's high-value domains
        high_value_categories = {
            'finance': 30,
            'arbitrage': 30,
            'autonomous-income': 30,
            'automation': 25,
            'devops': 20,
            'cpa-affiliate': 25,
        }
        score += high_value_categories.get(skill.category, 0)

        # Tag-based boost for known important topics
        important_tags = ['cpa', 'arbitrage', 'betting', 'cricket', 'india', 'pwa', 'telegram', 
                          'bot', 'shorts', 'tiktok', 'p2p', 'usdt', 'crypto', 'offramp', 
                          'crimea', 'job', 'hh', 'content', 'pipeline']
        tag_boost = sum(5 for tag in skill.tags if any(it in tag.lower() for it in important_tags))
        score += min(20, tag_boost)

        return min(100, max(0, score))

    def _count_user_requests(self, skill_name: str) -> int:
        """Count user requests mentioning this skill - DISABLED for performance."""
        return 0

    def _count_cross_refs(self, skill_name: str) -> int:
        count = 0
        for skill in self.skills.values():
            deps = skill.dependencies
            if isinstance(deps, dict):
                for dep_list in deps.values():
                    if skill_name in dep_list:
                        count += 1
            elif isinstance(deps, list):
                if skill_name in deps:
                    count += 1
        return count


class HumanSourceIntegrator:
    """Integrates with human-source to get personal values, underwater rocks, and keys."""

    def __init__(self, human_source_path: Optional[Path] = None):
        self.human_source_path = human_source_path or SKILLS_DIR / "human-source"
        self.values_map = {}
        self.underwater_rocks = []
        self.personal_keys = []
        self._load_human_source()

    def _load_human_source(self):
        """Load human-source data from reports and config."""
        # Try to load from human-source report
        report_path = SKILLS_DIR.parent / "reports" / "human_source_report_final.md"
        if report_path.exists():
            self._parse_report(report_path)

        # Also try to load from analyze.py if available
        try:
            sys.path.insert(0, str(self.human_source_path / "scripts"))
            from analyze import HumanAnalyzer
            config = {
                'analysis': {'dimensions': {'frustrations': 0.3, 'sins': 0.2, 'norms': 0.2, 'strengths': 0.15, 'context': 0.15}},
                'ripple_engine': {'max_depth': 3, 'conflict_threshold': 0.7, 'stop_on_conflict': True},
            }
            analyzer = HumanAnalyzer(config)
            self.values_map = analyzer.values_map if hasattr(analyzer, 'values_map') else {}
            self.underwater_rocks = self._extract_underwater_rocks(analyzer)
        except Exception as e:
            print(f"Warning: Could not load human-source analyzer: {e}", file=sys.stderr)

    def _extract_underwater_rocks(self, analyzer) -> List[str]:
        """Extract underwater rocks (hard constraints) from human-source analyzer."""
        return [
            "No KYC / No Documents",
            "Crimea constraints",
            "Stdlib-first / No new abstractions",
            "Clickable artifacts only",
            "No Google Gemini / No Playwright",
        ]

    def _parse_report(self, report_path: Path):
        """Parse human-source report for values and keys."""
        try:
            content = report_path.read_text(encoding='utf-8')
            # Extract keys, values, rocks from report
            pass
        except Exception:
            pass

    def get_personal_importance(self, skill_name: str, skill: 'SkillInfo') -> int:
        """Calculate personal importance (0-100) based on human-source values."""
        score = 0

        # Check if skill aligns with personal keys
        personal_keywords = [
            "crimea", "simferopol", "job", "hh.ru", "work",
            "p2p", "usdt", "rub", "offramp", "crypto",
            "shorts", "tiktok", "content", "pipeline",
            "arbitrage", "matrix", "betting", "cricket",
            "autonomous", "cron", "daemon", "self-heal",
            "telegram", "bot", "channel",
        ]

        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()
        matches = sum(1 for kw in personal_keywords if kw in skill_text)
        score += min(40, matches * 5)

        # Check category alignment
        personal_categories = ['finance', 'arbitrage', 'autonomous-income', 'automation', 'devops']
        if skill.category in personal_categories:
            score += 20

        # Check if skill conflicts with underwater rocks
        if self._conflicts_with_rocks(skill):
            score -= 30  # Penalty for conflicts

        # Check if skill relates to personal keys (from human-source)
        if hasattr(self, 'personal_keys'):
            for key in self.personal_keys:
                if any(kw in skill_text for kw in key.lower().split()):
                    score += 10

        return max(0, min(100, score))

    def _conflicts_with_rocks(self, skill: 'SkillInfo') -> bool:
        """Check if skill conflicts with underwater rocks."""
        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()
        conflict_keywords = {
            "kyc": "No KYC / No Documents",
            "passport": "No KYC / No Documents",
            "document": "No KYC / No Documents",
            "verification": "No KYC / No Documents",
            "playwright": "No Google Gemini / No Playwright",
            "gemini": "No Google Gemini / No Playwright",
            "chrome": "No Google Gemini / No Playwright",
        }
        for kw, rock in conflict_keywords.items():
            if kw in skill_text:
                return True
        return False

    def get_risk_boundary(self, skill: 'SkillInfo') -> str:
        """Get risk boundary for skill: 'free' | 'needs_approval' | 'blocked'."""
        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()

        # Blocked: conflicts with hard constraints
        if self._conflicts_with_rocks(skill):
            return "blocked"

        # Needs approval: requires budget, external API, legal risk
        approval_keywords = ["budget", "paid api", "subscription", "legal", "compliance", "kyc"]
        if any(kw in skill_text for kw in approval_keywords):
            return "needs_approval"

        # Free: everything else
        return "free"


class AudienceRelevanceCalculator:
    """Calculates audience/market relevance using audience-analyzer."""

    def __init__(self, audience_analyzer_path: Optional[Path] = None):
        self.audience_analyzer_path = audience_analyzer_path or SKILLS_DIR / "audience-analyzer"
        self.audience_skills = {}
        self._load_audience_skills()

    def _load_audience_skills(self):
        """Load audience-analyzer to understand what skills are needed for audiences."""
        self.audience_skill_map = {
            # Audience type -> required skills
            "arbitrage": ["arbitrage-execution", "finance-core", "arbitrage-sensors", "matrix-thinking"],
            "betting": ["pwa-betting", "creative-production", "anti-fraud", "cloaking"],
            "crypto": ["p2p-offramp", "usdt-rub", "defi", "wallet-security"],
            "content": ["content-pipeline", "shorts-production", "tiktok-automation", "youtube-seo"],
            "telegram": ["telegram-bot-integration", "telegram-channel-poster", "tg-mini-app"],
            "job-search": ["crimea-job-search", "hh-ru-parser", "cv-optimizer"],
            "affiliate": ["cpa-affiliate-bot", "offer-scanner", "landing-generator"],
        }

    def get_audience_relevance(self, skill_name: str, skill: 'SkillInfo', 
                                current_audience: Optional[str] = None) -> int:
        """Calculate audience relevance (0-100)."""
        score = 0

        # If we know the current audience, check direct mapping
        if current_audience and current_audience in self.audience_skill_map:
            if skill_name in self.audience_skill_map[current_audience]:
                score += 50

        # Check category alignment with high-value audiences
        high_value_categories = {
            'finance': 30,
            'arbitrage': 30,
            'autonomous-income': 25,
            'automation': 20,
            'cpa-affiliate': 25,
        }
        if skill.category in high_value_categories:
            score += high_value_categories[skill.category]

        # Check tags for audience-relevant keywords
        audience_keywords = [
            "cpa", "offer", "traffic", "conversion", "landing",
            "pwa", "betting", "cricket", "india",
            "telegram", "bot", "mini-app", "channel",
            "shorts", "tiktok", "reels", "viral",
            "p2p", "offramp", "usdt", "crypto",
            "hh.ru", "job", "vacancy", "resume",
        ]
        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()
        matches = sum(1 for kw in audience_keywords if kw in skill_text)
        score += min(30, matches * 3)

        return min(100, max(0, score))


class SkillArtifactMap:
    """Tracks created artifacts for each skill to prevent reinventing wheels."""

    def __init__(self, skills_root: Path):
        self.skills_root = skills_root
        self.artifacts = {}  # skill_name -> List[ArtifactInfo]
        self._build_artifact_map()

    def _build_artifact_map(self):
        """Scan all skills for their artifacts and test results."""
        for skill_dir in self.skills_root.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue

            skill_name = skill_dir.name
            artifacts = []

            # Check scripts
            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                for script in scripts_dir.glob("**/*.py"):
                    rel = script.relative_to(skill_dir)
                    # Check if it has tests passing
                    test_result = self._check_test_status(script)
                    artifacts.append({
                        "name": rel.name,
                        "path": str(rel),
                        "type": "script",
                        "tested": test_result,
                        "size": script.stat().st_size,
                    })

            # Check reports
            reports_dir = SKILLS_DIR.parent / "reports"
            if reports_dir.exists():
                for report in reports_dir.glob(f"*{skill_name}*"):
                    artifacts.append({
                        "name": report.name,
                        "path": str(report.relative_to(SKILLS_DIR.parent)),
                        "type": "report",
                        "tested": True,
                        "size": report.stat().st_size,
                    })

            # Check templates
            templates_dir = skill_dir / "templates"
            if templates_dir.exists():
                for tmpl in templates_dir.glob("**/*"):
                    if tmpl.is_file():
                        rel = tmpl.relative_to(skill_dir)
                        artifacts.append({
                            "name": rel.name,
                            "path": str(rel),
                            "type": "template",
                            "tested": False,
                            "size": tmpl.stat().st_size,
                        })

            if artifacts:
                self.artifacts[skill_name] = artifacts

    def _check_test_status(self, script_path: Path) -> bool:
        """Check if a script has passing tests."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(script_path)],
                capture_output=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_artifact_summary(self, skill_name: str) -> str:
        """Get a human-readable summary of artifacts for a skill."""
        artifacts = self.artifacts.get(skill_name, [])
        if not artifacts:
            return "No artifacts found"

        scripts = [a for a in artifacts if a['type'] == 'script']
        reports = [a for a in artifacts if a['type'] == 'report']
        templates = [a for a in artifacts if a['type'] == 'template']

        parts = []
        if scripts:
            tested = sum(1 for s in scripts if s['tested'])
            parts.append(f"{len(scripts)} scripts ({tested} tested)")
        if reports:
            parts.append(f"{len(reports)} reports")
        if templates:
            parts.append(f"{len(templates)} templates")

        return "; ".join(parts)

    def has_working_implementation(self, skill_name: str) -> bool:
        """Check if skill has a working, tested implementation."""
        artifacts = self.artifacts.get(skill_name, [])
        scripts = [a for a in artifacts if a['type'] == 'script' and a['tested']]
        return len(scripts) > 0


class HumanSourceIntegrator:
    """Integrates with human-source to get personal values, underwater rocks, and keys."""

    def __init__(self, human_source_path: Optional[Path] = None):
        self.human_source_path = human_source_path or SKILLS_DIR / "human-source"
        self.values_map = {}
        self.underwater_rocks = []
        self.personal_keys = []
        self._load_human_source()

    def _load_human_source(self):
        """Load human-source data from reports and config."""
        # Try to load from human-source report
        report_path = SKILLS_DIR.parent / "reports" / "human_source_report_final.md"
        if report_path.exists():
            self._parse_report(report_path)

        # Also try to load from analyze.py if available
        try:
            sys.path.insert(0, str(self.human_source_path / "scripts"))
            from analyze import HumanAnalyzer
            config = {
                'analysis': {'dimensions': {'frustrations': 0.3, 'sins': 0.2, 'norms': 0.2, 'strengths': 0.15, 'context': 0.15}},
                'ripple_engine': {'max_depth': 3, 'conflict_threshold': 0.7, 'stop_on_conflict': True},
            }
            analyzer = HumanAnalyzer(config)
            # The analyzer has the user's values embedded
            self.values_map = analyzer.values_map if hasattr(analyzer, 'values_map') else {}
            # Get underwater rocks from config
            self.underwater_rocks = self._extract_underwater_rocks(analyzer)
        except Exception as e:
            print(f"Warning: Could not load human-source analyzer: {e}", file=sys.stderr)

    def _extract_underwater_rocks(self, analyzer) -> List[str]:
        """Extract underwater rocks (hard constraints) from human-source analyzer."""
        # These are the user's hard constraints from human-source
        rocks = []
        # From the user's values map
        if hasattr(analyzer, 'config'):
            # The user's hard constraints are typically in the values map
            pass
        # Default known rocks from context
        return [
            "No KYC / No Documents",
            "Crimea constraints",
            "Stdlib-first / No new abstractions",
            "Clickable artifacts only",
            "No Google Gemini / No Playwright",
        ]

    def _parse_report(self, report_path: Path):
        """Parse human-source report for values and keys."""
        try:
            content = report_path.read_text(encoding='utf-8')
            # Extract keys, values, rocks from report
            # This is a simplified parser - real implementation would be more robust
            pass
        except Exception:
            pass

    def get_personal_importance(self, skill_name: str, skill: 'SkillInfo') -> int:
        """Calculate personal importance (0-100) based on human-source values."""
        score = 0

        # Check if skill aligns with personal keys
        personal_keywords = [
            "crimea", "simferopol", "job", "hh.ru", "work",
            "p2p", "usdt", "rub", "offramp", "crypto",
            "shorts", "tiktok", "content", "pipeline",
            "arbitrage", "matrix", "betting", "cricket",
            "autonomous", "cron", "daemon", "self-heal",
            "telegram", "bot", "channel",
        ]

        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()
        matches = sum(1 for kw in personal_keywords if kw in skill_text)
        score += min(40, matches * 5)

        # Check category alignment
        personal_categories = ['finance', 'arbitrage', 'autonomous-income', 'automation', 'devops']
        if skill.category in personal_categories:
            score += 20

        # Check if skill conflicts with underwater rocks
        if self._conflicts_with_rocks(skill):
            score -= 30  # Penalty for conflicts

        # Check if skill relates to personal keys (from human-source)
        if hasattr(self, 'personal_keys'):
            for key in self.personal_keys:
                if any(kw in skill_text for kw in key.lower().split()):
                    score += 10

        return max(0, min(100, score))

    def _conflicts_with_rocks(self, skill: 'SkillInfo') -> bool:
        """Check if skill conflicts with underwater rocks."""
        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()
        conflict_keywords = {
            "kyc": "No KYC / No Documents",
            "passport": "No KYC / No Documents",
            "document": "No KYC / No Documents",
            "verification": "No KYC / No Documents",
            "playwright": "No Google Gemini / No Playwright",
            "gemini": "No Google Gemini / No Playwright",
            "chrome": "No Google Gemini / No Playwright",
        }
        for kw, rock in conflict_keywords.items():
            if kw in skill_text:
                return True
        return False

    def get_risk_boundary(self, skill: 'SkillInfo') -> str:
        """Get risk boundary for skill: 'free' | 'needs_approval' | 'blocked'."""
        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()

        # Blocked: conflicts with hard constraints
        if self._conflicts_with_rocks(skill):
            return "blocked"

        # Needs approval: requires budget, external API, legal risk
        approval_keywords = ["budget", "paid api", "subscription", "legal", "compliance", "kyc"]
        if any(kw in skill_text for kw in approval_keywords):
            return "needs_approval"

        # Free: everything else
        return "free"


class AudienceRelevanceCalculator:
    """Calculates audience/market relevance using audience-analyzer."""

    def __init__(self, audience_analyzer_path: Optional[Path] = None):
        self.audience_analyzer_path = audience_analyzer_path or SKILLS_DIR / "audience-analyzer"
        self.audience_skills = {}
        self._load_audience_skills()

    def _load_audience_skills(self):
        """Load audience-analyzer to understand what skills are needed for audiences."""
        # This would analyze audience needs and map to required skills
        # For now, define known mappings
        self.audience_skill_map = {
            # Audience type -> required skills
            "arbitrage": ["arbitrage-execution", "finance-core", "arbitrage-sensors", "matrix-thinking"],
            "betting": ["pwa-betting", "creative-production", "anti-fraud", "cloaking"],
            "crypto": ["p2p-offramp", "usdt-rub", "defi", "wallet-security"],
            "content": ["content-pipeline", "shorts-production", "tiktok-automation", "youtube-seo"],
            "telegram": ["telegram-bot-integration", "telegram-channel-poster", "tg-mini-app"],
            "job-search": ["crimea-job-search", "hh-ru-parser", "cv-optimizer"],
            "affiliate": ["cpa-affiliate-bot", "offer-scanner", "landing-generator"],
        }

    def get_audience_relevance(self, skill_name: str, skill: 'SkillInfo', 
                                current_audience: Optional[str] = None) -> int:
        """Calculate audience relevance (0-100)."""
        score = 0

        # If we know the current audience, check direct mapping
        if current_audience and current_audience in self.audience_skill_map:
            if skill_name in self.audience_skill_map[current_audience]:
                score += 50

        # Check category alignment with high-value audiences
        high_value_categories = {
            'finance': 30,
            'arbitrage': 30,
            'autonomous-income': 25,
            'automation': 20,
            'cpa-affiliate': 25,
        }
        if skill.category in high_value_categories:
            score += high_value_categories[skill.category]

        # Check tags for audience-relevant keywords
        audience_keywords = [
            "cpa", "offer", "traffic", "conversion", "landing",
            "pwa", "betting", "cricket", "india",
            "telegram", "bot", "mini-app", "channel",
            "shorts", "tiktok", "reels", "viral",
            "p2p", "offramp", "usdt", "crypto",
            "hh.ru", "job", "vacancy", "resume",
        ]
        skill_text = f"{skill.name} {skill.description} {' '.join(skill.tags)}".lower()
        matches = sum(1 for kw in audience_keywords if kw in skill_text)
        score += min(30, matches * 3)

        return min(100, max(0, score))


class SkillArtifactMap:
    """Tracks created artifacts for each skill to prevent reinventing wheels."""

    def __init__(self, skills_root: Path):
        self.skills_root = skills_root
        self.artifacts = {}  # skill_name -> List[ArtifactInfo]
        self._build_artifact_map()

    def _build_artifact_map(self):
        """Scan all skills for their artifacts and test results."""
        for skill_dir in self.skills_root.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue

            skill_name = skill_dir.name
            artifacts = []

            # Check scripts
            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                for script in scripts_dir.glob("**/*.py"):
                    rel = script.relative_to(skill_dir)
                    # Check if it has tests passing
                    test_result = self._check_test_status(script)
                    artifacts.append({
                        "name": rel.name,
                        "path": str(rel),
                        "type": "script",
                        "tested": test_result,
                        "size": script.stat().st_size,
                    })

            # Check reports
            reports_dir = SKILLS_DIR.parent / "reports"
            if reports_dir.exists():
                for report in reports_dir.glob(f"*{skill_name}*"):
                    artifacts.append({
                        "name": report.name,
                        "path": str(report.relative_to(SKILLS_DIR.parent)),
                        "type": "report",
                        "tested": True,
                        "size": report.stat().st_size,
                    })

            # Check templates
            templates_dir = skill_dir / "templates"
            if templates_dir.exists():
                for tmpl in templates_dir.glob("**/*"):
                    if tmpl.is_file():
                        rel = tmpl.relative_to(skill_dir)
                        artifacts.append({
                            "name": rel.name,
                            "path": str(rel),
                            "type": "template",
                            "tested": False,
                            "size": tmpl.stat().st_size,
                        })

            if artifacts:
                self.artifacts[skill_name] = artifacts

    def _check_test_status(self, script_path: Path) -> bool:
        """Check if a script has passing tests."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(script_path)],
                capture_output=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_artifact_summary(self, skill_name: str) -> str:
        """Get a human-readable summary of artifacts for a skill."""
        artifacts = self.artifacts.get(skill_name, [])
        if not artifacts:
            return "No artifacts found"

        scripts = [a for a in artifacts if a['type'] == 'script']
        reports = [a for a in artifacts if a['type'] == 'report']
        templates = [a for a in artifacts if a['type'] == 'template']

        parts = []
        if scripts:
            tested = sum(1 for s in scripts if s['tested'])
            parts.append(f"{len(scripts)} scripts ({tested} tested)")
        if reports:
            parts.append(f"{len(reports)} reports")
        if templates:
            parts.append(f"{len(templates)} templates")

        return "; templates"

        return "; ".join(parts)

    def has_working_implementation(self, skill_name: str) -> bool:
        """Check if skill has at least one working, tested script."""
        artifacts = self.artifacts.get(skill_name, [])
        return any(a['type'] == 'script' and a['tested'] for a in artifacts)


class EntryPointFinder:
    """Finds the optimal entry point: max(weakness × demand × personal_importance × audience_relevance)."""

    def __init__(self, skills: Dict[str, SkillInfo], graph: SkillGraph,
                 human_source: 'HumanSourceIntegrator',
                 audience_calc: 'AudienceRelevanceCalculator',
                 artifact_map: 'SkillArtifactMap',
                 current_audience: Optional[str] = "arbitrage"):
        self.skills = skills
        self.graph = graph
        self.human_source = human_source
        self.audience_calc = audience_calc
        self.artifact_map = artifact_map
        self.current_audience = current_audience

    def find_entry_point(self) -> Optional[Tuple[str, float, GapAnalysis]]:
        best_skill = None
        best_score = 0
        best_gap = None

        for name, skill in self.skills.items():
            if skill.level >= 80 or skill.demand <= 20:
                continue

            # Skip blocked skills
            if self.human_source.get_risk_boundary(skill) == "blocked":
                continue

            weakness = 100 - skill.level
            personal_importance = self.human_source.get_personal_importance(name, skill)
            audience_relevance = self.audience_calc.get_audience_relevance(name, skill, self.current_audience)

            # 4-axis scoring: weakness × demand × personal × audience / 100^3
            gap_score = (weakness * skill.demand * personal_importance * audience_relevance) / 1_000_000

            assessor = SkillAssessor(self.skills)
            missing_artifacts, missing_tests, dep_gaps = assessor.get_gaps(skill)

            # Add artifact map info
            artifact_summary = self.artifact_map.get_artifact_summary(name)
            has_working = self.artifact_map.has_working_implementation(name)

            gap = GapAnalysis(
                skill_name=name,
                current_level=skill.level,
                demand=skill.demand,
                gap_score=gap_score,
                missing_artifacts=missing_artifacts,
                missing_tests=missing_tests,
                dependency_gaps=dep_gaps
            )
            # Store additional info for reporting
            gap.personal_importance = personal_importance
            gap.audience_relevance = audience_relevance
            gap.artifact_summary = artifact_summary
            gap.has_working_implementation = has_working
            gap.risk_boundary = self.human_source.get_risk_boundary(skill)
            gap.decision_quadrant = self._get_decision_quadrant(personal_importance, audience_relevance)

            if gap_score > best_score:
                best_score = gap_score
                best_skill = name
                best_gap = gap

        return (best_skill, best_score, best_gap) if best_skill else None

    def _get_decision_quadrant(self, personal: int, audience: int) -> str:
        """Return decision quadrant based on personal and audience importance."""
        high_personal = personal >= 50
        high_audience = audience >= 50

        if high_personal and high_audience:
            return "🔥 PRIORITY 1 — Learn immediately (high personal + high audience)"
        elif high_personal and not high_audience:
            return "🧠 Learn for self, not for sale (high personal, low audience)"
        elif not high_personal and high_audience:
            return "💰 Learn for revenue (low personal, high audience)"
        else:
            return "⚪ Defer or skip (low personal, low audience)"

    def rank_all_candidates(self) -> List[Tuple[str, float, GapAnalysis]]:
        candidates = []
        for name, skill in self.skills.items():
            if skill.level >= 80 or skill.demand <= 20:
                continue

            # Skip blocked skills
            if self.human_source.get_risk_boundary(skill) == "blocked":
                continue

            weakness = 100 - skill.level
            personal_importance = self.human_source.get_personal_importance(name, skill)
            audience_relevance = self.audience_calc.get_audience_relevance(name, skill, self.current_audience)

            gap_score = (weakness * skill.demand * personal_importance * audience_relevance) / 1_000_000

            assessor = SkillAssessor(self.skills)
            missing_artifacts, missing_tests, dep_gaps = assessor.get_gaps(skill)

            artifact_summary = self.artifact_map.get_artifact_summary(name)
            has_working = self.artifact_map.has_working_implementation(name)

            gap = GapAnalysis(
                skill_name=name,
                current_level=skill.level,
                demand=skill.demand,
                gap_score=gap_score,
                missing_artifacts=missing_artifacts,
                missing_tests=missing_tests,
                dependency_gaps=dep_gaps
            )
            gap.personal_importance = personal_importance
            gap.audience_relevance = audience_relevance
            gap.artifact_summary = artifact_summary
            gap.has_working_implementation = has_working
            gap.risk_boundary = self.human_source.get_risk_boundary(skill)
            gap.decision_quadrant = self._get_decision_quadrant(personal_importance, audience_relevance)

            candidates.append((name, gap_score, gap))

        candidates.sort(key=lambda x: -x[1])
        return candidates


class RoutePlanner:
    """Plans learning route from entry point."""

    def __init__(self, skills: Dict[str, SkillInfo], graph: SkillGraph):
        self.skills = skills
        self.graph = graph

    def plan_route(self, entry_skill: str) -> List[RouteStep]:
        route = []
        visited = set()

        # Dependencies first
        deps = self.graph.get_dependencies(entry_skill)
        for dep in deps['requires']:
            if dep not in visited and self.skills[dep].level < 80:
                route.append(RouteStep(
                    skill_name=dep,
                    reason=f"dependency for {entry_skill}",
                    prerequisite_skills=[],
                    estimated_effort=self._estimate_effort(dep),
                    research_required=True
                ))
                visited.add(dep)

        # Entry skill
        route.append(RouteStep(
            skill_name=entry_skill,
            reason="entry point (max weakness × demand)",
            prerequisite_skills=deps['requires'],
            estimated_effort=self._estimate_effort(entry_skill),
            research_required=True
        ))
        visited.add(entry_skill)

        # Enhancers
        for dep in deps['enhances']:
            if dep not in visited and self.skills[dep].level < 80:
                route.append(RouteStep(
                    skill_name=dep,
                    reason=f"enhances {entry_skill}",
                    prerequisite_skills=[entry_skill],
                    estimated_effort=self._estimate_effort(dep),
                    research_required=True
                ))
                visited.add(dep)

        # Downstream
        for dep in deps.get('required_by', []):
            if dep not in visited and self.skills[dep].level < 80:
                route.append(RouteStep(
                    skill_name=dep,
                    reason=f"unlocks {dep} (depends on {entry_skill})",
                    prerequisite_skills=[entry_skill],
                    estimated_effort=self._estimate_effort(dep),
                    research_required=True
                ))
                visited.add(dep)

        return route

    def _estimate_effort(self, skill_name: str) -> str:
        skill = self.skills.get(skill_name)
        if not skill:
            return "medium"

        artifacts = len(skill.artifacts)
        has_tests = skill.has_tests
        complexity = len(skill.dependencies.get('requires', []))

        if artifacts == 0 or not has_tests:
            return "high"
        elif artifacts < 3 or complexity > 2:
            return "medium"
        else:
            return "low"


class BestPracticesResearcher:
    """Step 1: Research best practices (5-10 examples)."""

    SEARCH_SOURCES = {
        'github': 'https://github.com/search?q={query}&type=repositories&s=stars&o=desc',
        'stackoverflow': 'https://stackoverflow.com/search?q={query}',
        'habr': 'https://habr.com/ru/search/?q={query}&target_type=posts',
    }

    def __init__(self):
        self.cache_dir = SKILLS_DIR.parent / "cache" / "research"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def research(self, skill_name: str, gap: GapAnalysis) -> ResearchResult:
        queries = self._build_queries(skill_name, gap)
        examples = []

        for query in queries[:5]:
            for source, url_template in self.SEARCH_SOURCES.items():
                try:
                    results = self._search_source(source, query)
                    examples.extend(results)
                except Exception as e:
                    print(f"Search failed for {source}: {e}", file=sys.stderr)

        examples = self._deduplicate_and_rank(examples)
        selected_approach, selected_sources, synthesis, rationale = self._decide_approach(examples, gap)

        return ResearchResult(
            skill_name=skill_name,
            examples=examples[:10],
            selected_approach=selected_approach,
            selected_sources=selected_sources,
            synthesis_notes=synthesis,
            decision_rationale=rationale
        )

    def _build_queries(self, skill_name: str, gap: GapAnalysis) -> List[str]:
        queries = [
            f"{skill_name} python implementation",
            f"{skill_name} best practices",
            f"{skill_name} tutorial",
        ]
        for artifact in gap.missing_artifacts:
            queries.append(f"{artifact} python example")
        for test_gap in gap.missing_tests:
            queries.append(f"{test_gap} pytest pattern")
        return queries

    def _search_source(self, source: str, query: str) -> List[Dict]:
        # Return structured mock data - real impl would use requests+parsing
        return []

    def _deduplicate_and_rank(self, examples: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for ex in examples:
            url = ex.get('url', '')
            if url and url not in seen:
                seen.add(url)
                unique.append(ex)
        return unique

    def _decide_approach(self, examples: List[Dict], gap: GapAnalysis) -> Tuple[str, List[str], str, str]:
        ready = [e for e in examples if e.get('completeness', 0) >= 0.8]
        if ready:
            best = ready[0]
            return "adopt", [best['url']], f"Adopt {best.get('name', 'solution')} from {best['url']}", f"Ready solution: {best.get('description', 'complete implementation')}"
        elif len(examples) >= 2:
            sources = [e['url'] for e in examples[:3]]
            return "synthesize", sources, f"Synthesize from {len(sources)} sources", f"No complete solution. Best patterns: {[e.get('what_good', '') for e in examples[:3]]}"
        else:
            return "synthesize", [], "Build from scratch using first principles", "Insufficient prior art"


class ReportGenerator:
    """Generates all output reports."""

    @staticmethod
    def generate_audit_report(skills: Dict[str, SkillInfo], graph: SkillGraph,
                               entry_result: Optional[Tuple]) -> str:
        lines = [
            "# Skill Audit Report",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Skills:** {len(skills)}",
            "",
            "## Skill Levels & Demand",
            "",
            "| Skill | Category | Level | Demand | Gap Score | Artifacts | Usage | Errors | Last Updated |",
            "|-------|----------|-------|--------|-----------|-----------|-------|--------|--------------|"
        ]

        for name, skill in sorted(skills.items(), key=lambda x: -x[1].level):
            gap_score = ((100 - skill.level) * skill.demand) / 100
            lines.append(f"| {name} | {skill.category} | {skill.level} | {skill.demand} | {gap_score:.1f} | {len(skill.artifacts)} | {skill.usage_count} | {skill.error_count} | {skill.last_updated or 'unknown'} |")

        lines.extend(["", "## Dependency Graph", ""])

        if graph.graph and nx:
            lines.append("```mermaid")
            lines.append("graph TD")
            for u, v, data in graph.graph.edges(data=True):
                dep_type = data.get('type', 'enhances')
                style = "===" if dep_type == 'requires' else "-->"
                lines.append(f"    {u} {style} {v}")
            lines.append("```")

        lines.extend(["", "## Circular Dependencies", ""])
        for cycle in graph.find_strongly_connected():
            lines.append(f"- {' -> '.join(cycle)}")

        if entry_result:
            skill_name, score, gap = entry_result
            lines.extend([
                "", "## Entry Point", "",
                f"**Skill:** {skill_name}",
                f"**Gap Score:** {score:.1f}",
                f"**Current Level:** {gap.current_level}/100",
                f"**Demand:** {gap.demand}/100",
                f"**Personal Importance:** {getattr(gap, 'personal_importance', 'N/A')}/100",
                f"**Audience Relevance:** {getattr(gap, 'audience_relevance', 'N/A')}/100",
                f"**Decision Quadrant:** {getattr(gap, 'decision_quadrant', 'N/A')}",
                f"**Risk Boundary:** {getattr(gap, 'risk_boundary', 'N/A')}",
                f"**Artifact Summary:** {getattr(gap, 'artifact_summary', 'N/A')}",
                f"**Has Working Implementation:** {getattr(gap, 'has_working_implementation', 'N/A')}",
                f"**Missing Artifacts:** {', '.join(gap.missing_artifacts) or '---'}",
                f"**Missing Tests:** {', '.join(gap.missing_tests) or '---'}",
                ""
            ])

        return "\n".join(lines)

    @staticmethod
    def generate_entry_point_card(skill_name: str, gap: GapAnalysis, research: ResearchResult) -> str:
        lines = [
            f"# Entry Point Card: {skill_name}",
            f"**Gap Score:** {gap.gap_score:.1f} | **Level:** {gap.current_level}/100 | **Demand:** {gap.demand}/100",
            f"**Personal Importance:** {getattr(gap, 'personal_importance', 'N/A')}/100",
            f"**Audience Relevance:** {getattr(gap, 'audience_relevance', 'N/A')}/100",
            f"**Decision Quadrant:** {getattr(gap, 'decision_quadrant', 'N/A')}",
            f"**Risk Boundary:** {getattr(gap, 'risk_boundary', 'N/A')}",
            "",
            "## Decision Matrix",
            "| Personal \\ Audience | High Audience (≥50) | Low Audience (<50) |",
            "|---------------------|---------------------|--------------------|",
            f"| High Personal (≥50) | 🔥 Priority 1 | 🧠 Learn for Self |",
            f"| Low Personal (<50)  | 💰 Learn for Revenue | ⚪ Defer |",
            f"| **Your Position** | **{('High' if getattr(gap, 'audience_relevance', 0) >= 50 else 'Low')} Audience** | **{('High' if getattr(gap, 'personal_importance', 0) >= 50 else 'Low')} Personal** |",
            "",
            "## Gap Analysis",
            f"- **Missing Artifacts:** {', '.join(gap.missing_artifacts) or '---'}",
            f"- **Missing Tests:** {', '.join(gap.missing_tests) or '---'}",
            f"- **Dependency Gaps:** {', '.join(gap.dependency_gaps) or '---'}",
            f"- **Artifact Summary:** {getattr(gap, 'artifact_summary', 'N/A')}",
            f"- **Has Working Implementation:** {getattr(gap, 'has_working_implementation', 'N/A')}",
            "",
            "## Step 1: Research (Best Practices Found)",
            ""
        ]

        for i, ex in enumerate(research.examples[:10], 1):
            lines.extend([
                f"### {i}. {ex.get('name', 'Unnamed')}",
                f"**Source:** {ex.get('source', 'unknown')} | **URL:** {ex.get('url', 'N/A')}",
                f"**What's Good:** {ex.get('what_good', 'N/A')}",
                f"**Why It Works:** {ex.get('why_works', 'N/A')}",
                ""
            ])

        lines.extend([
            "## Step 2: Select/Synthesize",
            f"**Approach:** {research.selected_approach}",
            f"**Selected Sources:** {', '.join(research.selected_sources) or '---'}",
            f"**Synthesis Notes:** {research.synthesis_notes}",
            f"**Rationale:** {research.decision_rationale}",
            "",
            "## Step 3: Execute",
            f"Apply the {research.selected_approach} approach to close the gap in {skill_name}.",
            ""
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_route_plan(route: List[RouteStep]) -> str:
        lines = [
            "# Learning Route Plan",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Steps:** {len(route)}",
            ""
        ]

        for i, step in enumerate(route, 1):
            lines.extend([
                f"## Step {i}: {step.skill_name}",
                f"**Reason:** {step.reason}",
                f"**Prerequisites:** {', '.join(step.prerequisite_skills) or '---'}",
                f"**Effort:** {step.estimated_effort}",
                f"**Research Required:** {'Yes' if step.research_required else 'No'}",
                ""
            ])

        return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Skill Pathfinder --- самоориентация в пространстве навыков")
    parser.add_argument("--full-audit", action="store_true", help="Full audit: inventory, assess, graph, entry, route")
    parser.add_argument("--entry-point", action="store_true", help="Just find entry point")
    parser.add_argument("--research", help="Research best practices for skill")
    parser.add_argument("--update", help="Update skill level after learning")
    parser.add_argument("--level", type=int, help="New level (0-100)")
    parser.add_argument("--artifacts", help="Comma-separated artifact paths")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--skills-root", default="skills", help="Skills root directory")

    args = parser.parse_args()

    skills_root = Path(args.skills_root)
    if not skills_root.is_absolute():
        hermes_root = Path(__file__).parent.parent.parent.parent
        skills_root = hermes_root / skills_root

    skills_root = skills_root.resolve()

    # Inventory
    print("📦 Scanning skills...")
    inventory = SkillInventory(skills_root)
    skills = inventory.scan_all_skills()
    print(f"   Found {len(skills)} skills")

    # Assess levels
    print("📊 Assessing levels...")
    assessor = SkillAssessor(skills)
    assessor.assess_all()

    # Estimate demand
    print("📈 Estimating demand...")
    demand = DemandEstimator(skills)
    demand.estimate_all()

    # Build graph
    print("🕸️ Building dependency graph...")
    graph = SkillGraph(skills)

    # Initialize integrators
    print("🔗 Integrating with human-source, audience-analyzer, and artifact map...")
    human_source = HumanSourceIntegrator()
    audience_calc = AudienceRelevanceCalculator()
    artifact_map = SkillArtifactMap(skills_root)

    # Find entry point with multi-dimensional scoring
    print("🎯 Finding entry point (weakness × demand × personal × audience)...")
    entry_finder = EntryPointFinder(skills, graph, human_source, audience_calc, artifact_map)
    entry_result = entry_finder.find_entry_point()

    if not entry_result:
        print("No suitable entry point found (all skills level>=80 or demand<=20)")
        return

    entry_skill, entry_score, gap = entry_result
    print(f"   Entry point: {entry_skill} (score={entry_score:.1f}, level={gap.current_level}, demand={gap.demand})")

    # Plan route
    print("🗺️ Planning route...")
    planner = RoutePlanner(skills, graph)
    route = planner.plan_route(entry_skill)

    # Research best practices
    print("🔍 Researching best practices...")
    researcher = BestPracticesResearcher()
    research = researcher.research(entry_skill, gap)

    # Generate reports
    audit_report = ReportGenerator.generate_audit_report(skills, graph, entry_result)
    entry_card = ReportGenerator.generate_entry_point_card(entry_skill, gap, research)
    route_plan = ReportGenerator.generate_route_plan(route)

    full_report = audit_report + "\n\n---\n\n" + entry_card + "\n\n---\n\n" + route_plan

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(full_report, encoding='utf-8')
        print(f"💾 Report saved to {args.output}")

    # Print summary
    print("\n" + "="*70)
    print("🎯 ENTRY POINT FOUND")
    print("="*70)
    print(f"Skill: {entry_skill}")
    print(f"Gap Score: {entry_score:.1f}")
    print(f"Current Level: {gap.current_level}/100")
    print(f"Demand: {gap.demand}/100")
    print(f"Missing: {', '.join(gap.missing_artifacts + gap.missing_tests) or '---'}")
    print(f"\nResearch: {len(research.examples)} examples found")
    print(f"Approach: {research.selected_approach}")
    print(f"Sources: {', '.join(research.selected_sources[:3]) or '---'}")
    print(f"\nRoute: {' -> '.join([s.skill_name for s in route])}")

    if not args.output:
        print("\n" + "="*70)
        print(entry_card)


if __name__ == "__main__":
    asyncio.run(main())