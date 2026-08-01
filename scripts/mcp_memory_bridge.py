#!/usr/bin/env python3
"""
MCP Memory Bridge — syncs Knowledge Cube data into MCP Memory graph format.

The MCP Memory Server stores entities, relations, and observations in a JSONL file.
This bridge reads KC experiences and creates graph entries for semantic memory.

Usage:
    python scripts/mcp_memory_bridge.py sync    # sync KC -> graph
    python scripts/mcp_memory_bridge.py query "salon bot"  # search graph
    python scripts/mcp_memory_bridge.py add "task" "description" "success"  # add entity
    python scripts/mcp_memory_bridge.py status  # show graph stats
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(__file__).resolve().parent.parent
CACHE_DIR = HERMES_HOME / "cache"
MEMORY_FILE = CACHE_DIR / "mcp_memory.jsonl"
KC_DB = CACHE_DIR / "knowledge_cube.db"
SYNC_STATE = CACHE_DIR / "mcp_sync_state.json"

sys.path.insert(0, str(HERMES_HOME / "scripts"))


# Entity patterns for extraction
ENTITY_PATTERNS = {
    "tool": r"\b(python|javascript|typescript|docker|nginx|git|sqlite|redis|telegram|aiogram|fastapi|flask|django|node|npm|pip|curl|ssh)\b",
    "project": r"\b(salon.?bot|hermes|crystal|knowledge.?cube|memory.?tree|icarus)\b",
    "error_type": r"\b(\w+Error|\w+Exception|timeout|connection.?refused|permission.?denied|not.?found)\b",
    "domain": r"\b(coding|devops|research|creative|communication|browser|system|architecture|testing|security)\b",
}


def _load_graph() -> dict:
    """Load existing graph from JSONL file."""
    entities = {}
    relations = []

    if MEMORY_FILE.exists():
        for line in MEMORY_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("type") == "entity":
                    name = entry.get("name", "")
                    if name:
                        entities[name] = entry
                elif entry.get("type") == "relation":
                    relations.append(entry)
            except json.JSONDecodeError:
                continue

    return {"entities": entities, "relations": relations}


def _save_graph(graph: dict):
    """Save graph to JSONL file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for name, entity in graph["entities"].items():
        lines.append(json.dumps(entity, ensure_ascii=False))
    for rel in graph["relations"]:
        lines.append(json.dumps(rel, ensure_ascii=False))

    MEMORY_FILE.write_text("\n".join(lines) + "\n" if lines else "", encoding="utf-8")


def _extract_entities(text: str) -> dict[str, list[str]]:
    """Extract entities from text by type."""
    found = {}
    text_lower = text.lower()
    for etype, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            found[etype] = list(set(matches))
    return found


def _ensure_entity(graph: dict, name: str, etype: str, observations: list[str] = None):
    """Add or update entity in graph."""
    name = name.lower().strip()
    if name in graph["entities"]:
        # Add new observations
        existing = graph["entities"][name].get("observations", [])
        for obs in (observations or []):
            if obs not in existing:
                existing.append(obs)
        graph["entities"][name]["observations"] = existing[-20:]  # Cap at 20
    else:
        graph["entities"][name] = {
            "type": "entity",
            "name": name,
            "entityType": etype,
            "observations": observations or [],
        }


def _ensure_relation(graph: dict, from_name: str, to_name: str, rel_type: str):
    """Add relation if not exists."""
    from_name = from_name.lower().strip()
    to_name = to_name.lower().strip()
    for rel in graph["relations"]:
        if (rel.get("from") == from_name and rel.get("to") == to_name
                and rel.get("relationType") == rel_type):
            return
    graph["relations"].append({
        "type": "relation",
        "from": from_name,
        "to": to_name,
        "relationType": rel_type,
    })


