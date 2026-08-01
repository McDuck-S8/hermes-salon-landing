#!/usr/bin/env python3
"""
Suggestion Applier — Applies critical suggestions from the queue.
Automatically registers skills, fixes code, updates configs.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
QUEUE_FILE = HERMES_HOME / "cache" / "suggestion_queue.json"
APPLIED_LOG = HERMES_HOME / "cache" / "applied_suggestions.json"

class SuggestionApplier:
    """Applies suggestions from the queue."""
    
    def __init__(self):
        self.queue_file = QUEUE_FILE
        self.applied_log = APPLIED_LOG
        self.applied_log.parent.mkdir(parents=True, exist_ok=True)
    
    def load_queue(self) -> List[Dict]:
        """Load suggestion queue."""
        if not self.queue_file.exists():
            return []
        try:
            return json.loads(self.queue_file.read_text(encoding="utf-8"))
        except Exception:
            return []
    
    def save_queue(self, queue: List[Dict]):
        """Save updated queue."""
        self.queue_file.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def load_applied(self) -> List[Dict]:
        """Load applied suggestions log."""
        if not self.applied_log.exists():
            return []
        try:
            data = json.loads(self.applied_log.read_text(encoding="utf-8"))
            # Handle both old format (list) and new format (dict with "failed" key)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "failed" in data:
                return data["failed"]
            return []
        except Exception:
            return []
    
    def save_applied(self, applied: List[Dict]):
        """Save applied log."""
        self.applied_log.write_text(json.dumps(applied, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def apply_suggestion(self, suggestion: Dict) -> bool:
        """Apply a single suggestion."""
        payload = suggestion.get("payload", {})
        source = payload.get("source", "")
        inner = payload.get("payload", {})
        action = inner.get("action", "")
        
        if source == "skill_usage_analyzer" and action == "register_skill":
            return self._register_skill(inner)
        
        if source == "maintenance_scanner" and action == "add_revisit":
            return self._add_revisit(inner)
        
        if source == "subagent_verifier" and action == "fix_file":
            return self._fix_file(inner)
        
        return False
    
    def _register_skill(self, payload: Dict) -> bool:
        """Register skill in CLAUDE.md and .claude/rules/always.md."""
        skill_name = payload.get("skill")
        skill_path = Path(payload.get("skill_path", ""))
        target_files = payload.get("target_files", [])
        
        if not skill_name or not skill_path.exists():
            print(f"  ✗ Skill path not found: {skill_path}")
            return False
        
        # Read skill metadata
        skill_md = skill_path / "SKILL.md"
        skill_desc = ""
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            # Extract description from frontmatter or first paragraph
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = parts[1]
                    for line in fm.split("\n"):
                        if line.startswith("description:"):
                            skill_desc = line.split(":", 1)[1].strip().strip('"')
                            break
        
        skill_entry = f"- **{skill_name}** ({skill_path.name}) — {skill_desc or 'Auto-registered skill'}"
        
        success_count = 0
        for target_file in target_files:
            target_path = HERMES_HOME / target_file
            if not target_path.exists():
                print(f"  ⚠ Target file not found: {target_file}")
                continue
            
            content = target_path.read_text(encoding="utf-8")
            
            # Check if already registered
            if skill_name in content:
                print(f"  ✓ Already registered in {target_file}")
                success_count += 1
                continue
            
            # Add skill reference
            if target_file == "CLAUDE.md":
                # Add to skills section or create one
                if "## Skills" in content:
                    content = content.replace(
                        "## Skills",
                        f"## Skills\n{skill_entry}"
                    )
                elif "### Available Skills" in content:
                    content = content.replace(
                        "### Available Skills",
                        f"### Available Skills\n{skill_entry}"
                    )
                else:
                    # Add at end of file
                    content = content.rstrip() + f"\n\n## Skills\n{skill_entry}\n"
            
            elif target_file == ".claude/rules/always.md":
                # Add to skills section in rules
                if "## Skills" in content:
                    content = content.replace(
                        "## Skills",
                        f"## Skills\n- Use **{skill_name}** skill for {skill_desc or 'related tasks'}"
                    )
                elif "# ALWAYS.md" in content:
                    # Add after header
                    parts = content.split("# ALWAYS.md", 1)
                    if len(parts) == 2:
                        content = parts[0] + "# ALWAYS.md\n\n## Skills\n- Use **" + skill_name + "** skill for " + (skill_desc or "related tasks") + "\n" + parts[1]
                else:
                    content = content.rstrip() + f"\n\n## Skills\n- Use **{skill_name}** skill for {skill_desc or 'related tasks'}\n"
            
            else:
                # Generic: add at end
                content = content.rstrip() + f"\n\n## Skills\n{skill_entry}\n"
            
            # Backup and write
            backup = target_path.with_suffix(target_path.suffix + ".bak")
            shutil.copy2(target_path, backup)
            target_path.write_text(content, encoding="utf-8")
            
            print(f"  ✓ Registered {skill_name} in {target_file}")
            success_count += 1
        
        return success_count > 0
    
    def _add_revisit(self, payload: Dict) -> bool:
        """Add Revisit frontmatter to files."""
        files = payload.get("files", [])
        date_str = payload.get("revisit_date", datetime.now().strftime("%Y-%m-%d"))
        
        for file_path in files:
            path = HERMES_HOME / file_path
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            if "Revisit:" in content:
                continue
            if content.startswith("---"):
                # Insert after first ---
                lines = content.split("\n")
                insert_idx = 1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == "---":
                        insert_idx = i + 1
                        break
                lines.insert(insert_idx, f"Revisit: {date_str}")
                path.write_text("\n".join(lines), encoding="utf-8")
            else:
                # Add frontmatter
                frontmatter = f"---\nRevisit: {date_str}\n---\n\n"
                path.write_text(frontmatter + content, encoding="utf-8")
            print(f"  ✓ Added Revisit to {file_path}")
        return True
    
    def _fix_file(self, payload: Dict) -> bool:
        """Fix a file based on verifier findings."""
        filepath = HERMES_HOME / payload.get("file", "")
        fix_type = payload.get("fix_type", "")
        
        if not filepath.exists():
            return False
        
        if fix_type == "add_frontmatter":
            content = filepath.read_text(encoding="utf-8")
            if not content.startswith("---"):
                name = filepath.stem.lower().replace(" ", "-").replace("_", "-")
                frontmatter = f"""---
