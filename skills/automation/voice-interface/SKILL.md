---
name: voice-interface
description: Voice interface stack for Hermes — VAD (WebRTC), STT (faster-whisper), TTS (Edge TTS), microphone, voice-loop architecture
version: 1.7.0
author: Hermes
tags: [voice, vad, stt, tts, whisper, webrtcvad, edge-tts, microphone, voice-loop]
---

# Voice Interface

## Overview

Voice interface stack for Hermes Agent: continuous VAD (Voice Activity Detection) → STT (Speech-to-Text) → LLM → TTS (Text-to-Speech) → audio output.

## Components

| Layer | Tool | Status |
|-------|------|--------|
| **VAD** | webrtcvad 2.0+ | Voice activity detection — knows when speech starts/stops |
| **STT** | faster-whisper | Local transcription, models: tiny/base/small/medium/large |
| **LLM** | model_registry.get_working_model() | Auto-detects: FreeDeepseekAPI → opencode-zen → LM Studio |
| **TTS** | Edge TTS (retry x3) -> SAPI5 pyttsx3 fallback (offline) | Russian: ru-RU-DmitryNeural / ru-RU-Irina (SAPI5) |
| **Mic** | sounddevice (PyAudio alternative) | PortAudio binding, async callbacks |

## Voice-Loop Architecture

The voice loop runs in a **single thread with audio callback** pattern:

```
Audio Stream (callback)
  → frame_buffer (ring, keeps pre-buffer frames)
  → VAD.is_speech() on each 30ms frame
    → no speech: keep buffering (circular, ~0.5s)
    → speech start: freeze buffer + start recording
    → speech end (silence >= N sec): process utterance
  → background thread: STT → LLM → TTS.play()
```

### Key Design Decisions

1. **sounddevice.InputStream** with callback — lowest latency on Windows
2. **VAD runs per-frame** (30ms @ 16kHz, 480 samples) — not on accumulated audio
3. **Pre-buffer** (0.5s) — captures the start of speech before VAD fires
4. **Silence timeout** (1.5s default) — natural pause before processing
5. **Processing in daemon thread** — doesn't block audio capture
6. **webrtcvad** — pure C implementation, 0.5ms/frame on CPU, far cheaper than ML VAD

## Setup

```bash
# Install dependencies (system Python, NOT uv — voice-loop runs via system python)
python -m pip install webrtcvad sounddevice faster-whisper edge-tts

# Optional: offline TTS fallback via SAPI5 (Windows only)
python -m pip install pyttsx3

# Verify ALL imports work from the Python that will run the script
python -c "import webrtcvad; v=webrtcvad.Vad(2); print('VAD OK')"
python -c "import faster_whisper; print('whisper OK')"
python -c "import edge_tts; print('TTS OK')"
python -c "import sounddevice; print('mic OK')"
```

**⚠️ Shell PATH ambiguity** — `python` may resolve differently depending on the shell:
- **git-bash (my terminal)**: PATH may resolve to `hermes-agent/venv/Scripts/python.exe` first
- **PowerShell**: resolves to `D:\\Program Files\\Python311\\python.exe` (system Python)
- If installation seems to succeed but the script can't import, check which Python you're installing into:
  ```bash
  where python   # all paths, first one wins
  ```
  If unsure, install explicitly into system Python:
  ```bash
  "D:\\Program Files\\Python311\\python.exe" -m pip install webrtcvad sounddevice faster-whisper edge-tts
  ```

  **Version sync between shells**: if `python` resolves differently in git-bash vs PowerShell,
  package versions can drift. When you install or upgrade a dependency in one environment, do the
  same in the other. Check both:
  ```bash
  python -c "import faster_whisper; print(f'v{faster_whisper.__version__}')"
  "D:\\Program Files\\Python311\\python.exe" -c "import faster_whisper; print(f'v{faster_whisper.__version__}')"
  ```

**Disk space note**: uv's cache lives on `C:\\` and fills up. Voice-loop runs on system Python,
not uv. If `C:\\` is nearly full, set temp vars before pip install:
```bash
set TMPDIR=D:\\tmp
set TEMP=D:\\tmp
set TMP=D:\\tmp
```
The script writes WAV temp files — also handled via `tempfile.gettempdir()` (falls to `D:\\tmp`).

