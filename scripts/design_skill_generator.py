#!/usr/bin/env python3
"""
Design Skill Generator — Creates new skills from extracted design patterns.
Implements: Skill Composition from Claude Code (pattern → skill).
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SKILLS_DIR = HERMES_HOME / "skills"
CACHE_DIR = HERMES_HOME / "cache" / "design"

SKILLS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class GeneratedSkill:
    """A skill generated from design patterns"""
    name: str
    description: str
    category: str
    version: str
    author: str = "Design Skill Generator"
    tags: List[str] = None
    triggers: List[str] = None
    related_skills: List[str] = None
    pattern_sources: List[str] = None
    patterns_used: List[str] = None
    components: List[str] = None
    code_templates: Dict[str, str] = None
    created_at: str = None


class DesignSkillGenerator:
    """Generates new skills from extracted design patterns"""
    
    def __init__(self):
        self.generated: List[GeneratedSkill] = []
        self._load_existing()
    
    def _load_existing(self):
        """Load existing generated skills"""
        generated_file = CACHE_DIR / "generated_skills.json"
        if generated_file.exists():
            try:
                data = json.loads(generated_file.read_text())
                for s in data.get("skills", []):
                    self.generated.append(GeneratedSkill(**s))
            except Exception:
                pass
    
    def _save(self):
        generated_file = CACHE_DIR / "generated_skills.json"
        data = {"skills": [asdict(s) for s in self.generated]}
        generated_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def generate_from_patterns(self, patterns: Dict, components: Dict) -> List[GeneratedSkill]:
        """Generate skills from extracted patterns and components"""
        new_skills = []
        
        # Group patterns by type
        by_type = {}
        for p in patterns.values():
            by_type.setdefault(p.pattern_type, []).append(p)
        
        # Generate skills for each pattern type
        for ptype, plist in by_type.items():
            if len(plist) >= 2:  # Need at least 2 patterns for a skill
                skill = self._create_pattern_skill(ptype, plist, components)
                if skill:
                    new_skills.append(skill)
        
        # Generate component-based skills
        by_comp_type = {}
        for c in components.values():
            by_comp_type.setdefault(c.type, []).append(c)
        
        for ctype, clist in by_comp_type.items():
            if len(clist) >= 1:
                skill = self._create_component_skill(ctype, clist)
                if skill:
                    new_skills.append(skill)
        
        # Save
        for skill in new_skills:
            self.generated.append(skill)
        self._save()
        
        return new_skills
    
    def _create_pattern_skill(self, ptype: str, patterns: List, components: Dict) -> Optional[GeneratedSkill]:
        """Create skill from pattern group"""
        name = f"design-{ptype}-patterns"
        
        # Build description
        pattern_names = [p.name for p in patterns]
        description = f"Applies {ptype} design patterns: {', '.join(pattern_names)}. Includes CSS/Tailwind implementations and usage contexts."
        
        # Collect all tailwind classes
        all_tw = []
        for p in patterns:
            all_tw.extend(p.tailwind_classes)
        all_tw = list(set(all_tw))
        
        # Build code templates
        code_templates = {}
        for p in patterns:
            if p.css_properties:
                code_templates[f"{p.name}_css"] = f"/* {p.name} */\n" + "\n".join(f"  {k}: {v};" for k, v in p.css_properties.items()) + "\n"
            if p.tailwind_classes:
                code_templates[f"{p.name}_tailwind"] = " ".join(p.tailwind_classes)
        
        # Related skills
        related = [f"design-{p.name.replace(' ', '-')}" for p in patterns]
        
        skill = GeneratedSkill(
            name=name,
            description=description,
            category=f"design-{ptype}",
            version="1.0.0",
            tags=[ptype, "design", "patterns", "css", "tailwind"] + pattern_names,
            triggers=[f"need {ptype} pattern"] + [f"apply {p.name}" for p in patterns],
            related_skills=related,
            pattern_sources=[p.id for p in patterns],
            patterns_used=[p.id for p in patterns],
            components=list(set().union(*[p.usage_context for p in patterns])),
            code_templates=code_templates,
            created_at=datetime.now().isoformat()
        )
        
        return skill
    
    def _create_component_skill(self, ctype: str, components: List) -> Optional[GeneratedSkill]:
        """Create skill from component group"""
        name = f"design-{ctype}-component"
        
        comp_names = [c.name for c in components]
        description = f"Provides reusable {ctype} components: {', '.join(comp_names)}. Includes HTML, CSS, Tailwind, and accessibility patterns."
        
        # Collect all tailwind
        all_tw = []
        for c in components:
            if c.tailwind_implementation:
                all_tw.append(c.tailwind_implementation)
        all_tw = list(set(all_tw))
        
        # Build code templates
        code_templates = {}
        for c in components:
            code_templates[f"{c.name}_html"] = c.html_structure
            code_templates[f"{c.name}_css"] = c.css_styles
            code_templates[f"{c.name}_tailwind"] = c.tailwind_implementation
        
        skill = GeneratedSkill(
            name=name,
            description=description,
            category=f"design-{ctype}",
            version="1.0.0",
            tags=[ctype, "design", "component", "html", "css", "tailwind", "accessibility"] + comp_names,
            triggers=[f"need {ctype} component"] + [f"create {c.name.lower()}" for c in components],
            related_skills=[f"design-{c.name.lower()}" for c in components],
            pattern_sources=[c.id for c in components],
            components=[ctype],
            code_templates=code_templates,
            created_at=datetime.now().isoformat()
        )
        
        return skill
    
    def write_skills_to_disk(self) -> int:
        """Write all generated skills to skills/ directory"""
        written = 0
        
        for skill in self.generated:
            skill_dir = SKILLS_DIR / "design" / skill.name
            skill_dir.mkdir(parents=True, exist_ok=True)
            
            # Write SKILL.md
            skill_md = self._render_skill_md(skill)
            (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
            
            # Write AGENTS.md
            agents_md = self._render_agents_md(skill)
            (skill_dir / "AGENTS.md").write_text(agents_md, encoding="utf-8")
            
            # Write code templates
            templates_dir = skill_dir / "templates"
            templates_dir.mkdir(exist_ok=True)
            for fname, content in skill.code_templates.items():
                ext = ".css" if fname.endswith("_css") else (".html" if fname.endswith("_html") else ".txt")
                (templates_dir / f"{fname}{ext}").write_text(content, encoding="utf-8")
            
            # Write config.yaml
            config = {
                "name": skill.name,
                "version": skill.version,
                "category": skill.category,
                "patterns_used": skill.patterns_used,
                "components": skill.components,
                "templates_dir": "templates"
            }
            (skill_dir / "config.yaml").write_text(json.dumps(config, indent=2), encoding="utf-8")
            
            written += 1
            print(f"[SKILL_GENERATOR] Written: {skill.name} -> {skill_dir}")
        
        return written
    
    def _render_skill_md(self, skill: GeneratedSkill) -> str:
        """Render SKILL.md frontmatter + body"""
        return f"""---
