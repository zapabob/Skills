---
name: hyperframes-hakua-video
category: media
description: Create a video using Hyperframes with Hakua voice (irodori TTS) for social media posting.
---
# Hyperframes Video with Hakua Voice

## Description
Create videos using either direct frame rendering or Hyperframes, with Hakua-style Japanese narration and QC validation before publishing.

## Prerequisites
- Python stack: `numpy`, `Pillow`, `OpenCV`, `ffmpeg` on PATH
- Optional: `npx hyperframes` if using the Hyperframes composition path
- TTS configured in `~/.hermes/config.yaml` under `tts:`; for Japanese female voice prefer `fishaudio` first, fall back to `irodori/voice=hakua`, then `voicevox`
- Basic knowledge of HTML/CSS if using Hyperframes; Python/PIL if using direct render

## Preferred Production Workflow
1. **Cheap layout pass** — run a pre-render text-fit check before generating frames.
2. **Look-test + iterate** — render one representative scene, inspect it, and only then proceed.
3. **Background full render** — generate all frames/images in a background task, not in the foreground turn.
4. **Master + QC audit** — stitch the master video, then build a contact sheet and per-scene frame-difference checks to verify expected motion and catch regressions.

### 1. Cheap layout pass
Before rendering, validate that titles and body text fit inside the target frame width for the chosen font/size. Reject or shorten text that overflows rather than rendering bad frames.

### 2. Look-test + iterate
Render a single representative scene, then inspect it with a vision tool. Iterate on palette, spacing, and typography before committing to the full render.

### 3. Background full render
Render every scene/frame in a `terminal(background=true)` run with `notify_on_complete=true`. Keep the render script idempotent so retries do not corrupt prior outputs.

### 4. Master + QC audit
- **Master**: encode to MP4 with `cv2.VideoWriter` or `ffmpeg`. Avoid giant stitched master PNGs; they can OOM.
- **Contact sheet**: sample frames at 35/65/90% of each scene and build a compact grid; label each sample with its scene name.
- **Frame diffs**: per scene, compare first→mid and mid→last frames with `cv2.absdiff` and save them as labeled QC images. These make motion regressions obvious.

## Render Paths

### Direct render path (Python/PIL/OpenCV/FFmpeg)
Use this when the scene graph is simpler than Hyperframes, or when you need deterministic zero-from-scratch frames.
- Frames: `PIL.Image.new` + `ImageDraw` for text and rounded rectangles; `numpy` for analytical masks such as scanlines; `cv2` only for frame I/O, diffs, and final MP4.
- QC: `cv2.absdiff(frame_A, frame_B)` for per-scene motion checks; build a contact-sheet PNG with `PIL`.
- Audio: after the silent MP4 is ready, mix narration with `ffmpeg` using `amix`/`amerge` or `aformat`/`acopy`.

### Hyperframes composition path
Use this when the design needs richer motion, timing blocks, or web-controllable preview.
- Initialize: `npx hyperframes init <project> --non-interactive --example blank`
- Compose: create `compositions/` with per-composition `data-width`, `data-height`, `data-composition-id`, and `window.__timelines` registration.
- Avoid: external Google Fonts links, overlapping clips on the same track without layering, missing timeline roots.
- Verify: `npx hyperframes info .` confirms the composition root.
- Render: `npx hyperframes render . --audio /path/to/narration.wav --output output.mp4`
- Note: Hyperframes audio must be WAV/MP3. Ensure narration track length matches the composition timeline; trim/silence padding with FFmpeg beforehand if needed.

## Narration strategy
Preferred voice order:
1. `fishaudio` provider, Japanese female voice if available
2. `irodori` provider, `voice=hakua` for Hakua-style speech
3. `voicevox` speaker `3` as a fallback

If TTS generation fails with a credit/quota error, surface the failure explicitly and offer narration omission rather than silently retrying. Do not silently switch providers without operator confirmation.