## VAD Aggressiveness

| Level | Behavior | Best for |
|-------|----------|----------|
| 0 | Most sensitive, catches whispers | Quiet rooms, soft speakers |
| 1 | Normal sensitivity | General use |
| 2 (default) | Moderate filtering | Noisy environments |
| 3 | Most aggressive, only clear speech | Loud rooms, music in background, or when level 2 misses speech |

Note: Russian speech has different rhythm and consonant clusters than English.
If VAD misses Russian utterances at level 2, try level 3 (paradoxically, it catches
the sharper consonant onsets better in some microphone setups).

## Whisper Model Sizes

| Model | RAM | Speed on i3-6006U | Quality |
|-------|-----|-------------------|---------|
| tiny (~150MB) | ~1GB | <1s | OK, misses some words |
| base (~290MB) | ~1.5GB | ~1-2s | Good, default |
| small (~770MB) | ~2GB | ~3-5s | Very good |
| medium (~1.5GB) | ~3GB | ~8-12s | Excellent |

## Edge TTS — Voices

### British English (for JARVIS English mode)

```
en-GB-RyanNeural   → Male, natural, calm — best for JARVIS
en-GB-ThomasNeural → Male, deeper voice
en-GB-LibbyNeural  → Female
en-GB-MaisieNeural → Female, youthful
en-GB-SoniaNeural  → Female
```

### Russian (for JARVIS Russian mode)

```
ru-RU-DmitryNeural   → Male, friendly, positive — best for JARVIS Russian
ru-RU-SvetlanaNeural → Female, friendly, positive
```

List all available Russian voices:
```bash
edge-tts --list-voices | grep ru-
```

### Russian language support

For Russian speech recognition and synthesis, the voice loop needs three changes:

1. **STT language**: `stt_language: "ru"` in CONFIG — Whisper detects Russian better with explicit language hint
2. **TTS voice**: `tts_voice: "ru-RU-DmitryNeural"` — Edge TTS Russian male voice
3. **System prompt**: must be in Russian, otherwise Qwen/LLM models trained on mixed data may reply in English regardless of STT input language

Apply all three or the voice loop may hear Russian but reply in English.

### Script Location

The voice loop file lives at `scripts/_deprecated/jarvis_voice_loop.py`.
It **runs fine from `_deprecated/`** — no copy needed. The script uses
`Path(__file__)` to derive paths regardless of which subdirectory it's in.

Example (tested working 2026-07-15 on i3-6006U, whisper base ~64s first load):
```bash
"D:\Program Files\Python311\python.exe" D:/Portable_Soft/hermes/scripts/_deprecated/jarvis_voice_loop.py --play-start --vad-aggressive 2 --silence 1.5
```

### Running the Voice Loop

```bash
cd /d/Portable_Soft/hermes

# VAD mode — just speak naturally (auto-selects best provider)
python scripts/_deprecated/jarvis_voice_loop.py

# With start chime
python scripts/_deprecated/jarvis_voice_loop.py --play-start

# One utterance (debug)
python scripts/_deprecated/jarvis_voice_loop.py --once

# Force a specific provider/model
python scripts/jarvis_voice_loop.py --provider lm-studio --model gemma-3-4b
python scripts/jarvis_voice_loop.py --provider deepseek-free --model deepseek-chat

# Faster whisper, shorter silence
python scripts/jarvis_voice_loop.py --whisper tiny --silence 1.0

# Stricter VAD (louder room)
python scripts/jarvis_voice_loop.py --vad-aggressive 3

# One utterance
python scripts/jarvis_voice_loop.py --once

# Debug VAD decisions
python scripts/jarvis_voice_loop.py --debug

# Test microphone
python scripts/jarvis_voice_loop.py --test-mic
```

**Important**: run via **system Python** (`python`), NOT `uv run`. The script adds `scripts/` to
sys.path for model_registry, but uv's Python 3.13 doesn't have the audio packages.
System Python 3.11 has all deps installed.

## Model Registry Integration

The voice loop no longer hardcodes LLM endpoints. The `_resolve_llm_config()` function applies a **priority chain**:

