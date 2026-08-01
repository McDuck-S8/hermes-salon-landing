#!/usr/bin/env python3
"""
Hermes + Infinite Brain OS Validator
Validates all entity files for frontmatter schema compliance, link integrity, and governance rules.

> Revisit: when entity validation rules, IBOS schema, or entity lifecycle changes. Last touched: 2026-07-02.

Usage:
    python scripts/validate_entities.py
    python scripts/validate_entities.py --fix
    python scripts/validate_entities.py --report
"""

import os
import sys
import yaml
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

REPO_ROOT = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes")).resolve()
SCHEMA_PATH = REPO_ROOT / "_system" / "schemas" / "frontmatter.schema.yaml"

@dataclass
class ValidationResult:
    file_path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    frontmatter: Dict = field(default_factory=dict)
    is_plumbing: bool = False

@dataclass
class Schema:
    required_keys: List[str]
    optional_keys: List[str]
    valid_types: List[str]
    valid_statuses: List[str]
    valid_owners: List[str]
    valid_retrieval_classes: List[str]
    valid_export_classes: List[str]
    namespace_profiles: List[Dict]
    rules: List[Dict]
    plumbing_patterns: List[str]

def load_schema() -> Schema:
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return Schema(**data)

SCHEMA = load_schema()

def is_plumbing(filepath: Path) -> bool:
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    for pattern in SCHEMA.plumbing_patterns:
        if pattern.endswith('/'):
            if rel.startswith(pattern) or f"/{pattern}" in f"/{rel}":
                return True
        else:
            if rel == pattern or rel.endswith(f"/{pattern}"):
                return True
            if '*' in pattern:
                regex = pattern.replace('*', '[^/]+')
                if re.match(f"^{regex}$", rel):
                    return True
    return False

def extract_frontmatter(filepath: Path) -> Tuple[Optional[Dict], Optional[str]]:
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

def validate_frontmatter(frontmatter: Dict, filepath: Path) -> Tuple[List[str], List[str]]:
    errors = []
    warnings = []
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    
    for key in SCHEMA.required_keys:
        if key not in frontmatter:
            errors.append(f"Missing required frontmatter key: {key}")
    
    all_keys = set(SCHEMA.required_keys) | set(SCHEMA.optional_keys)
    for key in frontmatter:
        if key not in all_keys:
            warnings.append(f"Unknown frontmatter key: {key} (not in schema)")
    
    if 'type' in frontmatter:
        if frontmatter['type'] not in SCHEMA.valid_types:
            errors.append(f"Invalid type: {frontmatter['type']}. Must be one of: {SCHEMA.valid_types}")
    
    if 'status' in frontmatter:
        if frontmatter['status'] not in SCHEMA.valid_statuses:
            errors.append(f"Invalid status: {frontmatter['status']}. Must be one of: {SCHEMA.valid_statuses}")
    
    if 'owner' in frontmatter:
        if frontmatter['owner'] not in SCHEMA.valid_owners:
            errors.append(f"Invalid owner: {frontmatter['owner']}. Must be one of: {SCHEMA.valid_owners}")
    
    if 'retrieval_class' in frontmatter:
        if frontmatter['retrieval_class'] not in SCHEMA.valid_retrieval_classes:
            warnings.append(f"Invalid retrieval_class: {frontmatter['retrieval_class']}. Must be one of: {SCHEMA.valid_retrieval_classes}")
    
    if 'export_class' in frontmatter:
        if frontmatter['export_class'] not in SCHEMA.valid_export_classes:
            warnings.append(f"Invalid export_class: {frontmatter['export_class']}. Must be one of: {SCHEMA.valid_export_classes}")
    
    if 'id' in frontmatter:
        id_val = frontmatter['id']
        if not re.match(r'^[a-z0-9-]+$', str(id_val)):
            errors.append(f"id must be kebab-case (lowercase, alphanumeric with hyphens): {id_val}")
        if re.search(r'\d{10,}', str(id_val)):
            warnings.append(f"id may contain timestamp/random suffix (should be stable): {id_val}")
    
    if 'namespace' in frontmatter:
        ns = frontmatter['namespace']
        if not re.match(r'^[a-z0-9-]+(/[a-z0-9-]+)*$', str(ns)):
            errors.append(f"namespace must be kebab-case path (e.g., knowledge/ai-core): {ns}")
    
    if 'version' in frontmatter:
        ver = frontmatter['version']
        if not re.match(r'^\d+\.\d+\.\d+$', str(ver)):
            errors.append(f"version must be semver (e.g., 1.0.0): {ver}")
    
    if 'created' in frontmatter:
        created = frontmatter['created']
        # Handle both string and datetime objects (YAML parses ISO8601 as datetime)
        if hasattr(created, 'isoformat'):
            created_str = created.isoformat()
        else:
            created_str = str(created)
        if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$', created_str):
            errors.append(f"created must be ISO8601 timestamp: {created_str}")
    
    if 'confidence' in frontmatter:
        try:
            conf = float(frontmatter['confidence'])
            if not (0.0 <= conf <= 1.0):
                warnings.append(f"confidence must be between 0.0 and 1.0: {conf}")
        except (ValueError, TypeError):
            warnings.append(f"confidence must be a number: {frontmatter['confidence']}")
    
    if frontmatter.get('status') == 'canon' and frontmatter.get('owner') != 'operator':
        errors.append("canon status requires operator approval (owner must be 'operator')")
    
    if frontmatter.get('status') == 'candidate':
        promotes_from = frontmatter.get('promotes_from', [])
        if not promotes_from or len(promotes_from) == 0:
            warnings.append("candidate status should have promotes_from (source synthesis nodes)")
    
    if 'promotes_to' in frontmatter:
        promotes_to = frontmatter['promotes_to']
        if isinstance(promotes_to, list) and frontmatter.get('id') in promotes_to:
            errors.append("entity cannot promote to itself")
    
    return errors, warnings

