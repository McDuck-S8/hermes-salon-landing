#!/usr/bin/env python3
"""
Graphify Parser — AST + YAML + Markdown parsing for Graphify.
Scans scripts/, skills/, config/ and extracts nodes/edges for knowledge graph.
"""

import ast
import json
import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

SCAN_DIRS = [
    "scripts",
    "skills",
    "config",
]

NODE_TYPES = {
    # Code entities
    "module": {"color": "#1f77b4", "icon": "📦"},
    "class": {"color": "#ff7f0e", "icon": "🏗️"},
    "function": {"color": "#2ca02c", "icon": "⚙️"},
    "import": {"color": "#d62728", "icon": "📥"},
    # Skill entities
    "skill": {"color": "#9467bd", "icon": "🎯"},
    "skill_trigger": {"color": "#8c564b", "icon": "🔫"},
    "skill_usage": {"color": "#e377c2", "icon": "📋"},
    # Config entities
    "config": {"color": "#7f7f7f", "icon": "⚙️"},
    "domain_definition": {"color": "#bcbd22", "icon": "🏷️"},
    # Knowledge entities
    "kc_entry": {"color": "#17becf", "icon": "🧠"},
    "kc_pattern": {"color": "#1f77b4", "icon": "🔍"},
    # Video/Content entities (from video analysis)
    "ContentNiche": {"color": "#ff7f0e", "icon": "🎯"},
    "MonetizationStrategy": {"color": "#2ca02c", "icon": "💰"},
    "ContentCreator": {"color": "#9467bd", "icon": "👤"},
    "TelegramCommunity": {"color": "#0088cc", "icon": "💬"},
    "FreeCourse": {"color": "#e377c2", "icon": "📚"},
    "IncomeReport": {"color": "#8c564b", "icon": "📊"},
}

EDGE_TYPES = {
    # Code dependencies
    "imports": {"color": "#d62728", "label": "imports"},
    "calls": {"color": "#ff7f0e", "label": "calls"},
    "inherits": {"color": "#9467bd", "label": "inherits"},
    "decorates": {"color": "#8c564b", "label": "decorates"},
    # Skill relationships
    "triggers": {"color": "#e377c2", "label": "triggers"},
    "requires_skill": {"color": "#8c564b", "label": "requires"},
    "uses_skill": {"color": "#9467bd", "label": "uses"},
    # Config relationships
    "configures": {"color": "#7f7f7f", "label": "configures"},
    # Knowledge relationships
    "mentions": {"color": "#17becf", "label": "mentions"},
    "categorizes": {"color": "#1f77b4", "label": "categorizes"},
    # Video/Content relationships
    "adaptsTo": {"color": "#ff7f0e", "label": "adapts to", "dashed": True},
    "promotes": {"color": "#0088cc", "label": "promotes", "dashed": True},
    "generatesIncome": {"color": "#2ca02c", "label": "generates $", "weight": 3},
    "requiresSkill": {"color": "#8c564b", "label": "requires skill"},
    "requiresEquipment": {"color": "#8c564b", "label": "needs equipment", "dashed": True},
    "funnelStep": {"color": "#e377c2", "label": "funnel →", "dashed": True},
    "hasPrerequisite": {"color": "#8c564b", "label": "requires"},
}


