# Faster-Whisper Guide for Video Learner

## Installation

```bash
pip install faster-whisper
```

## Model Sizes

| Size  | Parameters | VRAM (int8) | Speed | Accuracy |
|-------|------------|-------------|-------|----------|
| tiny  | 39M        | ~1 GB       | ~32x  | Baseline |
| base  | 74M        | ~1 GB       | ~16x  | Good     |
| small | 244M       | ~2 GB       | ~6x   | Better   |
| medium| 769M       | ~5 GB       | ~2x   | High     |
| large | 1.5B       | ~10 GB      | ~1x   | Best     |

**Recommended for video learning:** `base` or `small` with `int8` quantization.

## Usage

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("video.mp4", beam_size=5, word_timestamps=True)

for segment in segments:
    print(f"[{segment.start:.1f}s -> {segment.end:.1f}s] {segment.text}")
```

## GPU Acceleration

```python
# CUDA
model = WhisperModel("base", device="cuda", compute_type="float16")

# CPU with int8 (fastest on CPU)
model = WhisperModel("base", device="cpu", compute_type="int8")
```

## VAD (Voice Activity Detection)

```python
segments, info = model.transcribe(
    "video.mp4",
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500)
)
```

## Output Format

```python
for segment in segments:
    print(f"[{segment.start:.1f}s -> {segment.end:.1f}s] {segment.text}")
    for word in segment.words:
        print(f"  {word.start:.2f} {word.word} {word.end:.2f}")
```

## Multi-language

```python
# Auto-detect
segments, info = model.transcribe("video.mp4", language=None)

# Force language
segments, info = model.transcribe("video.mp4", language="ru")
```

## Performance Tips

1. Use `int8` on CPU for 2-4x speedup with minimal accuracy loss
2. Use `float16` on GPU for best speed/accuracy balance
3. `base` model is sweet spot for most use cases
4. Enable VAD to skip silence
5. Use `beam_size=5` for good accuracy/speed balance

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow on CPU | Use `int8` compute_type, smaller model |
| OOM on GPU | Use smaller model, `float16`, batch size 1 |
| Poor accuracy | Increase model size, use `float16`/`float32` |
| No GPU detected | Install CUDA toolkit, check `nvidia-smi` |

## Integration with Video Learner

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_video(video_path: str) -> list:
    segments, info = model.transcribe(
        video_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True
    )
    return [
        {
            "text": seg.text.strip(),
            "start": seg.start,
            "end": seg.end,
            "words": [{"word": w.word, "start": w.start, "end": w.end} for w in seg.words] if seg.words else []
        }
        for seg in segments
    ]
```