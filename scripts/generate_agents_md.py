#!/usr/bin/env python3
"""
Local AGENTS.md generator for skills missing AGENTS.md.
Fast, no subagents, no timeouts.
"""

import json
import os
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(r"D:\Portable_Soft\hermes\skills")

def parse_frontmatter(content):
    """Parse YAML-like frontmatter from SKILL.md"""
    meta = {}
    if not content.startswith("---"):
        return meta
    parts = content.split("---", 2)
    if len(parts) < 3:
        return meta
    yaml_text = parts[1].strip()
    for line in yaml_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            if val.startswith("[") and val.endswith("]"):
                # Simple list parsing
                items = val[1:-1].split(",")
                meta[key] = [item.strip().strip('"\'') for item in items if item.strip()]
            else:
                meta[key] = val
    return meta

def has_agents_md(skill_dir):
    return (skill_dir / "AGENTS.md").exists()

def get_child_dox_index(skill_dir):
    """List references/, templates/, scripts/ if they exist"""
    items = []
    for name in ["references", "templates", "scripts"]:
        p = skill_dir / name
        if p.exists() and p.is_dir():
            files = [f.name for f in p.iterdir() if f.is_file()]
            if files:
                items.append(f"{name}/ ({len(files)} files)")
    return items

def generate_agents_md(skill_name, meta, skill_dir):
    """Generate AGENTS.md content"""
    description = meta.get("description", "")
    category = meta.get("category", "general")
    tags = meta.get("tags", [])
    triggers = meta.get("triggers", [])
    related = meta.get("related_skills", [])
    
    # Purpose
    purpose = description if description else f"Skill for {skill_name} operations."
    
    # Local Contracts
    contracts = []
    if triggers:
        contracts.append(f"- **Triggers**: {', '.join(triggers)}")
    if tags:
        contracts.append(f"- **Tags**: {', '.join(tags)}")
    if related:
        contracts.append(f"- **Related Skills**: {', '.join(related)}")
    contracts.append("- **Required Tools**: standard Hermes tools")
    contracts.append("- **Config**: config.yaml in skill dir (optional)")
    
    # Work Guidance
    guidance = f"""**When to use**: {description}
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first"""
    
    # Verification
    verification = """- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist"""
    
    # Child DOX Index
    child_index = get_child_dox_index(Path(r"D:\Portable_Soft\hermes\skills") / skill_name)
    index_lines = ["| File/Dir | Purpose |"]
    index_lines.append("|----------|---------|")
    for item in child_index:
        index_lines.append(f"| {item} | Reference materials |")
    if len(index_lines) == 2:
        index_lines.append("| (none) | |")
    
    content = f"""# {meta.get('name', skill_name)} — Skill

## Purpose
{purpose}

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
{chr(10).join(contracts)}

## Work Guidance
{guidance}

## Verification
{verification}

## Child DOX Index
{chr(10).join(index_lines)}
"""
    return content

def main():
    skills_root = SKILLS_DIR
    missing = []
    
    # Find all skill directories with SKILL.md but no AGENTS.md
    for skill_dir in skills_root.rglob("*"):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            if not has_agents_md(skill_dir):
                rel_path = skill_dir.relative_to(skills_root)
                missing.append((skill_dir, rel_path))
    
    print(f"Found {len(missing)} skills missing AGENTS.md")
    
    created = 0
    errors = 0
    
    for skill_dir, rel_path in missing:
        try:
            skill_name = rel_path.parts[0] if rel_path.parts else rel_path.name
            content = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
            meta = parse_frontmatter(content)
            meta.setdefault("name", skill_name)
            
            agents_content = generate_agents_md(skill_name, meta, skill_dir)
            (skill_dir / "AGENTS.md").write_text(agents_content, encoding="utf-8")
            
            print(f"  ✅ Created: {rel_path}")
            created += 1
        except Exception as e:
            print(f"  ❌ Error: {rel_path} - {e}")
            errors += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Created: {created}")
    print(f"Errors: {errors}")
    
    # Final audit
    import subprocess
    result = subprocess.run(["python", "scripts/skill_audit.py"], capture_output=True, text=True, cwd=r"D:\Portable_Soft\hermes")
    for line in result.stdout.split("\n"):
        if "Missing AGENTS.md" in line:
            print(line.strip())
            break

if __name__ == "__main__":
    main()