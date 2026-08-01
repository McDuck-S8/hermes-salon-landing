#!/usr/bin/env python3
"""
space_manager.py — Herdr space/pane automation.
Interacts with Herdr CLI to create/manage spaces and panes.
"""
import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


@dataclass
class HerdrPane:
    """Represents a pane in a Herdr space."""
    index: int
    name: str
    space: str
    pid: Optional[int] = None
    command: Optional[str] = None


@dataclass
class HerdrSpace:
    """Represents a Herdr space."""
    name: str
    panes: List[HerdrPane]
    created_at: Optional[str] = None


class HerdrSpaceManager:
    """Manages Herdr spaces and panes via CLI."""
    
    def __init__(self):
        self.herdr_cmd = "herdr"
        self._verify_herdr()
    
    def _verify_herdr(self):
        """Verify Herdr is available."""
        try:
            result = subprocess.run([self.herdr_cmd, "--version"], 
                                    capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise RuntimeError("Herdr not found in PATH")
        except FileNotFoundError:
            raise RuntimeError("Herdr not installed. Run: cargo install herdr")
    
    def create_space(self, name: str) -> bool:
        """Create a new Herdr space."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "space", "create", name],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def remove_space(self, name: str) -> bool:
        """Remove a Herdr space."""
        try:
            # Kill processes first
            subprocess.run([self.herdr_cmd, "space", "kill", name], 
                           capture_output=True, timeout=10)
            # Then remove
            result = subprocess.run(
                [self.herdr_cmd, "space", "remove", name],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def list_spaces(self) -> List[str]:
        """List all Herdr spaces."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "space", "list", "--json"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("spaces", [])
        except Exception:
            pass
        return []
    
    def get_space_info(self, name: str) -> Optional[HerdrSpace]:
        """Get detailed info about a space."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "space", "info", name, "--json"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                panes = []
                for i, pane_data in enumerate(data.get("panes", [])):
                    panes.append(HerdrPane(
                        index=i,
                        name=pane_data.get("name", f"pane-{i}"),
                        space=name,
                        pid=pane_data.get("pid"),
                        command=pane_data.get("command"),
                    ))
                return HerdrSpace(name=name, panes=panes, created_at=data.get("created_at"))
        except Exception:
            pass
        return None
    
    def split_pane(self, space: str, direction: str = "vertical") -> bool:
        """Split a pane in a space."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "pane", "split", space, "--direction", direction],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def rename_pane(self, space: str, pane_index: int, name: str) -> bool:
        """Rename a pane in a space."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "pane", "rename", space, str(pane_index), name],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def send_to_pane(self, space: str, pane_name: str, command: str) -> bool:
        """Send command to a specific pane."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "send", space, pane_name, command],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def send_keys(self, space: str, pane_name: str, keys: str) -> bool:
        """Send keystrokes to a pane."""
        try:
            result = subprocess.run(
                [self.herdr_cmd, "send-keys", space, pane_name, keys],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def setup_agent_workspace(self, role: str, profile: str, 
                              panes: List[str], working_dir: str) -> Dict:
        """
        Full setup for an agent role:
        1. Create space
        2. Create/rename panes
        3. Launch Hermes agent in each pane
        """
        space_name = f"agent-{role}"
        results = {"space": space_name, "panes": [], "errors": []}
        
        # 1. Create space
        if not self.create_space(space_name):
            # Space might already exist - that's OK
            pass
        
        # 2. Setup panes
        for i, pane_name in enumerate(panes):
            if i == 0:
                # First pane exists, just rename
                self.rename_pane(space_name, 0, pane_name)
            else:
                # Split and rename
                direction = "vertical" if i % 2 == 1 else "horizontal"
                self.split_pane(space_name, direction)
                self.rename_pane(space_name, i, pane_name)
            
            # 3. Launch Hermes agent in pane
            cmd = f"cd {working_dir} && HERMES_PROFILE={profile} hermes chat"
            self.send_to_pane(space_name, pane_name, cmd)
            
            results["panes"].append({
                "name": pane_name,
                "profile": profile,
                "command": cmd,
            })
        
        return results
    
    def teardown_agent_workspace(self, role: str) -> bool:
        """Teardown agent workspace."""
        space_name = f"agent-{role}"
        return self.remove_space(space_name)
    
    def get_all_status(self) -> Dict:
        """Get status of all agent spaces."""
        spaces = self.list_spaces()
        agent_spaces = [s for s in spaces if s.startswith("agent-")]
        
        results = {"spaces": [], "total_panes": 0}
        for space_name in agent_spaces:
            info = self.get_space_info(space_name)
            if info:
                results["spaces"].append({
                    "name": info.name,
                    "panes": [
                        {"index": p.index, "name": p.name, "pid": p.pid, "command": p.command}
                        for p in info.panes
                    ],
                    "created_at": info.created_at,
                })
                results["total_panes"] += len(info.panes)
        
        return results


if __name__ == "__main__":
    mgr = HerdrSpaceManager()
    
    print("=== Herdr Spaces ===")
    spaces = mgr.list_spaces()
    for s in spaces:
        print(f"  {s}")
    
    print("\n=== Agent Spaces Status ===")
    status = mgr.get_all_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))