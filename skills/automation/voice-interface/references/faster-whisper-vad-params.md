# faster-whisper VAD parameter names

## Breaking change: v1.1.0 → v1.2.1

The `VadOptions` dataclass renamed its speech threshold parameters between versions:

| Version | Speech threshold | Silence threshold |
|---------|-----------------|-------------------|
| v1.1.0 | `onset` | `offset` |
| v1.2.1 | `threshold` | `neg_threshold` |

### Error

When running `python scripts/jarvis_voice_loop.py` with `faster-whisper < 1.2.0`:

```
TypeError: VadOptions.__init__() got an unexpected keyword argument 'threshold'
```

The script passes `vad_parameters=dict(threshold=0.5, min_speech_duration_ms=250, ...)` which only works in v1.2.x.

### Root cause

On this Windows setup, two different Python environments had different versions:
- System Python (`D:\Program Files\Python311\python.exe`) — `faster-whisper v1.1.0` (old API)
- venv Python (`hermes-agent\venv\Scripts\python.exe`) — `faster-whisper v1.2.1` (new API)

PowerShell resolves `python` → system Python, where the old version was installed.

### Fix

Upgrade system Python's faster-whisper:

```bash
"D:\Program Files\Python311\python.exe" -m pip install --upgrade faster-whisper
```

Verify:

```bash
"D:\Program Files\Python311\python.exe" -c "
from faster_whisper.transcribe import VadOptions
opts = VadOptions(threshold=0.5, min_speech_duration_ms=250, min_silence_duration_ms=500)
print('OK:', opts)
"
```

### Detection

To check which version a given Python will use:

```bash
python -c "import faster_whisper; print(f'v{faster_whisper.__version__}')"
```

If v1.1.x, the `VadOptions` class lives in `vad.py` and uses `onset`/`offset`.
If v1.2.x, the `VadOptions` class lives in `transcribe.py` and uses `threshold`/`neg_threshold`.
