#!/usr/bin/env python3
"""
Graphify Graph Builder — builds networkx graph from parsed nodes/edges.
Exports nodes.json + edges.json for HTML visualization and MCP server.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    import networkx as nx
except ImportError:
    nx = None

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = HERMES_HOME / "cache"
PARSED_DIR = CACHE_DIR / "graphify"

NODE_TYPES = {
    "module": {"color": "#1f77b4", "icon": "📦"},
    "class": {"color": "#ff7f0e", "icon": "🏗️"},
    "function": {"color": "#2ca02c", "icon": "⚙️"},
    "import": {"color": "#d62728", "icon": "📥"},
    "skill": {"color": "#9467bd", "icon": "🎯"},
    "skill_trigger": {"color": "#8c564b", "icon": "🔫"},
    "skill_usage": {"color": "#e377c2", "icon": "📋"},
    "config": {"color": "#7f7f7f", "icon": "⚙️"},
    "domain_definition": {"color": "#bcbd22", "icon": "🏷️"},
    "kc_entry": {"color": "#17becf", "icon": "🧠"},
    "kc_pattern": {"color": "#1f77b4", "icon": "🔍"},
    "ContentNiche": {"color": "#ff7f0e", "icon": "🎯"},
    "MonetizationStrategy": {"color": "#2ca02c", "icon": "💰"},
    "ContentCreator": {"color": "#9467bd", "icon": "👤"},
    "TelegramCommunity": {"color": "#0088cc", "icon": "💬"},
    "FreeCourse": {"color": "#e377c2", "icon": "📚"},
    "IncomeReport": {"color": "#8c564b", "icon": "📊"},
}

EDGE_TYPES = {
    "imports": {"color": "#d62728", "label": "imports"},
    "calls": {"color": "#ff7f0e", "label": "calls"},
    "inherits": {"color": "#9467bd", "label": "inherits"},
    "decorates": {"color": "#8c564b", "label": "decorates"},
    "triggers": {"color": "#e377c2", "label": "triggers"},
    "requires_skill": {"color": "#8c564b", "label": "requires"},
    "uses_skill": {"color": "#9467bd", "label": "uses"},
    "configures": {"color": "#7f7f7f", "label": "configures"},
    "mentions": {"color": "#17becf", "label": "mentions"},
    "categorizes": {"color": "#1f77b4", "label": "categorizes"},
    "adaptsTo": {"color": "#ff7f0e", "label": "adapts to", "dashed": True},
    "promotes": {"color": "#0088cc", "label": "promotes", "dashed": True},
    "generatesIncome": {"color": "#2ca02c", "label": "generates $", "weight": 3},
    "requiresSkill": {"color": "#8c564b", "label": "requires skill"},
    "requiresEquipment": {"color": "#8c564b", "label": "needs equipment", "dashed": True},
    "funnelStep": {"color": "#e377c2", "label": "funnel →", "dashed": True},
    "hasPrerequisite": {"color": "#8c564b", "label": "requires"},
}


class GraphBuilder:
    def __init__(self, parsed_dir: Path = PARSED_DIR):
        self.parsed_dir = parsed_dir
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.node_ids: Set[str] = set()
        self.edge_ids: Set[str] = set()
        self.G = nx.DiGraph() if nx else None
        
    def load_parsed(self, nodes_file: Path = None, edges_file: Path = None) -> bool:
            """Load parsed nodes/edges from JSON files."""
            nodes_file = nodes_file or self.parsed_dir / "nodes.json"
            edges_file = edges_file or self.parsed_dir / "edges.json"
        
            if not nodes_file.exists() or not edges_file.exists():
                return False
            
            try:
                self.nodes = json.loads(nodes_file.read_text(encoding="utf-8"))
                self.edges = json.loads(edges_file.read_text(encoding="utf-8"))
                # Initialize ID sets from loaded data
                self.node_ids = {n.get("id") or n.get("name") for n in self.nodes if n.get("id") or n.get("name")}
                self.edge_ids = {f"{e.get('source') or e.get('from')}_{e.get('type')}_{e.get('target') or e.get('to')}" 
                               for e in self.edges if e.get("source") and e.get("target")}
                print(f"Loaded {len(self.nodes)} nodes, {len(self.edges)} edges")
                return True
            except Exception as e:
                print(f"Failed to load parsed data: {e}")
                return False
    
    def build_graph(self) -> bool:
        """Build networkx graph from nodes and edges."""
        if not nx:
            print("networkx not available")
            return False
            
        self.G = nx.DiGraph()
        
        # Add nodes
        for node in self.nodes:
            node_id = node.get("id") or node.get("name")
            if node_id:
                self.G.add_node(node_id, **node)
        
        # Add edges
        for edge in self.edges:
            source = edge.get("source") or edge.get("from")
            target = edge.get("target") or edge.get("to")
            if source and target and self.G.has_node(source) and self.G.has_node(target):
                self.G.add_edge(source, target, **edge)
        
        print(f"Built graph: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
        return True
    
    def add_niche_analysis_nodes(self) -> None:
        """Add ContentNiche, MonetizationStrategy nodes from video analysis."""
        # Example niches from video analysis
        niches = [
            {
                "id": "niche_simple_blogs",
                "type": "ContentNiche",
                "name": "Simple Blogs",
                "monthlyRevenue": 300000,
                "currency": "RUB",
                "difficulty": "low",
                "equipmentNeeded": "minimal",
                "skillLevel": "none",
                "description": "3 simple blogs with income from 300K/month"
            },
            {
                "id": "niche_diana_1",
                "type": "ContentNiche",
                "name": "Diana Niche 1",
                "monthlyRevenue": 100000,
                "currency": "RUB",
                "difficulty": "low",
                "equipmentNeeded": "minimal",
                "skillLevel": "none"
            },
            {
                "id": "niche_diana_2",
                "type": "ContentNiche",
                "name": "Diana Niche 2",
                "monthlyRevenue": 100000,
                "currency": "RUB",
                "difficulty": "low",
                "equipmentNeeded": "minimal",
                "skillLevel": "none"
            },
            {
                "id": "niche_diana_3",
                "type": "ContentNiche",
                "name": "Diana Niche 3",
                "monthlyRevenue": 100000,
                "currency": "RUB",
                "difficulty": "low",
                "equipmentNeeded": "minimal",
                "skillLevel": "none"
            },
            {
                "id": "niche_diana_4",
                "type": "ContentNiche",
                "name": "Diana Niche 4",
                "monthlyRevenue": 100000,
                "currency": "RUB",
                "difficulty": "low",
                "equipmentNeeded": "minimal",
                "skillLevel": "none"
            },
        ]
        
        monetization = [
            {
                "id": "monet_blog_ads",
                "type": "MonetizationStrategy",
                "name": "Blog Advertising",
                "monetization_type": "ads",
                "avgRevenue": 300000,
                "timeToFirstIncome": "1-3 months",
                "platform": "blog"
            },
            {
                "id": "monet_telegram",
                "type": "MonetizationStrategy",
                "name": "Telegram Community",
                "monetization_type": "community",
                "avgRevenue": 100000,
                "timeToFirstIncome": "1-2 months",
                "platform": "telegram"
            },
            {
                "id": "monet_course",
                "type": "MonetizationStrategy",
                "name": "Free Course Funnel",
                "monetization_type": "course_funnel",
                "avgRevenue": 50000,
                "timeToFirstIncome": "immediate",
                "platform": "telegram_bot"
            },
        ]
        
        creators = [
            {
                "id": "creator_diana",
                "type": "ContentCreator",
                "name": "Diana Mulevskaya",
                "niches": ["simple_blogs", "diana_1", "diana_2", "diana_3", "diana_4"],
                "totalRevenue": 700000,
                "platforms": ["youtube", "telegram"]
            },
            {
                "id": "creator_user",
                "type": "ContentCreator",
                "name": "User",
                "niches": [],
                "totalRevenue": 0,
                "platforms": []
            },
        ]
        
        telegram_communities = [
            {
                "id": "tg_problogstart",
                "type": "TelegramCommunity",
                "name": "ProBlogStart",
                "url": "https://t.me/+mv5mG0hGRrhhNTcy",
                "members": 0,
                "purpose": "collections of videos"
            },
            {
                "id": "tg_problogstart_bot",
                "type": "TelegramCommunity",
                "name": "ProBlogStartBot",
                "url": "https://telegram.me/Problogstartbot",
                "members": 0,
                "purpose": "free course bot"
            },
        ]
        
        free_courses = [
            {
                "id": "course_problogstart",
                "type": "FreeCourse",
                "name": "ProBlogStart Free Course",
                "bot": "@Problogstartbot",
                "topics": ["blog creation", "niche selection", "monetization"],
                "difficulty": "beginner"
            }
        ]
        
        # Add all nodes
        for niche in niches:
            self.add_node(niche)
        for mon in monetization:
            self.add_node(mon)
        for creator in creators:
            self.add_node(creator)
        for tg in telegram_communities:
            self.add_node(tg)
        for course in free_courses:
            self.add_node(course)
        
        # Add edges
        # Niches -> monetization
        for niche in niches:
            self.add_edge(niche["id"], "monet_blog_ads", "generatesIncome", weight=3)
            if niche["id"] != "niche_simple_blogs":
                self.add_edge(niche["id"], "monet_telegram", "generatesIncome", weight=2)
        
        # Creator -> niches
        self.add_edge("creator_diana", "niche_simple_blogs", "creates")
        for i in range(1, 5):
            self.add_edge("creator_diana", f"niche_diana_{i}", "creates")
        
        # Creator -> monetization
        self.add_edge("creator_diana", "monet_blog_ads", "uses")
        self.add_edge("creator_diana", "monet_telegram", "uses")
        self.add_edge("creator_diana", "monet_course", "uses")
        
        # Video/funnel edges
        self.add_edge("video_pdmgLJacyA8", "tg_problogstart", "funnelStep")
        self.add_edge("video_pdmgLJacyA8", "tg_problogstart_bot", "funnelStep")
        self.add_edge("tg_problogstart_bot", "course_problogstart", "funnelStep")
        
        # Skill/equipment requirements
        for niche in niches:
            self.add_edge(niche["id"], "skill_none", "requiresSkill", required=False)
            self.add_edge(niche["id"], "equipment_minimal", "requiresEquipment", required=False)
        
        # Add skill/equipment nodes
        self.add_node({"id": "skill_none", "type": "Skill", "name": "No Skill Required", "level": "none"})
        self.add_node({"id": "equipment_minimal", "type": "Equipment", "name": "Minimal Equipment", "level": "minimal"})
    
    def add_node(self, node: Dict) -> str:
        """Add node to graph, return node ID."""
        node_id = node.get("id")
        if not node_id:
            # Generate ID from name
            import hashlib
            name = node.get("name", "unknown")
            node_id = f"{node['type']}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            node["id"] = node_id
        
        if node_id not in self.node_ids:
            self.node_ids.add(node_id)
            node_data = {
                "id": node_id,
                "type": node.get("type"),
                "name": node.get("name", node_id),
                **{k: v for k, v in node.items() if k not in ["id", "type", "name"]}
            }
            self.nodes.append(node_data)
            if self.G:
                self.G.add_node(node_id, **node_data)
        return node_id
    
    def add_edge(self, source: str, target: str, edge_type: str, **attrs) -> None:
        """Add edge to graph."""
        edge_id = f"{source}_{edge_type}_{target}"
        if edge_id not in self.edge_ids:
            self.edge_ids.add(edge_id)
            edge_data = {
                "id": edge_id,
                "source": source,
                "target": target,
                "type": edge_type,
                **attrs
            }
            self.edges.append(edge_data)
            if self.G and self.G.has_node(source) and self.G.has_node(target):
                self.G.add_edge(source, target, **edge_data)
    
    def export_json(self, output_dir: Path = None) -> None:
        """Export nodes and edges to JSON files."""
        output_dir = output_dir or self.parsed_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        (output_dir / "nodes.json").write_text(
            json.dumps(self.nodes, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (output_dir / "edges.json").write_text(
            json.dumps(self.edges, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        
        # Export networkx graph if available - sanitize list values for GraphML
        if self.G and nx:
            # Create a copy with sanitized attributes for GraphML
            G_copy = self.G.copy()
            for node_id, attrs in G_copy.nodes(data=True):
                for key, value in list(attrs.items()):
                    if isinstance(value, list):
                        attrs[key] = json.dumps(value, ensure_ascii=False)
                    elif not isinstance(value, (str, int, float, bool, type(None))):
                        attrs[key] = str(value)
            for u, v, attrs in G_copy.edges(data=True):
                for key, value in list(attrs.items()):
                    if isinstance(value, list):
                        attrs[key] = json.dumps(value, ensure_ascii=False)
                    elif not isinstance(value, (str, int, float, bool, type(None))):
                        attrs[key] = str(value)
            nx.write_graphml(G_copy, output_dir / "graph.graphml")
        
        print(f"Exported {len(self.nodes)} nodes, {len(self.edges)} edges to {output_dir}")
    
    def get_subgraph(self, node_ids: List[str], depth: int = 1) -> Dict:
        """Get subgraph around given nodes."""
        if not self.G:
            return {"nodes": [], "edges": []}
        
        sub_nodes = set(node_ids)
        for node in node_ids:
            if self.G.has_node(node):
                # Add neighbors up to depth
                for _ in range(depth):
                    neighbors = set()
                    for n in sub_nodes:
                        if self.G.has_node(n):
                            neighbors.update(self.G.predecessors(n))
                            neighbors.update(self.G.successors(n))
                    sub_nodes.update(neighbors)
        
        subgraph_nodes = [n for n in self.nodes if n["id"] in sub_nodes]
        subgraph_edges = [e for e in self.edges if e["source"] in sub_nodes and e["target"] in sub_nodes]
        
        return {"nodes": subgraph_nodes, "edges": subgraph_edges}
    
    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two nodes."""
        if not self.G or not self.G.has_node(source) or not self.G.has_node(target):
            return None
        try:
            return nx.shortest_path(self.G, source, target)
        except nx.NetworkXNoPath:
            return None


