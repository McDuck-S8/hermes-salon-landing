#!/usr/bin/env python3
"""Generate short-form video scripts for CPA/content-locking funnels."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

HERMES = Path("D:/Portable_Soft/hermes")

VIDEO_SCRIPTS = {
    "gaming-free": {
        "niche": "Gaming",
        "hook": "Want free V-Bucks? Here's the trick that actually works in 2026.",
        "body": [
            "I tested 20 methods and only ONE gives you free skins.",
            "No surveys, no downloads, no scams.",
            "Just follow these 3 simple steps and you'll have 5000 V-Bucks in 10 minutes.",
            "This works on PC, Xbox, and PlayStation.",
        ],
        "cta": "Link in bio — free V-Bucks generator (limited spots)",
        "tags": ["fortnite", "free v-bucks", "gaming hacks", "fyp"],
        "duration_s": 25,
    },
    "gaming-robux": {
        "niche": "Gaming",
        "hook": "FREE ROBUX 2026 — patched all other methods, this one STILL works.",
        "body": [
            "Roblox patched the browser exploits last week.",
            "But the API endpoint for item resale is still open.",
            "Here's how to exploit it before they fix it.",
            "Takes 2 minutes — works on mobile and desktop.",
        ],
        "cta": "Tap here — free Robux generator (fast!)",
        "tags": ["roblox", "free robux", "robux hack", "fyp"],
        "duration_s": 20,
    },
    "crypto-free": {
        "niche": "Crypto",
        "hook": "I made $500 in 1 hour with this crypto trick — no investment needed.",
        "body": [
            "Most 'free crypto' videos are scams. This one isn't.",
            "It's a faucet + compound strategy that actually pays.",
            "I withdrew $500 to my Binance in 1 hour.",
            "No deposit, no KYC, no bullshit.",
        ],
        "cta": "Link in bio — free crypto (verified paying)",
        "tags": ["crypto", "free money", "bitcoin", "make money online"],
        "duration_s": 30,
    },
    "survey-money": {
        "niche": "Make Money",
        "hook": "Tired of 'get rich quick' scams? Here's a REAL way to make $50/day.",
        "body": [
            "Paid surveys. Boring but it works.",
            "Companies pay $2-50 per survey for YOUR opinion.",
            "I made $1,240 last month just on my phone.",
            "No skills, no investment, no crypto.",
        ],
        "cta": "Start earning — link in bio (free registration)",
        "tags": ["make money", "side hustle", "passive income", "surveys"],
        "duration_s": 25,
    },
    "vpn-promo": {
        "niche": "Tech",
        "hook": "Your ISP is selling your data RIGHT NOW. Here's how to stop them.",
        "body": [
            "Every website you visit is logged and sold.",
            "VPN is the only protection — but most are scams.",
            "I tested 47 VPNs. Only ONE passed all privacy tests.",
            "And it's 60% off right now.",
        ],
        "cta": "Get protected — link in bio (limited discount)",
        "tags": ["vpn", "privacy", "security", "online safety"],
        "duration_s": 22,
    },
    "dating-promo": {
        "niche": "Dating",
        "hook": "Tired of fake profiles? This app actually VERIFIES every user.",
        "body": [
            "90% of dating apps are bots. Not this one.",
            "Video verification + AI profile screening.",
            "I found my girlfriend in 3 days.",
            "And it's free for the first month.",
        ],
        "cta": "Find love — link in bio (free trial)",
        "tags": ["dating", "relationships", "love", "single"],
        "duration_s": 20,
    },
    "content-locking": {
        "niche": "Gaming/Entertainment",
        "hook": "Unlock exclusive content — free V-Bucks, Robux, and game cheats.",
        "body": [
            "Step 1: Click the link in our bio.",
            "Step 2: Complete one quick offer.",
            "Step 3: Get your free code instantly.",
            "It's that simple. Thousands already claimed.",
        ],
        "cta": "Claim your free rewards — link in bio",
        "tags": ["free stuff", "giveaway", "gaming", "viral"],
        "duration_s": 15,
    },
}


def list_scripts():
    """Show all available video scripts."""
    print(f"Available video scripts ({len(VIDEO_SCRIPTS)}):")
    for name, s in VIDEO_SCRIPTS.items():
        print(f"\n  [{name}] {s['niche']} — {s['hook'][:60]}")
        print(f"    Duration: {s['duration_s']}s | Tags: {', '.join(s['tags'][:3])}")


def generate_script(template_name: str, output: Optional[str] = None) -> Optional[str]:
    """Generate a video script file from template."""
    s = VIDEO_SCRIPTS.get(template_name)
    if not s:
        print(f"Unknown: {template_name}. Available: {', '.join(VIDEO_SCRIPTS.keys())}")
        return None

    content = f"""# Video Script — {s['niche']}
# Generated: {datetime.now().isoformat()}
# Duration: ~{s['duration_s']}s
# Tags: {', '.join(s['tags'])}

## HOOK (0-3s)
{s['hook']}

## BODY (3-{s['duration_s']-5}s)
"""
    for i, line in enumerate(s['body'], 1):
        content += f"{i}. {line}\n"

    content += f"""
## CTA ({s['duration_s']-5}-{s['duration_s']}s)
{s['cta']}

## VISUAL NOTES
- Fast cuts (2-3s per scene)
- Text overlays for every line
- Background: {'gameplay footage' if s['niche'] == 'Gaming' else 'screen recording'}
- End screen: pointing to link in bio
"""

    out_path = output or (HERMES / "reports" / f"video_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    out_path = Path(out_path)
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return str(out_path)


def batch_scripts() -> list:
    """Generate all video scripts."""
    results = []
    for name in VIDEO_SCRIPTS:
        path = generate_script(name)
        if path:
            results.append((name, path))
    return results


def generate_for_scheme(scheme_name: str, niche: str) -> Optional[str]:
    """Generate a custom video script for a specific scheme."""
    s = VIDEO_SCRIPTS.get(niche)
    if not s:
        niche = next(iter(VIDEO_SCRIPTS))
    return generate_script(niche, HERMES / "reports" / f"video_{scheme_name.replace('#','').strip()}_{datetime.now().strftime('%Y%m%d')}.md")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            list_scripts()
        elif cmd == "generate" and len(sys.argv) >= 3:
            path = generate_script(sys.argv[2])
            if path:
                print(f"Generated: {path}")
        elif cmd == "batch":
            results = batch_scripts()
            print(f"Generated {len(results)} scripts:")
            for name, path in results:
                print(f"  {name}: {path}")
        elif cmd == "scheme" and len(sys.argv) >= 4:
            path = generate_for_scheme(sys.argv[2], sys.argv[3])
            if path:
                print(f"Generated: {path}")
        else:
            print("Usage: python video_scripts.py [list|generate <name>|batch|scheme <name> <niche>]")
    else:
        list_scripts()