def validate_wikilinks(filepath: Path, all_entity_ids: Set[str]) -> List[str]:
    warnings = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except:
        return warnings
    
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
    for link in wikilinks:
        link_id = link.split('|')[0].strip()
        if link_id not in all_entity_ids:
            warnings.append(f"Broken wikilink: [[{link}]] -> '{link_id}' not found in entity registry")
    
    return warnings

def collect_all_entities() -> Dict[str, Dict]:
    entities = {}
    entity_dirs = [
        REPO_ROOT / "entities" / "commands",
        REPO_ROOT / "entities" / "agents",
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
    
    for entity_dir in entity_dirs:
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

def validate_namespace_structure() -> Tuple[List[str], List[str]]:
    errors = []
    warnings = []
    
    knowledge_dir = REPO_ROOT / "knowledge"
    if not knowledge_dir.exists():
        return errors, warnings
    
    for ns_dir in knowledge_dir.iterdir():
        if not ns_dir.is_dir() or ns_dir.name.startswith('_') or ns_dir.name.startswith('.'):
            continue
        
        index_file = ns_dir / "INDEX.md"
        canon_dir = ns_dir / "canon"
        
        if not index_file.exists() and not canon_dir.exists():
            continue
        
        ns_profile = get_namespace_profile(ns_dir.name)
        
        if ns_profile and ns_profile.get('reduced_base'):
            required = ns_profile.get('required_surfaces', ['INDEX.md', 'canon/'])
        else:
            required = ['INDEX.md', 'canon/', 'playbooks/', 'support/', 'synthesis/']
        
        for surface in required:
            if surface.endswith('/'):
                if not (ns_dir / surface.rstrip('/')).exists():
                    errors.append(f"Namespace {ns_dir.name}: missing required surface {surface}")
            else:
                if not (ns_dir / surface).exists():
                    errors.append(f"Namespace {ns_dir.name}: missing required surface {surface}")
        
        if ns_profile and ns_profile.get('core_file'):
            core_file = ns_dir / "canon" / ns_profile['core_file']
            if not core_file.exists():
                errors.append(f"Namespace {ns_dir.name}: missing required canon file {ns_profile['core_file']}")
    
    return errors, warnings

def get_namespace_profile(namespace_slug: str) -> Optional[Dict]:
    ns_file = REPO_ROOT / "_system" / "namespaces" / f"{namespace_slug}.md"
    if ns_file.exists():
        fm, _ = extract_frontmatter(ns_file)
        if fm:
            return fm
    
    for profile in SCHEMA.namespace_profiles:
        if profile['name'] == namespace_slug:
            return profile
    
    return None

def run_validator(fix: bool = False) -> Dict:
    print(f"=== Hermes + IBOS Validator ===")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Schema: {SCHEMA_PATH}")
    print()
    
    results = []
    all_entities = collect_all_entities()
    all_entity_ids = set(all_entities.keys())
    
    print(f"Found {len(all_entities)} entities")
    
    for entity_id, entity_info in all_entities.items():
        filepath = entity_info['file']
        fm = entity_info['frontmatter']
        
        errors, warnings = validate_frontmatter(fm, filepath)
        
        wikilink_warnings = validate_wikilinks(filepath, all_entity_ids)
        warnings.extend(wikilink_warnings)
        
        result = ValidationResult(
            file_path=str(filepath.relative_to(REPO_ROOT)),
            errors=errors,
            warnings=warnings,
            frontmatter=fm,
            is_plumbing=False
        )
        results.append(result)
    
    ns_errors, ns_warnings = validate_namespace_structure()
    for err in ns_errors:
        print(f"  [NAMESPACE ERROR] {err}")
    for warn in ns_warnings:
        print(f"  [NAMESPACE WARN] {warn}")
    
    total_errors = sum(len(r.errors) for r in results) + len(ns_errors)
    total_warnings = sum(len(r.warnings) for r in results) + len(ns_warnings)
    
    print()
    print(f"=== SUMMARY ===")
    print(f"Entities validated: {len(results)}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    
    if total_errors > 0:
        print()
        print("ERRORS:")
        for r in results:
            for err in r.errors:
                print(f"  {r.file_path}: {err}")
        for err in ns_errors:
            print(f"  [namespace] {err}")
    
    if total_warnings > 0:
        print()
        print("WARNINGS:")
        for r in results:
            for warn in r.warnings:
                print(f"  {r.file_path}: {warn}")
        for warn in ns_warnings:
            print(f"  [namespace] {warn}")
    
    return {
        'results': results,
        'total_errors': total_errors,
        'total_warnings': total_warnings,
        'entities': all_entities,
        'namespace_errors': ns_errors,
        'namespace_warnings': ns_warnings,
    }

def generate_report(validation_result: Dict) -> str:
    lines = []
    lines.append("# Validation Report")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Repo: {REPO_ROOT}")
    lines.append(f"Schema: {SCHEMA_PATH}")
    lines.append("")
    lines.append(f"## Summary")
    lines.append(f"- Entities: {len(validation_result['results'])}")
    lines.append(f"- Errors: {validation_result['total_errors']}")
    lines.append(f"- Warnings: {validation_result['total_warnings']}")
    lines.append("")
    
    if validation_result['total_errors'] > 0:
        lines.append("## Errors")
        for r in validation_result['results']:
            for err in r.errors:
                lines.append(f"- `{r.file_path}`: {err}")
        for err in validation_result['namespace_errors']:
            lines.append(f"- `[namespace]` {err}")
        lines.append("")
    
    if validation_result['total_warnings'] > 0:
        lines.append("## Warnings")
        for r in validation_result['results']:
            for warn in r.warnings:
                lines.append(f"- `{r.file_path}`: {warn}")
        for warn in validation_result['namespace_warnings']:
            lines.append(f"- `[namespace]` {warn}")
        lines.append("")
    
    lines.append("## Entity Registry")
    lines.append("")
    lines.append("| ID | Type | Namespace | Status | File |")
    lines.append("|----|------|-----------|--------|------|")
    for entity_id, info in sorted(validation_result['entities'].items()):
        rel = info['file'].relative_to(REPO_ROOT).as_posix()
        fm = info['frontmatter']
        lines.append(f"| {entity_id} | {fm.get('type', '?')} | {fm.get('namespace', '?')} | {fm.get('status', '?')} | {rel} |")
    
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Hermes + IBOS Entity Validator')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix common issues (not implemented)')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    
    result = run_validator(fix=args.fix)
    
    if args.report:
        report = generate_report(result)
        report_path = REPO_ROOT / "_system" / "validation_report.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"\nReport written to: {report_path}")
    
    if args.json:
        json_out = {
            'total_errors': result['total_errors'],
            'total_warnings': result['total_warnings'],
            'entities_count': len(result['entities']),
            'errors': [
                {'file': r.file_path, 'error': err}
                for r in result['results'] for err in r.errors
            ],
            'warnings': [
                {'file': r.file_path, 'warning': warn}
                for r in result['results'] for warn in r.warnings
            ],
        }
        print(json.dumps(json_out, indent=2))
    
    sys.exit(1 if result['total_errors'] > 0 else 0)

if __name__ == "__main__":
    main()