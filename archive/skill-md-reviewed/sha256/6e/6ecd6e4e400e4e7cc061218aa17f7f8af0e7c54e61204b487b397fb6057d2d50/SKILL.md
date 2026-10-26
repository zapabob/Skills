---
name: aituber-onair-hakua-audio
description: Configure AITuber OnAir for Hakua voice I/O with Galaxy S9+ audio routing.
category: audio
---

# AITuber OnAir Hakua Audio I/O Setup

## Overview
This skill documents how to configure the AITuber OnAir plugin to use Hakua's voice (irodoriTTS) as the Hermes agent's speech output, and optionally route audio via a Galaxy S9+ device for input/output. It covers cloning the repository, preparing the environment, configuring Hakua, starting the TTS backend, and performing a basic speech test.

## Prerequisites
- Windows 11 (WSL2 not required; uses native CMD/PowerShell via git-bash)
- Git installed
- Node.js (v18+) and npm (or uv for Python)
- Hermes Agent installed and running
- Galaxy S9+ connected to PC via USB (for audio routing, optional)
- Optional: VOICEVOX engine installed if you prefer it over irodoriTTS

## Setup Steps

### 1. Clone the AITuber OnAir repository
If you haven't already, clone the repository to a local folder (e.g., `C:\aituber-onair`):
```bash
git clone https://github.com/shinshin86/aituber-onair.git C:\aituber-onair
```
*(Replace with your preferred URL if you have a fork.)*

### 2. Install dependencies and build
Enter the repository root and install Node.js dependencies, then build the TypeScript packages:
```bash
cd /c/Users/downl/Documents/New project/aituber-onair
npm install
npm run build
```
This will compile all workspaces (core, voice, chat, vrm-app, fbx-app, etc.).

### 3. Configure Hakua in Hermes
Use the Hermes tool `aituber_onair_configure_hakua` to persist non‑secret settings to `config.yaml`. Example:
```text
aituber_onair_configure_hakua(
    repo_root: "C:\\Users\\downl\\Documents\\New project\\aituber-onair",
    avatar_kind: "vrm",
    tts_provider: "auto",   # prefers irodoriTTS, then VOICEVOX
    tts_voice: "hakua",
    tts_speed: 1.0,
    voicevox_url: "http://127.0.0.1:50021",
    voicevox_speaker: 8     # adjust to your preferred speaker/style
)
```
This writes entries under `plugins.aituber-onair` in your Hermes config.

### 4. Start the TTS backend
Start the local TTS server that Hakua will use:
```text
aituber_onair_start_tts(
    provider: "auto",   # auto picks irodoriTTS then VOICEVOX
    timeout_seconds: 120
)
```
If successful, you should see the TTS engine listening on its default port (VOICEVOX: 50021; irodoriTTS: its own port).

### 5. Test Hakua speech
Run a quick synthesis to verify the voice works:
```text
aituber_onair_speak(
    text: "はくあ起動中です。ボブにゃん、聞こえてますか？",
    provider: "auto",
    voice: "hakua",
    speed: 1.0,
    format: "wav",
    play: true
)
```
You should hear the spoken phrase through your PC's default audio device.
### 6. (Optional) Route audio output to Galaxy S9+

Three approaches exist to make TTS audio come out of the Galaxy S9+ speaker instead of the PC. Choose by trade-off:

| Approach | Difficulty | Lip Sync | Code Changes | Latency |
|---|---|---|---|---|
| **① SoundWire** | ⭐ | ❌ | None | ~100ms |
| **② VRM VOICEVOX config** | ⭐⭐ | ✅? | None | ~50ms |
| **③ WebSocket audio push** | ⭐⭐⭐ | ✅ | Python+TS | ~30ms |

#### ⑥-a SoundWire (simplest, recommended for first try)

