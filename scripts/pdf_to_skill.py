#!/usr/bin/env python3
"""
PDF to Skill Converter — Integration of BookToSkill with Hermes Agent.
Converts any PDF/document into a Hermes-compatible Skill (SKILL.md + AGENTS.md + assets).
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
BOOKTOSKILL_DIR = HERMES_HOME / "BookToSkill"
SKILLS_DIR = HERMES_HOME / "skills"

sys.path.insert(0, str(BOOKTOSKILL_DIR))
sys.path.insert(0, str(HERMES_HOME / "scripts"))

from book_to_skill import convert_pdf_to_skill
from hermes_engine import SkillSynthesizer

class PDFToSkillConverter:
    """Wrapper that produces Hermes-compatible skill structure."""
    
    def __init__(self, model: str = "granite4.1:3b", mode: str = "text"):
        self.model = model
        self.mode = mode
        self.synthesizer = SkillSynthesizer(model_name=model)
    
    def convert(self, pdf_path: str, skill_name: str = None, output_base: Path = None) -> Dict[str, Any]:
        """Convert PDF to Hermes skill structure."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if not skill_name:
            skill_name = pdf_path.stem.lower().replace(" ", "-").replace("_", "-")
        
        if output_base is None:
            output_base = SKILLS_DIR
        
        skill_dir = output_base / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Chapter output dir
        chapters_dir = skill_dir / "chapters"
        chapters_dir.mkdir(exist_ok=True)
        
        print(f"\n📚 Converting: {pdf_path.name} → {skill_name}")
        print(f"📁 Output: {skill_dir}")
        
        start_time = time.time()
        
        # Step 1: Extract using BookToSkill
        print("🔍 Extracting content...")
        result = convert_pdf_to_skill(
            str(pdf_path),
            str(skill_dir),
            model_name=self.model,
            mode=self.mode
        )
        
        # Step 2: Generate Hermes AGENTS.md
        print("📝 Generating AGENTS.md...")
        self._generate_agents_md(skill_dir, skill_name, result.get("book_title", skill_name))
        
        # Step 3: Update SKILL.md with Hermes format
        print("🔧 Finalizing SKILL.md...")
        self._finalize_skill_md(skill_dir, skill_name, result.get("book_title", skill_name))
        
        # Step 4: Create skill metadata
        print("📋 Creating skill metadata...")
        self._create_skill_json(skill_dir, skill_name, result)
        
        elapsed = round(time.time() - start_time, 2)
        print(f"\n✅ Skill '{skill_name}' created in {elapsed}s")
        print(f"📁 Location: {skill_dir}")
        
        return {
            "skill_name": skill_name,
            "skill_dir": str(skill_dir),
            "book_title": result.get("book_title", skill_name),
            "elapsed_seconds": elapsed,
            "chapters": len(list(chapters_dir.glob("*.md"))) if chapters_dir.exists() else 0
        }
    
    def _generate_agents_md(self, skill_dir: Path, skill_name: str, book_title: str):
        """Generate AGENTS.md for the skill."""
        agents_md = f"""# {book_title} Skill — Agent Contract

## Purpose
This skill provides structured knowledge from **{book_title}** as an AI Agent capability.
Use when you need to apply concepts, frameworks, or methods from this source.

## Ownership
- **Domain**: knowledge-extraction
- **Source**: {book_title} (PDF → Skill conversion)
- **Generated**: Auto-generated via BookToSkill + Hermes Engine
- **Maintainer**: Hermes Agent

## Local Contracts
1. **Core Mental Models** — Apply the fundamental mental models from the source
2. **Frameworks & Decision Rules** — Use provided frameworks for problem-solving
3. **Chapter Reference** — Access detailed chapter breakdowns in `chapters/`
4. **Glossary** — Terminology in `glossary.md`
5. **Patterns** — Reusable patterns in `patterns.md`
6. **Cheatsheet** — Quick reference in `cheatsheet.md`

## Work Guidance
- When user asks about concepts from {book_title}, use this skill
- For deep-dive: read relevant chapter in `chapters/`
- For quick lookup: check `cheatsheet.md` or `glossary.md`
- For implementation: follow patterns in `patterns.md`

## Verification
- Run `python -m pytest skills/{skill_name}/tests/` if tests exist
- Validate SKILL.md structure matches Hermes skill specification

## Child DOX Index
| File | Purpose |
|------|---------|
| `SKILL.md` | Master skill specification |
| `AGENTS.md` | This file — agent contract |
| `glossary.md` | Key terms & definitions |
| `patterns.md` | Core patterns & methods |
| `cheatsheet.md` | Quick reference |
| `chapters/` | Per-chapter deep dives |
"""
        (skill_dir / "AGENTS.md").write_text(agents_md, encoding="utf-8")
    
    def _finalize_skill_md(self, skill_dir: Path, skill_name: str, book_title: str):
        """Ensure SKILL.md follows Hermes format."""
        skill_md_path = skill_dir / "SKILL.md"
        if not skill_md_path.exists():
            return
        
        content = skill_md_path.read_text(encoding="utf-8")
        
        # Ensure proper frontmatter
        if not content.startswith("---"):
            frontmatter = f"""---
name: {skill_name}
description: "Extracted knowledge from '{book_title}' — core mental models, frameworks, patterns, and chapter reference."
trigger: "When user asks about {book_title} concepts, frameworks, or methods"
usage: {skill_name}
---

"""
            content = frontmatter + content
            skill_md_path.write_text(content, encoding="utf-8")
    
    def _create_skill_json(self, skill_dir: Path, skill_name: str, result: Dict):
        """Create skill.json metadata file."""
        metadata = {
            "name": skill_name,
            "source_book": result.get("book_title", skill_name),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "generator": "BookToSkill + Hermes Engine",
            "version": "1.0",
            "files": {
                "skill_md": "SKILL.md",
                "agents_md": "AGENTS.md",
                "glossary": "glossary.md",
                "patterns": "patterns.md",
                "cheatsheet": "cheatsheet.md",
                "chapters_dir": "chapters/"
            }
        }
        (skill_dir / "skill.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def main():
    parser = argparse.ArgumentParser(description="Convert PDF to Hermes Skill")
    parser.add_argument("input", help="Path to PDF file")
    parser.add_argument("-n", "--name", help="Skill name (default: from filename)")
    parser.add_argument("-o", "--output", help="Output directory (default: skills/)")
    parser.add_argument("--model", default="granite4.1:3b", help="Ollama model name")
    parser.add_argument("--mode", default="text", choices=["text", "technical"], help="Extraction mode")
    
    args = parser.parse_args()
    
    output_base = Path(args.output) if args.output else None
    converter = PDFToSkillConverter(model=args.model, mode=args.mode)
    
    result = converter.convert(args.input, args.name, output_base)
    
    print(f"\n🎉 Done! Skill: {result['skill_name']}")
    print(f"📂 {result['skill_dir']}")
    print(f"📖 {result['book_title']}")
    print(f"⏱️ {result['elapsed_seconds']}s | Chapters: {result['chapters']}")


if __name__ == "__main__":
    import time
    main()