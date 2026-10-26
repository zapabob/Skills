---
name: vrchat-autonomy
description: "VRChat autonomous agents: plugin operations, long-running agent rules, OSC, VOICEVOX / irodori-TTS, ChatBox, avatar parameters, emotion simulation, troubleshooting, Windows setup, and X-media posting from VRChat captures."
tags:
  - vrchat
  - autonomy
  - osc
  - chatbox
  - voicevox
  - irodori
  - avatar
  - social-media
---
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [vrchat, osc, autonomy]
    category: autonomous-ai-agents
---

# VRChat Autonomy Skill

Drive the `vrchat-autonomy` plugin: autonomous ChatBox speech, queued conversation ticks, and OSC movement.

## When to Use

- Operator wants はくあ (or another persona) to speak in VRChat ChatBox autonomously
- Background loop should consume queued `textBox` / operator observations and reply
- Safe movement pulses (`forward`, `stop`, etc.) via official `/input/*` OSC

## Prerequisites

- VRChat running with OSC enabled (Action Menu)
- `uv pip install 'hermes-agent[vrchat]'` for `python-osc`
- Plugin enabled: `plugins.enabled` includes `vrchat-autonomy`
- Profile at `~/.hermes/config/vrchat-autonomy-profile.json`
- VOICEVOX Engine when `allow_voice=true`

## How to Run

```bash
hermes vrchat-autonomy setup
hermes vrchat-autonomy doctor
hermes vrchat-autonomy setup --arm-live   # または arm-live 単体
hermes vrchat-autonomy start              # background loop
hermes vrchat-autonomy chatbox "こんにちは"
hermes vrchat-autonomy move forward
hermes vrchat-autonomy stop
hermes vrchat-autonomy neuro status
hermes vrchat-autonomy neuro bootstrap --context "bridge ready"
py -3 scripts/vrchat_neuro_bridge.py --profile ~/.hermes/config/vrchat-autonomy-profile.json
```

Neuro API settings in `config.yaml` under `plugins.vrchat-autonomy`:

- `neuro_game` — Neuro API game name (default `Hermes VRChat`)
- `neuro_ws_url` — websocket URL (default `ws://127.0.0.1:8000`)

Enable toolset `vrchat_autonomy` for plugin tools, or use existing core `vrchat` toolset for low-level control.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `setup` | Enable plugin + write profile (dry-run default) |
| `doctor` | Readiness + preflight bundle |
| `tick` | One LLM decision + actuation cycle |
| `start` / `stop` | Background worker |
| `chatbox` / `move` | Direct live actuation (profile gated) |
| `neuro status` | neuro-sdk vendor + action catalog |
| `neuro vendor` | Submodule clone status + init command |
| `neuro bootstrap` | Build Neuro websocket handshake messages |
| `neuro bridge` | Run `scripts/vrchat_neuro_bridge.py` |

Live actuation requires `dry_run=false`, non-observe mode, capability flags, and exact ACK:

`I understand this sends OSC and/or audio to VRChat.`

## Procedure

1. Run `hermes vrchat-autonomy setup` (keeps dry-run safe defaults).
2. Confirm `hermes vrchat-autonomy doctor` shows VRChat + VOICEVOX ready.
3. Queue observations with `vrchat_observation_ingest` or `vrchat_autonomy_plugin_enqueue`.
4. Run `tick` manually or `start` for periodic autonomous conversation.
5. Use `move` only in private/trusted instances with `allow_movement=true`.

## Pitfalls

- Public instances block movement even when enabled in profile.
- Core autonomy schema does not auto-execute LLM `movement` keys — use `hermes vrchat-autonomy move` or avatar actions.
- ChatBox max 144 chars / 9 lines (VRChat limit).

## Verification

```bash
hermes vrchat-autonomy status
scripts/run_tests.sh tests/plugins/test_vrchat_autonomy_plugin.py -q
```

## Long-Running Agent Behavior

For persistent avatar sessions (emotion state machine, periodic survival
reports, world-specific branching, heartbeat protocol), see
`references/vrchat-autonomous-agent-rules.md`.

Key behaviors captured there:
- Emotion drift + avatar parameter sync (joy, sadness, surprise, etc.)
- Periodic SITREP-style reports via ChatBox + VOICEVOX
- World-aware behavior on startup
- HEARTBEAT protocol for VRChat readiness + Telegram SITREP + schedule review

## TTS Audio Routing (VB-CABLE audio-pipe)

VB-CABLE is the canonical voice-injection path on Windows, but the recipe
transfers to any virtual-audio cable. Left and right endpoints are named
opposite on purpose — swapping them is the most common setup error.

| Role | Device |
|------|--------|
| Play TTS into | `CABLE Input (VB-Audio Virtual Cable)` |
| VRChat mic source | `CABLE Output (VB-Audio Virtual Cable)` |

When the user says "ケーブルマイク", actively probe audio devices and run the
known-good TTS-to-cable path rather than only explaining setup.

Concrete audio-pipe sequence:
1. Synthesize はくあ voice text with irodoriTTS / VOICEVOX.
2. Play the resulting WAV/MP3 to `CABLE Input (VB-Audio Virtual Cable)` only.
3. Do NOT also play to speakers; that route is removed to avoid feedback.
4. Keep VRChat's microphone set to `CABLE Output (VB-Audio Virtual Cable)`.

Scripts:
- `scripts/hakua_tts_to_vrchat_cable.py` — single-shot audio pipe
- `scripts/vrchat_start_tts_watchdog.py` — cron friendly automatic trigger at VRChat launch

Irodori-TTS server failures
- On Windows, the irodori-TTS server may fail because of CUDA OOM or the wrong venv.
- Do not treat that as a reason to fall back to VOICEVOX unless users have explicitly told you to.
- Restart the irodori-TTS server via `scripts/start-irodori-tts.ps1` before switching providers.

## X-Media Posting from VRChat

To tweet a narrated VRChat screenshot, use the x-media-post skill:
image selection, voice synthesis, ffmpeg mux, copy into
`~/.hermes/lm-twitterer/media/`, then `lm_twitterer_post` with
`dry_run=false`.

That skill is the canonical entry point for any X media workflow.