### Local Irodori CPU narration
When FishStudio is unavailable, local Irodori-TTS is the expected fallback for Hakua voice.
- Start server from its repo: `IRODORI_TTS_BACKEND=cpu .venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088`
- Configure Hermes to talk to it via `tts.provider: irodori`, `tts.irodori.base_url: http://127.0.0.1:8088`, `tts.irodori.voice: hakua`
- Windows gotcha: MSYS `cd` needs quoted paths with spaces; `curl --data-binary @file` needs forward-slash or backslash-quoted absolute paths.
- Live HTTP synthesis may succeed server-side but still reset the client connection on Windows. If you get `ConnectionResetError` on a clean request after a successful server log, treat it as a known unstable path and reuse a local WAV or split into shorter requests instead of blind retry. Observed pattern: short test synthesis can succeed, then longer synthesis hits `curl: (28)` timeout around 180s, followed by connection refusal on next probe.
- Provider routing note: calling `text_to_speech` may still route through `fishaudio` even when local irodori is running. Verify `tts.provider: irodori` in Hermes config before relying on the built-in TTS tool. Observed pattern: short test synthesis can succeed, then longer synthesis hits `curl: (28)` timeout around 180s, followed by connection refusal on next probe.
- Provider routing note: calling `text_to_speech` may still route through `fishaudio` even when local irodori is running. Verify `tts.provider: irodori` in Hermes config before relying on the built-in TTS tool.
- Windows server lifetime: after a successful synthesis the irodori process can exit; do not assume port 8088 stays up across retries. Restart the server and re-probe `GET /health` before each new synthesis.
- Windows direct HTTP gotcha: `curl --data-binary @C:/path/file.json` often fails with `Recv failure` or `Connection was reset`; prefer `python -m urllib.request` with explicit `ensure_ascii=False` JSON body from a known-good UTF-8 file.
- Windows path quoting: do not use MSYS-style unquoted paths with spaces; wrap the whole path in double quotes or use `--data-binary @"C:/Users/.../file.json"`.

## Step-by-step playbook

1. **Script**
   - Write the narration script first.
   - Keep spoken lines under provider caps; note provider-specific caps from config.
   - Use Japanese for Hakua delivery; English-only only if explicitly requested.

2. **Scene design**
   - Title / split compare / feature cards / takeaway.
   - Dark baseline: `BG = (11, 12, 16)`; card: `(20, 22, 28)`; borders: `(42, 45, 53)`.
   - Accent colors: official = `(255, 123, 114)`, fork = `(126, 231, 135)`.

3. **Look-test**
   - Render one scene.
   - Review alignment, cut-off text, palette, and typography.
   - Iterate before full render.

4. **Full render**
   - Background render all frames/images.
   - Encode master MP4.
   - Build QC contact sheet + per-scene frame diffs.

5. **Audio mix**
   - Mix narration with the silent master using FFmpeg.
   - Re-verify duration and audio track presence.

6. **Deliver**
   - Deliver the MP4 path, QC sheet path, frame-diff paths, and narration path if present.
   - State FFprobe-verified playback info: resolution, fps, duration, bitrate.

## Pitfalls
- **Black/blank frames**: missing composition roots in Hyperframes; overlapping clips on the same track; forgetting timeline `window.__timelines` registration.
- **Audio provider failures**: FishAudio can return 402 quota errors; surface them and offer Narration omission or fallback provider rather than blind retry.
- **OOM on master PNG**: do not build one giant master PNG from all frames; use MP4 + QC contact sheet instead.
- **Black frame after audio mix**: ensure FFmpeg audio stream matches the video length; add `-shortest` or explicit padding to avoid truncation.
- **Lint errors**: always run `npx hyperframes lint` or equivalent before render when using Hyperframes.

## Example files
- `references/compare-video-qc-notes.md` — example QC interpretation and contact-sheet layout.
- `references/windows-irodori-cpu-notes.md` — Windows-specific local Irodori-TTS failure modes, reproducer, and FFmpeg audio mix recipe.

## Notes
- Prefer concise delivery: MP4 path, QC sheet path, quick verdict. Only expand if the operator asks for details.
- If FishAudio/narration is unavailable, the video without audio is still a valid deliverable; state that explicitly rather than attempting covert fallback provider changes.
- For X posting after video production, use the live posting reference under `references/lm-twitterer-live-posting.md`; verify auth first and use `--text` with finalized review-approved copy.

## Shortcuts
- **Still-image + narration shortcut**: for single-photo social posts, skip full scene rendering. Use `ffmpeg -loop 1 -i <png> -i <wav/ogg> -c:v libx264 -tune stillimage -shortest -c:a aac -b:a 192k out.mp4` to create a valid MP4 in one step.
- **lm-twitterer media restriction**: `lm_twitterer_post` only accepts media under `C:\Users\<user>\.hermes\lm-twitterer\media`. Copy or hardlink the final MP4 there before posting.