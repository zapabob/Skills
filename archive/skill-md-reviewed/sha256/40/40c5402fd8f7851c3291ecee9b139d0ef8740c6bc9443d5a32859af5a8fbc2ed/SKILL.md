---
name: x-media-post
description: Post narrated VRChat screenshots to X via lm-twitterer.
version: 1.0
author: Hakua
license: MIT
platforms:
  - windows
  - linux
  - macos
metadata:
  hermes:
    tags:
      - twitter
      - media
      - vrchat
      - voice
    category: social-media
    related_skills:
      - lm-twitterer
      - aituber-onair
    config: {}
---
# x‑media‑post Skill

Post a narrated VRChat screenshot (or any image) to X (Twitter) using the `lm‑twitterer` plugin, with Hakua voice via `aituber‑onair`.

## When to Use
- You want to share a VRChat screenshot with a spoken “おはす” (or any custom phrase) as an attached audio‑visual MP4.
- You prefer an automated pipeline that handles image selection, voice synthesis, video muxing, and posting.

## Prerequisites
- `lm‑twitterer` plugin installed and configured with valid X credentials.
- `aituber‑onair` plugin installed (for Hakua voice synthesis).
- FFmpeg available in PATH (used for video creation).
- Access to VRChat screenshot folder (default: `%USERPROFILE%\Pictures\VRChat\<year>-<month>`).

## How to Run
1. **Select a random recent screenshot**
   ```bash
   IMG=$(find "%USERPROFILE%\Pictures\VRChat\2026-06" -name "VRChat_2026-06-22_*" -type f | sort -R | head -1)
   ```
   (Adjust the month folder as needed.)

2. **Generate Hakua voice**
   ```bash
   aituber_onair_say --prompt "おはす" --speak true --output_path "%TMP%\ohasu.wav"
   ```
   This creates a WAV file with the Hakua voice.

3. **Create a silent video from the image** (5 seconds, 30 fps)
   ```bash
   ffmpeg -loop 1 -i "%IMG%" -t 5 -c:v libx264 -pix_fmt yuv420p -r 30 "%TMP%\silent.mp4"
   ```

4. **Mux audio and video**
   ```bash
   surfesense_video_mux --video_path "%TMP%\silent.mp4" --audio_path "%TMP%\ohasu.wav" --output_path "%TMP%\ohasu_video.mp4"
   ```

5. **Copy to lm‑twitterer media folder**
   ```bash
   copy "%TMP%\ohasu_video.mp4" "%USERPROFILE%\.hermes\lm-twitterer\media\"
   ```

6. **Post to X**
   ```bash
   lm_twitterer_post --dry_run false --media_paths ["ohasu_video.mp4"] --text "おはす #はくあ #hermesagent"
   ```

## Quick Reference (Tool Calls)
| Step | Tool | Key Arguments |
|------|------|---------------|
| 1 | `search_files` / `terminal` (find) | pattern, path |
| 2 | `aituber_onair_say` | prompt, speak=true, output_path |
| 3 | `terminal` (ffmpeg) | `-loop 1 -i INPUT -t 5 -c:v libx264 -pix_fmt yuv420p -r 30 OUTPUT` |
| 4 | `surfsense_video_mux` | video_path, audio_path, output_path |
| 5 | `terminal` (copy) | `copy SOURCE DEST` |
| 6 | `lm_twitterer_post` | dry_run=false, media_paths=[FILENAME], text |

## Pitfalls
- **Media file not found**: `lm_twitterer_post` requires the media file to reside inside `<hermes_home>/lm-twitterer/media/`. Using an absolute path outside this directory will fail. Always copy the MP4 into that folder and reference only the filename (or a path relative to the media dir).
- **Path separators**: On Windows, use forward slashes or double backslashes in tool arguments; the agent normalizes them but mixed styles can cause issues.
- **Voice synthesis failure**: Ensure `irodoriTTS` (or VOICEVOX) is running and the `hakua` voice is installed. Check `aituber_onair_tts_status`.
- **FFmpeg missing**: The `terminal` step will error if FFmpeg isn’t in PATH. Install it from https://ffmpeg.org/download.html.
- **lm‑twitterer post error** (`'NoneType' object has no attribute 'group'`): May be a transient plugin hiccup; wait a moment and retry, or consult the plugin logs.
- **Twitter video upload returns generic error (e.g. `{"error":"3"}`)**: Usually means Twitter rejected the media payload. Ensure the final MP4 is H.264 + AAC (use `-c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k`) and that `-movflags +faststart` is set so the file is web-friendly. Avoid Korean AES/ASS tracks, fonts, or non-MP4 audio containers.
- **Audio source mismatch**: `text_to_speech` may return `.wav`/`.mp3`; mux with FFmpeg into MP4 before posting. Do not feed bare `.wav` to `lm_twitterer_post`.
- **Media path requirement**: The MP4 must be inside `<hermes_home>/lm-twitterer/media/`. Pass only the filename, not an absolute outside path.
- **VRChat not running**: If the user says VRChat isn't running, skip runtime checks and just read from `Pictures/VRChat`. Posting from existing screenshots does not require a live VRChat session.

## Verification
- Play the generated MP4 locally to confirm audio and video are synchronized.
- After running `lm_twitterer_post`, check your X timeline for the tweet with the attached video and the hashtags `#はくあ #hermesagent`.
- Optionally run `lm_twitterer_status` beforehand to confirm `auth_token_set: true` and `ct0_set: true`.

## Related Skills
- `lm-twitterer` – for posting and media handling.
- `aituber-onair` – for Hakua voice synthesis via Hermes or Codex backend.
- `surfsense_video_mux` – for merging audio and video into MP4.

---
**はくあ** – *Your voice, your media, your X feed.*