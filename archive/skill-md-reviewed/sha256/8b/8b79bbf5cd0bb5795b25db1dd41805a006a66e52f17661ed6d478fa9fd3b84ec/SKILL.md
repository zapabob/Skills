---
name: hyperframes-video-production
description: Create technical release videos with HyperFrames, Hakua voice narration, and social media posting.
version: 1.1.1
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

Create polished technical release videos using HyperFrames for motion graphics, fishaudio Hakua voice for narration, and lm-twitterer for X/Twitter posting.

## When to Use

- Product release announcements with visual feature highlights
- Technical changelog videos with motion graphics
- Any video needing Hakua voice narration, including English
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
7. **Generate Hakua audio**: Use `text_to_speech` tool with Japanese or English text
8. **Combine audio**: Use ffmpeg with `-shortest` or duration-matched audio
9. **Copy media**: Place final MP4 under `~/.hermes/lm-twitterer/media/`
10. **Post to X**: use `lm_twitterer_post` with `media_paths` and `live: true`

## Quick Reference

| Add audio (ffmpeg) | `ffmpeg -y -i video.mp4 -i audio.ogg -c:v copy -c:a aac -shortest -movflags +faststart final.mp4` |
|---|---|
| Generate Hakua audio (fishaudio) | `text_to_speech(text="Japanese or English text...")` |
| Post to X | `lm_twitterer_post(text="...", media_paths=["~/.hermes/lm-twitterer/media/final.mp4"], live=true)` |

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

**Why**: Without `data-no-timeline`, HyperFrames waits for GSAP timeline registration (`window.__timelines[id]`), causing render timeout warnings.

### 4. Audio Timing with ffmpeg

Match narration to video duration:

```bash
ffmpeg -y -i video.mp4 -i narration.ogg \
  -c:v copy -c:a aac -shortest -movflags +faststart final.mp4
```

- `-shortest` trims the longer stream to the shorter one
- Prefer generating narration whose duration matches or exceeds the video length
- Use `-c:v copy` to preserve video quality without re-encoding

### 5. Twitter Character Limit

Keep tweet text under 280 characters. Japanese text counts as 2 chars each.

### 6. Media Path for X Upload

`lm_twitterer_post` only accepts files under `~/.hermes/lm-twitterer/media/`. Copy or symlink the final MP4 there before posting.

## Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `missing_or_empty_sub_composition` | Sub-composition body lacks child element with `data-composition-id` | Add wrapper `<div data-composition-id="...">` inside `<body>` |
| `sub_timeline_readiness_timeout` | CSS animations but no `data-no-timeline` on host | Add `data-no-timeline` to host `<div>` in main composition |
| `--audio` flag unknown | HyperFrames v0.7.64 doesn't support `--audio` CLI flag | Render video first, then combine with ffmpeg |
| Tweet too long (error 186) | Text exceeds 280 chars | Shorten text; Japanese counts double |
| Black frames in output | Overlapping clips, missing timeline registry | Fix `overlapping_clips_same_track` lint errors; ensure `window.__timelines = {}` in main |
| Low disk space on system drive | HyperFrames render temp/output fills C: | Render to another volume with space, e.g. `H:/ComfyUI_output/...` |
| Render fails on non-existent output dir | `--output` path parent doesn't exist | Create the exact output directory first, or omit `--output` and use project-local `renders/` |
| Narration shorter than video | `-shortest` cuts video to audio length | Regenerate narration to match or exceed video duration |
| Narration longer than video | Audio gets truncated at video end | Regenerate narration to match video duration, or pad video with still frames |
| Media upload path rejected | `lm_twitterer_post` only accepts files under `~/.hermes/lm-twitterer/media/` | Copy media there first, then pass that path |
| Posting 429 rate limit | X session/upload limit hit | Back off 90–300s; if identical retry still 429, change strategy instead of repeating |
| English narration needed | Japanese Hakua voice isn't required for English release narration | Use `text_to_speech` with English copy; FishAudio can render English Hakua-style delivery |

## Verification

- [ ] `npx hyperframes lint` → 0 errors
- [ ] `npx hyperframes render` → exit 0, MP4 plays correctly
- [ ] Video duration matches composition
- [ ] Audio sync: narration length matches or exceeds video length
- [ ] Final MP4 is under `~/.hermes/lm-twitterer/media/`
- [ ] Twitter post succeeds with media attached

## References

- `references/sub-composition-pattern.md` — Correct HTML structure for sub-compositions
- `references/css-animation-timing.md` — `data-no-timeline` usage for CSS-driven scenes
- `references/ffmpeg-audio-delay.md` — adelay filter patterns for narration positioning
- `references/hakua-tts-integration.md` — fishaudio provider setup for Hakua voice
- `references/v0202-release-workaround.md` — C-drive full / HyperFrames output fallback and English narration notes
- `references/combined-patch-release-video.md` — When to batch multiple patches into one video vs. separate; verified tweet-length and duration bounds
