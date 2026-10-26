---
name: multimodal-live-capture
category: gaming
description: "Webcam + mic capture with Whisper STT for agents."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vrchat, whisper, stt, camera, multimodal, dataset, autonomous, webcam, microphone]
---

# Multimodal Live Capture

Enables autonomous agents to perceive the real world via camera and microphone while running (especially useful for VRChat agents).

## Core Capabilities
- Periodic webcam capture using OpenCV
- Microphone recording + Whisper STT transcription
- Synchronized storage of image + audio + text
- Output formats: JSONL records + `latest.json` for easy polling
- Designed for integration with VRChat autonomous agents and dynamic dataset collection

## Usage
```bash
python scripts/multimodal_capture.py \
  --interval 10 \
  --audio-seconds 5 \
  --whisper-model base \
  --language ja
```

## Integration Points
- Can be called from Cron jobs
- Feeds into dynamic VOICEVOX + OSC dataset generation
- `latest.json` can be read by the main VRChat agent loop for real-time context

## Dependencies
- `opencv-python`
- `sounddevice`
- `numpy`
- Whisper (already installed in this environment)

## Pitfalls
- On Windows, the default camera index may not be 0 — use `--camera-index` to specify.
- Whisper `base` model is fast but low accuracy for Japanese; use `medium` or `large` for production.
- Long recordings without `--max-iterations` will run forever — always set a limit for testing.
- `sounddevice` may fail if another app holds the microphone exclusive; close Discord/VRChat mic input first.

## Notes for Future Sessions
- Always prefer `--camera-index` on Windows if default camera is not 0.
- Use `--max-iterations` for testing without running forever.
- Combine with `vrchat-voicevox-autostart` for full VRChat + real-world sensing.