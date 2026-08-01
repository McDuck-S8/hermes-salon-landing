#!/usr/bin/env python3
"""
One-shot setup for herdr-multiagent workspace.
Run once: python setup_herdr_multiagent.py
"""
import os
import sys
import subprocess
import json
from pathlib import Path

HERMES_ROOT = Path("D:/Portable_Soft/hermes")
CACHE_DIR = HERMES_ROOT / "cache"
PROFILES_DIR = Path.home() / ".hermes" / "profiles"

ROLES = {
    "orchestrator": {
        "skills": ["superpowers:using-superpowers", "superpowers:writing-plans"],
        "mcp": {},
    },
    "coder": {
        "skills": ["software-development:coding-toolkit", "superpowers:subagent-driven-development"],
        "mcp": {},
    },
    "browser": {
        "skills": ["automation:ego-windows", "automation:browser-automation-toolkit"],
        "mcp": {
            "browserclaw": {"type": "http", "url": "http://127.0.0.1:9010/mcp"},
            "browseros": {"type": "http", "url": "http://127.0.0.1:9003/mcp"},
        },
    },
    "researcher": {
        "skills": ["autonomous-ai-agents:omh-deep-research", "integration:agent-reach"],
        "mcp": {},
    },
    "deployer": {
        "skills": ["devops:github-pages-deployment", "devops:devops-toolkit"],
        "mcp": {},
    },
    "cpa-operator": {
        "skills": ["finance:cpa-affiliate-bot-development", "automation:n8n"],
        "mcp": {},
    },
}

def run(cmd, check=True, **kwargs):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    if result.stdout:
        print(f"    {result.stdout.strip()}")
    if result.stderr and check:
        print(f"    ERR: {result.stderr.strip()}")
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result

def main():
    print("=== herdr-multiagent ONE-SHOT SETUP ===\n")
    
    # 1. Create Hermes profiles
    print("1. Creating Hermes profiles...")
    for role, config in ROLES.items():
        profile_dir = PROFILES_DIR / role
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        config_yaml = profile_dir / "config.yaml"
        import yaml
        data = {"skills": config["skills"]}
        if config["mcp"]:
            data["mcp"] = {"servers": config["mcp"]}
        config_yaml.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        print(f"   ✅ {role}")
    
    # 2. Create workspace dirs
    print("\n2. Creating workspace dirs...")
    for role in ROLES:
        (HERMES_ROOT / "workspaces" / role).mkdir(parents=True, exist_ok=True)
    print("   ✅ workspaces/")
    
    # 3. Initialize agent bus
    print("\n3. Initializing agent bus...")
    sys.path.insert(0, str(HERMES_ROOT / "skills" / "herdr-multiagent"))
    from scripts.agent_bus import get_bus
    bus = get_bus()
    print(f"   ✅ Bus at {bus.bus_dir}")
    
    # 4. Create launch scripts for each agent
    print("\n4. Creating launch scripts...")
    launch_dir = HERMES_ROOT / "launch"
    launch_dir.mkdir(exist_ok=True)
    
    for role in ROLES:
        script = launch_dir / f"launch_{role}.bat"
        script.write_text(f"""@echo off
cd /d {HERMES_ROOT}
set HERMES_PROFILE={role}
hermes chat
""", encoding="utf-8")
    print("   ✅ launch/*.bat")
    
    # 5. Create master launcher
    print("\n5. Creating master launcher...")
    master = launch_dir / "launch_all.bat"
    master.write_text(f"""@echo off
echo Starting MCP servers...
start "BrowserClaw+BrowserOS" cmd /k "cd /d {HERMES_ROOT} && hermes gateway run"
timeout /t 5 >nul

echo Starting browser-harness...
start "browser-harness" cmd /k "cd /d {HERMES_ROOT}\\browser-harness && python -m src.browser_harness.daemon"
timeout /t 3 >nul

echo Launching agent workspaces...
""", encoding="utf-8")
    for role in ROLES:
        master.write_text(master.read_text(encoding="utf-8") + f'start "{role}" cmd /k "{launch_dir / f"launch_{role}.bat"}"\n', encoding="utf-8")
    print("   ✅ launch_all.bat")
    
    # 6. Create Herdr setup script
    print("\n6. Creating Herdr setup script...")
    herdr_setup = HERMES_ROOT / "herdr_setup.bat"
    herdr_setup.write_text(f"""@echo off
echo Creating Herdr spaces...
herdr-multiagent setup --roles orchestrator,coder,browser,researcher,deployer,cpa-operator
echo.
echo Done! Spaces created.
echo Run 'herdr' in Windows Terminal to see them.
pause
""", encoding="utf-8")
    print("   ✅ herdr_setup.bat")
    
    print("\n=== SETUP COMPLETE ===")
    print(f"""
NEXT STEPS (в Windows Terminal):

1. Запусти всё одной командой:
   {launch_dir / "launch_all.bat"}

2. В новом табе запусти Herdr setup:
   {herdr_setup}

3. Внутри Herdr (после setup) — работай:
   agent_send --to coder --type task --payload '{{\"task\": \"Fix login\"}}'
   agent_task --template cpa-scrape --params '{{\"geo\": \"IN\"}}' --send
   agent_status --all

Файлы созданы в:
- Профили: {PROFILES_DIR}
- Лаунчеры: {launch_dir}
- Herdr setup: {herdr_setup}
""")

if __name__ == "__main__":
    main()