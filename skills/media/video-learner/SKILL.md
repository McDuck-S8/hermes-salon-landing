---
name: video-learner
description: "Modular video learning capability: local transcription via faster-whisper, concept extraction via LLM, adaptation via PatternAdapter, storage in tactical_buffer. No yt-dlp dependency in core. yt-dlp handled via separate Docker/venv adapter."
version: "1.0.0"
author: "Hermes Agent"
tags:
  - video
  - transcription
  - learning
  - faster-whisper
  - modular
  - tactical-buffer
action_type: assist
output_type: skill
triggers:
  - video learning
  - video transcription
  - faster-whisper
  - video concept extraction
  - tactical buffer video
related_skills:
  - youtube-research
  - agent-autonomy-protocols
  - tactical-buffer
  - pattern-adapter
---

# Video Learner — Modular Video Learning Capability

## Overview
This skill provides a **modular, non-blocking video learning capability**. The core module uses local `faster-whisper` for transcription (no yt-dlp dependency in core). YouTube downloading is handled via a separate Docker/venv adapter (optional). All extracted concepts flow into the tactical buffer for validation and promotion.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VIDEO LEARNER                            │
├─────────────────────────────────────────────────────────────────┤
│  INPUT: local file OR URL                                       │
├─────────────────────────────────────────────────────────────────┤
│  STEP 1: TRANSCRIPTION                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ faster-whisper (local, GPU/CPU, multi-language)           │  │
│  │ Input: local file path or downloaded video                 │  │
│  │ Output: segments with timestamps + full of text with timestamps                  │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 2: CONCEPT EXTRACTION                                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ LLM + Structured Prompt                                   │  │
│  │ Input: transcript segments                                │  │
│  │ Output: structured concepts (JSON)                        │  │
│  │ - topic, key_points, action_items, tools, costs, etc.     │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 3: ADAPTATION (PatternAdapter)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ translation_map: foreign entities → local equivalents     │  │
│  │ e.g., "email" → "telegram", "AWS" → "local server"       │  │
│  │ Output: adapted concepts with local context               │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 4: TACTICAL BUFFER INSERTION                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ source: "video", confidence: 0.4, TTL: 7d                │  │
│  │ context_tags: {task_type, environment, video_id}         │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Module: `scripts/video_learner.py`

