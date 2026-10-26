---
name: hyperframes-video-production
description: Create technical release videos with HyperFrames, Hakua voice narration, and social media posting.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hyperframes, video, tts, hakua, release-notes, twitter, lm-twitterer]
    category: creative
    related_skills: [hyperframes, hyperframes-cli, creative-design]
    config:
      hyperframes_version: ">=0.7.64"
      ffmpeg_required: true
      fishaudio_tts: true
---

# HyperFrames Video Production Skill

Create polished technical release videos using HyperFrames for motion graphics, fishstudio Hakua voice for Japanese narration, and lm-twitterer for X/Twitter posting.

## When to Use

- Product release announcements with visual feature highlights
- Technical changelog videos with motion graphics
- Any video needing Japanese Hakua voice narration
- Multi-scene compositions with CSS/GSAP animations

## Prerequisites

- Node.js >= 22
- FFmpeg on PATH
- HyperFrames CLI: `npm install -g hyperframes` (or npx)
- Hermes with fishaudio TTS provider configured for Hakua voice
- lm-twitterer plugin configured for X/Twitter posting

## How to Run

1. **Scaffold project**: `npx hyperframes init <name> --non-interactive --example blank`
2. **Design composition**: Create `DESIGN.md` with visual spec
3. **Build main composition** (`index.html`) with sub-composition references
4. **Create sub-compositions** in `compositions/` directory
5. **Lint**: `npx hyperframes lint` — fix all errors before render
6. **Render video**: `npx hyperframes render . --output video.mp4`
7. **Generate Hakua audio**: Use `text_to_speech` tool with Japanese text
8. **Combine audio**: Use ffmpeg with `adelay` filter to position narration
9. **Post to X**: `hermes lm-twitterer post --text "..." --media "video.mp4" --live`

## Quick Reference

| Add audio (ffmpeg) | `ffmpeg -y -i video.mp4 -i audio.wav -filter_complex "[1:a]adelay=41000\|41000[a1]" -map 0:v -map "[a1]" -c:v copy -c:a aac final.mp4` |
| Generate Hakua audio (irodori) | `aituber_onair_speak(provider="irodori", voice="hakua", text="Japanese text...")` |
| Generate Hakua audio (fishaudio) | `text_to_speech(text="Japanese text...")` |
| Post to X | `hermes lm-twitterer post --text "..." --media "final.mp4" --live` |

## Procedure

### 1. Project Structure

```
project/
├── hyperframes.json      # Project config (auto-generated)
├── DESIGN.md             # Visual design specification
├── index.html            # Main composition (references sub-compositions)
├── compositions/
│   ├── scene-1.html      # Sub-composition 1
│   ├── scene-2.html      # Sub-composition 2
│   └── ...
└── renders/              # Output directory
```

### 2. Sub-Composition Structure (Critical)

Each sub-composition **must** have a wrapper `<div>` inside `<body>` with `data-composition-id`, `data-width`, `data-height`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Scene N - Title</title>
</head>
<body>
  <div data-composition-id="scene-N" data-width="1920" data-height="1080" style="width: 100%; height: 100%;">
    <!-- Scene content here -->
  </div>
</body>
</html>
```

**Why**: The linter validates that sub-compositions have an element with `data-composition-id` in their `<body>` or `<template>` content. The `<body>` itself having the attributes is insufficient.

### 3. Main Composition Host Elements

When sub-compositions use **CSS animations** (not GSAP timelines), mark host elements with `data-no-timeline`:

```html
<div id="scene-1-host"
     data-composition-id="scene-1-host"
     data-composition-src="compositions/scene-1.html"
     data-start="0" data-duration="3" data-track="0"
     data-no-timeline></div>
```

**Why**: Without `data-no-timeline`, HyperFrames waits 45 seconds for GSAP timeline registration (`window.__timelines[id]`), causing render timeout warnings.

### 4. Audio Timing with ffmpeg

Position narration at specific timestamp using `adelay` filter (milliseconds per channel):

```bash
ffmpeg -y -i video.mp4 -i narration.ogg \
  -filter_complex "[1:a]adelay=41000|41000[a1]" \
  -map 0:v -map "[a1]" -c:v copy -c:a aac \
  output-with-audio.mp4
