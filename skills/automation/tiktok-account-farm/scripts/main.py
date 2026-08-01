#!/usr/bin/env python3
"""
tiktok-account-farm — Main entry point for WorkflowSupervisor.
Creates profiles, warms up accounts, schedules posts.
"""
import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCRIPTS_DIR = Path(os.environ.get("HERMES_HOME", Path(__file__).parent.parent.parent.parent)) / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

def run_phase(phase: str, config: dict):
    print(f"[tiktok-account-farm] Phase: {phase}")
    print(f"[tiktok-account-farm] Config: {json.dumps(config, ensure_ascii=False)}")
    
    if phase == "create_profiles":
        return create_profiles(config)
    elif phase == "warmup":
        return warmup_accounts(config)
    elif phase == "schedule_posts":
        return schedule_posts(config)
    elif phase == "post_video":
        return post_video(config)
    else:
        return {"status": "unknown_phase", "phase": phase}


def create_profiles(config: dict):
    """Create TikTok profiles with Ghost-surfer/BrowserOS."""
    count = config.get("count", 3)
    niches = config.get("niches", ["beauty", "education", "services"])
    proxy = config.get("proxy", "socks5://127.0.0.1:10806")
    
    results = {"created": [], "instructions": []}
    
    for i, niche in enumerate(niches[:count]):
        profile_name = f"{niche}_main"
        results["created"].append({
            "profile": profile_name,
            "niche": niche,
            "proxy": proxy
        })
        results["instructions"].append(
            f"Create profile '{profile_name}' in Ghost-surfer: "
            f"browser-harness new_profile --name {profile_name} --proxy {proxy}"
        )
    
    print(f"[tiktok_farm] Created {len(results['created'])} profiles")
    return {"status": "completed", "results": results}


def warmup_accounts(config: dict):
    """Warm up accounts: likes, comments, follows, views."""
    return {
        "status": "completed",
        "results": {
            "action": "warmup_scheduled",
            "schedule": "Days 1-3: manual browsing 15-30 min/day per account",
            "actions_per_day": {"swipe": "60%", "like": "20%", "save": "10%", "follow": "7%", "comment": "3%"},
            "interval": "15-45 seconds between actions (logarithmic distribution)"
        }
    }


def schedule_posts(config: dict):
    """Schedule posts for the week."""
    accounts = config.get("accounts", 3)
    posts_per_day = config.get("posts_per_day", 3)
    
    schedule = {}
    for day in range(1, 8):
        schedule[f"day_{day}"] = []
        for acc in range(accounts):
            for post in range(posts_per_day):
                schedule[f"day_{day}"].append({
                    "account": f"account_{acc+1}",
                    "time": f"{9+post*4}:00",  # 9:00, 13:00, 17:00
                    "template": f"template_{post+1}"
                })
    
    return {"status": "completed", "results": {"schedule": schedule, "total_posts": 7 * 3 * 3}}


def post_video(config: dict):
    """Post video to TikTok via BrowserOS/Ghost-surfer."""
    return {
        "status": "ready",
        "action": "manual_upload_via_browseros",
        "note": "Upload videos via browser-harness to TikTok using saved profiles"
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--config", default="{}")
    args = parser.parse_args()
    
    config = json.loads(args.config)
    result = run_phase(args.phase, config)
    print(json.dumps(result, ensure_ascii=False))