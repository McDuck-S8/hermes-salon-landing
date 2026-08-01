#!/usr/bin/env python3
"""
Read-Only Auditor — Scans folders with read-only access, no writes.
Used for Step 1 shortcut in Prompt B: build a draft map from existing files.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import hashlib

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

class ReadOnlyAuditor:
    """Read-only folder scanner - no write tools, only read/search/list."""
    
    def __init__(self, token_budget: int = 5000):
        self.token_budget = token_budget
        self.tokens_used = 0
        self.findings = {
            "folders_scanned": 0,
            "files_found": 0,
            "total_size_mb": 0,
            "file_types": {},
            "key_files": [],
            "project_structure": {},
            "potential_layers": {
                "identity": [],
                "rules": [],
                "skills": [],
                "agents": [],
                "tools": [],
                "substrate": []
            }
        }
    
    def _estimate_tokens(self, text: str) -> int:
        return int(len(text.split()) / 0.75)
    
    def _check_budget(self, needed: int) -> bool:
        return (self.tokens_used + needed) <= self.token_budget
    
    def scan_folder(self, folder_path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Recursively scan folder (read-only)."""
        if current_depth > max_depth:
            return {"truncated": True}
        
        if not folder_path.exists() or not folder_path.is_dir():
            return {"error": "Not a directory"}
        
        result = {
            "path": str(folder_path),
            "files": [],
            "subdirs": [],
            "file_count": 0,
            "total_size": 0
        }
        
        try:
            for item in folder_path.iterdir():
                if item.name.startswith("."):
                    continue
                
                if item.is_file():
                    size = item.stat().st_size
                    ext = item.suffix.lower()
                    result["files"].append({
                        "name": item.name,
                        "size": size,
                        "ext": ext,
                        "path": str(item)
                    })
                    result["file_count"] += 1
                    result["total_size"] += size
                elif item.is_dir() and current_depth < max_depth:
                    result["subdirs"].append(str(item))
                    sub_result = self.scan_folder(item, max_depth, current_depth + 1)
                    # Merge subdir findings
        except PermissionError:
            result["error"] = "Permission denied"
        
        return result
    
    def scan_target_folders(self, target_folders: List[Path]) -> Dict:
        """Scan multiple target folders and build project map."""
        audit_result = {
            "timestamp": datetime.now().isoformat(),
            "folders_requested": [str(p) for p in target_folders],
            "folders_scanned": 0,
            "total_files": 0,
            "total_size_mb": 0,
            "folder_details": {},
            "layer_mapping": {
                "identity": [],
                "rules": [],
                "skills": [],
                "agents": [],
                "tools": [],
                "substrate": []
            }
        }
        
        for folder in target_folders:
            if not folder.exists():
                audit_result["layer_mapping"]["errors"] = audit_result.get("errors", [])
                audit_result["errors"].append(f"Folder not found: {folder}")
                continue
            
            audit_result["folders_scanned"] += 1
            detail = self.scan_folder(folder)
            audit_result["folder_details"][str(folder)] = detail
            audit_result["total_files"] += detail.get("file_count", 0)
            audit_result["total_size_mb"] += detail.get("total_size", 0) / (1024 * 1024)
            
            # Map to layers based on folder structure
            self._map_to_layers(folder, detail, audit_result["layer_mapping"])
        
        return audit_result
    
    def _map_to_layers(self, folder: Path, detail: Dict, layer_mapping: Dict):
        """Map found files to Agentic OS layers."""
        folder_name = folder.name.lower()
        
        for file_info in detail.get("files", []):
            name = file_info["name"].lower()
            ext = file_info["ext"]
            rel_path = file_info.get("path", "")
            
            # Identity layer
            if "claude.md" in name or "identity.md" in name:
                layer_mapping["identity"].append(rel_path)
            elif any(kw in name for kw in ["readme", "about", "vision", "mission"]):
                layer_mapping["identity"].append(rel_path)
            
            # Rules layer
            elif "always.md" in name or "never.md" in name or "rules" in folder_name:
                layer_mapping["rules"].append(rel_path)
            elif "hook" in name or "pre-commit" in name:
                layer_mapping["rules"].append(rel_path)
            
            # Skills layer
            elif "skill" in folder_name or ext in [".py", ".sh", ".js"] and "skill" in name:
                layer_mapping["skills"].append(rel_path)
            elif any(kw in name for kw in ["workflow", "pipeline", "automation", "script"]):
                layer_mapping["skills"].append(rel_path)
            
            # Agents layer
            elif "agent" in folder_name or "agent" in name:
                layer_mapping["agents"].append(rel_path)
            elif any(kw in name for kw in ["cfo", "editor", "reviewer", "orchestrator", "role"]):
                layer_mapping["agents"].append(rel_path)
            
            # Tools layer
            elif "tool" in folder_name or "mcp" in folder_name or "cli" in folder_name:
                layer_mapping["tools"].append(rel_path)
            elif ext in [".toml", ".yaml", ".yml", ".json"] and any(kw in name for kw in ["config", "settings", "env"]):
                layer_mapping["tools"].append(rel_path)
            
            # Substrate
            elif folder_name in [".wiki", "wiki", "memory", "docs", "notes", "knowledge"]:
                layer_mapping["substrate"].append(rel_path)
            elif ext in [".md", ".txt", ".wiki"]:
                layer_mapping["substrate"].append(rel_path)
    
    def generate_blueprint_draft(self, audit_result: Dict) -> str:
        """Generate os-blueprint.md draft from audit findings."""
        lines = [
            "# os-blueprint.md — Draft from Read-Only Audit",
            f"**Generated**: {audit_result['timestamp']}",
            f"**Folders Scanned**: {audit_result['folders_scanned']}",
            f"**Total Files**: {audit_result['total_files']}",
            f"**Total Size**: {audit_result['total_size_mb']:.1f} MB",
            "",
            "## Layer Mapping (Auto-Detected)",
            ""
        ]
        
        for layer, files in audit_result["layer_mapping"].items():
            if files:
                lines.append(f"### {layer.capitalize()} ({len(files)} files)")
                for f in files[:10]:
                    lines.append(f"- `{f}`")
                if len(files) > 10:
                    lines.append(f"- ... and {len(files) - 10} more")
                lines.append("")
        
        lines.extend([
            "## Recommended Build Order",
            "1. **Identity** — CLAUDE.md (core POV, voice, refusals)",
            "2. **Rules & Hooks** — .claude/rules/always.md, never.md",
            "3. **Skills** — .claude/skills/ (crystallize 3+ repeats)",
            "4. **Agents** — .claude/agents/ (roles with judgment)",
            "5. **Tools/MCPs/CLIs** — .claude/tools/ (wrap, don't marry)",
            "",
            "## Substrate",
            "- `.wiki/` folder for compounding memory",
            "- Re-ingest, don't rebuild",
            "",
            "## Next Steps",
            "1. Review this draft — confirm or correct",
            "2. Choose: PATH A (Blueprint only) or PATH B (Build it out)",
            "3. If PATH B: scaffold layer by layer from core out",
            "",
            "---",
            "*Draft generated by Read-Only Auditor. Verify before building.*"
        ])
        
        return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Read-Only Auditor - Build blueprint draft from existing files")
    parser.add_argument("folders", nargs="+", help="Folders to scan (read-only)")
    parser.add_argument("--output", help="Output blueprint file", default="os-blueprint.md")
    parser.add_argument("--token-budget", type=int, default=5000, help="Token budget")
    parser.add_argument("--max-depth", type=int, default=3, help="Max scan depth")
    args = parser.parse_args()
    
    folders = [Path(f) for f in args.folders]
    auditor = ReadOnlyAuditor(token_budget=args.token_budget)
    
    print(f"🔍 Scanning {len(folders)} folder(s) read-only...")
    result = auditor.scan_target_folders(folders)
    
    print(f"  Folders scanned: {result['folders_scanned']}")
    print(f"  Files found: {result['total_files']}")
    print(f"  Total size: {result['total_size_mb']:.1f} MB")
    
    # Generate blueprint draft
    blueprint = auditor.generate_blueprint_draft(result)
    output_path = Path(args.output)
    output_path.write_text(blueprint, encoding="utf-8")
    
    print(f"\n📄 Blueprint draft saved: {output_path}")
    print("\nLayer mapping:")
    for layer, files in result["layer_mapping"].items():
        if files:
            print(f"  {layer}: {len(files)} files")
    
    print(f"\n✅ Draft ready at {output_path} — review before building!")


if __name__ == "__main__":
    main()