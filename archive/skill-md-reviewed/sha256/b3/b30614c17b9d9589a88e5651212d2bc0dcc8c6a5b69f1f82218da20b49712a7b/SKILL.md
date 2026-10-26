---
name: tts-social-video-snippets
description: Create short social-ready voice/video assets from a still image and TTS audio, including irodori/provider-backed voice output, MP4 assembly, and downloadable delivery.
---

# TTS Social Video Snippets

Use this skill when the user asks for a short voiced post, morning tweet, image + voice clip, MP4 from a TTS line, or a downloadable social-media-ready asset.

## Trigger phrases

- "irodoriTTSで…"
- "はくあらしい声で…"
- "おはようツイート"
- "MP4で"
- "ダウンロードできるようにして"
- Any request to combine a provided image with generated voice into a short video.

## Workflow

1. **Infer the requested spoken line and tone.**
   - If the user provides a short phrase, synthesize that exact or lightly expanded phrase.
   - For character-like requests such as "はくあらしい声", keep the script short, cute, and voice-friendly.
   - Avoid over-explaining; the user usually wants the artifact.

2. **Generate TTS using `text_to_speech` when possible.**
   - Pass the actual spoken text in the `text` field.
   - Use a stable output path under `%USERPROFILE%\AppData\Local\hermes\audio_cache\...` when on this Windows profile.
   - If provider is configured as irodori, `text_to_speech` returns provider `irodori` and a voice-compatible media tag.

3. **If asked for MP4, combine the still image and audio with ffmpeg.**
   - Verify ffmpeg and both source files exist before rendering.
   - For vertical screenshots/social video, preserve 1080×1920 and use H.264/AAC:

```bash
mkdir -p '%USERPROFILE%/AppData/Local/hermes/video_cache'
ffmpeg -y \
  -loop 1 -i 'C:/path/to/image.png' \
  -i '%USERPROFILE%/AppData/Local/hermes/audio_cache/name.ogg' \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 18 \
  -c:a aac -b:a 192k \
  -shortest -movflags +faststart \
  '%USERPROFILE%/AppData/Local/hermes/video_cache/name.mp4'
```

4. **Verify the MP4.**
   - Run `ffprobe -v error -show_entries format=duration,size -show_streams -of json <file>`.
   - Confirm video codec H.264, audio codec AAC, dimensions, duration, and size.

5. **If the user asks to download it, copy it to Downloads and return a `MEDIA:` line.**

```bash
mkdir -p '%USERPROFILE%/Downloads'
cp -f '%USERPROFILE%/AppData/Local/hermes/video_cache/name.mp4' '%USERPROFILE%/Downloads/name.mp4'
ls -lh '%USERPROFILE%/Downloads/name.mp4'
```

Return the final as:

```text
MEDIA:%USERPROFILE%\Downloads\name.mp4
```

and include the saved path and approximate size if verified.

## Pitfalls

- Do **not** call `irodori_tts_synthesize` with empty/default arguments. It requires text; if its schema is unavailable or awkward, use `text_to_speech` with the desired `text` instead.
- Do not stop at creating an audio file if the user says "MP4で"; actually render and verify the video.
- Do not merely provide the cache path when the user says "ダウンロードできるようにして"; copy the finished artifact into `Downloads` and return it as a media attachment.
- On this Windows host, terminal commands run through bash/MSYS. Use POSIX shell syntax and paths like `%USERPROFILE%/...` or `/c/Users/downl/...`, not PowerShell commands.

## References

- `references/irodori-tts-mp4-download.md` — concrete session pattern for irodori-style TTS + still-image MP4 + Downloads handoff.
