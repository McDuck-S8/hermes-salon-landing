#!/usr/bin/env python3
"""
Video Generation Pipeline — Content-Locking-CPA
Orchestrates: script → stock footage → voiceover → ffmpeg compose → metadata → upload
"""

import os
import sys
import json
import asyncio
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

HERMES = Path("D:/Portable_Soft/hermes")
SCRIPTS = HERMES / "scripts"
OUTPUT = SCRIPTS

TOPICS = [
    "Free V-Bucks",
    "Free Robux", 
    "Free GTA Money",
    "Netflix Generator",
    "Spotify Premium",
    "Free Crypto",
    "Amazon Gift Cards",
    "Discord Nitro",
]

VARIANTS = {
    "A": {"name": "control", "suffix": "control_neutral"},
    "B": {"name": "fomo", "suffix": "fomo_timer"},
    "C": {"name": "social", "suffix": "social_live"},
}

HOOKS = {
    "Free V-Bucks": {
        "A": ["Want free V-Bucks without human verification?", "Stop buying V-Bucks! Get 13,500 FREE", "Fortnite players HATE this free V-Bucks trick"],
        "B": ["ONLY 3 SPOTS LEFT for free V-Bucks!", "TIMER: 15:00 — Free V-Bucks expires soon!", "HURRY: Free V-Bucks offer ends in 15 minutes!"],
        "C": ["1,247 players got FREE V-Bucks today!", "Join 1,247+ who unlocked V-Bucks!", "See why 1,247 gamers trust this V-Bucks method"],
    },
    "Free Robux": {
        "A": ["Want free Robux without human verification?", "Stop buying Robux! Get 10,000 FREE", "Roblox players HATE this free Robux trick"],
        "B": ["ONLY 3 SPOTS LEFT for free Robux!", "TIMER: 15:00 — Free Robux expires soon!", "HURRY: Free Robux offer ends in 15 minutes!"],
        "C": ["2,156 players got FREE Robux today!", "Join 2,156+ who unlocked Robux!", "See why 2,156 gamers trust this Robux method"],
    },
    "default": {
        "A": ["Want {topic} for free?", "Stop paying for {topic}! Get it FREE", "People HATE this free {topic} trick"],
        "B": ["ONLY 3 SPOTS LEFT for free {topic}!", "TIMER: 15:00 — Free {topic} expires soon!", "HURRY: Free {topic} offer ends in 15 minutes!"],
        "C": ["1,247 people got FREE {topic} today!", "Join 1,247+ who unlocked {topic}!", "See why 1,247 users trust this {topic} method"],
    },
}

DEMO_SCRIPTS = {
    "Free V-Bucks": "Go to the link in bio, enter your username, complete one quick offer, and the V-Bucks appear in your account instantly.",
    "Free Robux": "Go to the link in bio, enter your Roblox username, complete one quick offer, and the Robux appear in your account instantly.",
    "default": "Go to the link in bio, enter your username, complete one quick offer, and get your {topic} instantly.",
}

CTAS = {
    "tiktok": "Link in bio 👆",
    "youtube_shorts": "Link in description 👇", 
    "instagram_reels": "Link in bio 🔗",
}

@dataclass
class VideoScript:
    topic: str
    variant: str
    hook: str
    demo: str
    cta: str
    duration_sec: int = 15
    platform: str = "tiktok"
    utm_content: str = ""
    
    def to_dict(self):
        return asdict(self)


def get_hooks(topic: str, variant: str) -> List[str]:
    """Get hooks for topic/variant, fallback to default."""
    if topic in HOOKS and variant in HOOKS[topic]:
        return HOOKS[topic][variant]
    return [h.format(topic=topic) for h in HOOKS["default"][variant]]


def get_demo(topic: str) -> str:
    return DEMO_SCRIPTS.get(topic, DEMO_SCRIPTS["default"].format(topic=topic))


