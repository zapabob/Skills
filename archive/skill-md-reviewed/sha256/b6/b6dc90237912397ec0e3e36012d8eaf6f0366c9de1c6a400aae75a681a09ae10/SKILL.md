---
name: plugin-tts-audio-buffer
description: >-
  Buffer TTS audio to disk and zip when backlog threshold is exceeded.
version: 0.2.0
author: Hermes Agent
metadata:
  hermes:
    tags: [tts, audio, buffer, zip, plugin]
    category: mlops
---

# Plugin TTS Audio Buffer

Extend an existing Hermes TTS plugin so every synthesized audio file is retained
in a rolling file buffer, zipped when a threshold is hit, and **not** pushed to
`audio_ws` in zipped form.

## When to use

- After adding `irodori_tts_synthesize` or similar synthesis tools to a plugin.
- When downstream consumers (AITuber OnAir, VRChat autonomy, SillyTavern) need
  batches of WAV files bundled as zip archives on disk.
- When you want to keep the live `audio_ws` push path intact while also
  accumulating files for later retrieval.

## Trigger conditions

- The plugin already has a synthesis function that writes to a `file_path`.
- There is an `audio_ws_push_wav(...)` call (or equivalent) near the end of the
  synthesis success path.
- You want buffer control tools (`buffer_status`, `buffer_zip`, `buffer_add`)
  exposed alongside the synthesis tools.

## Implementation

### 1. Add `plugins/<plugin>/audio_buffer.py`

Create a small module that owns a singleton `AudioBuffer`:

```python
class AudioBuffer:
    def __init__(self, buffer_dir, max_files=100, max_bytes=200*1024*1024):
        ...

    def add(self, path):
        # copy file into buffer_dir with timestamp prefix
        ...

    def maybe_zip(self):
        # if len(files) >= max_files or total bytes >= max_bytes:
        #   zip all files, unlink originals, return zip metadata
        ...
```

Keep the module small: `buffer_status`, `maybe_zip`, `add_audio`.

### 2. Register buffer tools in `plugins/<plugin>/__init__.py`

Import the new module and register three tools:

- `*_tts_buffer_status` — returns `{buffer_dir, files, bytes, max_files, max_bytes}`
- `*_tts_buffer_zip` — forces a zip if threshold is met, returns zip metadata
- `*_tts_buffer_add(path)` — manually adds an existing audio file to the buffer

This lets the agent observe and control the backlog without shelling out.

### 3. Hook the buffer in `synthesize_text(...)` (auto-buffer at source)

For the irodori plugin specifically, the buffer is hooked **inside `synthesize_text`** itself so every synthesis client (CLI, aituber, cron) automatically buffers without each caller remembering:

```python
def _auto_buffer(file_path: str, result: dict) -> None:
    try:
        from .audio_buffer import add_audio, maybe_zip
        buf = add_audio(file_path)
        result["buffer"] = {"buffered": bool(buf), "path": str(buf) if buf else None}
        zip_r = maybe_zip()
        if zip_r.get("zipped"):
            result["buffer"]["zip"] = zip_r
    except Exception as exc:
        result["buffer"] = {"buffered": False, "error": str(exc)}

# Called right before return:
_auto_buffer(str(destination), result)
return result
```

### 4. Hook the buffer in `synthesize_speech(...)` (aituber path)

When the aituber_onair plugin calls `synthesize_speech`, the buffer step runs **before** `audio_ws_push_wav(...)`. It also syncs any newly created zip into the aituber workspace audio dir:

```python
buffer_info = {}
try:
    from plugins.irodori_tts.audio_buffer import add_audio, maybe_zip
    buffered = add_audio(result["file_path"])
    buffer_info["buffered"] = bool(buffered)

    # Sync zip into aituber workspace audio dir
    if zip_result.get("zipped"):
        try:
            dest = _audio_dir() / Path(zip_result["zip_path"]).name
            shutil.copy2(zip_result["zip_path"], dest)
            buffer_info["aituber_audio"] = str(dest)
        except Exception as exc:
            buffer_info["sync_error"] = str(exc)
except Exception as exc:
    buffer_info["buffer_error"] = str(exc)
result["buffer"] = buffer_info

# Live path unchanged:
result["audio_ws"] = audio_ws_push_wav(result["file_path"])
```

### 5. SillyTavern audio landing

Add a `st_audio_land` tool to the sillytavern plugin that copies the latest buffer file (zip or wav) into `vendor/SillyTavern/data/_uploads/`:

- When `source_path` is omitted, auto-detect the newest `.zip` or `.wav` from the irodori buffer dir.
- The file becomes accessible at the SillyTavern `/uploads/` endpoint.

### 6. Config-driven buffer dir and thresholds

Make the buffer dir and thresholds configurable via `config.yaml` under `tts.irodori.*`:

| Config key | Env var | Default |
|---|---|---|
| `tts.irodori.audio_buffer_dir` | `HERMES_IRODORI_BUFFER_DIR` | `~/.hermes/workspace/irodori-tts/audio-buffer` |
| `tts.irodori.max_files` | `HERMES_IRODORI_MAX_FILES` | `100` |
| `tts.irodori.max_bytes` | `HERMES_IRODORI_MAX_BYTES` | `209715200` (200 MB) |
| `tts.irodori.max_age_seconds` | `HERMES_IRODORI_MAX_AGE` | `3600` |

Implementation uses `_buffer_dir_from_config()` and `_buffer_int_config(key, fallback)` in `audio_buffer.py`.

## Pitfalls

- **Zip must not go to `audio_ws`.** The zipped archive is for offline retrieval
  or batch transfer; do not broadcast zip bytes to audio WebSocket clients.
- **Non-interactive Windows shells reject `export` when launching background
  processes from the terminal tool.** Use `env VAR=val ...` instead of
  `export VAR=val && cmd`.
- **Importing the buffer module from `__init__.py` can trigger pyright errors**
  if the function names clash or are missing. Keep buffer functions in a
  separate `audio_buffer.py` and import them with stable names.
- **`_buffer` singleton can be hard to replace in tests.** If you need to swap
  implementations for verification, inject via
  `object.__setattr__(module, '_buffer', new_buffer)`.
- **Update change-detector tests when adding new plugin tools.** The
  `test_register_exposes_*_to_agents` test in `tests/plugins/` hardcodes the
  set of tool names. Adding `st_audio_land` or similar tools will fail that
  test until the expected set is updated.
- **New `subprocess.run` calls trigger CI `test_subprocess_stdin_guard`.**
  Every `subprocess.run` or `Popen` call in the Hermes codebase must include
  an explicit `stdin=` parameter. The CI test
  `tests/tools/test_subprocess_stdin_guard.py` scans all `.py` files and fails
  if any `subprocess.run(...)` or `subprocess.Popen(...)` lacks `stdin=`.
  When adding a helper `_run(cmd)` function in a new plugin, always write
  `subprocess.run(cmd, ..., stdin=subprocess.DEVNULL)`.

## Verification

```bash
# Compile all affected files
python -m py_compile plugins/<plugin>/audio_buffer.py plugins/<plugin>/__init__.py plugins/<plugin>/core.py

# Run existing plugin tests to confirm no regression
pytest tests/plugins/test_<plugin>_plugin.py -q
```

## References

- `references/irodori-aituber-buffer-implementation.md` — session-specific notes
  from the first wiring of `irodori_tts` → `aituber_onair` with buffer→zip.