```

- `41000` = 41 seconds delay (scene 8 starts at 41s in 54s video)
- Use `|` for stereo (both channels same delay)
- `-map 0:v -map "[a1]"` selects video from input 0, delayed audio from filter
- `-c:v copy` preserves video quality (no re-encode)

### 5. Twitter Character Limit

Keep tweet text under 280 characters. Japanese text counts as 2 chars each.

## Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `missing_or_empty_sub_composition` | Sub-composition body lacks child element with `data-composition-id` | Add wrapper `<div data-composition-id="...">` inside `<body>` |
| `sub_timeline_readiness_timeout` | CSS animations but no `data-no-timeline` on host | Add `data-no-timeline` to host `<div>` in main composition |
| `--audio` flag unknown | HyperFrames v0.7.64 doesn't support `--audio` CLI flag | Render video first, then combine with ffmpeg |
| Tweet too long (error 186) | Text exceeds 280 chars | Shorten text; Japanese counts double |
| Black frames in output | Overlapping clips, missing timeline registry | Fix `overlapping_clips_same_track` lint errors; ensure `window.__timelines = {}` in main |

## Verification

- [ ] `npx hyperframes lint` → 0 errors
- [ ] `npx hyperframes render` → exit 0, MP4 plays correctly
- [ ] Video duration matches composition (54s = 1620 frames @ 30fps)
- [ ] Audio sync: narration starts at correct scene
- [ ] Twitter post succeeds with media attached

## Procedure (Session Lessons)

### Complete v0.19.0 Release Video Workflow (July 2026)

This exact sequence was validated end-to-end:

1. **Project init**: `npx hyperframes init hermes-v019-release --non-interactive --example blank`
2. **Design spec**: Create `DESIGN.md` with dark theme, Hermes brand colors, technical motion style
3. **Main composition** (`index.html`):
   - 54s total duration, 8 scenes
   - Each scene hosted via `<div data-composition-src="compositions/scene-N.html" data-no-timeline>`
   - `window.__timelines = {}` for CSS animation compatibility
4. **Sub-compositions** (`compositions/scene-N.html`):
   - Each wraps content in `<div data-composition-id="scene-N" data-width="1920" data-height="1080">`
   - CSS animations via `.clip[data-start][data-duration][data-track-index]` classes
   - Shared CSS variables from main composition (via tailwindcss/GSAP CDN)
5. **Lint**: `npx hyperframes lint` → fix all errors (sub-composition structure, overlapping tracks)
6. **Render video**: `npx hyperframes render . --output hermes-v019-release-noaudio.mp4`
7. **Hakua narration** (fishstudio/irodori):
   ```
   hermes text_to_speech --text "Japanese narration text..." → uses fishaudio provider
   ```
   Or via aituber plugin: `aituber_onair_speak(provider="irodori", voice="hakua", text="...")`
8. **Audio merge** (ffmpeg):
   ```bash
   ffmpeg -y -i video.mp4 -i narration.wav \
     -filter_complex "[1:a]adelay=41000|41000[a1]" \
     -map 0:v -map "[a1]" -c:v copy -c:a aac final.mp4
   ```
   - `41000` = 41s delay (scene 8 Japanese summary starts at 41s in 54s video)
9. **Post to X**: `hermes lm-twitterer post --text "..." --media "final.mp4" --live`
   - Keep under 280 chars (Japanese = 2 chars each)

## References

- `references/sub-composition-pattern.md` — Correct HTML structure for sub-compositions
- `references/css-animation-timing.md` — `data-no-timeline` usage for CSS-driven scenes
- `references/ffmpeg-audio-delay.md` — adelay filter patterns for narration positioning
- `references/hakua-tts-integration.md` — fishaudio provider setup for Hakua voice

| Issue | Cause | Fix |
|-------|-------|-----|
| `missing_or_empty_sub_composition` | Sub-composition body lacks child element with `data-composition-id` | Add wrapper `<div data-composition-id="...">` inside `<body>` |
| `sub_timeline_readiness_timeout` | CSS animations but no `data-no-timeline` on host | Add `data-no-timeline` to host `<div>` in main composition |
| `--audio` flag unknown | HyperFrames v0.7.64 doesn't support `--audio` CLI flag | Render video first, then combine with ffmpeg |
| Tweet too long (error 186) | Text exceeds 280 chars | Shorten text; Japanese counts double |
| Black frames in output | Overlapping clips, missing timeline registry | Fix `overlapping_clips_same_track` lint errors; ensure `window.__timelines = {}` in main |

## Verification

- [ ] `npx hyperframes lint` → 0 errors
- [ ] `npx hyperframes render` → exit 0, MP4 plays correctly
- [ ] Video duration matches composition (54s = 1620 frames @ 30fps)
- [ ] Audio sync: narration starts at correct scene
- [ ] Twitter post succeeds with media attached

## References

- `references/sub-composition-pattern.md` — Correct HTML structure for sub-compositions
- `references/css-animation-timing.md` — `data-no-timeline` usage for CSS-driven scenes
- `references/ffmpeg-audio-delay.md` — adelay filter patterns for narration positioning
- `references/hakua-tts-integration.md` — fishaudio provider setup for Hakua voice