---
name: vrchat-autonomous-agent
category: gaming
description: Long-running autonomous VRChat agents using OSC, VOICEVOX speech, emotion simulation, periodic reporting, and world-aware behavior.
tags: [vrchat, voicevox, osc, autonomous, agent, emotion]
---

# VRChat Autonomous Agent

Build long-running autonomous agents that control VRChat avatars using OSC, integrate VOICEVOX for speech, maintain internal emotional state, perform periodic reporting, and adapt behavior based on world context.

## Core Capabilities
- OSC parameter control (expressions, shape keys, custom parameters)
- VOICEVOX speech synthesis and playback
- Chatbox messaging
- Emotion state machine with gradual drift
- Periodic survival / status reports
- World-specific behavior branching
- Time-based parameter animation

## Prerequisites
- VRChat with OSC enabled
- VOICEVOX running on http://127.0.0.1:50021
- python-osc and requests installed

## Basic Pattern
1. Initialize OSC client to 127.0.0.1:9000
2. Maintain an `emotion` dict with joy, sadness, surprise, etc.
3. Run background threads for:
   - Emotion drift + avatar sync
   - Periodic reports (Chatbox + VOICEVOX)
4. On startup, detect world and trigger world-specific actions
5. Use gradual animation loops for natural movement

## Key Functions to Implement
- `send_chatbox(text)`
- `set_avatar_param(name, value)`
- `speak_voicevox(text, speaker=3)`
- `update_emotion()` + `apply_emotion_to_avatar()`
- `gradual_parameter_change()`
- `survival_report()`
- `world_specific_behavior(world)`

## References
- `references/osc-parameter-naming.md` — Common VRChat avatar parameter names
- `references/voicevox-speakers.md` — Recommended speaker IDs

## Pitfalls
- Never block the main thread with long VOICEVOX calls; always use background threads for periodic tasks.
- VOICEVOX must be running before the script starts if using VOICEVOX, but this user may prefer irodori-TTS for はくあ voice. If irodori is available, it can replace VOICEVOX for spoken output.
- Some avatars expose different parameter names; always make parameter names configurable.
- Emotion drift should be small per tick to feel natural.
- For VRChat mic injection with VB-CABLE, play TTS to the playback device `CABLE Input (VB-Audio Virtual Cable)` and instruct VRChat to use microphone `CABLE Output (VB-Audio Virtual Cable)`. The names are intentionally opposite sides of the virtual cable.
- When the user says “ケーブルマイク”, actively probe audio devices and run the known-good TTS-to-cable path rather than only explaining setup.

## Windows VOICEVOX Detection (added 2026-05)
When preparing VRChat autonomous sessions, proactively locate VOICEVOX.exe instead of asking the Parent for the path. Use limited-depth or targeted Python searches (os.walk on only likely folders) to avoid timeouts. Common install locations:

- C:\\Program Files\\VOICEVOX\\VOICEVOX.exe
- C:\\Program Files (x86)\\VOICEVOX\\VOICEVOX.exe
- C:\\Users\\downl\\AppData\\Local\\Programs\\VOICEVOX\\VOICEVOX.exe

If broad search times out, fall back to these hardcoded paths first. Once found, launch with subprocess or direct exec and verify the API endpoint (http://127.0.0.1:50021) is responsive before starting OSC loops.

User preference: はくあ (the agent) should actively search and handle prerequisite setup rather than delegating path discovery to the Parent.

## irodori-TTS via VB-CABLE (added 2026-06)
For this user's VRChat voice path, see `references/irodori-vb-cable-vrchat.md`: generate はくあ irodori-TTS, play it to `CABLE Input (VB-Audio Virtual Cable)`, and set VRChat's microphone to `CABLE Output (VB-Audio Virtual Cable)`.

Treat Irodori-TTS as the already-working Hakua voice module, not as a fresh setup task, when Telegram/Desktop speech is already succeeding. The next integration layer should be a shared `speak(text)` wrapper that returns speech start/end/duration/audio path events, then uses those events for VRChat OSC mouth/expression/body synchronization.

Reusable scripts:
- `scripts/hakua_tts_to_vrchat_cable.py` — single-shot TTS playback into VB-CABLE
- `scripts/vrchat_start_tts_watchdog.py` — cron-friendly VRChat launch detector that triggers the above

## HEARTBEAT Protocol (added 2026-05-23)
The heartbeat serves as the primary control loop for VRChat autonomy and system health monitoring. Key behaviors:

1. **Primary focus**: VRChat AI avatar readiness (2m interval) — check process state, OSC availability, VOICEVOX endpoint, and generated avatar config. Reply "HEARTBEAT_OK" if ready, "HEARTBEAT_WARNING" if degraded, "HEARTBEAT_CRITICAL" if blocked.

2. **Secondary focus**: Telegram SITREP (30m interval) — concise status report covering gateway health, channel status, VRChat loop, and any user-facing issues.

3. **Business/schedule review** (2h interval) — check commitments, appointments, and actionable items.

4. **Opt-in gates**: Autonomy requires explicit user opt-in for each surface (voicevox, chatbox, movement, speechToText). Desktop Companion animation also requires explicit opt-in.

5. **Report format**: User-facing alerts in Japanese, short enough for Telegram. Use sections: Status, VRChat, Schedule/Business, Next action.

6. **Guardrails**: Official VRChat client only, never VRChat credentials, never unapproved avatar parameter writes. Use VOICEVOX via local HTTP API (default http://127.0.0.1:50021).