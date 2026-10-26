---
name: hermes-tts-plugin-providers
description: Build, verify, and troubleshoot Hermes TTS providers implemented through the plugin harness rather than legacy command-provider blocks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, tts, plugins, voice, windows, provider-dispatch]
    related_skills: [hermes-agent]
---

# Hermes TTS Plugin Providers

Reference: for stabilizing the user-approved cute Hakua voice in Irodori-TTS, see `references/fixed-hakua-voice.md`.

Use this skill when adding or debugging a Hermes Text-to-Speech provider that should be registered by the plugin harness and used by `tools.tts_tool.text_to_speech_tool`, gateway voice replies, or `hermes <plugin-command>` CLI commands.

This is for provider classes such as local TTS servers, GPU-backed voice engines, or offline synthesizers. Do **not** create a one-session skill for each engine; put engine-specific quirks in `references/` and keep the workflow here generic.

## Trigger Conditions

Load this skill when the task mentions any of:

- Hermes TTS provider registration
- `tts.provider`, `tts.providers`, or `tools.tts_tool`
- plugin `register_tts_provider`, plugin CLI, plugin tools, or `plugins/<name>/plugin.yaml`
- local voice engines such as Irodori-TTS, VOICEVOX, Kokoro, sherpa-onnx, Piper, etc. being wired into Hermes
- gateway voice output not using the expected provider

## Core Principle

Prefer a **plugin provider** when the integration is part of Hermes, needs tools/CLI/status, or should be reusable across gateway and standard TTS paths. Use a legacy `tts.providers.<name>.type: command` block only for simple external command wrappers.

Important dispatch pitfall:

- If `tts.providers.<provider>.type: command` exists, Hermes may resolve that command provider before the plugin provider with the same name.
- For a plugin-backed provider, remove the same-name command-provider block and set only the top-level provider selection, e.g.:

```yaml
tts:
  provider: irodori
  output_format: wav
  voice: none
  model: irodori-tts
```

## Expected Plugin Shape

A complete Hermes TTS plugin usually has:

```text
plugins/<provider>_tts/
├── plugin.yaml
├── __init__.py
├── core.py
└── cli.py
```

Recommended registrations:

- TTS provider: `<provider>`
- status tool: `<provider>_tts_status`
- synthesize tool: `<provider>_tts_synthesize`
- CLI group: `hermes <provider>-tts ...`
  - `status`
  - `start` if there is a local server process
  - `synthesize`

For Windows/local-server engines, prefer Hermes-side script harness wrappers under `scripts/windows/` so CLI/tools/provider all share the same invocation behavior.

## Implementation Checklist

1. **Read current TTS dispatch code**
   - Inspect `tools/tts_tool.py` and the plugin registration surfaces before editing.
   - Confirm whether plugin providers and command providers share the same namespace.

2. **Add plugin files**
   - `plugin.yaml`: metadata, enabled defaults, commands/tools/providers declared in the repo's current plugin format.
   - `__init__.py`: plugin entry point and registration hooks.
   - `core.py`: provider implementation, status checks, synthesis call, output normalization.
   - `cli.py`: human-friendly smoke commands.

3. **Add script harness wrappers when needed**
   - For Windows PowerShell wrappers, quote paths with spaces.
   - Set environment defaults inside the script for cache paths, GPU/runtime flags, and known upstream quirks.
   - Keep server start and synthesis invocation separate when possible.

4. **Update config carefully**
   - Set `tts.provider` to the plugin provider name.
   - Set format/model/voice defaults as needed.
   - Add the plugin to `plugins.enabled`.
   - Remove same-name legacy command-provider blocks unless the intent is to bypass the plugin.

5. **Add tests at three layers**
   - Plugin unit/status/synthesis behavior.
   - TTS dispatch selecting the plugin provider.
   - CLI/plugin registration visibility.