name: {name}
description: "Auto-generated from {filepath.name}"
trigger: "When user asks about {name} concepts"
usage: {name}
Revisit: {datetime.now().strftime('%Y-%m-%d')}
---

"""
                filepath.write_text(frontmatter + content, encoding="utf-8")
                print(f"  ✓ Added frontmatter to {filepath}")
                return True
        return False
    
    def process_queue(self) -> Dict[str, int]:
        """Process all suggestions in queue."""
        queue = self.load_queue()
        if not queue:
            return {"processed": 0, "applied": 0, "failed": 0, "skipped": 0}
        
        applied_log = self.load_applied()
        # Handle case where applied_log might be a string (corrupted)
        if isinstance(applied_log, str):
            applied_log = []  # Reset corrupted log
        applied_ids = {a.get("timestamp") for a in applied_log if isinstance(a, dict)}
        
        results = {"processed": 0, "applied": 0, "failed": 0, "skipped": 0}
        new_queue = []
        
        for suggestion in queue:
            results["processed"] += 1
            
            # Skip if already applied
            if suggestion.get("timestamp") in applied_ids:
                results["skipped"] += 1
                continue
            
            try:
                success = self.apply_suggestion(suggestion)
                if success:
                    results["applied"] += 1
                    applied_log.append({
                        "timestamp": suggestion["timestamp"],
                        "source": suggestion["payload"].get("source"),
                        "action": suggestion["payload"].get("action"),
                        "applied_at": datetime.now().isoformat()
                    })
                else:
                    results["failed"] += 1
                    new_queue.append(suggestion)  # Re-queue for retry
            except Exception as e:
                print(f"  ✗ Error applying suggestion: {e}")
                results["failed"] += 1
                new_queue.append(suggestion)
        
        # Save updated queue and applied log
        self.save_queue(new_queue)
        self.save_applied(applied_log)
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Suggestion Applier - Auto-applies queued suggestions")
    parser.add_argument("--once", action="store_true", help="Process queue once and exit")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    applier = SuggestionApplier()
    results = applier.process_queue()
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Processed: {results['processed']}, Applied: {results['applied']}, Failed: {results['failed']}, Skipped: {results['skipped']}")


if __name__ == "__main__":
    main()