def main():
    import sys
    parser = argparse.ArgumentParser(description="Graphify Graph Builder")
    parser.add_argument("--load", action="store_true", help="Load parsed nodes/edges")
    parser.add_argument("--build", action="store_true", help="Build graph")
    parser.add_argument("--export", action="store_true", help="Export to JSON")
    parser.add_argument("--add-niches", action="store_true", help="Add niche analysis nodes")
    parser.add_argument("--query", type=str, help="Query: find_niches_by_revenue, find_skill_free, monetization_path")
    parser.add_argument("--min-revenue", type=int, default=100000, help="Minimum revenue for niche queries")
    parser.add_argument("--output", type=str, help="Output file")
    args = parser.parse_args()
    
    builder = GraphBuilder()
    
    if args.load:
        if not builder.load_parsed():
            print("No parsed data found. Run parser first.")
            return 1
    
    if args.add_niches:
        builder.add_niche_analysis_nodes()
        print("Added niche analysis nodes and edges")
    
    if args.build:
        if not builder.build_graph():
            return 1
    
    if args.export:
        builder.export_json()
    
    if args.query:
        if args.query == "find_niches_by_revenue":
            if not builder.G:
                builder.build_graph()
            results = []
            for node in builder.nodes:
                if node.get("type") == "ContentNiche" and node.get("monthlyRevenue", 0) >= args.min_revenue:
                    results.append({
                        "id": node["id"],
                        "name": node.get("name"),
                        "monthlyRevenue": node.get("monthlyRevenue"),
                        "difficulty": node.get("difficulty"),
                        "skillLevel": node.get("skillLevel"),
                        "equipmentNeeded": node.get("equipmentNeeded")
                    })
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.query == "find_skill_free":
            if not builder.G:
                builder.build_graph()
            results = []
            for node in builder.nodes:
                if node.get("type") == "ContentNiche" and node.get("skillLevel") == "none":
                    results.append({
                        "id": node["id"],
                        "name": node.get("name"),
                        "monthlyRevenue": node.get("monthlyRevenue"),
                        "equipmentNeeded": node.get("equipmentNeeded")
                    })
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.query == "monetization_path":
            niche = args.output  # using output as niche parameter
            if builder.G and builder.G.has_node(niche):
                paths = []
                for edge in builder.edges:
                    if edge["source"] == niche and edge["type"] == "generatesIncome":
                        target = edge["target"]
                        mon_node = next((n for n in builder.nodes if n["id"] == target), None)
                        if mon_node:
                            paths.append({
                                "monetization": mon_node.get("name"),
                                "type": mon_node.get("type"),
                                "avgRevenue": mon_node.get("avgRevenue"),
                                "timeToFirstIncome": mon_node.get("timeToFirstIncome")
                            })
                print(json.dumps(paths, ensure_ascii=False, indent=2))
            else:
                print(f"Niche {niche} not found")
    
    return 0


if __name__ == "__main__":
    import argparse
    import sys
    sys.exit(main())