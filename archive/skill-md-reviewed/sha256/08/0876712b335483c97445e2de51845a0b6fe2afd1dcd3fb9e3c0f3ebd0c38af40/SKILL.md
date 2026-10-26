---
name: sillytavern-voice-roleplay
description: "Voice roleplay with STT/TTS bridging ST-native and Hermes memory."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [SillyTavern, Voice, Roleplay, STT, TTS, Irodori, Hakua]
    category: devops
---

# SillyTavern Voice Roleplay

Voice roleplay integration for `/st-voice-roleplay` slash command and `st_voice_roleplay` / `st_voice_roleplay_complete` tools.

## Implementation Location

### Files touched

| File | Role |
|------|------|
| `plugins/sillytavern/__init__.py` | Handler functions `st_voice_roleplay()` / `st_voice_roleplay_complete()` + registration in `register(ctx)` |
| `cli.py` | `process_command()` dispatch: `elif canonical == "st-voice-roleplay": self._handle_st_voice_roleplay_command(cmd_original)` |
| `hermes_cli/commands.py` | `COMMAND_REGISTRY` entry for `/st-voice-roleplay` with subcommands `("start", "complete", "status")` |
| `hermes_cli/cli_commands_mixin.py` | `_handle_st_voice_roleplay_command(self, cmd)` — parses subcommand, loads plugin, calls tool handler |

### Plugin layer (`plugins/sillytavern/__init__.py`)

```python
def st_voice_roleplay(args, **kwargs) -> str:
    """Phase 1: record audio -> STT -> ST-native prompt assembly.
    Returns {ok, stage="prompt_ready", transcript, prompt, tts_voice, ...}
    """
    # 1. AudioRecorder from tools.voice_mode
    # 2. transcribe_recording(wav_path, model=stt_model)
    # 3. _native().add_message + build_prompt(...)

def st_voice_roleplay_complete(args, **kwargs) -> str:
    """Phase 2: TTS -> play -> memory bridge.
    Returns {ok, tts_file, memory_records}
    """
    # 1. _native().add_message(session_id, "assistant", ...)
    # 2. text_to_speech_tool(text=reply_content) -> routes to irodori/hakua
    # 3. play_audio_file(tts_file)
    # 4. _native().session_to_memory_records(session_id) if auto_memory
```

Registered with `ctx.register_tool()` inside `register()`:
- `st_voice_roleplay` — schema has session_id (required), duration_seconds=10, lore_book, history_limit=20, tts_voice="hakua", stt_model="base", auto_memory=true
- `st_voice_roleplay_complete` — schema has session_id (required), reply_content (required), tts_voice="hakua", tts_speed=1.0, auto_memory=true

### CLI dispatch chain

1. **Command definition**: `hermes_cli/commands.py` → `COMMAND_REGISTRY` adds `CommandDef("st-voice-roleplay", "Voice roleplay with STT/TTS", "Tools & Skills", args_hint="[start|complete|status]", cli_only=True, subcommands=("start", "complete", "status"))`
2. **Resolution**: `cli.py` `process_command()` resolves via `resolve_command()`, gets canonical name
3. **Dispatch**: `elif canonical == "st-voice-roleplay": self._handle_st_voice_roleplay_command(cmd_original)`
4. **Mixin delegation**: `hermes_cli/cli_commands_mixin.py` → `_handle_st_voice_roleplay_command(self, cmd)` — thin import-and-delegate:
   ```python
   def _handle_st_voice_roleplay_command(self, cmd):
       from hermes_cli.st_voice_rp_handler import handle_voice_roleplay_command
       handle_voice_roleplay_command(cmd, _cprint)
   ```
5. **Handler module**: `hermes_cli/st_voice_rp_handler.py` — standalone module with three functions:
   - `_get_plugin_tools()` — loads the plugin via `importlib.util.spec_from_file_location`, returns registered tool list
   - `_call_tool(tools, name, **kwargs)` — looks up a registered tool by name and calls its handler
   - `handle_voice_roleplay_command(cmd, _cprint)` — subcommand dispatch, results display

**Pattern note**: CLI handlers should live in a dedicated module under `hermes_cli/` (e.g. `st_voice_rp_handler.py`) rather than inline in the mixin class. The mixin imports and delegates. The module file is created via `write_file` (not `patch`).

## Flow

### Phase 1: `/st-voice-roleplay start <session_id> [duration=10] [stt_model=base] [lore_book]`
1. `AudioRecorder` from `tools.voice_mode` records WAV for `duration_seconds`
2. `transcribe_recording(wav_path, model=stt_model)` → transcript
3. `st_session_say(session_id, transcript)` → ST-native prompt (system + lore + history)
4. Returns `{ok: true, stage: "prompt_ready", transcript, prompt, tts_voice, tts_model, tts_speed, auto_memory}`