def generate_script(topic: str, variant: str, platform: str = "tiktok") -> VideoScript:
    """Generate a single video script."""
    hooks = get_hooks(topic, variant)
    hook = hooks[0]  # Could rotate
    demo = get_demo(topic)
    cta = CTAS.get(platform, CTAS["tiktok"])
    utm = f"{topic.lower().replace(' ', '_')}_{VARIANTS[variant]['suffix']}"
    
    return VideoScript(
        topic=topic,
        variant=variant,
        hook=hook,
        demo=demo,
        cta=cta,
        duration_sec=15,
        platform=platform,
        utm_content=utm,
    )


def generate_batch(topics: List[str] = None, variants: List[str] = None, platforms: List[str] = None) -> List[VideoScript]:
    """Generate scripts for all combinations."""
    topics = topics or TOPICS
    variants = variants or list(VARIANTS.keys())
    platforms = platforms or ["tiktok", "youtube_shorts", "instagram_reels"]
    
    scripts = []
    for topic in topics:
        for variant in variants:
            for platform in platforms:
                scripts.append(generate_script(topic, variant, platform))
    return scripts


def save_scripts(scripts: List[VideoScript], output_dir: Path):
    """Save scripts as JSON for next pipeline stages."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for script in scripts:
        filename = f"script_{script.topic.lower().replace(' ', '_')}_{script.variant}_{script.platform}_{timestamp}.json"
        path = output_dir / filename
        path.write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Also save combined
    combined_path = output_dir / f"scripts_batch_{timestamp}.json"
    combined_path.write_text(json.dumps([s.to_dict() for s in scripts], ensure_ascii=False, indent=2), encoding="utf-8")
    
    return combined_path


def render_ffmpeg_script(video_script: VideoScript, clips_dir: Path, audio_path: Path, output_path: Path) -> str:
    """Generate FFmpeg command for composition."""
    # Build drawtext filters for hook, demo, CTA
    hook_text = video_script.hook.replace("'", "\\'").replace(":", "\\:")
    demo_text = video_script.demo.replace("'", "\\'").replace(":", "\\:")
    cta_text = video_script.cta.replace("'", "\\'").replace(":", "\\:")
    
    # Duration splits
    t_hook = 3
    t_demo = 10
    t_cta = video_script.duration_sec
    
    filter_complex = f"""
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v];
[v]drawtext=text='{hook_text}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=100:enable='between(t,0,{t_hook})'[v1];
[v1]drawtext=text='{demo_text}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=400:enable='between(t,{t_hook},{t_demo})'[v2];
[v2]drawtext=text='{cta_text}':fontsize=50:fontcolor=yellow:x=(w-text_w)/2:y=1600:enable='between(t,{t_demo},{t_cta})'[v3];
[v3]drawbox=x=0:y=0:w=1080:h=1920:color=black@0.3:t=fill[v4]
"""
    
    # Find clips
    clip_files = list(clips_dir.glob("*.mp4")) + list(clips_dir.glob("*.mov"))
    if not clip_files:
        # Generate color clips as placeholder
        clip_inputs = ""
        filter_inputs = ""
        for i in range(5):
            clip_inputs += f" -f lavfi -i color=c=0x000000:size=1080x1920:duration={video_script.duration_sec/5}:rate=30 "
            filter_inputs += f"[{i+1}:v]"
        filter_inputs += f"concat=n=5:v=1:a=0[vc];"
        filter_complex = filter_inputs + filter_complex.replace("[0:v]", "[vc]")
    else:
        # Use first clip, loop if needed
        clip_inputs = f" -i \"{clip_files[0]}\" "
        filter_complex = filter_complex.replace("[0:v]", "[0:v]")
    
    cmd = f"""ffmpeg -y {clip_inputs} -i "{audio_path}" \\
  -filter_complex "{filter_complex.strip()}" \\
  -map "[v4]" -map 1:a \\
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \\
  -shortest -movflags +faststart \\
  "{output_path}"