- **PC**: Install [SoundWire Server](https://soundwire-server.en.lo4d.com/) — captures all PC audio and streams over WiFi.
- **Galaxy S9+**: Install SoundWire Client from Play Store — connects to server IP and plays through phone speaker.
- **Flow**: `TTS → winsound.PlaySound → SoundWire captures → WiFi → Galaxy speaker`
- Zero code changes. All PC audio (not just TTS) plays through phone.
- Warning: use 5 GHz WiFi for lowest latency.

#### ⑥-b VRM app VOICEVOX direct (most integrated, no extra apps)

The VRM app (`react-vrm-app`) has **full VOICEVOX support built-in** in its Settings panel:
- TTS engine dropdown includes `voicevox`
- Fetches speaker list from VOICEVOX API automatically
- `voicevoxApiUrl` configurable (default `http://localhost:50021`)

**Config** (in VRM app Settings panel on the Galaxy browser):
```
TTS Engine: VOICEVOX
API URL:    http://10.228.75.52:50021   ← PC's LAN IP
Speaker:    <pick from auto-fetched list>
```

**Flow**: `Galaxy Chrome → VRM app → http://10.228.75.52:50021 → VOICEVOX synthesizes → Galaxy plays audio + lipsync`

**Caveat**: The VRM app's TTS integration works with the Inworld AI / Codex SDK chat pipeline, not directly with the Hermes Python plugin's `aituber_onair_say()`. For Hermes-plugin-driven conversation, approach ① (SoundWire) or ③ (WebSocket push) are more appropriate.

#### ⑥-c WebSocket audio push (best quality, requires code)

The Python plugin and VRM web client already include the WebSocket audio path.

- **Python**: after TTS synthesis, the plugin pushes `.wav` bytes to `ws://<lan-host>:5176`.
- **VRM app**: the client receives binary frames and calls `play()`, playing audio through the device speaker and deriving RMS-based lip sync automatically.

**Required config** (LAN delivery):
```python
aituber_onair_configure_hakua(
    audio_ws_host="0.0.0.0",
    audio_ws_port=5176,
    audio_ws_allow_lan=True,
)
aituber_onair_start(
    avatar_kind="vrm",
    force=True,
    host="0.0.0.0",
    public_host="<LAN_IP>",
    repo_root="<repo>",
    vrm_port=5175,
)
```

Caveat: Chrome on Android suspends `AudioContext` until the first user gesture; the app recovers from a one-time tap.

See `references/websocket-audio-push.md` for verification steps.

### 7. Integrate with Hermes voice
Once Hakua's TTS is operational, Hermes will automatically use the configured provider (`irodori` or `voicevox`) for any `text_to_speech` or voice‑mediated tool calls (e.g., `vrchat_autonomy_*`, `aituber_onair_say`). No further configuration is needed.

## Troubleshooting
- **TTS not starting**: Check that the required engine (irodoriTTS or VOICEVOX) is installed and not blocked by firewall. Verify the port is free.
- **No audio output**: Ensure the correct output device is selected in Windows Sound settings. Test with a local WAV file.
- **Microphone not detected**: On Android, confirm USB audio mode is active. On PC, check the recording devices list.
- **Build fails**: Delete `node_modules` and `package-lock.json`, then rerun `npm install`. Ensure you have a recent Node.js LTS version.
- **irodoriTTS health OK but synthesis fails / "loaded": false**: Health endpoint alone does not prove the model is loaded. Trigger a test synthesis to force model load:
  ```bash
  curl -X POST "http://127.0.0.1:8088/v1/audio/speech" \
    -H "Content-Type: application/json" \
    -d '{"model":"irodori-tts","input":"テスト","voice":"hakua","response_format":"wav"}' \
    --output test.wav
  ```
  Verify with `file test.wav` → should show RIFF WAVE 48000Hz. If model fails to load, check CUDA/torch compatibility: `IRODORI_MODEL_DEVICE=auto IRODORI_CODEC_DEVICE=auto` avoids hard-fail on GPU drift.
- **Avatar visible on Galaxy but silent / "stuck"**: This is a voice pipeline issue, not avatar render. Check in order:
  1. `aituber_onair_status` → `loops.autonomous.alive` and `loops.comments.alive` must be `true`. If `false`, restart both:
     ```text
     aituber_onair_stop_loops(force=true, target="all")
     aituber_onair_start_autonomous_talk(force=true, interval_seconds=90, play=true)
     aituber_onair_start_comment_reactions(force=true, poll_seconds=2, play=true)
     ```
  2. `tts.active.provider` must be `"irodori"` (not `"voicevox"` if VoiceVox is down). The config shows `selected_provider: "irodori"` but `active.provider` can lag — restart TTS: `aituber_onair_start_tts(provider="irodori")`.
  3. Audio WebSocket (`audio_ws_port=5176`) must be running and reachable from Galaxy LAN. If worker processes can't push to it, use the loopback push path (see `references/irodori-galaxy-ws-recovery.md`).
  4. `aituber_onair_speak` with `play: true` must produce audible output on PC first; only then test Galaxy delivery.
- **lm-twitterer media upload fails with "must be under lm-twitterer media dir"**: Files must be copied to `C:\Users\<user>\.hermes\lm-twitterer\media\` and referenced by full absolute path in `media_paths`. Relative filenames are rejected by the path validator.

## Smartphone as Stack-chan Face Display

The AITuber OnAir VRM app doubles as a **remote avatar display**. Any device on the same LAN (Galaxy S9+, tablet, second monitor) can show Hakua's face by opening the VRM app URL in a browser — exactly like Stack-chan's smartphone-as-face design.

### How it works

```
[PC] AITuber OnAir VRM app (Vite dev server, port 5175)
  └─ avatar_host=0.0.0.0  →  bind all interfaces
  └─ avatar_public_host=<LAN_IP>  →  auto-detected or explicit
       ↓
[Smartphone] Chrome → http://<LAN_IP>:5175/
  └─ Hakua VRM avatar displayed full-screen = Stack-chan face
```

### Setup

1. **Ensure VRM app is running** — verify with `netstat -ano | grep 5175` or check `aituber_onair_status` (after restarting Hermes if the handler bug is still active).

2. **Verify LAN access** — from the smartphone, open `http://<PC_LAN_IP>:5175/` in Chrome. If it fails, check Windows Firewall (allow Node.js on private networks) and confirm the PC's `avatar_host` is `0.0.0.0` (config: `plugins.entries.aituber-onair.avatar_host`).

3. **Phone placement** — Galaxy S9+ in a tablet stand, propped up as the "head" of a Stack-chan-like desktop companion. Audio comes from PC speakers (irodoriTTS/VOICEVOX); the phone handles display only.

4. **Optional: Robot body** — M5Stack + servo motor + the S9+ as face for a full Stack-chan robot. The VRM app is purely visual; physical movement requires a separate controller.

### Troubleshooting

- **`TypeError: handle_*() got an unexpected keyword argument 'task_id'`** — All `aituber_onair_*` tool handlers in `plugins/aituber_onair/core.py` are declared as `def handle_*(args)` but `registry.dispatch()` passes system kwargs (`task_id`, `session_id`). Fix: add `**kwargs: Any` to every handler signature. This only affects the running Hermes process — restart the agent after patching.
- **VRM port not listening** — verify the VRM app process is alive. Run `npx vite --port 5175 --host 0.0.0.0` manually from `packages/core/examples/react-vrm-app/` if the plugin-managed start fails.
- **Blank screen on smartphone** — check that the smartphone is on the same subnet. Chrome on Android may block `http` LAN URLs by default; enable "Allow insecure origins" or use `https` via a reverse proxy (Caddy, ngrok, etc.).
- **Audio delay between face and voice** — the smartphone display has inherent network latency (50-200ms). This is acceptable for a desktop companion; for lip-sync precision, switch to a wired HDMI display or use `vrchat_avatar_param` Viseme drive on a local render.
- **WS says `thinking` but never returns `reply`** — isolate the stack: raw WS ready → tiny WAV binary push → TTS-only smoke → chat E2E. Ensure the WS chat worker catches exceptions and always sends a terminal `reply` JSON. See `references/websocket-audio-push.md` for the verification ladder and pitfalls.
- **`auto` TTS selects irodori but no audio arrives** — irodori can look available while runtime synthesis fails. Keep VOICEVOX reachable as fallback and preserve the original irodori error in `fallback_error` instead of making the Galaxy client wait silently.
- **Avatar is visible on Galaxy but stands silently or speech is intermittent** — treat this as a voice pipeline issue, not an avatar-render issue. Check irodori synthesis with real WAV output, then verify Audio WS process-boundary delivery. If the WS server lives in a background process and synthesis runs in worker processes, `audio_ws_push_wav()` must loop back into the running WS server instead of relying only on process-local `_audio_ws_clients`. See `references/irodori-galaxy-ws-recovery.md`.
- **irodori health is OK but synthesis returns 500 or hangs** — verify the torch build and device configuration. On Windows/CUDA, avoid `uv run --no-sync`; sync/start with the correct CUDA extra and prefer `IRODORI_MODEL_DEVICE=auto` / `IRODORI_CODEC_DEVICE=auto` so stale `cuda` settings do not hard-fail when the environment changes. See `references/irodori-galaxy-ws-recovery.md`.
- **Hakua reply backend degrades despite configured `hermes_provider`/`hermes_model`** — AITuber plugin LLM overrides require explicit allow-list config. Use `hermes config set plugins.entries.aituber-onair.llm.allow_provider_override true` and the matching allowed provider/model lists; do not direct-edit guarded `~/.hermes/config.yaml`.

## Provider Rotation

The AITuber OnAir plugin supports round-robin rotation through multiple Hermes LLM providers. Configure a list of `provider:model` pairs and each `aituber_onair_say()` call advances to the next backend automatically.

```yaml
plugins:
  entries:
    aituber-onair:
      provider_rotation:
        - opencode-zen
        - xai-oauth:grok-3
        - openai-codex:gpt-5.5-low
```

- Each entry: `"provider"` or `"provider:model"`.
- Rotation preempts static `hermes_provider`/`hermes_model` when the list is non-empty.
- Per-call `provider_rotation` in `aituber_onair_say()` overrides the config-level list.
- Thread-safe round-robin (in-memory counter, resets on process restart).
- Only affects the `hermes` reply backend; Codex SDK path is unchanged.

See `references/provider-rotation.md` for the full implementation pattern and design decisions.

## References
- `references/setup-notes.md` – session‑specific notes from the 2026-06-19 AITuber OnAir Hakua audio setup.
- `references/provider-rotation.md` – implementation pattern for round-robin LLM provider rotation in the plugin.
- `references/stack-chan-smartphone-face.md` – session‑specific notes from the 2026-06-19 Galaxy S9+ as Stack-chan face display setup, including VRM app architecture and handler bug fix details.
- `references/irodori-galaxy-ws-recovery.md` – recovery checklist for irodoriTTS CUDA/env drift, Audio WS loopback WAV delivery, and silent Galaxy avatar symptoms.
- `references/lm-twitterer-media-path.md` – lm-twitterer media directory requirement (absolute path under `~/.hermes/lm-twitterer/media/`).
- `references/vrchat-photo-to-video-tweet.md` – end-to-end pipeline: VRChat screenshot + irodoriTTS audio → ffmpeg MP4 → lm-twitterer post.
- Official AITuber OnAir docs: https://docs.aituberonair.com
- irodoriTTS repository: https://github.com/Irodori-TTS/irodoriTTS-server
- VOICEVOX: https://voicevox.hiroshiba.jp/

## Notes
- This skill assumes the default Hakua voice (`hakua`) is available in irodoriTTS. If you installed a different voice, adjust `tts_voice` accordingly.
- For VRChat avatar lip‑sync, ensure the VRC‑OSC plugin is running and the avatar's `Viseme` parameter is driven by the voice output (handled automatically by the AITuber OnAir VRM/FBX apps when using the provided example scenes).