```python
#!/usr/bin/env python3
"""
Video Learner — Core Module
Local transcription + LLM extraction + PatternAdapter → tactical_buffer
"""

import json
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from faster_whisper import WhisperModel

# Import PatternAdapter from autonomy
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "autonomy"))
from pattern_adapter import PatternAdapter

@dataclass
class VideoConcept:
    """Extracted concept from video"""
    topic: str
    key_points: List[str]
    action_items: List[str]
    tools: List[str]
    costs: Dict[str, str]
    restricted_ok: bool
    source_video_id: str
    timestamp_start: float
    timestamp_end: float

class VideoLearner:
    """
    Core video learning module.
    Uses local faster-whisper, no yt-dlp dependency.
    """
    
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.adapter = PatternAdapter()
        self.translation_map = self._load_translation_map()
    
    def _load_translation_map(self) -> Dict[str, str]:
        """Load entity translation map for local adaptation"""
        map_path = Path(__file__).parent.parent / "cache" / "autonomy" / "translation_map.json"
        if map_path.exists():
            return json.loads(map_path.read_text())
        # Default mappings
        return {
            "email": "telegram",
            "slack": "telegram",
            "discord": "telegram",
            "aws": "local_server",
            "gcp": "local_server",
            "azure": "local_server",
            "stripe": "crypto_usdt",
            "paypal": "crypto_usdt",
            "patreon": "crypto_usdt",
            "substack": "telegram_channel",
            "youtube": "rutube_or_local",
            "instagram": "vk_or_telegram",
            "tiktok": "vk_clips_or_telegram",
            "linkedin": "habr_or_telegram",
            "github": "gitlab_or_local_git",
            "stackoverflow": "ru.stackoverflow_or_telegram",
            "reddit": "pikabu_or_telegram",
            "medium": "habr_or_telegra_ph",
        }
    
    def transcribe(self, video_path: str, language: str = "auto") -> List[Dict]:
        """
        Transcribe video using faster-whisper.
        Returns list of segments with text, start, end timestamps.
        """
        segments, info = self.model.transcribe(
            video_path,
            language=None if language == "auto" else language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        segments = []
        for seg in segments:
            segments.append({
                "text": seg.text.strip(),
                "start": seg.start,
                "end": seg.end,
                "words": [{"word": w.word, "start": w.start, "end": w.end} for w in seg.words] if seg.words else []
            })
        return segments
    
    def extract_concepts(self, segments: List[Dict], video_id: str) -> List[VideoConcept]:
        """Extract structured concepts from transcript segments using LLM"""
        # Combine transcript
        full_text = " ".join([s["text"] for s in segments])
        
        # Structured prompt for concept extraction
        prompt = f"""Extract structured concepts from this video transcript.
Video ID: {video_id}

Transcript:
{full_text[:8000]}

Output JSON array of concepts, each with:
- topic: main topic name
- key_points: array of key takeaways
- action_items: array of specific actions
- tools: array of tools/technologies mentioned
- costs: object with cost items and amounts
- restricted_ok: boolean (works in restricted regions)
- source_video_id: "{video_id}"
- timestamp_start: number
- timestamp_end: number

Only include concepts that are actionable and specific. Ignore fluff."""
        
        # Call LLM (using existing LLM client)
        from scripts.llm_client import llm_complete
        response = llm_complete(prompt, temperature=0.1, max_tokens=2000)
        
        try:
            concepts = json.loads(response)
            return [VideoConcept(**c) for c in concepts]
        except json.JSONDecodeError:
            return []
    
    def adapt_concepts(self, concepts: List[VideoConcept]) -> List[VideoConcept]:
        """Adapt concepts using translation_map"""
        adapted = []
        for concept in concepts:
            # Adapt tools
            adapted_tools = [self.translation_map.get(t.lower(), t) for t in concept.tools]
            # Adapt action items (simple string replacement)
            adapted_actions = []
            for action in concept.action_items:
                adapted = action
                for foreign, local in self.translation_map.items():
                    adapted = adapted.replace(foreign, local)
                adapted_actions.append(adapted)
            
            adapted_concept = VideoConcept(
                topic=concept.topic,
                key_points=concept.key_points,
                action_items=adapted_actions,
                tools=adapted_tools,
                costs=concept.costs,
                restricted_ok=concept.restricted_ok,
                source_video_id=concept.source_video_id,
                timestamp_start=concept.timestamp_start,
                timestamp_end=concept.timestamp_end
            )
            adapted.append(adapted_concept)
        return adapted
    
    def process_video(self, video_path: str, video_id: str = None, language: str = "auto") -> List[VideoConcept]:
        """Main pipeline: transcribe → extract → adapt → return concepts"""
        # Transcribe
        segments = self.transcribe(video_path)
        
        # Extract concepts
        concepts = self.extract_concepts(segments, video_id)
        
        # Adapt to local context
        adapted = self.adapt_concepts(concepts)
        
        return adapted
    
    def save_to_tactical_buffer(self, concepts: List[VideoConcept], video_id: str) -> List[str]:
        """Save adapted concepts to tactical buffer"""
        from scripts.autonomy.tactical_buffer import TacticalBuffer
        tb = TacticalBuffer()
        hypothesis_ids = []
        
        for concept in concepts:
            hid = tb.add(
                param=f"video_{video_id}_{concept.topic}",
                value=asdict(concept),
                source="video_learner",
                context_tags={
                    "task_type": "video_learning",
                    "source": "youtube_or_local",
                    "video_id": video_id,
                    "topic": concept.topic
                }
            )
            hypothesis_ids.append(hid)
        
        return hypothesis_ids


if __name__ == "__main__":
    import sys
    video_path = sys.argv[1] if len(sys.argv) > 1 else "test_video.mp4"
    video_id = sys.argv[2] if len(sys.argv) > 2 else Path(video_path).stem
    
    learner = VideoLearner()
    concepts = learner.process_video(video_path, video_id)
    ids = learner.save_to_tactical_buffer(concepts, video_id)
    print(f"Processed {len(concepts)} concepts, saved to tactical buffer: {ids}")
```

## Adapter: `scripts/video_learner/adapters/yt_dlp_adapter.py`

```python
#!/usr/bin/env python3
"""
yt-dlp Adapter — Optional YouTube Downloader
Run in isolated Docker/venv to avoid Python 3.13 compatibility issues.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

class YtDlpAdapter:
    """Optional yt-dlp adapter for YouTube downloads. Run in isolated environment."""
    
    def __init__(self, proxy: str = "socks5://127.0.0.1:10806"):
        self.proxy = proxy
        self.docker_image = "yt-dlp:latest"
    
    def download_audio(self, url: str, output_dir: Path) -> Path:
        """Download audio only, return path to audio file"""
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{output_dir}:/output",
            "-e", f"ALL_PROXY={self.proxy}",
            "yt-dlp:latest",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", "/output/%(id)s.%(ext)s",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")
        
        # Find downloaded file
        for f in output_dir.glob("*.mp3"):
            return f
        raise FileNotFoundError("No audio file found after download")
    
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """Get video metadata via yt-dlp --dump-json"""
        cmd = [
            "docker", "run", "--rm",
            "-e", f"ALL_PROXY={self.proxy}",
            "yt-dlp:latest",
            "--dump-json", "--no-download", url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp metadata failed: {result.stderr}")
        return json.loads(result.stdout)
    
    def get_subtitles(self, url: str, langs: list = ["en", "ru"]) -> Dict[str, str]:
        """Extract subtitles, return dict of lang -> subtitle text"""
        # Implementation for subtitle extraction
        pass


if __name__ == "__main__":
    adapter = YtDlpAdapter()
    # Test
    meta = adapter.get_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(json.dumps(meta, indent=2))
```

