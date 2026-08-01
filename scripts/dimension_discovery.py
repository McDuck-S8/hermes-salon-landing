#!/usr/bin/env python3
"""
Dimension Discovery — finds new axes for the Knowledge Cube.
Runs after cube population. Analyzes white spot clusters via LLM to discover new dimensions.
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
CUBE_SCRIPT = Path(__file__).parent / "knowledge_cube.py"

sys.path.insert(0, str(CUBE_SCRIPT.parent))
import importlib.util
spec = importlib.util.spec_from_file_location("kc", str(CUBE_SCRIPT))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def discover_dimensions():
    """Find white spot clusters and propose new dimensions."""
    clusters = mod.cluster_white_spots()
    
    if not clusters:
        print("No white spot clusters found yet. Need more data.")
        return
    
    print(f"Found {len(clusters)} white spot clusters:")
    
    proposals = []
    for c in clusters:
        print(f"\n  Cluster {c['cluster_id']} ({c['size']} spots):")
        print(f"    Keywords: {', '.join(c['shared_keywords'][:8])}")
        print(f"    Sample: {c['representative_text'][:120]}")
        
        # Analyze what dimension this cluster might represent
        keywords = c['shared_keywords']
        sample = c['representative_text']
        
        # Heuristic dimension proposals based on keywords
        proposals_for_cluster = []
        
        # Time-related patterns
        time_kw = [k for k in keywords if k in ["morning","afternoon","evening","night","hour","time","schedule","cron","periodic"]]
        if time_kw:
            proposals_for_cluster.append(("time_of_day_effect", "Does task success vary by time of day?"))
        
        # Complexity-related
        complex_kw = [k for k in keywords if k in ["complex","simple","large","small","many","few","heavy","light"]]
        if complex_kw:
            proposals_for_cluster.append(("task_complexity", "How complex was this task?"))
        
        # Error-pattern
        error_kw = [k for k in keywords if k in ["error","fail","crash","timeout","hang","broken","wrong","bug"]]
        if error_kw:
            proposals_for_cluster.append(("error_category", "What type of failure? (timeout/crash/logic/config)"))
        
        # Tool-specific
        tool_kw = [k for k in keywords if k in ["browser","terminal","file","web","api","ssh","docker"]]
        if tool_kw:
            proposals_for_cluster.append(("tool_dependency", "Which tools are required vs optional for this task type?"))
        
        # Novelty
        novel_kw = [k for k in keywords if k in ["new","first","never","unknown","unexpected","mysterious","strange"]]
        if novel_kw:
            proposals_for_cluster.append(("novelty_score", "How novel/unexpected is this experience?"))
        
        # If no heuristic matched, it's a genuine unknown
        if not proposals_for_cluster:
            proposals_for_cluster.append(("unknown_dimension", f"Cluster keywords: {', '.join(keywords[:5])} — needs human analysis"))
        
        proposals.append({
            "cluster_id": c['cluster_id'],
            "size": c['size'],
            "proposals": proposals_for_cluster
        })
    
    # Store proposals
    proposals_file = HERMES_HOME / "cache" / "dimension_proposals.json"
    proposals_file.parent.mkdir(parents=True, exist_ok=True)
    
    existing = []
    if proposals_file.exists():
        try:
            existing = json.loads(proposals_file.read_text(encoding="utf-8"))
        except:
            pass
    
    existing.append({
        "timestamp": datetime.now().isoformat(),
        "proposals": proposals
    })
    
    proposals_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nProposals saved to {proposals_file}")
    
    # Auto-accept high-confidence proposals
    conn = mod.get_db()
    for p in proposals:
        for dim_name, dim_desc in p['proposals']:
            if dim_name != "unknown_dimension":
                conn.execute(
                    "INSERT OR IGNORE INTO dimensions (name, discovered_at, source, dim_values, description) VALUES (?, ?, ?, ?, ?)",
                    (dim_name, datetime.now().isoformat(), "auto_cluster", "[]", dim_desc)
                )
                print(f"  AUTO-ACCEPTED dimension: {dim_name} — {dim_desc}")
    conn.commit()
    conn.close()
    
    return proposals

if __name__ == "__main__":
    discover_dimensions()