name: {skill.name}
description: "{skill.description}"
version: {skill.version}
author: {skill.author}
tags:
{chr(10).join(f"  - {t}" for t in (skill.tags or []))}
category: {skill.category}
triggers:
{chr(10).join(f"  - {t}" for t in (skill.triggers or []))}
related_skills:
{chr(10).join(f"  - {s}" for s in (skill.related_skills or []))}
---

# {skill.name}

{skill.description}

## Patterns Used
{chr(10).join(f"- {p}" for p in (skill.patterns_used or []))}

## Components
{chr(10).join(f"- {c}" for c in (skill.components or []))}

## Code Templates
Available in `templates/`:
{chr(10).join(f"- {fname}" for fname in (skill.code_templates or {}).keys())}

## Usage
```yaml
# Load skill
skill: {skill.name}

# Triggers
{chr(10).join(f"- {t}" for t in (skill.triggers or []))}
```

## Related Skills
{chr(10).join(f"- {s}" for s in (skill.related_skills or []))}

---

*Generated: {skill.created_at}*
*Pattern Sources: {len(skill.pattern_sources or [])}*
"""
    
    def _render_agents_md(self, skill: GeneratedSkill) -> str:
        """Render AGENTS.md"""
        return f"""# {skill.name} — Skill

## Purpose
{skill.description}

## Ownership
Managed by Hermes Agent. Self-contained skill with templates.

## Local Contracts
- **Triggers**: {', '.join(skill.triggers or [])}
- **Required tools**: standard Hermes tools
- **Config**: config.yaml in skill dir

## Work Guidance
**When to use**: {skill.description}
**Common patterns**: {', '.join(skill.patterns_used or [])}
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in templates/
- Verify templates/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `templates/` | Code templates (HTML, CSS, Tailwind) |
| `config.yaml` | Skill configuration |
| `SKILL.md` | This skill definition |
| `AGENTS.md` | This file |
"""
    
    def list_generated(self) -> List[Dict]:
        """List all generated skills"""
        return [asdict(s) for s in self.generated]


# CLI
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python design_skill_generator.py <command>")
        print("Commands: generate, write, list")
        sys.exit(1)
    
    # Load patterns and components from analyzers
    from design_analyzer import DesignAnalyzer
    from design_reference_collector import DesignReferenceCollector
    
    collector = DesignReferenceCollector()
    analyzer = DesignAnalyzer()
    
    # Analyze all references
    for ref in collector.references.values():
        analyzer.analyze_reference(ref)
    analyzer.extract_components_from_refs(collector.references.values())
    
    generator = DesignSkillGenerator()
    
    cmd = sys.argv[1]
    
    if cmd == "generate":
        skills = generator.generate_from_patterns(analyzer.patterns, analyzer.components)
        print(f"Generated {len(skills)} skills:")
        for s in skills:
            print(f"  - {s.name}")
    
    elif cmd == "write":
        count = generator.write_skills_to_disk()
        print(f"Written {count} skills to skills/design/")
    
    elif cmd == "list":
        for s in generator.generated:
            print(f"{s.name}: {s.description[:80]}...")
    
    else:
        print(f"Unknown command: {sys.argv[1]}")


if __name__ == "__main__":
    main()