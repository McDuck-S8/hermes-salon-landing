#!/usr/bin/env python3
"""
IBOS Entity Sensor Module — Core validation logic for IBOS entities.


> Revisit: when entity sensor logic, IBOS entity detection, or entity event emission changes. Last touched: 2026-07-02.
This module is imported by sensor_array.py on startup to validate all entities
and emit events for violations. It blocks chain execution for invalid entities.
"""

import json
import re
import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field, asdict

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / "cache"
SCHEMA_PATH = REPO_ROOT / "_system" / "schemas" / "frontmatter.schema.yaml"
VALIDATION_STATE_FILE = CACHE / "ibos_validation_state.json"
ENTITY_DEPENDENCY_GRAPH = CACHE / "entity_dependency_graph.json"
BLOCKED_ENTITIES_FILE = CACHE / "blocked_entities.json"

ENTITY_DIRS = [
    REPO_ROOT / "entities" / "agents",
    REPO_ROOT / "entities" / "commands",
    REPO_ROOT / "entities" / "skills",
    REPO_ROOT / "entities" / "rules",
    REPO_ROOT / "entities" / "workflows",
    REPO_ROOT / "entities" / "tools",
    REPO_ROOT / "entities" / "knowledge",
    REPO_ROOT / "knowledge",
    REPO_ROOT / "projects",
    REPO_ROOT / "departments",
    REPO_ROOT / "outputs",
    REPO_ROOT / "memory",
    REPO_ROOT / "data",
    REPO_ROOT / "tools",
    REPO_ROOT / "workflows",
    REPO_ROOT / "automations",
]

PLUMBING_PATTERNS = [
    "README.md", "CLAUDE.md", "AGENTS.md", "CANONICAL-GATES.md",
    "CONTRIBUTING.md", "START-HERE.md", "OBSIDIAN-DASHBOARD.md",
    ".obsidian/", "_system/", "swarms/", "docs/", "data/source-archives/",
    ".claude/hooks/", "entities/README.md", "sessions/",
    "*/waves/surfaces/dist/", "*/knowledge/*/archive/", "*/knowledge/*/support/",
    "*/outputs/crm-corpus/generated/", "*/outputs/crm-corpus/assets/",
    "node_modules/", "knowledge/*/INDEX.md", "knowledge/*/support/*",
    "knowledge/*/archive/*", "knowledge/*/canon/README.md",
    "knowledge/*/canon/agent-load-order.md", "knowledge/*/synthesis/README.md",
    "intake/*", "projects/README.md", "departments/README.md",
    "outputs/README.md", "memory/README.md", "data/README.md",
    "tools/README.md", "workflows/README.md", "automations/README.md",
]

REQUIRED_KEYS = [
    "id", "type", "namespace", "status", "version", 
    "owner", "created", "summary", "description"
]

VALID_TYPES = [
    "command", "agent", "skill", "rule", "workflow", 
    "tool", "knowledge", "data", "memory", "output", "project"
]

VALID_STATUSES = [
    "scratch", "research", "candidate", "canon", 
    "deprecated", "archived"
]

VALID_OWNERS = ["operator", "agent"]

VALID_RETRIEVAL_CLASSES = ["hot", "warm", "cold"]
VALID_EXPORT_CLASSES = ["public", "private", "operator"]

ID_PATTERN = re.compile(r'^[a-z0-9-]+$')
NAMESPACE_PATTERN = re.compile(r'^[a-z0-9-]+(/[a-z0-9-]+)*$')
VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')
CREATED_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$')


@dataclass
class EntityValidationResult:
    entity_id: str
    file_path: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    frontmatter: Dict = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class ValidationState:
    timestamp: str
    total_entities: int
    valid_entities: int
    invalid_entities: int
    blocked_entities: List[str] = field(default_factory=list)
    entity_results: Dict[str, Dict] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)


def is_plumbing(filepath: Path) -> bool:
    """Check if file is plumbing (exempt from validation)."""
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    for pattern in PLUMBING_PATTERNS:
        if pattern.endswith('/'):
            if rel.startswith(pattern) or f"/{pattern}" in f"/{rel}":
                return True
        elif '*' in pattern:
            regex = pattern.replace('*', '[^/]+')
            if re.match(f"^{regex}$", rel):
                return True
        elif rel == pattern or rel.endswith(f"/{pattern}"):
            return True
    return False