6. **Verify in the real checkout**
   - Plugin list shows the plugin enabled.
   - Plugin status returns `ok: true` or a precise reason it is unavailable.
   - Plugin CLI synthesis writes an audio file.
   - Standard `text_to_speech_tool(...)` returns `provider: <provider>`.
   - If voice delivery matters, verify the final file format is compatible with gateway/platform expectations.

## Verification Commands

On this Windows checkout the terminal tool uses bash/MSYS, so POSIX syntax is usually safest inside Hermes tools. For user-facing PowerShell snippets, quote paths that include spaces.

```bash
cd "/c/Users/downl/Documents/New project/hermes-agent"
uv run python -m hermes_cli.main plugins list --plain | grep -i '<provider>'
uv run python -m hermes_cli.main <provider>-tts status
PYTHONUTF8=1 uv run --with pytest python -m pytest -o addopts='' \
  tests/plugins/test_<provider>_tts_plugin.py \
  tests/tools/test_tts_plugin_dispatch.py \
  tests/hermes_cli/test_plugins_tts_registration.py \
  -q
PYTHONUTF8=1 uv run python - <<'PY'
from pathlib import Path
from tools.tts_tool import text_to_speech_tool
out = Path.home() / 'AppData' / 'Local' / 'hermes' / 'audio_cache' / '<provider>_plugin_smoke.wav'
print(text_to_speech_tool('Hermes TTS plugin smoke test.', output_path=str(out)))
PY
```

## Reference Voice Identity

For voice-cloning providers, do not leave the configured voice as `none` when the user expects a stable persona voice. `voice: none` is useful for bring-up, but it can produce a voice that sounds unlike the established assistant/persona and may vary between generations.

When a user approves a voice style:

1. Save the approved sample under the provider's reference-voice directory with a stable persona ID (for example `voices/hakua.ogg`).
2. Verify the server lists that ID via its voice-list/status endpoint.
3. Set Hermes' default voice through the CLI/config path, not by hand-editing protected config when a CLI is available, e.g. `hermes config set tts.voice hakua`.
4. Regenerate any already-produced audio/video assets using the fixed voice ID.
5. Report both the correction and the new asset path so the user can compare.

See `references/irodori-reference-voice-persona.md` for the session-proven Irodori/Hakua pattern.

## Windows Pitfalls

- Paths under `%USERPROFILE%\Documents\New project\...` contain spaces; quote them in PowerShell and shell snippets.
- Prefer `uv run python ...` from the Hermes checkout so plugin discovery uses the intended source tree.
- Set `PYTHONUTF8=1` / `$env:PYTHONUTF8='1'` for Japanese synthesis smoke tests.
- Endpoint changes require request-level verification. Read back the active-profile setting, test a fresh standard TTS call, and correlate that exact request with the destination server's runtime log. A long-lived desktop/tool process can still use an older code/config path; do not infer GPU execution from config or provider name, and do not relabel a CPU-generated artifact. Verify warm synthesis and safe cold auto-start separately. For a nondefault loopback port, both plugin CLI start and the synthesis wrapper must forward that configured host/port to the shared launcher.
- Avoid filling the C drive with model downloads; local TTS scripts may need explicit cache directories.
- If an upstream model downloader respects `HF_HUB_ENABLE_HF_TRANSFER`, disable it in scripts when `hf_transfer` is not installed, instead of letting first-run downloads fail.

## Reference Notes

- `references/irodori-tts-plugin.md` — session-proven Irodori-TTS provider details, config, verification output, and pitfalls.
- `references/irodori-reference-voice-persona.md` — how to pin an approved Irodori reference voice as a stable persona voice and regenerate media.
- `references/irodori-runtime-recovery.md` — recovery pattern for already-configured Irodori/Hakua runtime failures such as JSON error files, CUDA/OOM responses, duplicate server processes, or connection resets during voice-asset generation.

## Reporting Pattern

When reporting completion, include real verification evidence:

- plugin list line
- status summary with provider availability/device if relevant
- pytest result
- standard `text_to_speech_tool` result showing `provider: <provider>`
- any unrelated dirty/untracked files that were intentionally not touched
