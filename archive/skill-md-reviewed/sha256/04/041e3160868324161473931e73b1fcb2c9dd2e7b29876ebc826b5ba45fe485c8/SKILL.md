---
name: multimodal-live-capture
category: gaming
description: Real-time webcam + microphone capture with Whisper STT for autonomous agents, especially VRChat. Supports periodic multimodal recording and integration with dataset generation and agent loops.
tags: [vrchat, whisper, stt, camera, multimodal, dataset, autonomous]
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

## References
- `references/multimodal_capture.md` — detailed usage and integration guide
- `references/capture_script.py` — the actual runnable script

## Notes for Future Sessions
- Always prefer `--camera-index` on Windows if default camera is not 0.
- Use `--max-iterations` for testing without running forever.
- Combine with `vrchat-voicevox-autostart` for full VRChat + real-world sensing.