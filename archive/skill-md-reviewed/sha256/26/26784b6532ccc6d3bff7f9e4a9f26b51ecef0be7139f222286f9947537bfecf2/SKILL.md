---
name: video-frames
description: Extract frames or short clips from videos using ffmpeg.
homepage: https://ffmpeg.org
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["ffmpeg"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg (brew)",
            },
          ],
      },
  }
---

# Video Frames (ffmpeg)

Extract a single frame from a video, create quick thumbnails for inspection, or assemble simple image-based MP4s with narration.

## References

- `references/static-image-tts-mp4.md` — create a 1920x1080 H.264/AAC MP4 from static images plus Hermes TTS, with captions/persona styling.
- `references/windows-static-image-tts-mp4-pitfalls.md` — Windows fallback for static-image TTS MP4s when `ffmpeg drawtext`/Fontconfig crashes; pre-render captions with Pillow and encode with a simple ffmpeg mux.

## Quick start

First frame:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

At a timestamp:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

## Notes

- Prefer `--time` for “what is happening around here?”.
- Use a `.jpg` for quick share; use `.png` for crisp UI frames.