def sync_kc_to_graph():
    """Read KC experiences and create graph entries."""
    import sqlite3
    if not KC_DB.exists():
        print("Knowledge Cube DB not found")
        return

    graph = _load_graph()
    state = _load_sync_state()
    last_id = state.get("last_kc_id", 0)

    conn = sqlite3.connect(str(KC_DB))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, ts, raw_text, axis_domain, axis_outcome, source "
            "FROM experiences WHERE raw_text IS NOT NULL AND raw_text != '' ORDER BY id DESC LIMIT 100"
        )
        rows = cur.fetchall()
    except Exception as e:
        print(f"DB error: {e}")
        return
    finally:
        conn.close()

    if not rows:
        print("No new experiences to sync")
        return

    synced = 0
    for row in rows:
        text = row["raw_text"] or ""
        domain = row["axis_domain"] or "unknown"
        outcome = row["axis_outcome"] or "unknown"
        ts = row["ts"] or ""

        # Extract entities from text
        entities = _extract_entities(text)

        # Create domain entity
        _ensure_entity(graph, domain, "domain", [f"Domain with experiences"])

        # Create entities found in text
        for etype, names in entities.items():
            for name in names[:5]:  # Cap per type
                _ensure_entity(graph, name, etype, [text[:200]])
                _ensure_relation(graph, name, domain, "belongs_to")

        # Create experience entity (deduplicated by hash)
        exp_hash = str(row["id"])
        _ensure_entity(graph, f"experience-{exp_hash}", "experience", [
            f"Domain: {domain}",
            f"Outcome: {outcome}",
            text[:200],
        ])
        _ensure_relation(graph, f"experience-{exp_hash}", domain, "in_domain")

        synced += 1

    _save_graph(graph)
    state["last_kc_id"] = max(r["id"] for r in rows)
    state["last_sync"] = datetime.now().isoformat()
    state["total_synced"] = state.get("total_synced", 0) + synced
    _save_sync_state(state)

    print(f"Synced {synced} experiences to graph")
    print(f"Graph: {len(graph['entities'])} entities, {len(graph['relations'])} relations")


def add_task_memory(task: str, result: str, outcome: str = "success"):
    """Add a task completion to the memory graph."""
    graph = _load_graph()

    # Create task entity
    task_name = task[:80].lower().strip()
    _ensure_entity(graph, task_name, "task", [
        f"Result: {result[:200]}",
        f"Outcome: {outcome}",
        f"Completed: {datetime.now().isoformat()}",
    ])

    # Extract and link entities
    entities = _extract_entities(f"{task} {result}")
    for etype, names in entities.items():
        for name in names[:3]:
            _ensure_entity(graph, name, etype, [f"Related to task: {task[:100]}"])
            _ensure_relation(graph, task_name, name, "uses")

    _save_graph(graph)
    print(f"Added task memory: {task_name[:50]}")


def query_memory(query: str) -> str:
    """Search the memory graph by keyword."""
    graph = _load_graph()
    query_lower = query.lower()

    matches = []
    for name, entity in graph["entities"].items():
        score = 0
        if query_lower in name:
            score += 10
        for obs in entity.get("observations", []):
            if query_lower in obs.lower():
                score += 5
        if entity.get("entityType", "") in query_lower:
            score += 3
        if score > 0:
            matches.append((score, name, entity))

    matches.sort(key=lambda x: -x[0])

    if not matches:
        return "No matching memories found."

    lines = ["=== MEMORY GRAPH RESULTS ==="]
    for score, name, entity in matches[:10]:
        etype = entity.get("entityType", "?")
        obs = entity.get("observations", [])
        lines.append(f"\n[{etype}] {name} (score={score})")
        for o in obs[:3]:
            lines.append(f"  - {o}")

    # Show relations for top matches
    top_names = {m[1] for m in matches[:5]}
    rels = [r for r in graph["relations"]
            if r.get("from") in top_names or r.get("to") in top_names]
    if rels:
        lines.append("\nRelations:")
        for r in rels[:10]:
            lines.append(f"  {r['from']} --{r['relationType']}--> {r['to']}")

    return "\n".join(lines)


def status():
    """Show graph statistics."""
    graph = _load_graph()
    state = _load_sync_state()

    print("=== MCP Memory Graph ===")
    print(f"Entities: {len(graph['entities'])}")
    print(f"Relations: {len(graph['relations'])}")

    # Count by type
    type_counts = {}
    for e in graph["entities"].values():
        t = e.get("entityType", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    if type_counts:
        print("\nEntity types:")
        for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t}: {c}")

    print(f"\nLast sync: {state.get('last_sync', 'never')}")
    print(f"Total synced: {state.get('total_synced', 0)}")
    print(f"Last KC id: {state.get('last_kc_id', 0)}")


def _load_sync_state() -> dict:
    if SYNC_STATE.exists():
        try:
            return json.loads(SYNC_STATE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_sync_state(state: dict):
    SYNC_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "status":
        status()
    elif args[0] == "sync":
        sync_kc_to_graph()
    elif args[0] == "query" and len(args) > 1:
        q = " ".join(args[1:])
        print(query_memory(q))
    elif args[0] == "add" and len(args) > 2:
        add_task_memory(args[1], args[2], args[3] if len(args) > 3 else "success")
    else:
        print("Usage: mcp_memory_bridge.py [sync|query <q>|add <task> <result> [outcome]|status]")
