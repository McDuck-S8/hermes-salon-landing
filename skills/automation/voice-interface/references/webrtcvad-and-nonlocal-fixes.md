# webrtcvad + nonlocal fixes

## Session: 2026-06-10

### Error 1 — ModuleNotFoundError: No module named 'webrtcvad'

When running `python scripts/jarvis_voice_loop.py` from PowerShell:

```
Traceback:
  File "jarvis_voice_loop.py", line 99, in __init__
    import webrtcvad
ModuleNotFoundError: No module named 'webrtcvad'
```

**Root cause**: `webrtcvad` was installed in the hermes-agent venv site-packages, but the voice loop
runs via system Python (D:\Program Files\Python311\python.exe). On this Windows setup:
- git-bash (agent terminal) resolves `python` → venv first
- PowerShell (user) resolves `python` → system Python first

**Fix**: Install explicitly into system Python:
```bash
"D:\Program Files\Python311\python.exe" -m pip install webrtcvad
```

Verify:
```bash
"D:\Program Files\Python311\python.exe" -c "import webrtcvad; v=webrtcvad.Vad(2); print('VAD OK')"
```

### Error 2 — UnboundLocalError: utterance_count

After fixing webrtcvad, the voice loop crashed with:

```
UnboundLocalError: local variable 'utterance_count' referenced before assignment
```

**Root cause**: In `jarvis_voice_loop.py`, line 188 declares `utterance_count = 0` in `process_stream()`,
but line 191's `nonlocal` declaration omitted it:

```python
# Line 188
utterance_count = 0

def audio_callback(indata, frames, time_info, status):
    # Line 191 — utterance_count NOT listed
    nonlocal buffer, recording, is_recording, silent_count, total_frames
    ...
    utterance_count += 1  # Line 238 — UnboundLocalError
```

Python treats `utterance_count += 1` as an assignment to a local variable. Since `utterance_count`
isn't declared `nonlocal`, Python creates a new local — but it's referenced before assignment.

**Fix**: Add `utterance_count` to the nonlocal declaration:

```python
nonlocal buffer, recording, is_recording, silent_count, total_frames, utterance_count
```

### Pattern

Any new state variable added to the voice loop that is assigned inside `audio_callback` must be:
1. Declared in `process_stream()` scope (before `audio_callback` definition)
2. Added to the `nonlocal` statement at the top of `audio_callback`
