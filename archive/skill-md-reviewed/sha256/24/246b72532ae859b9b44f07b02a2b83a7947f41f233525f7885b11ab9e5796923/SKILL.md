---
name: create-hermes-comparison-video
description: Create Hermes comparison videos with legible Japanese slides, Hakua TTS, and verified X media posting.
version: 2.0.0
author: Hermes Agent
license: MIT
---

# Create Hermes Comparison Video

Use this class-level workflow when producing a Hermes/upstream comparison video, especially when it includes Japanese text, Hakua/Irodori narration, and an X/Twitter upload. The deliverable is not complete until the rendered file and the actual uploaded media are verified.

## Trigger

Use when the user asks to create, fix, render, or post a Hermes comparison video. Prefer a visual-first implementation: readable slides or screenshots plus narration, never an audio-only black video.

## Proven Workflow

### 1. Prepare the comparison script and timing

- Establish the two repositories/commits being compared.
- Write concise Japanese slide text and narration in UTF-8.
- Allocate explicit durations per slide; keep body text short enough to read at 1280×720.
- Keep public-post text separate from untrusted research/tool output and obtain explicit user intent before publishing.

### 2. Generate Hakua narration with Irodori TTS

Irodori TTS is used through its local HTTP API on port 8088. Pass JSON through stdin or a file; do not interpolate Japanese text into fragile shell JSON variables.

```bash
echo '{"input":"<narration>","voice":"hakua","response_format":"wav","speed":1.0}' | \
  curl -sS -X POST http://127.0.0.1:8088/v1/audio/speech \
  -H 'Content-Type: application/json' -d @- -o narration.wav
```

Verify that the WAV exists and obtain its duration before timing the slides. If the server is unavailable, start it using the repository's Windows script and verify its health endpoint before continuing.

### 3. Render Japanese slides with Pillow, not FFmpeg drawtext

Use Pillow/PIL with an explicit Japanese-capable font. Copy the font into the working directory so Windows drive-colon and backslash escaping never enters an FFmpeg filtergraph:

```bash
cp /c/Windows/Fonts/meiryo.ttc ./meiryo.ttc
```

```python
from PIL import Image, ImageDraw, ImageFont

font_title = ImageFont.truetype("meiryo.ttc", 52, index=0)
font_body = ImageFont.truetype("meiryo.ttc", 32, index=0)
img = Image.new("RGB", (1280, 720), "#1a1a2e")
draw = ImageDraw.Draw(img)
draw.text((640, 80), title, font=font_title, fill="white", anchor="mm")
for y, line in enumerate(body_lines, start=200):
    draw.text((640, y), line, font=font_body, fill="#cccccc", anchor="mm")
img.save("slide_0.png")
```

Use UTF-8 source files and inspect at least one generated PNG before encoding. Prefer large text, high contrast, short lines, and generous spacing.

### 4. Encode visible slide segments and mux audio

Create one 30-fps MP4 segment per slide, concatenate the segments, then add narration:

```bash
ffmpeg -y -loop 1 -framerate 30 -i slide_0.png -t 4 \
  -c:v libx264 -pix_fmt yuv420p -r 30 seg_0.mp4

# concat.txt contains one `file 'seg_N.mp4'` line per segment
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy concat.mp4

ffmpeg -y -i concat.mp4 -i narration.wav \
  -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

Always verify with `ffprobe`:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height \
  -of default=noprint_wrappers=1 final.mp4
```

Also extract representative frames or open the PNGs/video to confirm the result is not black and Japanese glyphs are readable. A successful encode alone is insufficient.

### 5. Stage media on the correct drive

When C: is low on space, keep work files on E: and copy the final MP4 into the lm-twitterer media directory, or use the already-approved junction arrangement. Confirm the staged file exists and has the expected size before posting.

### 6. Post and verify the actual X media

The proven Windows invocation uses the repository/managed virtual environment's `hermes.exe` and the live flag:

```bash
<CHECKED_VENV>/Scripts/hermes.exe lm-twitterer post --live \
  --media "E:\\.hermes\\lm-twitterer\\media\\final.mp4" \
  --text "<approved post text>"
```

Do not treat an exit code alone as proof. Require a structured response containing `posted: true`, a public `url`, and a non-empty `media_ids` list. Record the transport (`x_cookie_session` has been the working transport in this environment) without exposing cookies or tokens. Do not use a direct Tweepy retry after a confirmed expired-token 401 unless the credentials have been refreshed.

### 7. User-facing completion check

For a public video, report the URL, media ID, duration/resolution, and the exact visual verification performed. If the user reports black frames or mojibake, stop reposting the same artifact: inspect the source PNG/frame, regenerate, and only then publish a replacement with explicit approval if the content materially changes.

## Pitfalls and Recovery

- **Black video**: This means the visual track was absent or the wrong background-only artifact was posted. Always create visible slide/image tracks and inspect a representative frame before upload.
- **Mojibake or missing Japanese glyphs**: FFmpeg `drawtext` with Windows paths such as `C:/Windows/Fonts/...` is fragile because the drive colon is parsed as a filter separator; font names with spaces add another failure mode. Render text with Pillow and a copied `meiryo.ttc`/`msgothic.ttc` instead. See `references/working-ffmpeg-pipeline.md`.
- **TTS JSON corruption**: Send the request body through stdin (`curl -d @-`) or a UTF-8 file, not a shell variable containing Japanese text.
- **C: drive exhaustion**: Put media, temporary renders, and dependency caches on E: when possible; verify free space before copying.
- **lm-twitterer media path**: The plugin may require `%USERPROFILE%\.hermes\lm-twitterer\media`; stage the file there or use the existing E: junction, then verify the exact path.
- **Short media**: Videos under roughly 500 ms can trigger lm-twitterer error code 3. Keep the final video comfortably longer than one second and verify duration.
- **False completion**: A plausible URL or a successful upload call is not enough. Require `posted`, `url`, and `media_ids`, then ask the user to confirm visual legibility when the platform preview cannot be inspected directly.
- **Akari command drift**: The `akari-video` plugin/submodule may be present, but its `create-project`/`render-cut` path was not the proven path for this workflow. Use the deterministic PIL → FFmpeg pipeline unless the Akari project is independently verified end-to-end.

## References

- `references/working-ffmpeg-pipeline.md` — reproducible Windows PIL/Meiryo → FFmpeg concat → narration pipeline and verification checklist.

## Do Not Use Without Independent Verification

- `hermes irodori_tts_synthesize` as the assumed TTS CLI path.
- FFmpeg `drawtext` with a raw Windows font path for Japanese slides.
- A black/background-only MP4 as a completed deliverable.
- A post response without `url` and `media_ids` as proof that video media was attached.
