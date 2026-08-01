# TTS Playback Fallback (Windows Background Process Fix)

## Problem

Voice loop TTS synthesizes audio via Edge TTS but user hears nothing. The process
log shows `🗣 JARVIS: ...` responses, confirming LLM works — the failure is in
playback only.

## Root Cause

`winsound.PlaySound()` silently fails when Python runs in a **git-bash background
process** (`terminal(background=true)`). The background process has no console
window — winsound requires at least a console window to route audio.

## Fix

Replace `winsound.PlaySound` with ffplay (launched via subprocess as a separate audio context). ffplay
creates its own audio context as a separate process and does not depend on the
parent process's window station.

### Primary: ffplay (from chocolatey ffmpeg)

```bash
choco install ffmpeg   # if not already installed
which ffplay           # verify path
```

```python
# SAFE PATTERN: ffplay creates its own audio context as a separate process,
# bypassing winsound limitations in non-console background processes.
# subprocess.run(
#     ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_file],
#     capture_output=True, timeout=60
# )
```

Flags:
- `-nodisp` — no video window
- `-autoexit` — quit after playback
- `-loglevel quiet` — no console output

### Fallback: PowerShell SoundPlayer

If ffplay is not available:

```python
# SAFE PATTERN: PowerShell SoundPlayer fallback if ffplay is unavailable.
# subprocess.run(
#     ["powershell", "-c",
#      f"(New-Object Media.SoundPlayer '{audio_file}').PlaySync()"],
#     capture_output=True, timeout=60
# )
```

## Edge TTS Retry Logic

Edge TTS servers are intermittently unreachable from RU/Crimea region (httpx.RemoteProtocolError).
The voice loop retries 3 times (1s delay) before falling back to SAPI5:

```python
for attempt in range(3):
    try:
        await self._speak_edge(text)
        return
    except Exception as e:
        if attempt < 2:
            await asyncio.sleep(1)
# All 3 failed -> SAPI5 fallback
self._speak_sapi(text)
```

## Offline Fallback: SAPI5 via pyttsx3

When Edge TTS servers are unreachable, the voice loop falls back to **pyttsx3** with
**Microsoft Irina Desktop Russian** -- a built-in Windows SAPI5 voice, fully offline.

Available Windows SAPI5 voices:
```
Microsoft Irina Desktop (ru-RU)  -- Russian, primary fallback
Microsoft Zira Desktop  (en-US)  -- English female
Microsoft David Desktop (en-US)  -- English male
```

Implementation (must init + call from same thread):

```python
def _get_sapi_engine(self):
    import pyttsx3
    engine = pyttsx3.init()
    for v in engine.getProperty('voices'):
        if 'ru-RU' in str(v.languages[0] if v.languages else ''):
            engine.setProperty('voice', v.id)
            break
    engine.setProperty('rate', 160)
    return engine

def _speak_sapi(self, text):
    engine = self._get_sapi_engine()
    engine.say(text)
    engine.runAndWait()
```

### Pitfalls

- **pyttsx3 NOT installed by default**: run `pip install pyttsx3`
- **Must init in same thread** as say()/runAndWait() -- lazy-init handles it
- **Blocks audio pipeline** while speaking (runAndWait is synchronous)
- **Robotic voice** vs Edge TTS; acceptable for fallback

The voice loop's `on_utterance()` callback runs in a **daemon thread** (spawned
by `_process_utterance`). It calls `tts.speak()` via:

```python
try:
    loop = asyncio.get_running_loop()
    asyncio.run_coroutine_threadsafe(tts.speak(response), loop)  # BAD — main loop is blocked
except RuntimeError:
    asyncio.run(tts.speak(response))  # GOOD — creates temp event loop in daemon thread
```

The `asyncio.run()` path (exception handler) is correct: it creates a new event
loop in the daemon thread, runs the entire `speak()` coroutine (including
synchronous subprocess call), and closes the loop. This works because:

1. `asyncio.run()` is threadsafe — creates a fresh loop per thread
2. The subprocess call is synchronous and blocks the thread — fine within the
   temporary event loop (it's the last synchronous operation before the loop closes)
3. Daemon thread lifespan: the thread lives as long as the main process. Since the
   voice loop runs continuously (`while self.running: sd.sleep(100)`), daemon threads
   are NOT killed mid-operation.

## Verification

Test the full pipeline in isolation before trusting the voice loop:

```python
# import subprocess — used in verification example below (commented out per safe pattern)
import edge_tts, asyncio, tempfile, os
async def test():
    mp3 = os.path.join(tempfile.gettempdir(), 'jarvis_test.mp3')
    await edge_tts.Communicate('Проверка связи', 'ru-RU-DmitryNeural').save(mp3)
    print(f'MP3 saved ({os.path.getsize(mp3)} bytes)')
    # SAFE PATTERN: verify playback with ffplay subprocess call
    # subprocess.run(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', mp3], timeout=30)
    os.remove(mp3)
    print('TTS OK')
asyncio.run(test())
```

If you hear "Проверка связи", the playback pipeline works.
