---
name: voice-roleplay-tts-stt
description: "Voice roleplay pipeline: STT (faster-whisper) to LLM prompt assembly to TTS (irodori/hakua) to Ebbinghaus memory bridge"
version: 1.0.0
category: mlops
tags: [voice, stt, tts, roleplay, sillytavern, ebbinghaus, irodori, faster-whisper]
---

# Voice Roleplay: STT to LLM to TTS Pipeline with Memory Integration

## Description
Implements a voice roleplay system for Hermes/SillyTavern that orchestrates Speech-to-Text (faster-whisper), LLM prompt assembly via ST-native roleplay engine, Text-to-Speech (irodori TTS with hakua voice), and Ebbinghaus memory bridging — all in a two-phase agent tool pattern.

## When to Use
- Building voice-enabled roleplay characters for SillyTavern/Hermes
- Adding STT/TTS to any agent workflow with memory persistence
- Integrating local TTS (irodori) with faster-whisper STT

## Prerequisites
- `tools.voice_mode` available (faster-whisper, sounddevice, numpy)
- `tools.tts_tool` with irodori provider configured (hakua voice reference)
- ST-native roleplay database (`HERMES_HOME/sillytavern/native.db`)
- Ebbinghaus memory system enabled

## Architecture

### Phase 1: `st_voice_roleplay` (Input)
1. Record audio via `AudioRecorder` (duration_seconds)
2. STT transcribe via `transcribe_recording()` (faster-whisper)
3. Add user message to ST-native session
4. Build ST-style prompt with lorebook + history
5. Return `{stage: "prompt_ready", transcript, prompt, tts_voice, tts_model, tts_speed, auto_memory}`

### Phase 2: `st_voice_roleplay_complete` (Output)
1. Record assistant reply into ST-native session
2. TTS synthesize via `text_to_speech_tool()` (irodori/hakua)
3. Play audio via `play_audio_file()`
4. Emit session to ebbinghaus memory via `session_to_memory_records()`

## Key Implementation Patterns

### Audio Recording
```python
from tools.voice_mode import create_audio_recorder
recorder = create_audio_recorder()
recorder.start()
time.sleep(duration_seconds)
wav_path = recorder.stop()  # Returns None if too short/quiet
```

### STT Transcription
```python
from tools.voice_mode import transcribe_recording
result = transcribe_recording(wav_path, model="base")
# Returns: {"success": bool, "transcript": str, "error": str?, "no_speech": bool?}
```

### TTS Synthesis (irodori/hakua)
```python
from tools.tts_tool import text_to_speech_tool
result = text_to_speech_tool(text=reply_content)
# Returns: {"file_path": str, ...} - handles temp dir automatically
```

### Audio Playback
```python
from tools.voice_mode import play_audio_file
play_audio_file(file_path)  # Handles WAV/MP3 via sounddevice or system players
```

### Memory Bridge
```python
# ST-native session to Ebbinghaus memory
records = native.session_to_memory_records(session_id)
# Agent persists via memory tool (not done automatically in tool)
```

## Configuration
- STT model: `base` (default), `small`, `medium`, `large-v3`
- TTS voice: `hakua` (default, requires reference audio in irodori/voices/)
- TTS model: `irodori-tts`
- TTS speed: `1.0` (0.25-4.0)

## FishAudio Cloud TTS (alternative provider)
FishAudio is a cloud TTS provider usable standalone or as the `tts.provider`. It supports cloned/reference voices via a `reference_id` (the voice UUID from fish.audio My Voices). The plugin lives at `plugins/fish_audio_tts/` and is enabled when `fish_audio_tts` is in `plugins.enabled` (or auto-discovered).

### Config (use `hermes config set`, NOT direct file edits)
The agent cannot `patch` `~/.hermes/config.yaml` (security guard). Set nested keys via the CLI:
```bash
hermes config set tts.provider fishaudio
hermes config set tts.fishaudio.reference_id <VOICE_UUID>   # e.g. f715fa52... (hakua clone)
hermes config set tts.fishaudio.model s2.1-pro-free
hermes config set tts.fishaudio.format mp3
hermes config set tts.fishaudio.speed 1.0
```
The `tts.fishaudio.*` keys are saved even though `hermes config set` warns they are "not a recognized config key" — the plugin's `_fish_config()` reads them from the `tts` section regardless. API key must be in `~/.hermes/.env` as `FISH_AUDIO_API_KEY` (plugin reads it via `get_env_value`). Verify with `fish_audio_tts_status` (`api_key_present: true`).

### PITFALL: `fish_audio_tts_synthesize` tool wrapper bug
The wrapped tool `fish_audio_tts_synthesize` currently raises `AttributeError: 'dict' object has no attribute 'strip'` even with valid args — the tool-registration wrapper mismatches the underlying signature. **Workaround: call the plugin function directly** (this is what actually works):
```python
# from the project root with the venv active
import sys; sys.path.insert(0, '.')
from plugins.fish_audio_tts.core import synthesize_text
result = synthesize_text(text="こんにちは、ボブにゃん！")
# -> {'ok': True, 'file_path': '...mp3', 'voice': '<reference_id>', ...}
```
Output lands in `~/.hermes/cache/audio/fishaudio_<timestamp>.mp3` (MPEG layer III, 128 kbps, 44.1 kHz, mono). Use this path for playback/attachment. The `text_to_speech` top-level tool and the `fish_audio_tts_synthesize` wrapper should be avoided until the wrapper is fixed; prefer `synthesize_text()` in scripts/cron.

### When to prefer FishAudio vs irodori
- FishAudio: cloud, no local server, cloned multi-language voices, needs API key + network.
- irodori: local CPU server, hakua reference audio, offline-friendly (see irodori-tts-windows-startup).

## Common Pitfalls
1. **Audio too short/quiet** -> `recorder.stop()` returns `None`; increase duration or check mic
2. **STT hallucination on silence** -> `transcribe_recording` filters known Whisper hallucinations; check `no_speech` flag
3. **TTS file missing** -> `text_to_speech_tool` manages temp dir; don't assume path persistence
4. **Memory not persisted** -> Tool returns records; agent must call memory tool to persist
5. **irodori server not running** -> Ensure `irodori_tts_status` shows available before TTS calls

## Tool Registration
Register in plugin's `register(ctx)`:
```python
ctx.register_tool(
    name="st_voice_roleplay",
    description="Voice roleplay turn (phase 1): record audio -> STT -> ST-native prompt assembly. Returns prompt for LLM completion.",
    schema={...},
    handler=st_voice_roleplay,
)
ctx.register_tool(
    name="st_voice_roleplay_complete",
    description="Voice roleplay turn (phase 2): record assistant reply -> TTS (irodori/hakua) -> play -> memory bridge.",
    schema={...},
    handler=st_voice_roleplay_complete,
)
```

## Related Skills
- `mlops/inference/local-llm-serving` — for LLM backend
- `autonomous-ai-agents/agent-memory-consolidation` — for Ebbinghaus memory
- `plugins/sillytavern` — parent plugin context

## References
- `references/voice-roleplay-architecture.md` — full pipeline diagram
- `references/irodori-hakua-setup.md` — voice reference preparation
- `references/ebbinghaus-bridge.md` — memory integration details