#!/usr/bin/env python3
"""
herdr-multiagent — Main orchestrator class.
Manages Herdr spaces, agent processes, and task delegation.
"""
import os
import json
import subprocess
import uuid
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    from scripts.crystal.omh_integration import CrystalOMHResearchPipeline
except ImportError:
    CrystalOMHResearchPipeline = None


@dataclass
class AgentRole:
    """Definition of an agent role."""
    name: str
    description: str
    profile: str          # Hermes profile name
    skills: List[str]     # Skills to load
    panes: List[str]      # Pane names in this space
    working_dir: str      # Working directory for this agent


# Default role configurations
DEFAULT_ROLES = {
    "orchestrator": AgentRole(
        name="orchestrator",
        description="Human orchestrator - issues tasks, monitors all agents",
        profile="orchestrator",
        skills=["superpowers:using-superpowers", "superpowers:writing-plans"],
        panes=["command", "logs"],
        working_dir="D:/Portable_Soft/hermes",
    ),
    "coder": AgentRole(
        name="coder",
        description="Code implementation agent - writes, tests, reviews code",
        profile="coder",
        skills=["software-development:coding-toolkit", "superpowers:subagent-driven-development"],
        panes=["editor", "tests"],
        working_dir="D:/Portable_Soft/hermes",
    ),
    "browser": AgentRole(
        name="browser",
        description="Web automation agent - ego-windows, BrowserClaw, browser-harness",
        profile="browser",
        skills=["automation:ego-windows", "automation:browser-automation-toolkit"],
        panes=["browserclaw", "harness"],
        working_dir="D:/Portable_Soft/hermes",
    ),
    "researcher": AgentRole(
        name="researcher",
        description="Deep research agent - OMH, Agent Reach, YouTube, GitHub",
        profile="researcher",
        skills=["autonomous-ai-agents:omh-deep-research", "integration:agent-reach"],
        panes=["search", "synthesize"],
        working_dir="D:/Portable_Soft/hermes",
    ),
    "deployer": AgentRole(
        name="deployer",
        description="Deployment agent - GitHub Pages, n8n, servers, Docker",
        profile="deployer",
        skills=["devops:github-pages-deployment", "devops:devops-toolkit"],
        panes=["deploy", "monitor"],
        working_dir="D:/Portable_Soft/hermes",
    ),
    "cpa-operator": AgentRole(
        name="cpa-operator",
        description="CPA funnel operator - Telegram bot, n8n, content locker",
        profile="cpa-operator",
        skills=["finance:cpa-affiliate-bot-development", "automation:n8n"],
        panes=["bot", "funnel"],
        working_dir="D:/Portable_Soft/hermes",
    ),
}


