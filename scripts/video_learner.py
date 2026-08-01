#!/usr/bin/env python3
"""
Video Learner Module — Local Video Processing Pipeline
Uses faster-whisper (local) + OpenRouter LLM for concept extraction.
Does NOT require yt-dlp. Works with local video/audio files.
Integrates with tactical_buffer for hypothesis storage.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add scripts to path
SCRIPTS_DIR = Path(__file__).parent
HERMES_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from autonomy.tactical_buffer import TacticalBuffer


class VideoLearner:
    """
    Local video processing pipeline:
    1. Extract audio from video (ffmpeg)
    2. Transcribe with faster-whisper (local)
    3. Extract concepts via LLM (OpenRouter)
    4. Save hypotheses to tactical_buffer
    """
    
    def __init__(self, model_size: str = "large-v3", device: str = "auto", compute_type: str = "float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.tb = TacticalBuffer()
        self.whisper_model = None
        
    def _load_whisper(self):
        """Lazy load faster-whisper model"""
        if self.whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel(
                    self.model_size, 
                    device=self.device, 
                    compute_type=self.compute_type
                )
            except ImportError:
                raise RuntimeError("faster-whisper not installed: pip install faster-whisper")
        return self.whisper_model
    
    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """Extract audio from video using ffmpeg"""
        if output_path is None:
            output_path = video_path.rsplit('.', 1)[0] + '.wav'
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr}")
        
        return output_path
    
    def transcribe(self, audio_path: str, language: str = None) -> Dict:
        """Transcribe audio using faster-whisper"""
        model = self._load_whisper()
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Collect segments
        segments_list = []
        full_text = []
        
        for segment in segments:
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": [
                    {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                    for w in (segment.words or [])
                ] if segment.words else []
            })
            full_text.append(segment.text.strip())
        
        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "text": " ".join(full_text),
            "segments": segments_list
        }
    
    def extract_concepts(self, transcript: str, metadata: Dict = None) -> List[Dict]:
        """Extract concepts from transcript using OpenRouter LLM"""
        # Use existing OpenRouter client pattern from project
        try:
            from openrouter_client import openrouter_chat
        except ImportError:
            # Fallback to direct API call
            return self._extract_concepts_direct(transcript, metadata)
        
        prompt = self._build_extraction_prompt(transcript, metadata)
        
        try:
            response = openrouter_chat([
                {"role": "system", "content": "You are a concept extractor. Extract actionable business/technical concepts from video transcripts. Output JSON only."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse JSON from response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return self._parse_concepts_json(content)
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            return self._fallback_extraction(transcript)
    
    def _build_extraction_prompt(self, transcript: str, metadata: Dict) -> str:
        video_info = ""
        if metadata:
            video_info = f"Video: {metadata.get('title', 'Unknown')}\nAuthor: {metadata.get('author', 'Unknown')}\n"
        
        return f"""{video_info}
Extract actionable concepts from this transcript. Focus on:
- Business models / value propositions
- Technical methods / tools / workflows
- Cost structures / pricing / revenue models
- Step-by-step processes / frameworks
- Specific tools / platforms / APIs mentioned
- Costs / pricing numbers
- Target audiences / customer segments
- Key metrics / results

Output JSON array of concepts:
[
  {{
    "concept": "string",
    "type": "business_model|technical_method|tool|pricing|workflow|framework|metric",
    "description": "string",
    "confidence": 0.0-1.0,
    "source_evidence": "exact quote or timestamp reference"
  }}
]

