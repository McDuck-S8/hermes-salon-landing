#!/usr/bin/env python3
"""
FFmpeg Composer — Assemble clips + voiceover + text overlays → MP4
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

CACHE = Path("D:/Portable_Soft/hermes/cache")
STOCK = CACHE / "stock_footage"
VOICE = CACHE / "voiceovers"
OUTPUT = CACHE / "videos"
OUTPUT.mkdir(parents=True, exist_ok=True)

@dataclass
class VideoSpec:
    topic: str
    variant: str
    platform: str
    hook: str
    demo: str
    cta: str
    duration: int = 15
    utm_content: str = ""

class FFmpegComposer:
    def __init__(self):
        self.font_path = "C:/Windows/Fonts/arial.ttf"  # Windows
        if not Path(self.font_path).exists():
            self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    def _escape_text(self, text: str) -> str:
        """Escape text for FFmpeg drawtext filter"""
        return text.replace("'", "\\'").replace(":", "\\:").replace("%", "\\%")
    
    def _build_filter(self, spec: VideoSpec, clip_count: int, clip_duration: float) -> str:
        """Build FFmpeg filter_complex for composition"""
        t_hook = 3
        t_demo = spec.duration - 4  # leave 1s for CTA
        t_cta = spec.duration
        
        hook = self._escape_text(spec.hook)
        demo = self._escape_text(spec.demo)
        cta = self._escape_text(spec.cta)
        
        # Build concat input for clips
        if clip_count > 1:
            clip_inputs = "".join(f"[{i}:v]" for i in range(clip_count))
            concat_filter = f"{clip_inputs}concat=n={clip_count}:v=1:a=0[vc];"
        else:
            concat_filter = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[vc];"
        
        filter_complex = f"""
{concat_filter}
[vc]drawtext=fontfile={self.font_path}:text='{hook}':fontsize=70:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=150:enable='between(t,0,{t_hook})'[v1];
[v1]drawtext=fontfile={self.font_path}:text='{demo}':fontsize=45:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=500:enable='between(t,{t_hook},{t_demo})'[v2];
[v2]drawtext=fontfile={self.font_path}:text='{cta}':fontsize=60:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=1650:enable='between(t,{t_demo},{t_cta})'[v3];
[v3]drawbox=x=0:y=0:w=1080:h=1920:color=black@0.2:t=fill[vout]
"""
        return filter_complex.strip()
    
    def compose(self, spec: VideoSpec, clips: List[Path], audio: Path, output: Path) -> bool:
        """Compose final video"""
        if not clips:
            print("  No clips provided")
            return False
        if not audio.exists():
            print(f"  Audio not found: {audio}")
            return False
        
        # Build command
        clip_inputs = " ".join(f'-i "{c}"' for c in clips)
        
        filter_complex = self._build_filter(spec, len(clips), spec.duration / len(clips))
        
        cmd = f"""ffmpeg -y {clip_inputs} -i "{audio}" \\
  -filter_complex "{filter_complex}" \\
  -map "[vout]" -map {len(clips)}:a \\
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \\
  -shortest -movflags +faststart \\
  -t {spec.duration} \\
  "{output}"
"""
        
        print(f"  Composing {spec.topic} ({spec.variant}) → {output.name}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and output.exists():
            print(f"  ✅ Done: {output.stat().st_size/1024/1024:.1f}MB")
            return True
        else:
            print(f"  ❌ Failed: {result.stderr[:500]}")
            return False
    
    def compose_batch(self, specs: List[VideoSpec], clips_dir: Path, audio_dir: Path) -> List[Path]:
        """Compose multiple videos"""
        outputs = []
        for spec in specs:
            safe_topic = spec.topic.replace(" ", "_").lower()
            clip_paths = list((clips_dir / safe_topic).glob("*.mp4"))[:5]
            audio_path = audio_dir / safe_topic / f"{safe_topic}_line1_*.mp3"
            audio_matches = list(audio_dir.glob(f"{safe_topic}/*.mp3"))
            
            if not clip_paths:
                print(f"  ⚠️ No clips for {spec.topic}")
                continue
            if not audio_matches:
                print(f"  ⚠️ No audio for {spec.topic}")
                continue
            
            # Use first audio file (hook) - ideally should concatenate all lines
            audio_path = audio_matches[0]
            output_path = OUTPUT / f"video_{safe_topic}_{spec.variant}_{spec.platform}.mp4"
            
            if self.compose(spec, clip_paths, audio_path, output_path):
                outputs.append(output_path)
        return outputs


def load_scripts(scripts_dir: Path) -> List[VideoSpec]:
    """Load video scripts from JSON files"""
    specs = []
    for f in scripts_dir.glob("script_*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            specs.append(VideoSpec(**data))
        except Exception as e:
            print(f"  Failed to load {f}: {e}")
    return specs


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scripts", default="cache/video_pipeline", help="Scripts directory")
    parser.add_argument("--clips", default="cache/stock_footage", help="Clips directory")
    parser.add_argument("--audio", default="cache/voiceovers", help="Audio directory")
    parser.add_argument("--output", default="cache/videos", help="Output directory")
    parser.add_argument("--topic", help="Single topic to compose")
    parser.add_argument("--variant", default="A", help="Variant A/B/C")
    parser.add_argument("--platform", default="tiktok", help="Platform")
    args = parser.parse_args()
    
    composer = FFmpegComposer()
    
    if args.topic:
        # Single video
        spec = VideoSpec(
            topic=args.topic,
            variant=args.variant,
            platform=args.platform,
            hook="Want free " + args.topic + "?",
            demo="Click the link, complete an offer, get it free.",
            cta="Link in bio!",
        )
        clips = list(Path(args.clips).glob(f"{args.topic.replace(' ', '_').lower()}/*.mp4"))[:5]
        audio = list(Path(args.audio).glob(f"{args.topic.replace(' ', '_').lower()}/*.mp3"))
        if clips and audio:
            output = Path(args.output) / f"video_{args.topic.replace(' ', '_')}_{args.variant}_{args.platform}.mp4"
            composer.compose(spec, clips, audio[0], output)
    else:
        # Batch
        specs = load_scripts(Path(args.scripts))
        if not specs:
            print("No scripts found")
            return
        outputs = composer.compose_batch(specs, Path(args.clips), Path(args.audio))
        print(f"\n✅ Composed {len(outputs)} videos")


if __name__ == "__main__":
    main()