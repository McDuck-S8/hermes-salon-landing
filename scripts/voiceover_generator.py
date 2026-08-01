#!/usr/bin/env python3
"""
Voiceover Generator — ElevenLabs TTS
Generates MP3 files from script lines
"""

import os
import sys
import json
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

HERMES = Path("D:/Portable_Soft/hermes")
CACHE = HERMES / "cache" / "video_pipeline" / "voiceover"
CACHE.mkdir(parents=True, exist_ok=True)

ELEVENLABS_API = "https://api.elevenlabs.io/v1"
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Voice settings per niche
VOICE_CONFIG = {
    "gaming": {"voice_id": "21m00Tcm4TlvDq8ikWAM", "stability": 0.5, "similarity_boost": 0.75},  # Energetic male
    "tech": {"voice_id": "AZnzlk1XvdvUeBnXmlld", "stability": 0.6, "similarity_boost": 0.7},      # Professional
    "crypto": {"voice_id": "VR6AewLTigWG4xSOukaG", "stability": 0.4, "similarity_boost": 0.8},     # Hype
    "default": {"voice_id": "21m00Tcm4TlvDq8ikWAM", "stability": 0.5, "similarity_boost": 0.75},
}

TOPIC_NICHE = {
    "Free V-Bucks": "gaming",
    "Free Robux": "gaming", 
    "Free GTA Money": "gaming",
    "Netflix Generator": "tech",
    "Spotify Premium": "tech",
    "Free Crypto": "crypto",
    "Amazon Gift Card": "tech",
}

@dataclass
class VoiceoverLine:
    text: str
    filename: str
    duration_estimate: float  # seconds

class VoiceoverGenerator:
    def __init__(self):
        self.api_key = ELEVENLABS_KEY
        if not self.api_key:
            print("WARNING: ELEVENLABS_API_KEY not set. Using mock mode.")
    
    def _get_voice_config(self, topic: str) -> Dict:
        niche = TOPIC_NICHE.get(topic, "default")
        return VOICE_CONFIG.get(niche, VOICE_CONFIG["default"])
    
    def _estimate_duration(self, text: str) -> float:
        # ~150 words per minute = 2.5 words per second
        words = len(text.split())
        return max(words / 2.5, 1.0)
    
    async def generate(self, text: str, topic: str, line_num: int) -> Optional[Path]:
        """Generate voiceover MP3 for a single line"""
        voice_cfg = self._get_voice_config(topic)
        voice_id = voice_cfg["voice_id"]
        
        # Create cache key
        cache_key = hashlib.md5(f"{text}{voice_id}".encode()).hexdigest()[:12]
        safe_topic = topic.replace(" ", "_").lower()
        filename = f"{safe_topic}_line{line_num}_{cache_key}.mp3"
        path = CACHE / safe_topic / filename
        path.parent.mkdir(exist_ok=True)
        
        if path.exists() and path.stat().st_size > 1000:
            return path
        
        if not self.api_key:
            # Mock mode - create silent MP3 placeholder
            print(f"  [MOCK] Would generate: {text[:50]}...")
            # Create minimal valid MP3 (silent)
            import subprocess
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(self._estimate_duration(text)),
                "-c:a", "libmp3lame", "-b:a", "128k", str(path)
            ], capture_output=True)
            return path
        
        url = f"{ELEVENLABS_API}/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": voice_cfg["stability"],
                "similarity_boost": voice_cfg["similarity_boost"],
            },
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(path, 'wb') as f:
                            async for chunk in resp.content.iter_chunked(8192):
                                await f.write(chunk)
                        print(f"  Generated: {filename} ({path.stat().st_size/1024:.0f}KB)")
                        return path
                    else:
                        err = await resp.text()
                        print(f"  ElevenLabs error {resp.status}: {err}")
        except Exception as e:
            print(f"  Failed: {e}")
        return None
    
    async def generate_script(self, script: Dict, topic: str) -> List[Path]:
        """Generate voiceovers for all lines in a script"""
        lines = [
            ("hook", script.get("hook", "")),
            ("demo", script.get("demo", "")),
            ("cta", script.get("cta", "")),
        ]
        results = []
        for i, (name, text) in enumerate(lines, 1):
            if text:
                path = await self.generate(text, topic, i)
                if path:
                    results.append(path)
        return results


async def main():
    import argparse
    import hashlib
    parser = argparse.ArgumentParser()
    parser.add_argument("--script-file", help="JSON file with scripts")
    parser.add_argument("--topic", help="Single topic to generate for")
    parser.add_argument("--hook", help="Hook text")
    parser.add_argument("--demo", help="Demo text")
    parser.add_argument("--cta", help="CTA text")
    args = parser.parse_args()
    
    gen = VoiceoverGenerator()
    
    if args.script_file:
        with open(args.script_file) as f:
            scripts = json.load(f)
        for script in scripts:
            topic = script.get("topic", "Unknown")
            print(f"\n=== {topic} ({script.get('variant')}) ===")
            await gen.generate_script(script, topic)
    elif args.topic:
        script = {
            "hook": args.hook or "Want free stuff?",
            "demo": args.demo or "Click the link and complete an offer.",
            "cta": args.cta or "Link in bio!",
        }
        await gen.generate_script(script, args.topic)
    else:
        print("Usage: --script-file <file> OR --topic <topic> [--hook --demo --cta]")

if __name__ == "__main__":
    asyncio.run(main())