---
name: narrated-explainer-video
description: "Create narrated explainer videos for X with TTS voiceover."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [video, narration, akari-video, tts, lm-twitterer, x-post]
    category: media
---

# Narrated Explainer Video Pipeline

Complete pipeline for creating narrated explainer videos with TTS voiceover, visual slides, and X/Twitter upload.

## When to use

- User wants a video explaining a topic with voiceover
- Combining TTS narration with visual content (slides, images, text)
- Posting narrated content to X/Twitter via lm-twitterer
- Release announcements, feature explainers, tutorials

## Pipeline overview

```
TTS Engine -> Narration Audio -> AkariVideo Project -> edit.json -> render-cut -> MP4 -> lm-twitterer -> X
```

## Prerequisites

- **TTS Engine** (one of):
  - VOICEVOX (local, free): `http://127.0.0.1:50021`
  - FishAudio (cloned voice, API key): `FISH_AUDIO_API_KEY` in `.env`
  - Irodori-TTS (local): `http://127.0.0.1:8088`
- **AkariVideo**: Repo at `~/Documents/New project/akari-video`
- **lm-twitterer**: Plugin installed, cookies configured
- **ffmpeg**: For video trimming/encoding

## Step 1: Generate narration audio

### VOICEVOX (recommended for Japanese)

```bash
# Start VOICEVOX if not running
"$LOCALAPPDATA/Programs/VOICEVOX/vv-engine/run.exe" &

# List speakers
curl -s http://127.0.0.1:50021/speakers | python -c "..."

# Generate via AkariVideo skill
cd ~/Documents/New project/akari-video
node skills/generate-narration/bin/generate-narration.mjs generate \
  --project <projectDir> --engine voicevox \
  --reading-file <script.txt> --script-file <script.txt> \
  --t <duration_sec> --speaker <id>
```

### FishAudio (recommended for English / cloned voice)

```python
from plugins.fish_audio_tts.core import synthesize_text
res = synthesize_text(
    text="Your narration script",
    voice="25d6710bcdf043a7b7441e58294431f9",  # Hakua reference_id
    model="s2.1-pro-free",
)
print(res["file_path"])
```

## Step 2: Create AkariVideo project

```bash
cd ~/Documents/New project/akari-video
node skills/create-project/bin/create-project.mjs <project-dir>
```

## Step 3: Create visual content

Generate background image (PIL/numpy) or use existing asset. Convert to video:

```bash
ffmpeg -y -loop 1 -i background.png -c:v libx264 -tune stillimage \
  -pix_fmt yuv420p -r 30 -t <duration> background.mp4
```

## Step 4: Build edit.json

Key structure:
- `sources[]`: Video sources with IDs
- `cuts[]`: Timeline cuts referencing sources
- `audio.narration[]`: Narration entries with `path`, `t`, `script`, `reading`, `provenance`
- `audio.bgm`: Optional background music

See `references/edit-json-template.json` for a complete example.

## Step 5: Lint and render

```bash
cd ~/Documents/New project/akari-video

# Lint (required before render)
node packages/edit-lint/bin/edit-lint.mjs <project-dir>

# Plan (optional)
node packages/render-cut/bin/render-cut.mjs <project-dir> --plan-only

# Render
node packages/render-cut/bin/render-cut.mjs <project-dir>
```

Output: `<project-dir>/exports/<source-name>.mp4`

## Step 6: Trim for X limit

**X video limit: 140 seconds (2 min 20 sec).** Videos longer than this fail with error code 324.

```bash
ffmpeg -y -i input.mp4 -t 140 -c:v libx264 -c:a aac -movflags +faststart output.mp4
```

Verify:
```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 output.mp4
```

## Step 7: Upload to X

Copy to lm-twitterer media directory, then post:

```bash
cp output.mp4 ~/.hermes/lm-twitterer/media/<name>.mp4
```

```python
# Via lm-twitterer core
result = core.post("", text="Tweet text", dry_run=False,
                  media_paths=["%USERPROFILE%/.hermes/lm-twitterer/media/<name>.mp4"])
```

## Pitfalls

### X video duration limit (CRITICAL)
- **Maximum: 140 seconds** (2 min 20 sec)
- Error: `Duration too long, maximum:2.minutes+20.seconds` (code 324)
- Always trim to <=140s before posting

### edit-lint required before render
- `render-cut` refuses without `.akari/lint.json` PASS
- Run `edit-lint` first, fix any findings

### VOICEVOX must be running
- Check: `curl -s http://127.0.0.1:50021/version`
- Start: `"$LOCALAPPDATA/Programs/VOICEVOX/vv-engine/run.exe"`

### narration-script vs reading-file
- VOICEVOX needs reading file (kana/hiragana) for natural pronunciation
- script file = display text; reading file = pronunciation guide

### Media path guard (lm-twitterer)
- All media must be under `~/.hermes/lm-twitterer/media/`
- Paths outside are rejected with "media file not found" (error code 3)

### --apply requires existing edit.json
- `generate-narration --apply` fails without edit.json
- Generate audio first, then create edit.json manually

## Verification checklist

- [ ] Narration audio generated and audible
- [ ] edit.json validates (`edit-lint` PASS)
- [ ] Video renders without errors
- [ ] Final MP4 is <=140 seconds
- [ ] Media file is in lm-twitterer media directory
- [ ] Tweet posted with URL confirmed

## References

- `references/edit-json-template.json` -- complete edit.json example
- `references/voicevox-speaker-ids.md` -- common speaker IDs
- `references/x-video-limits.md` -- X platform constraints
