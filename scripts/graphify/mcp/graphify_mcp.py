#!/usr/bin/env python3
"""
Graphify MCP Server — Provides graph navigation tools for agents.
Runs on port 9005.
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    import networkx as nx
except ImportError:
    nx = None

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CACHE_DIR = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")) / "cache"
GRAPH_DIR = CACHE_DIR / "graphify"

NODES_FILE = CACHE_DIR / "graphify" / "nodes.json"
EDGES_FILE = CACHE_DIR / "graphify" / "edges.json"

class GraphMCP:
    def __init__(self):
        self.G = None
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.node_index: Dict[str, Dict] = {}
        self.loaded = False
        
    def load(self) -> bool:
        """Load graph from JSON files."""
        if not NODES_FILE.exists() or not EDGES_FILE.exists():
            return False
        try:
            self.nodes = json.loads(NODES_FILE.read_text(encoding="utf-8"))
            self.edges = json.loads(EDGES_FILE.read_text(encoding="utf-8"))
            
            # Build index
            self.node_index = {n["id"]: n for n in self.nodes}
            
            # Build networkx graph
            import networkx as nx
            self.G = nx.DiGraph()
            for node in self.nodes:
                self.G.add_node(node["id"], **node)
            for edge in self.edges:
                source = edge.get("source") or edge.get("from")
                target = edge.get("target") or edge.get("to")
                if source and target:
                    self.G.add_edge(source, target, **edge)
            
            self.loaded = True
            return True
        except Exception as e:
            print(f"Failed to load graph: {e}")
            return False
    
    def get_graph(self) -> Dict:
        """Return full graph."""
        if not self.loaded:
            self.load()
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
                "types": len(set(n.get("type") for n in self.nodes))
            }
        }
    
    def get_subgraph(self, node_ids: List[str], depth: int = 1) -> Dict:
        """Get subgraph around given nodes."""
        if not self.G:
            return {"nodes": [], "edges": []}
        
        sub_nodes = set(node_ids)
        for _ in range(depth):
            neighbors = set()
            for n in list(sub_nodes):
                if self.G.has_node(n):
                    neighbors.update(self.G.predecessors(n))
                    neighbors.update(self.G.successors(n))
            sub_nodes.update(neighbors)
        
        sub_nodes = [n for n in self.nodes if n["id"] in sub_nodes]
        sub_edges = [e for e in self.edges if e["source"] in sub_nodes and e["target"] in sub_nodes]
        
        return {"nodes": sub_nodes, "edges": sub_edges}
    
    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two nodes."""
        if not self.G or not self.G.has_node(source) or not self.G.has_node(target):
            return None
        try:
            import networkx as nx
            return nx.shortest_path(self.G, source, target)
        except:
            return None
    
    def get_neighbors(self, node_id: str) -> Dict:
        """Get neighbors of a node."""
        if not self.G or not self.G.has_node(node_id):
            return {"predecessors": [], "successors": []}
        return {
            "predecessors": list(self.G.predecessors(node_id)),
            "successors": list(self.G.successors(node_id))
        }
    
    def search_nodes(self, query: str, limit: int = 20) -> List[Dict]:
        """Search nodes by name/id/type."""
        query = query.lower()
        results = []
        for node in self.nodes:
            if (query in node.get("id", "").lower() or 
                query in node.get("name", "").lower() or
                query in node.get("type", "").lower()):
                results.append(node)
                if len(results) >= 20:
                    break
        return results
    
    def find_niches_by_revenue(self, min_revenue: int = 100000) -> List[Dict]:
        """Find content niches with revenue >= min_revenue."""
        results = []
        for node in self.nodes:
            if node.get("type") == "ContentNiche":
                revenue = node.get("monthlyRevenue", 0)
                if revenue >= min_revenue:
                    results.append({
                        "id": node["id"],
                        "name": node.get("name"),
                        "monthlyRevenue": node.get("monthlyRevenue"),
                        "difficulty": node.get("difficulty"),
                        "skillLevel": node.get("skillLevel"),
                        "equipmentNeeded": node.get("equipmentNeeded")
                    })
        return results
    
    def find_skill_free_niches(self) -> List[Dict]:
        """Find niches requiring no skills."""
        results = []
        for node in self.nodes:
            if node.get("type") == "ContentNiche" and node.get("skillLevel") == "none":
                results.append({
                    "id": node["id"],
                    "name": node.get("name"),
                    "monthlyRevenue": node.get("monthlyRevenue"),
                    "equipmentNeeded": node.get("equipmentNeeded")
                })
        return results
    
    def monetization_path(self, niche_id: str) -> List[Dict]:
        """Get monetization path for a niche."""
        if not self.G or not self.G.has_node(niche_id):
            return []
        paths = []
        for edge in self.edges:
            if edge.get("source") == niche_id and edge.get("type") == "generatesIncome":
                target = edge.get("target")
                mon_node = next((n for n in self.nodes if n["id"] == target), None)
                if mon_node:
                    return [{
                        "monetization": mon_node.get("name"),
                        "type": mon_node.get("type"),
                        "avgRevenue": mon_node.get("avgRevenue"),
                        "timeToFirstIncome": mon_node.get("timeToFirstIncome")
                    }]
        return []


# FastAPI app
app = FastAPI(title="Graphify MCP Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_mcp = GraphMCP()

@app.on_event("startup")
async def startup():
    graph_mcp.load()

class SearchRequest(BaseModel):
    query: str
    limit: int = 20

class SubgraphRequest(BaseModel):
    node_ids: List[str]
    depth: int = 1

class PathRequest(BaseModel):
    source: str
    target: str

class NicheRevenueRequest(BaseModel):
    min_revenue: int = 100000

class NichePathRequest(BaseModel):
    niche_id: str

@app.get("/health")
async def health():
    return {"status": "ok", "loaded": graph_mcp.loaded}

@app.get("/graph")
async def get_graph():
    return graph_mcp.get_graph()

@app.post("/subgraph")
async def get_subgraph(req: SubgraphRequest):
    return graph_mcp.get_subgraph(req.node_ids, req.depth)

@app.post("/path")
async def find_path(req: PathRequest):
    path = graph_mcp.find_path(req.source, req.target)
    if path is None:
        raise HTTPException(status_code=404, detail="No path found")
    return {"path": path}

@app.post("/neighbors")
async def get_neighbors(node_id: str):
    return graph_mcp.get_neighbors(node_id)

@app.post("/search")
async def search_nodes(req: SearchRequest):
    return {"results": graph_mcp.search_nodes(req.query, req.limit)}

@app.post("/niches/revenue")
async def niches_by_revenue(req: NicheRevenueRequest):
    return {"niches": graph_mcp.find_niches_by_revenue(req.min_revenue)}

@app.post("/niches/skill-free")
async def skill_free_niches():
    return {"niches": graph_mcp.find_skill_free_niches()}

@app.post("/monetization/path")
async def monetization_path(req: NichePathRequest):
    return {"paths": graph_mcp.monetization_path(req.niche_id)}

@app.post("/niche/{niche_id}/monetization")
async def niche_monetization(niche_id: str):
    return {"paths": graph_mcp.monetization_path(niche_id)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9005)