"""
    return cmd.strip()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Video Generation Pipeline — Content Locking CPA")
    parser.add_argument("stage", choices=["scripts", "compose", "metadata", "all"], help="Pipeline stage")
    parser.add_argument("--topics", nargs="+", help="Topics to generate (default: all)")
    parser.add_argument("--variants", nargs="+", default=list(VARIANTS.keys()), help="Variants A/B/C")
    parser.add_argument("--platforms", nargs="+", default=["tiktok"], help="Target platforms")
    parser.add_argument("--output", default="cache/video_pipeline", help="Output directory")
    parser.add_argument("--clips", default="cache/video_clips", help="Stock clips directory")
    parser.add_argument("--audio", help="Voiceover audio file")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    clips_dir = Path(args.clips)
    
    if args.stage in ("scripts", "all"):
        print(f"[1/4] Generating scripts...")
        scripts = generate_batch(args.topics, args.variants, args.platforms)
        combined = save_scripts(scripts, output_dir)
        print(f"  Generated {len(scripts)} scripts → {combined}")
        
        if args.stage == "scripts":
            return
    
    if args.stage in ("compose", "all"):
        print(f"[2/4] Composing videos (placeholder)...")
        # Load scripts
        script_files = list(output_dir.glob("script_*.json"))
        if not script_files:
            print("  No scripts found. Run 'scripts' stage first.")
            return
        
        for sf in script_files[:3]:  # Demo: first 3
            script_data = json.loads(sf.read_text(encoding="utf-8"))
            vs = VideoScript(**script_data)
            
            # Placeholder: generate FFmpeg command
            audio_path = Path(args.audio) if args.audio else (clips_dir / "voiceover.mp3")
            output_path = output_dir / f"video_{vs.topic.lower().replace(' ', '_')}_{vs.variant}_{vs.platform}.mp4"
            
            cmd = render_ffmpeg_script(vs, clips_dir, audio_path, output_path)
            print(f"  FFmpeg for {vs.topic} ({vs.variant}):")
            print(f"  {cmd[:200]}...")
            
            # Save command
            cmd_path = output_path.with_suffix(".sh")
            cmd_path.write_text(cmd, encoding="utf-8")
        
        if args.stage == "compose":
            return
    
    if args.stage in ("metadata", "all"):
        print(f"[3/4] Generating metadata...")
        # Generate titles, descriptions, hashtags, UTM links
        script_files = list(output_dir.glob("script_*.json"))
        metadata_dir = output_dir / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        for sf in script_files:
            script_data = json.loads(sf.read_text(encoding="utf-8"))
            vs = VideoScript(**script_data)
            
            title = f"How to Get FREE {vs.topic.upper()} in 2024 (Actually Works)"
            if vs.variant == "B":
                title = f"⚡ ONLY 3 SPOTS LEFT — FREE {vs.topic.upper()}!"
            elif vs.variant == "C":
                title = f"🔥 1,247+ People Got FREE {vs.topic.upper()} Today!"
            
            description = f"""{vs.demo}

👉 {vs.cta}

#{' #'.join(['freestuff', 'giveaway', vs.topic.lower().replace(' ', ''), 'viral', 'fyp'])}"""
            
            utm_base = "https://mcduck-s8.github.io/hermes-salon-landing/cpa/"
            topic_slug = vs.topic.lower().replace(' ', '-')
            utm_url = f"{utm_base}{topic_slug}/?utm_source={vs.platform}&utm_medium=organic&utm_campaign=content_locking&utm_content={vs.utm_content}&utm_term={datetime.now().strftime('%m%d')}"
            
            metadata = {
                "title": title,
                "description": description,
                "hashtags": ["freestuff", "giveaway", vs.topic.lower().replace(" ", ""), "viral", "fyp"],
                "utm_url": utm_url,
                "thumbnail_text": f"FREE {vs.topic.upper()}",
                "script_file": str(sf),
            }
            
            meta_path = metadata_dir / f"meta_{vs.topic.lower().replace(' ', '_')}_{vs.variant}_{vs.platform}.json"
            meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  {meta_path.name}")
        
        if args.stage == "metadata":
            return
    
    print("\n✅ Pipeline stage complete")


if __name__ == "__main__":
    main()