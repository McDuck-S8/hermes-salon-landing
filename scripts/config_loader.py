#!/usr/bin/env python3
"""
Config Loader for Web Automation.
Loads site-specific configurations from JSON files.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
CONFIGS_DIR = HERMES_HOME / "configs"


def load_site_config(site: str) -> dict:
    """Load site configuration from JSON file."""
    config_path = CONFIGS_DIR / f"{site}.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Error parsing {site}.json: {e}")
    return {}


def list_available_sites() -> list:
    """List all available site configs."""
    if not CONFIGS_DIR.exists():
        return []
    return [f.stem for f in CONFIGS_DIR.glob("*.json")]


def detect_ghost_surfer() -> bool:
    """Check if Ghost-surfer is available."""
    # Check for Ghost-surfer binary or Docker image
    try:
        # Check for binary
        result = subprocess.run(["which", "ghost-surfer"], capture_output=True)
        if result.returncode == 0:
            return True
        # Check for Docker image
        result = subprocess.run(["docker", "images", "ghost-surfer"], capture_output=True, text=True)
        if "ghost-surfer" in result.stdout:
            return True
        # Check for local installation
        ghost_paths = [
            Path.home() / ".ghost-surfer",
            Path("/opt/ghost-surfer"),
            Path("/usr/local/bin/ghost-surfer"),
        ]
        for path in ghost_paths:
            if path.exists():
                return True
    except Exception:
        pass
    return False


async def launch_ghost_surfer(proxy: str = None) -> Optional[object]:
    """Launch Ghost-surfer browser process."""
    try:
        # Try Docker first
        cmd = ["docker", "run", "-d", "--rm"]
        if proxy:
            cmd.extend(["-e", f"PROXY={proxy}"])
        cmd.extend(["-p", "9222:9222", "ghost-surfer"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            container_id = result.stdout.strip()
            return {"container_id": container_id, "type": "docker"}
    except Exception as e:
        print(f"Failed to launch Ghost-surfer via Docker: {e}")
    
    try:
        # Try binary
        cmd = ["ghost-surfer"]
        if proxy:
            cmd.extend(["--proxy", proxy])
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {"process": process, "type": "binary"}
    except Exception as e:
        print(f"Failed to launch Ghost-surfer binary: {e}")
    
    return None


def get_site_base_url(site: str) -> str:
    """Get base URL for a site."""
    urls = {
        "github": "https://github.com",
        "gitlab": "https://gitlab.com",
        "youtube": "https://youtube.com",
        "dzen": "https://dzen.ru",
        "vc_ru": "https://vc.ru",
    }
    return urls.get(site, "")


def get_default_selectors(site: str) -> dict:
    """Get default selectors for common actions."""
    defaults = {
        "github": {
            "new_repo_button": 'a[href="/new"]',
            "repo_name_input": 'input[name="repository[name]"]',
            "repo_description_input": 'input[name="repository[description]"]',
            "private_checkbox": 'input[name="repository[visibility]"][value="private"]',
            "create_button": 'button[type="submit"]',
            "file_upload": 'input[type="file"]',
            "commit_message": 'input[name="commit_message"]',
            "commit_button": 'button[type="submit"]',
        },
        "gitlab": {
            "new_project_button": 'a[href*="/projects/new"]',
            "project_name": 'input[name="project[name]"]',
            "visibility_private": 'input[value="private"]',
            "create_button": 'button[type="submit"]',
        },
        "youtube": {
            "upload_button": 'a[href="/upload"]',
            "file_input": 'input[type="file"]',
            "title_input": 'input[name="title"]',
            "description_input": 'textarea[name="description"]',
            "next_button": 'button:has-text("Next")',
            "publish_button": 'button:has-text("Publish")',
        },
        "dzen": {
            "new_post_button": 'button:has-text("Новая публикация")',
            "title_input": 'input[placeholder*="заголовок"]',
            "editor_iframe": 'iframe[class*="editor"]',
            "publish_button": 'button:has-text("Опубликовать")',
        },
        "vc_ru": {
            "new_article_button": 'a[href*="/write"]',
            "title_input": 'input[name="title"]',
            "editor": 'div[contenteditable="true"]',
            "publish_button": 'button:has-text("Опубликовать")',
        },
    }
    return defaults.get(site, {})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Config Loader for Web Automation")
    parser.add_argument("--site", help="Site name")
    parser.add_argument("--list", action="store_true", help="List available sites")
    args = parser.parse_args()
    
    if args.list:
        sites = list_available_sites()
        print("Available sites:", ", ".join(sites))
    elif args.site:
        config = load_site_config(args.site)
        print(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        print("Usage: --site <name> or --list")