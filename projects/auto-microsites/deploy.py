#!/usr/bin/env python3
"""
Deploy microsite to GitHub Pages.
Usage: python deploy.py <project_name> [--repo <repo_name>]
"""
import subprocess
import sys
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
GENERATED = BASE / "generated"
DEPLOY_DIR = BASE / "deploy"


def deploy(project_name: str, repo_name: str = None):
    """Deploy a generated site to GitHub Pages via gh-pages branch."""
    site_dir = GENERATED / project_name
    if not site_dir.exists():
        print(f"❌ Site not found: {site_dir}")
        return False

    repo_name = repo_name or f"{project_name}-site"
    
    # Check gh CLI
    try:
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ GitHub CLI (gh) not installed. Install: https://cli.github.com/")
            return False
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not installed.")
        return False

    # Check auth
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Not authenticated. Run: gh auth login")
        return False

    # Create repo if needed
    result = subprocess.run(["gh", "repo", "view", repo_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Creating repo {repo_name}...")
        subprocess.run(["gh", "repo", "create", repo_name, "--public", "--description", f"Landing page for {project_name}"], check=True)

    # Prepare deploy
    deploy_repo = DEPLOY_DIR / repo_name
    if deploy_repo.exists():
        shutil.rmtree(deploy_repo)
    
    # Clone repo
    print(f"Cloning {repo_name}...")
    user = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "clone", f"https://github.com/{user}/{repo_name}.git", str(deploy_repo)], check=True)

    # Copy site files
    for item in site_dir.iterdir():
        dst = deploy_repo / item.name
        if item.is_file():
            shutil.copy2(item, dst)

    # Commit and push
    subprocess.run(["git", "add", "."], cwd=str(deploy_repo), check=True)
    subprocess.run(["git", "commit", "-m", f"Deploy {project_name}"], cwd=str(deploy_repo), check=True)
    subprocess.run(["git", "push"], cwd=str(deploy_repo), check=True)

    # Enable GitHub Pages
    subprocess.run(["gh", "api", f"repos/{user}/{repo_name}/pages", 
                     "--method", "POST", 
                     "-f", "build_type=legacy",
                     "-f", "source[branch]=main",
                     "-f", "source[path]=/"], 
                    capture_output=True)

    url = f"https://{user}.github.io/{repo_name}/"
    print(f"✅ Deployed: {url}")
    return url


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy.py <project_name> [--repo <repo_name>]")
        sys.exit(1)
    
    project = sys.argv[1]
    repo = None
    if "--repo" in sys.argv:
        idx = sys.argv.index("--repo")
        repo = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
    
    deploy(project, repo)
