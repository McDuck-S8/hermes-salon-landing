#!/usr/bin/env python3
"""
Skill Composer — Dynamic Agent Assembly from Skills
Implements: Skill Composition from Claude Code (Flowise-style visual agent builder)

Combines multiple skills into a unified subagent with shared context.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SKILLS_DIR = HERMES_HOME / "skills"


@dataclass
class SkillSpec:
    """Specification for a skill component"""
    name: str
    path: Path
    category: str
    triggers: List[str]
    tools: List[str]
    description: str


@dataclass
class ComposedAgent:
    """A dynamically composed agent from multiple skills"""
    name: str
    skills: List[SkillSpec]
    combined_triggers: List[str]
    combined_tools: List[str]
    description: str
    system_prompt: str


class SkillComposer:
    """Dynamically composes agents from existing skills"""
    
    def __init__(self):
        self.skills_cache: Dict[str, SkillSpec] = {}
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all skill specifications from skills/ directory"""
        for skill_dir in SKILLS_DIR.rglob("SKILL.md"):
            try:
                content = skill_dir.read_text(encoding="utf-8")
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1])
                        rel_path = skill_dir.parent.relative_to(SKILLS_DIR)
                        category = str(rel_path).split("\\")[0] if "\\" in str(rel_path) else str(rel_path).split("/")[0]
                        
                        self.skills_cache[frontmatter.get("name", rel_path.name)] = SkillSpec(
                            name=frontmatter.get("name", rel_path.name),
                            path=skill_dir.parent,
                            category=category,
                            triggers=frontmatter.get("triggers", []),
                            tools=frontmatter.get("tools", []),
                            description=frontmatter.get("description", "")
                        )
            except Exception:
                continue
    
    def find_skills_for_task(self, task: str, max_skills: int = 3) -> List[SkillSpec]:
        """Find best matching skills for a task using trigger matching"""
        task_lower = task.lower()
        scored = []
        
        for spec in self.skills_cache.values():
            score = 0
            for trigger in spec.triggers:
                if trigger.lower() in task_lower:
                    score += 2
            # Keyword overlap
            for word in spec.description.lower().split():
                if word in task_lower and len(word) > 3:
                    score += 1
            if score > 0:
                scored.append((score, spec))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:max_skills]]
    
    def compose_agent(self, name: str, task: str, skills: List[SkillSpec] = None) -> ComposedAgent:
        """Compose a unified agent from selected skills"""
        if skills is None:
            skills = self.find_skills_for_task(task)
        
        if not skills:
            raise ValueError("No matching skills found for task")
        
        # Merge triggers and tools
        all_triggers = []
        all_tools = []
        for s in skills:
            all_triggers.extend(s.triggers)
            all_tools.extend(s.tools)
        
        # Build system prompt
        skill_blocks = []
        for i, s in enumerate(skills, 1):
            skill_blocks.append(f"""
### Skill {i}: {s.name} ({s.category})
**Purpose:** {s.description}
**Triggers:** {', '.join(s.triggers) or 'auto'}
**Tools:** {', '.join(s.tools) or 'all'}
**Path:** {s.path}
""")
        
        system_prompt = f"""You are a COMPOSED AGENT: {name}

You are dynamically assembled from {len(skills)} skills to handle: {task}

Your component skills:
{''.join(skill_blocks)}

EXECUTION RULES:
1. You have ALL tools from all component skills
2. Route sub-tasks to the most relevant skill internally
3. Maintain unified context across all skills
4. Output final result as single coherent response
5. Log which skill handled each sub-task for traceability
"""
        
        return ComposedAgent(
            name=name,
            skills=skills,
            combined_triggers=list(set(all_triggers)),
            combined_tools=list(set(all_tools)),
            description=f"Composed from {len(skills)} skills: {', '.join(s.name for s in skills)}",
            system_prompt=system_prompt
        )
    
    def save_composed_agent(self, agent: ComposedAgent, output_dir: Path = None) -> Path:
        """Save composed agent as runnable specification"""
        if output_dir is None:
            output_dir = HERMES_HOME / "cache" / "composed_agents"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        agent_file = output_dir / f"{agent.name}.json"
        agent_file.write_text(json.dumps(asdict(agent), default=str, indent=2, ensure_ascii=False))
        
        # Also save runnable prompt
        prompt_file = output_dir / f"{agent.name}_prompt.md"
        prompt_file.write_text(agent.system_prompt)
        
        return agent_file
    
    def list_available_skills(self) -> List[Dict]:
        """List all available skills for manual composition"""
        return [
            {
                "name": s.name,
                "category": s.category,
                "description": s.description[:100],
                "triggers": s.triggers[:5],
                "tools": s.tools[:5]
            }
            for s in self.skills_cache.values()
        ]


# CLI
def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python skill_composer.py <agent_name> <task> [skill1,skill2,...]")
        print("Example: python skill_composer.py research_agent 'analyze competitors and write report' research,web-search,writing")
        sys.exit(1)
    
    name = sys.argv[1]
    task = sys.argv[2]
    forced_skills = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    
    composer = SkillComposer()
    
    if forced_skills:
        skills = [composer.skills_cache[n] for n in forced_skills if n in composer.skills_cache]
    else:
        skills = composer.find_skills_for_task(task)
    
    agent = composer.compose_agent(name, task, skills)
    agent_file = composer.save_composed_agent(agent)
    
    print(f"\n✅ Composed agent: {agent.name}")
    print(f"Skills: {', '.join(s.name for s in agent.skills)}")
    print(f"Tools: {', '.join(agent.combined_tools)}")
    print(f"Saved to: {agent_file}")
    print(f"\nSystem prompt saved to: {str(agent_file).replace('.json', '_prompt.md')}")


if __name__ == "__main__":
    main()