def extract_frontmatter(filepath: Path) -> tuple:
    """Extract YAML frontmatter from markdown file."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return None, f"Failed to read file: {e}"
    
    if not content.startswith('---'):
        return None, "Missing frontmatter delimiter (---)"
    
    end_match = re.search(r'^---\s*\n', content[3:], re.MULTILINE)
    if not end_match:
        return None, "Unclosed frontmatter delimiter"
    
    frontmatter_text = content[3:3+end_match.start()]
    try:
        fm = yaml.safe_load(frontmatter_text)
        if fm is None:
            return {}, None
        return fm, None
    except yaml.YAMLError as e:
        return None, f"Invalid YAML in frontmatter: {e}"


def validate_frontmatter(fm: Dict, filepath: Path) -> tuple:
    """Validate frontmatter against schema."""
    errors = []
    warnings = []
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    
    # Required keys
    for key in REQUIRED_KEYS:
        if key not in fm:
            errors.append(f"Missing required frontmatter key: {key}")
    
    # Type validation
    if 'type' in fm and fm['type'] not in VALID_TYPES:
        errors.append(f"Invalid type: {fm['type']}. Must be one of: {VALID_TYPES}")
    
    # Status validation
    if 'status' in fm and fm['status'] not in VALID_STATUSES:
        errors.append(f"Invalid status: {fm['status']}. Must be one of: {VALID_STATUSES}")
    
    # Owner validation
    if 'owner' in fm and fm['owner'] not in VALID_OWNERS:
        errors.append(f"Invalid owner: {fm['owner']}. Must be one of: {VALID_OWNERS}")
    
    # ID format (kebab-case)
    if 'id' in fm:
        id_val = fm['id']
        if not ID_PATTERN.match(str(id_val)):
            errors.append(f"id must be kebab-case (lowercase, alphanumeric with hyphens): {id_val}")
        if re.search(r'\d{10,}', str(id_val)):
            warnings.append(f"id may contain timestamp/random suffix (should be stable): {id_val}")
    
    # Namespace format
    if 'namespace' in fm:
        ns = fm['namespace']
        if not NAMESPACE_PATTERN.match(str(ns)):
            errors.append(f"namespace must be kebab-case path (e.g., knowledge/ai-core): {ns}")
    
    # Version format (semver)
    if 'version' in fm:
        ver = fm['version']
        if not VERSION_PATTERN.match(str(ver)):
            errors.append(f"version must be semver (e.g., 1.0.0): {ver}")
    
    # Created format (ISO8601)
    if 'created' in fm:
        created = fm['created']
        # Handle datetime objects (YAML parses ISO8601 as datetime)
        if hasattr(created, 'isoformat'):
            created_str = created.isoformat()
        else:
            created_str = str(created)
        if not CREATED_PATTERN.match(created_str):
            errors.append(f"created must be ISO8601 timestamp: {created_str}")
    
    # Canon requires operator approval
    if fm.get('status') == 'canon' and fm.get('owner') != 'operator':
        errors.append("canon status requires operator approval (owner must be 'operator')")
    
    # Candidate must have promotes_from
    if fm.get('status') == 'candidate':
        promotes_from = fm.get('promotes_from', [])
        if not promotes_from or len(promotes_from) == 0:
            warnings.append("candidate status should have promotes_from (source synthesis nodes)")
    
    # No self-promotion
    if 'promotes_to' in fm:
        promotes_to = fm['promotes_to']
        if isinstance(promotes_to, list) and fm.get('id') in promotes_to:
            errors.append("entity cannot promote to itself")
    
    return errors, warnings


def collect_all_entities() -> Dict[str, Dict]:
    """Collect all entity files and their frontmatter."""
    entities = {}
    for entity_dir in ENTITY_DIRS:
        if not entity_dir.exists():
            continue
        for md_file in entity_dir.rglob("*.md"):
            if is_plumbing(md_file):
                continue
            fm, err = extract_frontmatter(md_file)
            if err:
                continue
            if fm and 'id' in fm:
                entities[fm['id']] = {
                    'file': md_file,
                    'frontmatter': fm,
                    'namespace': fm.get('namespace', ''),
                    'type': fm.get('type', ''),
                    'status': fm.get('status', ''),
                }
    return entities


def run_startup_validation() -> ValidationState:
    """Main validation routine — runs on Hermes startup."""
    all_entities = collect_all_entities()
    all_entity_ids = set(all_entities.keys())
    
    results = []
    blocked = []
    dependency_graph = {}
    
    for entity_id, entity_info in all_entities.items():
        filepath = entity_info['file']
        fm = entity_info['frontmatter']
        
        errors, warnings = validate_frontmatter(fm, filepath)
        
        # Validate wikilinks
        wikilink_warnings = []
        try:
            content = filepath.read_text(encoding='utf-8')
            wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in wikilinks:
                link_id = link.split('|')[0].strip()
                if link_id not in all_entity_ids:
                    wikilink_warnings.append(f"Broken wikilink: [[{link}]] -> '{link_id}' not found")
        except:
            pass
        
        warnings.extend(wikilink_warnings)
        
        valid = len(errors) == 0
        if not valid:
            blocked.append(entity_id)
        
        # Extract dependencies
        depends_on = fm.get('depends_on', [])
        if depends_on:
            dependency_graph[entity_id] = depends_on
        
        result = EntityValidationResult(
            entity_id=entity_id,
            file_path=str(filepath.relative_to(REPO_ROOT)),
            valid=valid,
            errors=errors,
            warnings=warnings,
            frontmatter=fm,
            depends_on=depends_on
        )
        results.append(result)
    
    # Build validation state
    total = len(results)
    valid = sum(1 for r in results if r.valid)
    invalid = total - valid
    
    state = ValidationState(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_entities=total,
        valid_entities=valid,
        invalid_entities=invalid,
        blocked_entities=blocked,
        entity_results={r.entity_id: asdict(r) for r in results},
        dependency_graph=dependency_graph
    )
    
    # Save validation state
    CACHE.mkdir(parents=True, exist_ok=True)
    VALIDATION_STATE_FILE.write_text(
        json.dumps(asdict(state), indent=2, ensure_ascii=False, default=str),
        encoding='utf-8'
    )
    
    # Save dependency graph for memory_guard
    ENTITY_DEPENDENCY_GRAPH.write_text(
        json.dumps(dependency_graph, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    # Save blocked entities list
    BLOCKED_ENTITIES_FILE.write_text(
        json.dumps(blocked, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    # Emit event via event_bus if validation failed
    if invalid > 0:
        try:
            sys.path.insert(0, str(REPO_ROOT / "scripts"))
            from event_bus import emit
            emit("ibos_validation_failed", {
                "total": total,
                "valid": valid,
                "invalid": invalid,
                "blocked": blocked,
                "timestamp": state.timestamp
            })
        except:
            pass  # event_bus may not be available
    
    return state


def is_entity_blocked(entity_id: str) -> bool:
    """Check if an entity is blocked due to validation failure."""
    if BLOCKED_ENTITIES_FILE.exists():
        try:
            blocked = json.loads(BLOCKED_ENTITIES_FILE.read_text(encoding='utf-8'))
            return entity_id in blocked
        except:
            pass
    return False


def get_entity_dependencies(entity_id: str) -> List[str]:
    """Get dependencies for an entity (for chain execution)."""
    if ENTITY_DEPENDENCY_GRAPH.exists():
        try:
            graph = json.loads(ENTITY_DEPENDENCY_GRAPH.read_text(encoding='utf-8'))
            return graph.get(entity_id, [])
        except:
            pass
    return []


def get_validation_state() -> Optional[ValidationState]:
    """Load the last validation state."""
    if VALIDATION_STATE_FILE.exists():
        try:
            data = json.loads(VALIDATION_STATE_FILE.read_text(encoding='utf-8'))
            return ValidationState(**data)
        except:
            pass
    return None


def main():
    """CLI for manual validation."""
    if len(sys.argv) < 2:
        print("IBOS Entity Sensor")
        print("  validate    - Run full validation")
        print("  state       - Show last validation state")
        print("  blocked     - Show blocked entities")
        print("  deps <id>   - Show dependencies for entity")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "validate":
        state = run_startup_validation()
        print(f"Validation complete:")
        print(f"  Total: {state.total_entities}")
        print(f"  Valid: {state.valid_entities}")
        print(f"  Invalid: {state.invalid_entities}")
        print(f"  Blocked: {state.blocked_entities}")
        if state.invalid_entities > 0:
            for eid, result in state.entity_results.items():
                if not result['valid']:
                    print(f"\n  {eid}:")
                    for err in result['errors']:
                        print(f"    ERROR: {err}")
                    for warn in result['warnings']:
                        print(f"    WARN: {warn}")
    
    elif cmd == "state":
        state = get_validation_state()
        if state:
            print(f"Last validation: {state.timestamp}")
            print(f"  Total: {state.total_entities}")
            print(f"  Valid: {state.valid_entities}")
            print(f"  Invalid: {state.invalid_entities}")
            print(f"  Blocked: {state.blocked_entities}")
        else:
            print("No validation state found")
    
    elif cmd == "blocked":
        if BLOCKED_ENTITIES_FILE.exists():
            blocked = json.loads(BLOCKED_ENTITIES_FILE.read_text(encoding='utf-8'))
            print(f"Blocked entities ({len(blocked)}):")
            for eid in blocked:
                print(f"  {eid}")
        else:
            print("No blocked entities")
    
    elif cmd == "deps" and len(sys.argv) > 2:
        deps = get_entity_dependencies(sys.argv[2])
        print(f"Dependencies for {sys.argv[2]}:")
        for dep in deps:
            print(f"  {dep}")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()