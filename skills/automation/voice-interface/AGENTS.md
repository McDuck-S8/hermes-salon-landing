# voice-interface — Skill

## Purpose
Voice interface stack for Hermes — VAD (WebRTC), STT (faster-whisper), TTS (Edge TTS), microphone, voice-loop architecture

## Ownership
Managed by Hermes Agent. Self-contained skill with SKILL.md, references/, templates/, scripts/.

## Local Contracts
- **Triggers**: auto-detected from context
- **Required tools**: voice, vad, stt, tts, whisper, webrtcvad, edge-tts, microphone, voice-loop
- **Config**: config.yaml in skill dir (optional)

## Work Guidance
**When to use**: Voice interface stack for Hermes — VAD (WebRTC), STT (faster-whisper), TTS (Edge TTS), microphone, voice-loop architecture
**Common patterns**: Standard skill invocation
**Anti-patterns**: Using without reading SKILL.md first

## Verification
- Load SKILL.md and validate frontmatter
- Run any test scripts in scripts/
- Verify references/ files exist

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/` | Reference materials (11 files) |