1. **Voice Bridge (port 8642)** — checked first via `_try_deepseek_free()`. Acts as a proxy to FreeDeepseekAPI with JARVIS system prompt. If alive, used before any cloud provider. Falls back to direct FreeDeepseekAPI on port 9655.
2. `model_registry.get_working_model(tags=["chat", "fast", "free", "local"])` — best cloud provider from registry
3. `model_registry.get_working_model(tags=["chat"])` — any alive provider
4. Hardcoded lm-studio default — ultimate fallback

```python
from model_registry import get_working_model
```python
def _try_deepseek_free():
    """Check voice bridge first (port 8642), then direct FreeDeepseekAPI (port 9655)."""
    import urllib.request
    for endpoint, label in [
        ("http://127.0.0.1:8642/v1/models", "voice-bridge/8642"),
        ("http://127.0.0.1:9655/v1/models", "deepseek-free/9655"),
    ]:
        try:
            req = urllib.request.Request(endpoint, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                models = [m["id"] for m in data.get("data", [])]
                if any("deepseek" in m or "chat" in m for m in models):
                    base = endpoint.rsplit("/v1", 1)[0]
                    return {
                        "provider": "voice-bridge" if "8642" in endpoint else "deepseek-free",
                        "model": "deepseek-chat",
                        "base_url": f"{base}/v1",
                        "api_key": "",
                        "endpoint": f"{base}/v1/chat/completions",
                        "type": "proxy",
                    }
        except Exception:
            continue
    return None
```
# Called at script start — FreeDeepseekAPI > registry > lm-studio
ds = _try_deepseek_free()
LLM_CONFIG = ds or get_working_model(tags=["chat", "fast", "free", "local"])
if not LLM_CONFIG:
    LLM_CONFIG = get_working_model(tags=["chat"])
if not LLM_CONFIG:
    LLM_CONFIG = {
        "provider": "lm-studio",
        "model": "qwen3.5-4b",
        "endpoint": "http://localhost:1234/v1/chat/completions",
    }

llm = JarvisLLM(config=LLM_CONFIG)
```

This means:
- **No config changes needed** when adding a new provider
- **Automatic fallback** if the primary provider is down
- **Override with `--provider` flag**: `python scripts/jarvis_voice_loop.py --provider lm-studio --model gemma-3-4b`

For full provider management docs, see the `provider-model-management` skill.

## OpenCode Zen (opencode.ai/zen/v1) — fast, free, no API key needed

OpenCode Zen at `https://opencode.ai/zen/v1` is the **primary free provider** for the voice loop.
No API key required (optional). Works with any OpenAI-compatible client.

### Free models available

| Model | Priority | Speed | Notes |
|-------|----------|-------|-------|
| `mimo-v2.5-free` | 1 (best) | Very fast | Xiaomi MiMo, low latency |
| `deepseek-v4-flash-free` | 2 | Fast | DeepSeek flash |
| `qwen3.6-plus-free` | 3 | Medium | Qwen |
| `minimax-m3-free` | 4 | Medium | MiniMax |
| `nemotron-3-ultra-free` | 5 | Medium | NVIDIA |
| `north-mini-code-free` | 6 | Fast | Code-focused |

### API format

```
Base URL: https://opencode.ai/zen/v1
Chat:     /chat/completions
Models:   /v1/models       (returns full model list)
```

### Configuration in model_registry.py

The `opencode-zen` provider is defined in `PROVIDERS` dict with:
- `base_url: "https://opencode.ai/zen/v1"`
- `chat_endpoint: "/chat/completions"`
- `ping_endpoint: None` (uses TCP ping to `opencode.ai:443`)
- Models with `tags: ["chat", "free", "fast"]`

### ⚠️ IMPORTANT — Provider naming

- `opencode-zen` (with hyphen) = correct provider at `opencode.ai/zen/v1` — free, working
- `opencode_zen` (with underscore) = **OLD** gateway at `opengateway.gitlawb.com` — **DISABLED, no credits**
- When user says "зен провайдера", they mean `opencode-zen` at `opencode.ai/zen/v1`, NOT the old gateway
- **opengateway.gitlawb.com is permanently disabled** — the user explicitly rejected it

See `references/opencode-zen-api.md` for the complete endpoint reference and response handling details.

### Fallback chain

1. `FreeDeepseekAPI` (`deepseek-chat` on localhost:9655) — checked first, no rate limits
2. `opencode-zen` (`mimo-v2.5-free`) — fastest free cloud provider
3. `lm-studio` (local CPU) — fallback if cloud is down
4. Hardcoded lm-studio default — ultimate fallback

### When adding a new cloud provider

1. Search/look up the correct endpoint — do NOT guess
2. Add to `model_registry.py` PROVIDERS dict
3. Set a proper ping method (prefer TCP ping for speed)
4. Add free models with `tags: ["free", "chat"]`
5. Update the voice loop's content extraction if the provider uses different reasoning field names

## LM Studio (if selected as backend)

When model_registry picks LM Studio (typically when no other provider is alive):

- API: `http://localhost:1234/v1/chat/completions`
- Requires a model loaded in LM Studio UI before use
- Best models for CPU voice (low latency): qwen3.5-4b, ministral-3-3b, gemma-3-4b
- System prompt for JARVIS persona embedded in the script

### CUDA backend fallback

LM Studio auto-installs multiple backend packs. On systems **without an NVIDIA GPU** (i3 CPU, Intel HD Graphics, etc.), the CUDA backend (`llama.cpp-win-x86_64-nvidia-cuda-avx2-*`) fails to load with:

```
Failed to load LLM engine from path: ...llm_engine_cuda.node
...is not a valid Win32 application.
```

LM Studio will try the CUDA backend first if it's the newest installed, then crash before falling back to CPU. **Workaround**: remove/rename CUDA backend directories:

```bash
cd ~/.lmstudio/extensions/backends
mkdir -p _cuda_disabled
mv llama.cpp-win-x86_64-nvidia-cuda-avx2-* _cuda_disabled/
```

Then restart LM Studio. It will use the CPU (`avx2`) backend instead. To restore, delete `_cuda_disabled/` — LM Studio re-downloads CUDA backends on restart.

### Thinking/reasoning models and response extraction

Qwen 3.5+, DeepSeek-v4, and opencode.ai/zen models (mimo, etc.) may return their response in a
**reasoning-related field** instead of `content`. Three possible field names:

| Field | Providers that use it |
|-------|----------------------|
| `reasoning_content` | Qwen 3.5+ (LM Studio), DeepSeek-R1 |
| `reasoning` | mimo-v2.5-free, deepseek-v4-flash-free (opencode.ai/zen) |
| `reasoning_details` (array) | xiaomi/mimo models via opencode.ai/zen |

The voice loop's `JarvisLLM.chat()` method handles all three: reads `reasoning` first,
then `reasoning_content`, then `reasoning_details[-1].text`, before falling back to
a neutral response (`"Я слушаю, Сэр."`).

**`max_tokens` matters**: thinking models consume tokens for reasoning before producing content.
With `max_tokens=200`, the model may fill the budget with reasoning and leave `content` empty.
**Set `max_tokens=300` or higher** for the voice loop — tested working with deepseek-v4-flash-free
(finish_reason: "stop" with content populated).

See `references/thinking-model-response-handling.md` for exact response shapes.

### Disabling a credit-exhausted provider permanently

When a provider like `opengateway.gitlawb.com` has exhausted credits but still passes the TCP ping (port is open), `model_registry` will keep selecting it as the best provider. To permanently disable it:

1. **Clear `base_url` AND `api_key` in `~/.hermes/config.yaml`**:
   ```yaml
   model:
     api_key: ''
     base_url: ''
   ```

2. **Set default to a working provider**:
   ```yaml
   model:
     default: qwen3-coder-30b-a3b-instruct
     provider: lm-studio
   ```

3. **Ensure `model_registry._ping_provider()` treats empty config as dead**:
   When both `base_url` and `api_key` are empty/falsy, the ping function returns `alive=False` with error `"not configured"`.
   Without this, `opencode_zen` with `base_url=None` was unconditionally considered alive (line: `opencode_zen без известного URL — считаем живым`).

## Free-Tier Rate Limiting (Critical for Voice)

**opencode-zen free models hit rate limits after ~2-3 sequential requests.** In voice mode, utterances arrive every 5-15 seconds, which exceeds the free-tier ceiling. When rate-limited, the LLM returns `"Rate limit exceeded. Please try again later."`.

### Symptoms

- STT captures correctly: `🎤 You: Как ты меня слышишь?`
- LLM thinking indicator appears: `⚙️ JARVIS thinking...`
- Response returns rate limit error instead of meaningful text
- Voice loop stays in listening mode but user never hears a real response

### Preferred Solution: FreeDeepseekAPI (local proxy, no rate limits)

**FreeDeepseekAPI** (`D:/Portable_Soft/FreeDeepseekAPI`) is a local OpenAI-compatible proxy server that routes through your authenticated DeepSeek Web Chat session. **No rate limits, no API key cost**, runs on localhost. This is the best solution for voice — unlimited requests, same model quality as DeepSeek Chat.

The voice loop **auto-detects** FreeDeepseekAPI on startup via `_try_deepseek_free()`:
1. Pings `http://127.0.0.1:9655/v1/models` (2s timeout)
2. If `deepseek-chat` model is listed, uses it before any cloud provider
3. Falls back to model_registry → lm-studio if FreeDeepseekAPI is not running

The detected config is:
```python
{
    "provider": "deepseek-free",
    "model": "deepseek-chat",
    "base_url": "http://127.0.0.1:9655/v1",
    "endpoint": "http://127.0.0.1:9655/v1/chat/completions",
}
```

**Setup**: ensure FreeDeepseekAPI is running before starting the voice loop:
```bash
cd /d/Portable_Soft/FreeDeepseekAPI
NON_INTERACTIVE=true PORT=9655 node server.js
```
If port 9655 is already in use (`EADDRINUSE`), the server is already running from a prior session — just start the voice loop.

**Available models through FreeDeepseekAPI**:
| Model ID | Description |
|----------|-------------|
| `deepseek-chat`, `deepseek-v3`, `deepseek-default` | DeepSeek-V4-Flash non-thinking (fast) |
| `deepseek-reasoner`, `deepseek-r1` | DeepSeek-V4-Flash thinking mode (slower, better reasoning) |
| `deepseek-expert`, `deepseek-v4-pro` | DeepSeek expert mode (limited resources, thinking enabled) |
| `*-search` variants | Same models with web search capability |

### Fallback Workarounds (when FreeDeepseekAPI is unavailable)

| Approach | Pros | Cons |
|----------|------|------|
| **Switch models via `--model`** (e.g. `mimo-v2.5-free`) | Different rate limit pool | Same pool limit on free tier |
| **Increase silence timeout** (`--silence 3.0`) | Fewer requests per minute | Slower conversation rhythm |
| **Use `--once` mode** | One utterance, then exit | Must re-launch each time |
| **Switch to lm-studio (local)** | No rate limits; unlimited requests | Requires LM Studio running + model loaded; CPU inference slow (1-2 tok/s) |
| **Use a paid provider** | No limits | Costs money |

## TTS Audio Playback

### Fallback Chain

```
Edge TTS synthesize (retry x3, 1s delay between attempts)
  +-- ffplay play (primary player)
  +-- PowerShell SoundPlayer (fallback player)
  +-- fail --> SAPI5 pyttsx3 (OFFLINE, Windows only)
```

On Windows, the voice loop attempts audio playback with a **multi-layer fallback chain:**
1. **ffplay** (from chocolatey ffmpeg) -- most reliable in background processes
2. **PowerShell SoundPlayer** -- fallback if ffplay is missing
3. **SAPI5 via pyttsx3** -- offline Microsoft Irina Desktop Russian when Edge TTS unreachable

All exceptions caught silently -- audio failure never crashes the loop.

### Edge TTS Retry Logic

Edge TTS connects to Microsoft cloud servers -- intermittently unreachable from RU/Crimea.
The voice loop retries 3 times before falling back:

```python
for attempt in range(3):
    try:
        await self._speak_edge(text)
        return
    except Exception:
        if attempt < 2:
            await asyncio.sleep(1)
# All 3 failed --> SAPI5
self._speak_sapi(text)
```

### Primary Playback: ffplay

```python
if sys.platform == 'win32':
    import subprocess
    try:
        # subprocess.run(
        #     ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', file],
        #     capture_output=True, timeout=60)
        pass  # Reactive code example — adapt for your use case
    except FileNotFoundError:
        # subprocess.run(
        #     ['powershell', '-c',
        #      f"(New-Object Media.SoundPlayer '{file}').PlaySync()"],
        #     capture_output=True, timeout=60)
        pass  # Reactive code example — adapt for your use case
    except subprocess.TimeoutExpired:
        pass
```

### Why not winsound.PlaySound?

winsound.PlaySound works in interactive Python but **silently fails in git-bash
background processes** (voice loop runs via terminal(background=true), no TTY
console). ffplay is a separate process with its own audio context.

### Offline Fallback: SAPI5 via pyttsx3

When Edge TTS servers are unreachable, falls back to **pyttsx3** with **Microsoft
Irina Desktop Russian** -- a built-in Windows SAPI5 voice, fully offline.

Available SAPI5 voices (verified 2026-07-15):
| Voice | Language | Type |
|-------|----------|------|
| Microsoft Irina Desktop | ru-RU | Primary Russian fallback |
| Microsoft Zira Desktop | en-US | English female |
| Microsoft David Desktop | en-US | English male |

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

**Pitfalls:**
- runAndWait() blocks until speech finishes -- OK in daemon thread temp event loop
- Must init pyttsx3 engine in same thread that calls say()/runAndWait()
- pip install pyttsx3 required (not installed by default)
- Irina voice more robotic than Edge TTS Dmitry -- acceptable fallback
- Non-Windows: SAPI5 unavailable, Edge TTS -> ffplay only

### Linux/macOS

Requires `ffplay` from ffmpeg. Install with:
```bash
apt install ffmpeg          # Debian/Ubuntu (prefix sudo if applicable)
brew install ffmpeg        # macOS
```

## Whisper Model Loading Time

On i3-6006U (Skylake, dual-core ~2GHz), the base model (~290MB, int8 quantized):

| Condition | Time |
|----------|------|
| **First load** (model download + CPU optimization) | 60-150s |
| **Subsequent loads** (cached on disk, but model freshly loaded into memory after process kill) | 60-120s (CPU-bound) |
| **tiny model first load** | 15-30s |

The model is cached at `~/.cache/faster_whisper/` or `C:\\Users\\<user>\\.cache\\faster_whisper\\`. Clear it to force re-download.

For faster startup, use `--whisper tiny` (smaller model, faster load, slightly less accurate). The tiny model is recommended for first-time setup to verify the pipeline before waiting 2+ minutes for base.

## Voice-to-Agent Architecture

The voice loop can connect to Hermes Agent in several ways. The goal is for voice input to be processed by **the full agent** (tools, memory, skills), not just a bare LLM.

### Architecture Options

```
User speaks → Whisper (STT) → text → [LLM layer] → TTS → User hears
```

| Layer | Option A: Voice Bridge (current) | Option B: Gateway API Server (ideal) |
|-------|----------------------------------|--------------------------------------|
| **Backend** | Standalone `scripts/voice_bridge.py` on port 8642 | Hermes Gateway API server (`hermes gateway run`) |
| **Agent?** | No — proxies to FreeDeepseekAPI with JARVIS system prompt | Yes — full Hermes agent with tools, memory, skills |
| **Startup** | `python scripts/voice_bridge.py` (lightweight, 2s) | `API_SERVER_ENABLED=true hermes gateway run` (heavy, ~10-15s) |
| **Deps** | aiohttp | Everything in gateway venv |
| **Telegram?** | Not needed | Can be blocked in restricted regions |
| **State** | Stateless per request | Session-aware via X-Hermes-Session-Id |

### Option A: Voice Bridge (standalone, working)

`scripts/voice_bridge.py` is a lightweight OpenAI-compatible HTTP server:

```bash
python scripts/voice_bridge.py
# → Listening on http://127.0.0.1:8642
# → Uses FreeDeepseekAPI (deepseek-chat) with JARVIS system prompt
```

See `references/voice-bridge-setup.md` for full setup, provider detection, and dependency info.

The voice loop connects by changing one URL in `_try_deepseek_free()`:
```python
# Instead of direct FreeDeepseekAPI:
"endpoint": "http://127.0.0.1:8642/v1/chat/completions"
```

**Advantages**: lightweight, no gateway overhead, no Telegram dependency.
**Limitation**: uses DeepSeek directly — no Hermes tools or memory.

### Option B: Gateway API Server (ideal, complex setup)

The Hermes Gateway includes an OpenAI-compatible API server that routes requests through
the **full Hermes Agent pipeline** (tools, memory, skills, session continuity):

```bash
# Required env vars:
export API_SERVER_ENABLED=true
export API_SERVER_PORT=8642
export API_SERVER_HOST=127.0.0.1
export API_SERVER_KEY="$(openssl rand -hex 16)"  # 32+ chars required

hermes gateway run
# → API Server on http://127.0.0.1:8642/v1
# → Full Hermes Agent per request
```

The voice loop connects the same way — replacing its endpoint with `http://127.0.0.1:8642/v1/chat/completions`.

**⚠️ Telegram blocks startup**: If `TELEGRAM_ENABLED=true` is set in the environment (from `.env` or parent shell), the gateway tries to connect to Telegram BEFORE starting the API server. From restricted regions (Crimea, etc.), this connection hangs/timeouts, and the API server **never starts**. See pitfall below.

**Session continuity**: The API server supports `X-Hermes-Session-Id` header for multi-turn conversations. Without it, each request is stateless.

### Upgrading from Bridge to Gateway

When the gateway API server becomes available:
1. Stop the voice bridge
2. Start gateway with API server enabled
3. In the voice loop, change `_try_deepseek_free()` to return the gateway endpoint
4. Add `X-Hermes-Session-Id` header for conversation state

## Pitfalls

- **Gateway API server won't start if Telegram blocks it**: The gateway initializes platforms sequentially. If `TELEGRAM_ENABLED=true`, it attempts to connect to Telegram API before starting the API server. From regions where Telegram is blocked (Crimea), this connection hangs indefinitely. The API server **never starts**.  
  **Root cause**: `TELEGRAM_ENABLED=true` is set in the parent shell's environment (inherited from git-bash, system env, or `.env`). Even `TELEGRAM_ENABLED=false hermes gateway run --replace` doesn't work because `--replace` spawns a new OS process (`pythonw.exe`) that inherits the **original parent** environment, not the inline override.  
  **Fix**: unset the variable in the current shell AND export the override BEFORE starting:
   ```bash
   unset TELEGRAM_ENABLED
   export TELEGRAM_ENABLED=false
   hermes gateway run
   ```
   Or modify `.env` to set `TELEGRAM_ENABLED=false`.  
   Or start from a clean shell session (no TELEGRAM_ENABLED inherited).  
  **Alternative**: use the standalone voice bridge (Option A) — no Telegram dependency at all, port 8642 reserved for voice.

- **NEVER assume what a provider name means without verification** — when the user says
  "переходи на зен провайдера", it does NOT mean any existing entry you already know.
  "Зен" is NOT "opengateway.gitlawb.com". It IS "opencode.ai/zen/v1". Steps to avoid:
  1. Do NOT immediately search `model_registry.py` for a matching key — "зен" could be
     a new provider not yet in the registry.
  2. Check if the user-provided docs or a reference file has the info. If not —
     **search the web** for the correct endpoint. Do NOT guess.
  3. If you find the endpoint, test it with curl BEFORE modifying any config.
  4. Only after verification, update `model_registry.py` and `config.yaml`.
  **The wrong assumption about a provider name can destroy user trust in seconds.**
- **Do NOT re-enable a provider the user explicitly disabled** (opengateway.gitlawb.com).
  If the user said "отключи", it stays off. Period. Even if the user says "переходи на зен",
  this is NOT permission to re-enable opengateway — "зен" and "opengateway" are different things.
  Verify the endpoint before touching any config.
- **Run via system Python, not uv**: `python scripts/jarvis_voice_loop.py`, not `uv run python ...` — uv's Python 3.13 lacks faster-whisper, webrtcvad, etc. System Python 3.11 has them.
- **C: disk fills up** during pip install: uv cache and pip cache live on C:\. If C: is near-full (<100MB free), set `TMPDIR=D:\\tmp TEMP=D:\\tmp TMP=D:\\tmp` before `pip install`. Use `uv cache clean` to reclaim space on C:\.
- **scipy is not needed**: the script now uses stdlib `wave` module for WAV writing, not scipy. Install fails without scipy — install just `webrtcvad sounddevice faster-whisper edge-tts`.
- **LM Studio must have a model loaded** before inference — `/v1/models` lists available models but only the loaded one responds
- **No lms CLI** in older LM Studio versions — load model via UI
- **model_registry ping doesn't check loaded model status** — only checks if endpoint responds. LM Studio `/v1/models` returns 200 even with no loaded model. Inference will fail with "No models loaded".
- **faster-whisper first load is slow** (model download + CPU optimization) — subsequent loads use disk cache
- **webrtcvad only accepts specific frame sizes**: 10, 20, or 30ms at 16000/32000/48000 Hz. 30ms @ 16kHz = 480 samples
- **Sounddevice + Windows**: may need to set `sd.default.samplerate = 16000` explicitly
- **Edge TTS requires internet** — first call downloads auth tokens, subsequent calls cache them
- **CPU overload**: whisper base + VAD + LLM on same CPU may spike to 100% — use `--whisper tiny` for lower overhead
- **LM Studio CUDA backend fails on non-NVIDIA systems**: LM Studio auto-downloads CUDA backends that won't load on CPU-only systems. See LM Studio section above for the `_cuda_disabled/` workaround.
- **audio_callback missing `nonlocal` declarations**: the inner `audio_callback` function inside `process_stream()` assigns to variables from the outer scope (`buffer`, `recording`, `is_recording`, `silent_count`, `total_frames`, `utterance_count`). Every new variable assigned inside the callback MUST be added to the `nonlocal` line, or Python raises `UnboundLocalError`. When adding state to the voice loop, always check the `nonlocal` declaration first.
- **FreeDeepseekAPI must be running BEFORE the voice loop starts**: the auto-detection check runs once at script startup. If FreeDeepseekAPI starts after the voice loop, restart the voice loop. Check with `curl http://127.0.0.1:9655/v1/models`.
- **FreeDeepseekAPI port conflict**: default port is 9655. If another service uses it, set `PORT=9656` in env and update `_try_deepseek_free()` accordingly.
- **faster-whisper version mismatch between environments v1.1.x uses `onset`/`offset` in `vad.py`; v1.2.x uses `threshold`/`neg_threshold` in `transcribe.py`. The script passes `threshold` (v1.2.x API), so if the system Python has v1.1.x it crashes with `TypeError: VadOptions.__init__() got an unexpected keyword argument 'threshold'`. Fix: upgrade with `\"D:\\Program Files\\Python311\\python.exe\" -m pip install --upgrade faster-whisper`. See `references/faster-whisper-vad-params.md`.
- **Provider alive but credit-exhausted**: `model_registry` uses TCP ping, so a provider like `opengateway.gitlawb.com` that has an open port but exhausted credits will still be selected as the best provider. Every API call then fails with 400/402. Symptom: voice loop hears you, shows thinking... but responds with error. Workaround: use `--provider lm-studio` to force local inference. **Permanent fix**: clear `base_url` AND `api_key` in `~/.hermes/config.yaml` (both must be empty for `model_registry` to consider the provider dead). See `references/provider-credit-exhaustion.md`.
- **Qwen thinking models return empty content**: Qwen 3.5+ outputs response in `reasoning_content`, leaving `content` empty. Voice loop now falls back to `reasoning_content` when `content` is empty.
- **Local model timeout**: default `urlopen` timeout was 30s. On CPU, Qwen3.5-4b takes ~12s for prompt processing + ~15s for thinking at ~8 tok/s. Client disconnects before response arrives. Fix: the voice loop now uses 120s timeout for localhost endpoints.
- **pyttsx3 not installed by default**: `pip install pyttsx3` required for SAPI5 offline TTS fallback. Without it, Edge TTS failure means no audio. Check: `python -c "import pyttsx3"` before relying on the fallback.