Transcript:
{transcript[:8000]}"""
    
    def _parse_concepts_json(self, content: str) -> List[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Find JSON array in response
            import re
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(content)
        except:
            return []
    
    def _fallback_extraction(self, transcript: str) -> List[Dict]:
        """Simple keyword-based fallback"""
        concepts = []
        keywords = {
            "business_model": ["business model", "revenue", "monetization", "pricing", "subscription"],
            "tool": ["tool", "platform", "API", "software", "library", "framework"],
            "workflow": ["workflow", "process", "step by step", "pipeline", "automation"],
            "technical_method": ["method", "technique", "algorithm", "approach", "implementation"],
            "pricing": ["price", "cost", "$", "USD", "per month", "per year"],
            "metric": ["conversion", "ROI", "CTR", "CAC", "LTV", "retention", "growth"]
        }
        
        text_lower = transcript.lower()
        for concept_type, kws in keywords.items():
            for kw in kws:
                if kw in text_lower:
                    concepts.append({
                        "concept": kw.replace("_", " "),
                        "type": concept_type,
                        "description": f"Mentioned in context: {kw}",
                        "confidence": 0.5,
                        "source_evidence": f"Keyword '{kw}' found in transcript"
                    })
                    break
        return concepts
    
    def _extract_concepts_direct(self, transcript: str, metadata: Dict) -> List[Dict]:
        """Direct API call to OpenRouter"""
        import requests
        import os
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return self._fallback_extraction(transcript)
        
        prompt = self._build_extraction_prompt(transcript, metadata)
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemini-flash-1.5",
                    "messages": [
                        {"role": "system", "content": "Extract actionable concepts from transcripts. JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return self._parse_concepts_json(content)
        except Exception as e:
            print(f"Direct API failed: {e}")
        
        return self._fallback_extraction(transcript)
    
    def process_local_file(self, video_path: str, metadata: Dict = None) -> Dict:
        """
        Main pipeline: video/audio file -> concepts -> tactical_buffer
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {"error": f"File not found: {video_path}"}
        
        metadata = metadata or {}
        metadata.setdefault("title", video_path.stem)
        metadata.setdefault("source", "local_file")
        
        # 1. Extract audio if video
        audio_path = video_path
        if video_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
            print(f"Extracting audio from {video_path}...")
            audio_path = self.extract_audio(str(video_path))
            metadata["extracted_audio"] = True
        elif video_path.suffix.lower() in ['.wav', '.mp3', '.m4a', '.flac']:
            metadata["extracted_audio"] = False
        else:
            return {"error": f"Unsupported file type: {video_path.suffix}"}
        
        # 2. Transcribe
        print(f"Transcribing {audio_path}...")
        transcript_data = self.transcribe(str(audio_path))
        transcript = transcript_data["text"]
        language = transcript_data["language"]
        
        # 3. Extract concepts
        print("Extracting concepts...")
        concepts = self.extract_concepts(transcript, metadata)
        
        # 4. Save to tactical_buffer
        saved = 0
        for concept in concepts:
            hyp_id = self.tb.add(
                param=f"video_concept_{concept.get('concept', 'unknown').lower().replace(' ', '_')}",
                value={
                    "concept": concept.get("concept"),
                    "type": concept.get("type"),
                    "description": concept.get("description"),
                    "confidence": concept.get("confidence", 0.4),
                    "source": "video",
                    "source_metadata": metadata,
                    "language": language
                },
                source="video_learner",
                context_tags={
                    "task_type": "video_concept_extraction",
                    "environment": "production",
                    "video_source": "local_file",
                    "language": language
                }
            )
            saved += 1
            print(f"  Saved: {concept.get('concept')} -> {hyp_id}")
        
        # Cleanup temp audio if extracted
        if metadata.get("extracted_audio") and Path(audio_path).exists():
            try:
                os.remove(audio_path)
            except:
                pass
        
        return {
            "status": "success",
            "video_path": str(video_path),
            "transcript_length": len(transcript),
            "language": language,
            "concepts_extracted": len(concepts),
            "hypotheses_saved": saved,
            "concepts": concepts
        }
    
    def process_youtube_url(self, url: str, metadata: Dict = None) -> Dict:
        """
        Process YouTube URL - downloads audio, transcribes, extracts concepts.
        Requires yt-dlp (see yt-dlp compatibility notes).
        """
        # This requires yt-dlp working. For now, return guidance.
        return {
            "error": "YouTube URL processing requires yt-dlp. Use local file processing or set up yt-dlp in compatible Python environment.",
            "guidance": "Use Python 3.11 venv with yt-dlp, or process downloaded local file via process_local_file()"
        }


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Learner - Local video concept extraction")
    parser.add_argument("input", help="Video/audio file path or YouTube URL")
    parser.add_argument("--model", default="large-v3", help="Whisper model size")
    parser.add_argument("--device", default="auto", help="Device: auto, cpu, cuda")
    parser.add_argument("--lang", help="Language code (optional)")
    parser.add_argument("--title", help="Video title for metadata")
    parser.add_argument("--author", help="Author/channel name")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    learner = VideoLearner(model_size=args.model, device=args.device)
    
    metadata = {}
    if args.title:
        metadata["title"] = args.title
    if args.author:
        metadata["author"] = args.author
    
    if args.input.startswith("http"):
        result = learner.process_youtube_url(args.input, metadata)
    else:
        result = learner.process_local_file(args.input, metadata)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()