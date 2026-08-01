# VAD Voice Loop — Implementation Reference

## Architecture Overview

```
[sounddevice InputStream callback]
       │  30ms frames @ 16kHz, int16
       ▼
[Ring Buffer]  ← keeps last 0.5s (pre-buffer)
       │
       ▼  each frame
[webrtcvad.is_speech()]
       │
       ├── false & not recording → drop oldest frame from buffer
       ├── true & not recording → FREEZE buffer → start recording mode
       ├── false & recording → increment silence counter
       └── false & recording & silence >= threshold → FINALIZE utterance
                                                            │
                               ┌────────────────────────────┘
                               ▼
                    [Background Thread]
                    raw PCM → trim to speech boundaries
                           ↓
                    save WAV to temp
                           ↓
                    faster-whisper transcribe
                           ↓
                    LM Studio (HTTP) → response text
                           ↓
                    Edge TTS → play .mp3 via winsound
```

## Key Variables

| Variable | Default | Why |
|----------|---------|-----|
| `frame_ms` | 30ms | webrtcvad requirement: 10/20/30ms |
| `sample_rate` | 16000 | whisper native, VAD supports it |
| `frame_size` | 480 | `16000 × 0.03` |
| `pre_buffer_frames` | ~17 (0.5s) | Catches speech onset before VAD fires |
| `silence_frames` | ~50 (1.5s) | Natural speech pause |
| `min_speech_frames` | ~17 (0.5s) | Rejects coughs/click noise |
| `max_recording_frames` | ~1000 (30s) | Safety limit |

## VAD Buffer Algorithm

```python
buffer = []        # ring buffer, max = pre_buffer_frames + 5
recording = []     # current utterance
is_recording = False
silent_count = 0

def audio_callback(indata):
    frame = quantize_to_int16(indata)
    
    # Keep ring buffer topped
    buffer.append(frame)
    if len(buffer) > pre_buffer_frames + 5:
        buffer.pop(0)
    
    is_speech = vad.is_speech(frame, 16000)
    
    if not is_recording:
        if is_speech:
            # Start recording with pre-buffer
            is_recording = True
            silent_count = 0
            recording = list(buffer) + [frame]
        else:
            pass  # buffer handles itself
    else:
        recording.append(frame)
        
        if is_speech:
            silent_count = 0
        else:
            silent_count += 1
            
        if silent_count >= silence_frames:
            process_utterance(b''.join(recording))
            # reset state
```

## VAD Frame Size Validation

webrtcvad is strict about frame size. These are the only valid combinations:

| Sample Rate | 10ms | 20ms | 30ms |
|-------------|------|------|------|
| 8000 | 80 | 160 | 240 |
| 16000 | 160 | 320 | 480 |
| 32000 | 320 | 640 | 960 |
| 48000 | 480 | 960 | 1440 |

If frame size is wrong, `webrtcvad.Vad.is_speech()` raises `assertion error`.

## Thread Safety

- Audio callback runs in **real-time thread** — must not block
- LLM inference / TTS runs in **daemon thread(s)**
- asyncio.run_coroutine_threadsafe() bridges TTS back to event loop
- No locks needed — the VAD state (is_recording, silent_count) is only touched by the callback

## Windows-Specific Notes

- `winsound.PlaySound()` plays synchronously — for non-blocking TTS, run in thread
- sounddevice uses PortAudio MME/WASAPI depending on config
- If sounddevice fails with `UnanticipatedHostError`, install PyAudio as fallback:
  ```
  uv pip install pipwin
  pipwin install pyaudio
  ```

## Microphone Testing

```python
python -c "
import sounddevice as sd
import numpy as np
import time

def callback(indata, frames, time_info, status):
    vol = np.abs(indata).mean()
    bars = int(vol * 200)
    print(f'{\"█\" * bars}{\" \" * (40-bars)} {vol*100:.1f}%')

with sd.InputStream(samplerate=16000, channels=1, callback=callback):
    time.sleep(5)
"
```