class HerdrMultiAgent:
    """Main orchestrator for Herdr-based multi-agent workspace."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("D:/Portable_Soft/hermes/cache/herdr_multiagent.json")
        self.roles: Dict[str, AgentRole] = DEFAULT_ROLES.copy()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_config()
    
    def _load_config(self):
        """Load saved configuration."""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                for name, role_data in data.get("roles", {}).items():
                    self.roles[name] = AgentRole(**role_data)
            except Exception:
                pass
    
    def _save_config(self):
        """Save current configuration."""
        data = {
            "roles": {name: asdict(role) for name, role in self.roles.items()},
            "updated": datetime.now().isoformat(),
        }
        self.config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def setup(self, roles: List[str] = None, force: bool = False) -> Dict:
        """
        Create Herdr spaces and panes for specified roles.
        
        Args:
            roles: List of role names to setup (default: all)
            force: Recreate even if exists
            
        Returns:
            Dict with created spaces info
        """
        target_roles = roles or list(self.roles.keys())
        results = {"spaces": [], "errors": []}
        
        for role_name in target_roles:
            if role_name not in self.roles:
                results["errors"].append(f"Unknown role: {role_name}")
                continue
            
            role = self.roles[role_name]
            space_name = f"agent-{role_name}"
            
            try:
                # Create space in Herdr
                self._herdr_create_space(space_name)
                
                # Create panes in the space
                for i, pane_name in enumerate(role.panes):
                    if i == 0:
                        # First pane - already exists in new space
                        self._herdr_rename_pane(space_name, 0, pane_name)
                    else:
                        # Split to create additional panes
                        self._herdr_split_pane(space_name, "vertical" if i % 2 == 1 else "horizontal")
                        self._herdr_rename_pane(space_name, i, pane_name)
                    
                    # Launch Hermes agent in pane
                    self._launch_agent_in_pane(space_name, pane_name, role)
                
                results["spaces"].append({
                    "role": role_name,
                    "space": space_name,
                    "panes": role.panes,
                    "profile": role.profile,
                })
                
            except Exception as e:
                results["errors"].append(f"{role_name}: {e}")
        
        self._save_config()
        return results
    
    def _herdr_create_space(self, space_name: str):
        """Create a new Herdr space."""
        # Herdr CLI: herdr space create <name>
        subprocess.run(["herdr", "space", "create", space_name], 
                       capture_output=True, timeout=10)
    
    def _herdr_split_pane(self, space_name: str, direction: str = "vertical"):
        """Split current pane in Herdr space."""
        # Herdr CLI: herdr pane split <space> --direction vertical|horizontal
        subprocess.run(["herdr", "pane", "split", space_name, "--direction", direction],
                       capture_output=True, timeout=10)
    
    def _herdr_rename_pane(self, space_name: str, pane_index: int, name: str):
        """Rename a pane in Herdr space."""
        # Herdr CLI: herdr pane rename <space> <index> <name>
        subprocess.run(["herdr", "pane", "rename", space_name, str(pane_index), name],
                       capture_output=True, timeout=10)
    
    def _launch_agent_in_pane(self, space_name: str, pane_name: str, role: AgentRole):
        """Launch Hermes agent in a specific Herdr pane."""
        # This sends keystrokes to the pane to start the agent
        # Herdr CLI: herdr send <space> <pane> <command>
        profile_env = f"HERMES_PROFILE={role.profile}"
        cmd = f"{profile_env} hermes chat"
        
        # For now, we prepare the command - actual sending depends on Herdr API
        # This is a placeholder for the actual implementation
        pass
    
    def teardown(self, roles: List[str] = None) -> Dict:
        """Stop agents and remove Herdr spaces."""
        target_roles = roles or list(self.roles.keys())
        results = {"stopped": [], "errors": []}
        
        for role_name in target_roles:
            space_name = f"agent-{role_name}"
            try:
                # Kill processes in space
                subprocess.run(["herdr", "space", "kill", space_name], 
                               capture_output=True, timeout=10)
                # Remove space
                subprocess.run(["herdr", "space", "remove", space_name], 
                               capture_output=True, timeout=10)
                results["stopped"].append(space_name)
            except Exception as e:
                results["errors"].append(f"{space_name}: {e}")
        
        return results
    
    def status(self) -> Dict:
        """Get status of all agent spaces."""
        results = {"spaces": [], "total_panes": 0}
        
        for role_name, role in self.roles.items():
            space_name = f"agent-{role_name}"
            try:
                # Query Herdr for space info
                result = subprocess.run(
                    ["herdr", "space", "info", space_name, "--json"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    results["spaces"].append({
                        "role": role_name,
                        "space": space_name,
                        "panes": info.get("panes", []),
                        "profile": role.profile,
                        "status": "running",
                    })
                    results["total_panes"] += len(info.get("panes", []))
                else:
                    results["spaces"].append({
                        "role": role_name,
                        "space": space_name,
                        "status": "not_found",
                    })
            except Exception as e:
                results["spaces"].append({
                    "role": role_name,
                    "space": space_name,
                    "status": "error",
                    "error": str(e),
                })
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Herdr Multi-Agent Orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Create spaces/panes for roles")
    setup_parser.add_argument("--roles", nargs="+", help="Roles to setup")
    setup_parser.add_argument("--force", action="store_true", help="Force recreate")
    
    # Teardown command
    teardown_parser = subparsers.add_parser("teardown", help="Stop agents, remove spaces")
    teardown_parser.add_argument("--roles", nargs="+", help="Roles to teardown")
    
    # Status command
    subparsers.add_parser("status", help="Show status of all agent spaces")
    
    args = parser.parse_args()
    
    orchestrator = HerdrMultiAgent()
    
    if args.command == "setup":
        result = orchestrator.setup(args.roles, args.force)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "teardown":
        result = orchestrator.teardown(args.roles)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "status":
        result = orchestrator.status()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()