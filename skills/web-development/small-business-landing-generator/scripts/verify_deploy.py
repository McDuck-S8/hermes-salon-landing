#!/usr/bin/env python3
"""
Verify GitHub Pages deployments.
Usage: python scripts/verify_deploy.py [project_name]
       python scripts/verify_deploy.py --all
"""

import sys
import time
import subprocess
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import generate_from_json

GH_USER = "McDuck-S8"

def check_pages_status(repo_name: str) -> dict:
    """Check GitHub Pages build status for a repo."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{GH_USER}/{repo_name}/pages"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def wait_for_build(repo_name: str, max_wait: int = 120) -> bool:
    """Poll Pages build until built or timeout."""
    start = time.time()
    while time.time() - start < max_wait:
        status = check_pages_status(repo_name)
        if status.get("status") == "built":
            return True
        elif status.get("status") == "error":
            return False
        time.sleep(5)
    return False

def verify_url(url: str) -> bool:
    """Check if URL returns 200."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Hermes/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except:
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_deploy.py <project_name> | --all")
        sys.exit(1)
    
    project_root = Path(__file__).parent.parent
    generated_dir = project_root / "generated"
    
    if sys.argv[1] == "--all":
        projects = [d.name for d in generated_dir.iterdir() if d.is_dir() and (d / "index.html").exists()]
    else:
        projects = [sys.argv[1]]
    
    print(f"Verifying {len(projects)} deployment(s)...\n")
    
    for project in projects:
        repo_name = f"{project}-site"
        url = f"https://{GH_USER}.github.io/{repo_name}/"
        
        print(f"📦 {project}")
        print(f"   Repo: {repo_name}")
        print(f"   URL:  {url}")
        
        # Check Pages status
        status = check_pages_status(repo_name)
        print(f"   Pages status: {status.get('status', 'unknown')}")
        
        if status.get("status") != "built":
            print(f"   ⏳ Waiting for build...")
            if wait_for_build(repo_name):
                print(f"   ✅ Build complete")
            else:
                print(f"   ❌ Build failed or timeout")
                continue
        
        # Verify live URL
        if verify_url(url):
            print(f"   ✅ Live and responding 200")
        else:
            print(f"   ⚠️  URL not responding (may need more time)")
        
        print()

if __name__ == "__main__":
    main()