### Phase 2: `/st-voice-roleplay complete <session_id> <reply_content> [tts_voice=hakua] [tts_speed=1.0]`
1. Records assistant reply: `st_session_reply(session_id, reply_content)`
2. TTS: `text_to_speech_tool(text=reply_content)` → routes to irodori provider (default voice "hakua")
3. Play: `play_audio_file(tts_file)` from `tools.voice_mode`
4. Memory bridge (if `auto_memory`): `st_session_to_memory(session_id)` → emits ebbinghaus records

## Dependencies

| Tool | Source | Purpose |
|------|--------|---------|
| `create_audio_recorder` | `tools.voice_mode` | Microphone capture |
| `transcribe_recording` | `tools.voice_mode` | Faster-whisper STT |
| `play_audio_file` | `tools.voice_mode` | Audio playback |
| `text_to_speech_tool` | `tools.tts_tool` | TTS routing (irodori/voicevox) |
| `st_session_say` | `plugins/sillytavern` | Add user turn + build prompt |
| `st_session_reply` | `plugins/sillytavern` | Record assistant reply |
| `st_session_to_memory` | `plugins/sillytavern` | Emit ebbinghaus records |

## Configuration

No extra config needed. Uses existing:
- `stt.model` from config (default "base")
- `tts.provider` = "irodori-tts" (default voice "hakua")
- `HERMES_HOME` for ST-native SQLite (`sillytavern/native.db`)

## Testing

```bash
# 1. Create character & persona (once)
hermes rp create はくあ --first "ボブにゃん！" --personality "元気で忠実"
hermes rp persona ボブにゃん --desc "上田市の開発者"

# 2. Start session
hermes rp start はくあ
# → session_id

# 3. Voice roleplay turn
/st-voice-roleplay start <session_id> 10
# → speak → get prompt
# (Agent completes via LLM)
/st-voice-roleplay complete <session_id> "森は静かだ…"
# → TTS (hakua) plays, memory emitted
```

## Pitfalls

- **AudioRecorder dependency**: `st_voice_roleplay` depends on `create_audio_recorder()` from `tools/voice_mode.py`. If no microphone is available or the recorder fails to create, the tool returns `{ok: false, error: "Failed to record audio"}` — no fallback to text input exists within the tool. Use `/rp say` as the text-only alternative.
- **STT model first-download delay**: `transcribe_recording()` uses faster-whisper locally. The first call downloads the model file (~GB range) and can take 30s+. Subsequent calls are instant.
- **TTS provider must be configured**: `text_to_speech_tool` routes to the configured provider. Requires `tts.provider: irodori-tts` in `config.yaml` and the Irodori-TTS server running. TTS/playback failure is non-fatal — the reply is still recorded in ST-native.
- **Memory bridge is emit-only**: `st_session_to_memory` only emits `{content, tags, salience}` records. The agent must call the `memory` tool separately to persist them. `auto_memory` controls emission, not persistence.
- **CLI handler path is fork-hardcoded**: `cli_commands_mixin.py` loads the plugin via absolute path `"/c/Users/downl/Documents/New project/hermes-agent/plugins/sillytavern/__init__.py"`. This breaks outside the fork.
- **Session ID must be integer**: The CLI handler parses `session_id` with `int()`. ST-native SQLite uses integer IDs.
- **Stateless two-phase flow**: `st_voice_roleplay` (phase 1) and `st_voice_roleplay_complete` (phase 2) are independent calls — no state is tracked between them. The caller must orchestrate: phase 1 → LLM generates → phase 2.
- **No audio level monitoring**: The current `AudioRecorder` records for a fixed duration (`duration_seconds`). It does not stop early on silence or support voice-activity detection for variable-length recording.
- **Plugin registration must be inside `register()`**: The `ctx.register_tool()` calls for `st_voice_roleplay` and `st_voice_roleplay_complete` must be inside the `register(ctx)` function, not at module level. Module-level `ctx.register_tool()` raises `NameError: name 'ctx' is not defined`.
- **`patch` tool requires old_string/new_string format**: When editing plugin files with Hermes `patch`, use `{"old_string": "exact existing text", "new_string": "replacement text"}` parameters — NOT unified diff (`@@ -N,M +N,M @@`) format. The unified diff format is silently rejected. For new files (like the handler module), use `write_file` instead of `patch`.