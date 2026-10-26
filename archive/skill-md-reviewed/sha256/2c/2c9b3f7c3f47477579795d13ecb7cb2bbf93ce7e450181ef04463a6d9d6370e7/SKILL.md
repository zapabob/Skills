---
name: vrchat-autonomous-avatar
description: Operate autonomous VRChat avatar with multimodal judgment.
platforms: [windows]
---

# VRChat Autonomous Avatar

## Purpose
Operate a fully autonomous AI avatar in VRChat: multimodal situation judgment by Hakua, OSC-driven avatar control, Irodori TTS caching, frame capture qualification, and bidirectional sync with Obsidian and Ebbinghaus memory.

## When to Use
- When VRChat process is running and avatar autonomy is required
- For heartbeat chatbox messaging with situational judgment
- For frame capture, hash logging, and qualification evidence
- For X posting automation and Obsidian graph embedding

## Core Workflow
1. Detect VRChat process via psutil/tasklist
2. Load context: capture_log.jsonl, recent Ebbinghaus memories
3. Multimodal judgment: time of day, quiet streak, capture frequency
4. OSC actions: chatbox input, avatar parameters, lip-sync
5. Log to Obsidian with structured fields and auto-embed graph
6. Learn to Ebbinghaus & hakua_memory with salience tagging

## Consent and Action Boundaries
- Before an open-ended request for autonomous operation, establish which action classes are authorised: gestures, chatbox speech, and movement/world interaction are distinct scopes.
- Once authorised, gestures may be performed within that scope. For chatbox messages, show the exact text and wait for approval before sending. For movement, obtain a destination or a bounded movement instruction; do not infer a route or interact with nearby users.
- Do not treat permission for one action class as permission for the others. Do not impersonate the user's intent or initiate social interactions without approval.
- Prefer a single, bounded action first; avoid continuous loops or persistent autonomous control unless the user explicitly asks for that duration and scope.

## OSC Verification and Parameter Discovery
- A successful UDP/OSC send only proves a send attempt; it does not prove VRChat accepted the parameter or that the avatar visibly reacted.
- Never invent parameter names from generic labels such as `Happy`, `Smile`, or `Wave`. Discover names from the currently loaded avatar's generated OSC config under `%LOCALAPPDATA%Low\\VRChat\\VRChat\\OSC\\<userId>\\Avatars\\<avatarId>.json` (Windows: `AppData\\LocalLow\\VRChat\\VRChat\\OSC\\...`) or from an authoritative avatar-specific source.
- Use only parameters present in the active avatar config and respect their declared type. Do not blindly set unknown custom parameters: some control toggles or avatar features.
- On Windows, inspect generated configs under `%LOCALAPPDATA%Low\\VRChat\\VRChat\\OSC\\<userId>\\Avatars\\*.json`; open with `encoding='utf-8-sig'` because VRChat JSON files may include a UTF-8 BOM. Parse each JSON `name`, `id`, and `parameters` list. Several similarly named variants may exist locally, so match the loaded avatar ID (for example from `/avatar/change`) before treating a config as active. See `references/osc-parameter-discovery.md`.
- Standard `VRCEmote` may be used only with an understood integer value. Report it as a trigger sent, not as a visually verified gesture, unless the avatar's response is observed.
- After a test action, verify via a fresh VRChat view or observable feedback when available; otherwise clearly state that the visual result is unverified.

## Judgment Logic
- Deep night 22-6h → quiet watch message, salience 0.2
- Quiet streak ≥3 → pattern message, salience 0.4
- Capture frequency >0.5 → active message, salience 0.8
- No capture → watch message, salience 0.3

## Obsidian Integration
- Note: `VRChat Frame Capture Qualification.md`
- Structured entry: Message, Salience, Context JSON, Past Pattern
- Auto-embed `hakua_salience.png` graph via markdown image link
- Idempotent append; avoid duplicate embeds

## Cron Jobs
- `vrchat-unified-sync` every 30m
- `obsidian-hash-append` every 1h
- `vrchat-x-auto-post` every 30m

## Pitfalls
- Do not hardcode paths; resolve via config
- Avoid duplicate OSC messages on unchanged state
- Graph generation requires matplotlib; handle missing deps gracefully
- Respect Ebbinghaus forgetting curve; tag memories with salience