class GraphifyParser:
    def __init__(self, root: Path = HERMES_HOME):
        self.root = root
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.node_ids: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}
        
    def scan_project(self) -> Dict[str, Any]:
        """Scan all configured directories and parse files."""
        results = {"nodes": [], "edges": [], "stats": {}}
        
        for scan_dir in SCAN_DIRS:
            dir_path = self.root / scan_dir
            if not dir_path.exists():
                continue
            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and not self._should_skip(file_path):
                    try:
                        self._parse_file(file_path)
                    except Exception as e:
                        print(f"  ⚠️ Parse error {file_path}: {e}")
        
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": self._count_node_types(),
                "scanned_files": len(self.file_hashes),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _should_skip(self, path: Path) -> bool:
        skip_patterns = [
            "__pycache__", ".pyc", ".git", ".venv", "node_modules",
            ".pytest_cache", ".ruff_cache", ".tmp", "dist", "build"
        ]
        return any(p in str(path) for p in skip_patterns)
    
    def _parse_file(self, file_path: Path):
        """Parse a single file based on extension."""
        rel_path = file_path.relative_to(self.root)
        self.file_hashes[str(rel_path)] = self._file_hash(file_path)
        
        suffix = file_path.suffix.lower()
        
        if suffix == ".py":
            self._parse_python(file_path)
        elif suffix in (".yaml", ".yml"):
            self._parse_yaml(file_path)
        elif suffix == ".md":
            self._parse_markdown(file_path)
        elif suffix in (".json",):
            self._parse_json(file_path)
    
    def _file_hash(self, path: Path) -> str:
        import hashlib
        return hashlib.md5(path.read_bytes()).hexdigest()[:16]
    
    def _parse_python(self, file_path: Path):
        """Parse Python file with AST."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"  ⚠️ AST parse failed {file_path}: {e}")
            return
        
        rel_path = str(file_path.relative_to(self.root))
        module_id = f"module:{rel_path}"
        self._add_node(module_id, "module", rel_path, file=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imp_id = f"import:{alias.name}"
                    self._add_node(imp_id, "import", alias.name, module=alias.name)
                    self._add_edge(module_id, imp_id, "imports")
                    
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imp_id = f"import:{module}.{alias.name}"
                    self._add_node(imp_id, "import", f"{module}.{alias.name}")
                    self._add_edge(module_id, imp_id, "imports")
                    
            elif isinstance(node, ast.ClassDef):
                class_id = f"class:{rel_path}:{node.name}"
                self._add_node(class_id, "class", node.name, file=str(file_path), line=node.lineno,
                              docstring=ast.get_docstring(node))
                self._add_edge(module_id, class_id, "contains")
                
                # Check decorators
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        dec_id = f"decorator:{dec.id}"
                        self._add_node(dec_id, "decorator", dec.id)
                        self._add_edge(class_id, dec_id, "decorates")
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                        dec_id = f"decorator:{dec.func.id}"
                        self._add_node(dec_id, "decorator", dec.func.id)
                        self._add_edge(class_id, dec_id, "decorates")
                
                # Check inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_id = f"class:{base.id}"
                        self._add_node(base_id, "class", base.id)
                        self._add_edge(class_id, base_id, "inherits")
                        
            elif isinstance(node, ast.FunctionDef):
                func_id = f"function:{rel_path}:{node.name}"
                self._add_node(func_id, "function", node.name, file=str(file_path), line=node.lineno,
                              docstring=ast.get_docstring(node))
                self._add_edge(module_id, func_id, "contains")
                
                # Check decorators on function
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        dec_id = f"decorator:{dec.id}"
                        self._add_node(dec_id, "decorator", dec.id)
                        self._add_edge(func_id, dec_id, "decorates")
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                        dec_id = f"decorator:{dec.func.id}"
                        self._add_node(dec_id, "decorator", dec.func.id)
                        self._add_edge(func_id, dec_id, "decorates")
                
                # Check function calls
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        call_id = f"call:{child.func.id}"
                        self._add_node(call_id, "call", child.func.id)
                        self._add_edge(func_id, call_id, "calls")
    
    def _parse_yaml(self, file_path: Path):
        """Parse YAML config files."""
        try:
            content = file_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
        except Exception as e:
            print(f"  ⚠️ YAML parse failed {file_path}: {e}")
            return
        
        rel_path = str(file_path.relative_to(self.root))
        config_id = f"config:{rel_path}"
        self._add_node(config_id, "config", file_path.name, file=str(file_path))
        
        if isinstance(data, dict):
            for key, value in data.items():
                key_id = f"config_key:{rel_path}:{key}"
                self._add_node(key_id, "config_key", key, parent=config_id)
                self._add_edge(config_id, key_id, "configures")
                
                # Check for domain definitions
                if key == "domains" and isinstance(value, dict):
                    for domain, domain_data in value.items():
                        domain_id = f"domain:{domain}"
                        self._add_node(domain_id, "domain_definition", domain, 
                                     properties=json.dumps(domain_data) if isinstance(domain_data, dict) else str(domain_data))
                        self._add_edge(config_id, domain_id, "configures")
                        
                        # Check for failure_rate / min_entries (high-risk domains)
                        if isinstance(domain_data, dict):
                            if "failure_rate" in domain_data or "min_entries" in domain_data:
                                self._add_node(f"risk:{domain}", "risk_indicator", 
                                             f"High-risk domain: {domain}")
                                self._add_edge(domain_id, f"risk:{domain}", "hasPrerequisite")
    
    def _parse_markdown(self, file_path: Path):
        """Parse Markdown files for skills, AGENTS.md, SKILL.md."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return
        
        rel_path = str(file_path.relative_to(self.root))
        
        # Check for SKILL.md
        if file_path.name == "SKILL.md":
            skill_name = file_path.parent.name
            skill_id = f"skill:{skill_name}"
            self._add_node(skill_id, "skill", skill_name, file=str(file_path))
            
            # Extract triggers
            triggers = re.findall(r"trigger[:\s]+([^\n]+)", content, re.IGNORECASE)
            for trigger in triggers:
                trigger_id = f"trigger:{trigger.strip()}"
                self._add_node(trigger_id, "skill_trigger", trigger.strip())
                self._add_edge(skill_id, trigger_id, "triggers")
            
            # Extract related skills
            related = re.findall(r"related_skills[:\s]+\[([^\]]+)\]", content)
            for rel in related:
                for skill in rel.split(","):
                    skill = skill.strip().strip('"\'')
                    if skill:
                        related_id = f"skill:{skill}"
                        self._add_node(related_id, "skill", skill)
                        self._add_edge(skill_id, related_id, "requires_skill")
            
            # Extract tags
            tags = re.findall(r"tags[:\s]+\[([^\]]+)\]", content)
            for tag_list in tags:
                for tag in tag_list.split(","):
                    tag = tag.strip().strip('"\'')
                    if tag:
                        tag_id = f"tag:{tag}"
                        self._add_node(tag_id, "tag", tag)
                        self._add_edge(skill_id, tag_id, "categorizes")
        
        # Check for AGENTS.md
        elif file_path.name == "AGENTS.md":
            # Extract domain from path
            domain = file_path.parent.name
            domain_id = f"domain:{domain}"
            self._add_node(domain_id, "domain_definition", domain, file=str(file_path))
            
            # Extract child DOX references
            child_dox = re.findall(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', content)
            for child in child_dox:
                if len(child) >= 2:
                    child_name = child[0].strip()
                    child_desc = child[1].strip()
                    child_id = f"child_dox:{child_name}"
                    self._add_node(child_id, "child_dox", child_name, description=child_desc)
                    self._add_edge(domain_id, child_id, "contains")
    
    def _parse_json(self, file_path: Path):
        """Parse JSON files for config, cron jobs, etc."""
        try:
            content = file_path.read_text(encoding="utf-8")
            data = json.loads(content)
        except Exception:
            return
        
        rel_path = str(file_path.relative_to(self.root))
        
        if file_path.name == "jobs.json" and isinstance(data, dict):
            jobs = data.get("jobs", [])
            for job in jobs:
                if job.get("enabled"):
                    job_id = f"cron:{job.get('name', job.get('id', 'unknown'))}"
                    self._add_node(job_id, "cron_job", job.get("name", "unknown"),
                                  schedule=job.get("schedule_display", ""),
                                  script=job.get("script", ""))
                    # Link to script file
                    script = job.get("script", "")
                    if script:
                        script_path = f"scripts/{script}"
                        script_id = f"module:{script_path}"
                        self._add_node(script_id, "module", script_path)
                        self._add_edge(job_id, script_id, "uses_skill")
    
    def _add_node(self, node_id: str, node_type: str, name: str, **attrs):
        """Add node if not exists."""
        if node_id in self.node_ids:
            return
        self.node_ids.add(node_id)
        
        node_info = NODE_TYPES.get(node_type, {"color": "#7f7f7f", "icon": "❓"})
        
        node = {
            "id": node_id,
            "type": node_type,
            "name": name,
            "color": node_info["color"],
            "icon": node_info["icon"],
            **attrs
        }
        self.nodes.append(node)
    
    def _add_edge(self, source: str, target: str, edge_type: str, **attrs):
        """Add edge between nodes."""
        edge_id = f"{source}→{target}:{edge_type}"
        edge_info = EDGE_TYPES.get(edge_type, {"color": "#7f7f7f", "label": edge_type})
        
        edge = {
            "id": edge_id,
            "source": source,
            "target": target,
            "type": edge_type,
            "label": edge_info["label"],
            "color": edge_info["color"],
            "dashed": edge_info.get("dashed", False),
            "weight": edge_info.get("weight", 1),
            **attrs
        }
        self.edges.append(edge)
    
    def _count_node_types(self) -> Dict[str, int]:
        counts = {}
        for node in self.nodes:
            counts[node["type"]] = counts.get(node["type"], 0) + 1
        return counts


def scan_project(root: Path = HERMES_HOME) -> Dict[str, Any]:
    """Main entry point for scanning project."""
    parser = GraphifyParser(root)
    return parser.scan_project()


if __name__ == "__main__":
    result = scan_project()
    print(json.dumps(result, ensure_ascii=False, indent=2))