## Integration with Autonomy Core

```python
# In autonomy_core.py
from scripts.video_learner import VideoLearner

class AutonomyCore:
    def __init__(self):
        self.video_learner = VideoLearner()
    
    def process_video(self, video_path: str, video_id: str = None) -> List[str]:
        """Process video → concepts → tactical_buffer"""
        concepts = self.video_learner.process_video(video_path, video_id)
        return self.video_learner.save_to_tactical_buffer(concepts, video_id or "unknown")
```

## Usage

```bash
# Process local video
python scripts/video_learner.py /path/to/video.mp4 video_id_123

# Process YouTube URL (requires yt-dlp adapter in Docker)
python scripts/video_learner.py "https://youtu.be/VIDEO_ID" video_id_123 --use-docker

# Or use via autonomy core
python -c "
from scripts.autonomy_core import AutonomyCore
core = AutonomyCore()
core.process_video('my_video.mp4', 'my_video')
"
```

## Configuration

```yaml
# config/video_learner.yaml
video_learner:
  model_size: "base"  # tiny, base, small, medium, large
  device: "cpu"  # cpu, cuda
  compute_type: "int8"  # int8, float16, float32
  language: "auto"
  default_confidence: 0.4
  ttl_days: 7

  yt_dlp_adapter:
    enabled: true
    docker_image: "yt-dlp:latest"
    proxy: "socks5://127.0.0.1:10806"
    timeout: 300
    
  # yt-dlp-rescue (v2026-07-29) battle-tested settings
  rescue_settings:
    player_clients: ["tv", "web_embedded", "android_vr", "tv_downgraded", "web_creator", "mweb"]
    player_skip: "webpage"
    force_ipv4: true
    format_sort: "res:1080"
    extractor_args: "youtube:player_client=tv,web_embedded,android_vr,tv_downgraded,web_creator,mweb;player_skip=webpage"
```

## Verification

```bash
# Health check
python -c "from scripts.video_learner import VideoLearner; vl = VideoLearner(); print('VideoLearner OK')"

# Test transcription
python scripts/video_learner.py test_audio.mp3 test_video

# Check tactical buffer
python -c "
from scripts.autonomy.tactical_buffer import TacticalBuffer
tb = TacticalBuffer()
for h in tb.get_all():
    if h.source == 'video_learner':
        print(h.id, h.param, h.confidence)
"
```

## Integration Points

- **tactical_buffer** — receives hypotheses from video concepts
- **strategic_db** — promoted patterns after 3 occurrences / 80% success
- **feedback_store** — tracks video learning outcomes
- **pattern_adapter** — adapts external concepts to local context
- **youtube_research** — uses video_learner for deep-dive research

## DIRECTIVES (from agent-autonomy-protocols)

- **0x11: VIDEO_LEARNER_MODULARITY** — Core is `video_learner.py` with local `faster-whisper`. `yt-dlp` via separate Docker/venv adapter. Never block main process on video download.
- **0x10: YOUTUBE_RESEARCH_BATCHING** — For >5 queries: parallel batching, ≤5 per subagent, Agent Reach `yt-dlp` preferred.
- **0x0C: YT_DLP_FALLBACK** — When yt-dlp fails: 1) curl + v2rayN proxy + oembed, 2) curl + proxy + HTML regex, 3) isolated Python 3.11 venv/Docker.
- **0x10: YOUTUBE_RESEARCH_BATCHING** — For >5 queries: parallel batching, ≤5 per subagent, Agent Reach `yt-dlp` (5-10x faster). If subagent >60s — kill, retry with curl+v2rayN.
- **0x0F: SUBAGENT_ENV_INHERITANCE** — Subagent for video MUST inherit proxy env (ALL_PROXY, HTTPS_PROXY).
- **0x0E: PRINCIPAL_OBLIGATION** — If cannot provide full env to video subagent → execute self in background.

## References
- `references/faster-whisper-guide.md`
- `references/yt-dlp-docker-setup.md`
- `references/pattern-adapter-guide.md`
- `references/tactical-buffer-guide.md`