---
name: desktop-companion
description: Operate the local OpenClaw Desktop Companion avatar through approved tools: load VRM/FBX/Live2D assets, speak, emote, move gaze, trigger motions, and diagnose local-only companion behavior.
user-invocable: false
---

# Desktop Companion

Use this skill when the user asks OpenClaw to move, speak through, load, animate, or diagnose the desktop avatar companion.

## First choice

Use `control_companion` for direct local control.

```json
{ "action": "speak", "value": "I am ready." }
```

```json
{ "action": "emotion", "value": "happy" }
```

```json
{ "action": "motion", "value": "idle", "motion_index": 0 }
```

```json
{ "action": "look_at", "x": 0.2, "y": -0.1 }
```

```json
{ "action": "load_model", "model_path": "assets/NFD/Hakua/FBX/FBX/Hakua.fbx" }
```

## Harness bridge

Use `hypura_harness_companion` only when the user asks for the Hypura path or the direct companion tool is unavailable. Call `hypura_harness_status` first if daemon health is unknown.

## Creator-safe asset flow

1. Verify the avatar path is local.
2. Confirm the user has rights to use the asset before activation.
3. Prefer VRM/FBX for current Desktop Companion work. Live2D is compatibility mode.
4. Load with `control_companion`.
5. Prove visible control with `emotion`, `look_at`, and a short `speak`.

## Do not

- Do not upload avatar files, screenshots, tab text, mic audio, or browser context.
- Do not enable broad browser monitoring.
- Do not use raw exec or raw HTTP control when OpenClaw tools exist.
- Do not edit `SOUL.md` for companion operation.
