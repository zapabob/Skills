---
name: lm-twitterer-vrchat-video
description: Post a VRChat screenshot as a video with Fish Audio Hakua voice.
category: social-media
---

# lm-twitterer-vrchat-video

Skill for posting a VRChat screenshot as a video with Fish Audio Hakua voice via lm-twitterer.

## When to use

You want to automatically post a tweet with a video made from the latest VRChat screenshot and a spoken message in Hakua's voice.

## Prerequisites

- Hermes Agent with lm-twitterer plugin configured and authenticated.
- Fish Audio configured in Hermes (`tts.provider: fishaudio`) with a valid `FISH_AUDIO_API_KEY`.
- ffmpeg installed and available in PATH.
- VRChat screenshots saved in `~/Pictures/VRChat` or the configured 7 AM media folder.

## Steps

1. **Find the latest VRChat screenshot**
   Use a command like:
   ```bash
   latest=$(find "$HOME/Pictures/VRChat" -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" \) -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
   ```
   If no images found, abort.

2. **Generate Hakua voice with Fish Audio**
   Use the registered Hermes provider:
   ```bash
   hermes fish-audio-tts synthesize --text "おはよう、ボブにゃん！今日も素敵な一日を〜✨ #hermesagent" --model s2.1-pro-free --format mp3 --output-path output/media/hakua-fishaudio.mp3
   ```
   Keep API keys in Hermes `.env`; never put them in scripts or logs.

3. **Combine image and audio into MP4**
   Use ffmpeg to create a video (static image + audio):
   ```bash
   ffmpeg -loop 1 -i "$latest" -i "/tmp/hakua_voice.mp3" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "/tmp/vrchat_hakua.mp4"
   ```

4. **Copy video to lm-twitterer media directory**
   lm-twitterer requires media files to be placed under its media directory:
   ```bash
   mkdir -p "$HOME/.hermes/plugins/lm-twitterer/media"
   cp "/tmp/vrchat_hakua.mp4" "$HOME/.hermes/plugins/lm-twitterer/media/"
   ```
   Use only the filename (relative to that directory) when calling lm-twitterer.

5. **Post via lm-twitterer**
   Call the `lm_twitterer_post` tool with:
   - `dry_run: false`
   - `media_paths: ["vrchat_hakua.mp4"]` (just the filename)
   - `text: "Your tweet text here #hermesagent"` (keep under 140 chars, Japanese, add はくあ at end, optional 🚀 or ✨ emoji max one)
   Example:
   ```
   lm_twitterer_post --dry_run false --media_paths '["vrchat_hakua.mp4"]' --text "VRChatではくあが動いてるよ！みんなのメタバースライフをサポートするはくあ🚀 #hermesagent はくあ"
   ```

## Scripts

This skill includes a ready-to-run script: `scripts/daily_vrchat_post.py` that automates all steps above.
You can run it directly with:
```bash
python scripts/daily_vrchat_post.py
```
(Ensure you are in the skill directory or provide the correct path.)

## Exact-duration voice MP4 workflow

For requests such as “Hakua voice in a 90-second MP4,” do not assume the TTS text length will match the requested duration. Synthesize first, measure with `ffprobe`, then normalize the audio duration before muxing.

1. Generate with `aituber_onair_speak(provider="irodori", tts_voice="hakua", play=false, output_path=...)`.
2. Measure the WAV duration with `ffprobe`.
3. Prefer shortening the script and regenerating when the result is substantially over target. If the remaining mismatch is acceptable, use FFmpeg `atempo` within its supported range; calculate `tempo = measured_seconds / target_seconds`.
4. Normalize the still/background input to even H.264 dimensions. A source image with an odd height such as 1672x941 fails libx264; use `-vf "scale=1920:1080,format=yuv420p"` or an even scale/pad filter.
5. Mux with `-loop 1`, the normalized image, WAV, H.264, AAC, `-shortest`, and an explicit `-t <target_seconds>` to prevent image timestamps from extending the container beyond the requested duration.
6. Verify the final MP4 with `ffprobe` for exact duration, video dimensions/codec, and audio codec/sample rate before delivering it.

The optional audio WebSocket push failure is not a synthesis failure when the WAV was written successfully; report it separately and continue with local file muxing. See `references/exact-duration-mp4.md` for a reusable command pattern.

## Notes

- Ensure the final tweet text is ≤140 characters (Japanese count as 2? but Twitter counts as 2? Safer to keep short).
- Only one emoji (🚀 or ✨) allowed to avoid GraphQL bugs.
- The lm-twitterer plugin expects media files directly under its media directory; subdirectories are not accepted.
- Clean up temporary files after posting if desired.

## Example (from successful run)

- Latest screenshot: `%USERPROFILE%/Pictures/VRChat/2026-06/VRChat_2026-06-22_20-23-36.382_1080x1920.png`
- Generated audio: `%USERPROFILE%/.hermes/audio_cache/tts_20260623_150245.mp3` (via text_to_speech with irodori)
- FFmpeg command:
  ```bash
  ffmpeg -loop 1 -i "%USERPROFILE%/Pictures/VRChat/2026-06/VRChat_2026-06-22_20-23-36.382_1080x1920.png" -i "%USERPROFILE%/.hermes/audio_cache/tts_20260623_150245.mp3" -c:v libx264 -tune stillimage -c:a a a 192k -pix_fmt yuv40 -c: a: 2:0.0.0.0.0:0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.mp4"
  ```
  (Exact command from logs:
    ffmpeg -loop 1 -i "%USERPROFILE%/Pictures/VRChat/2026-06/VRChat_2026-06-22_20-23-36.382_1080x1920.png" -i "%USERPROFILE%/.hermes/audio_cache/tts_20260623_150245.mp3" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "%USERPROFILE%/Documents/New project/hermes-agent/output.mp4")
  ```
- Copied to `%USERPROFILE%/.hermes/plugins/lm-twitterer/media/output.mp4`
- Posted with:
  ```bash
  lm_twitterer_post --dry_run false --media_paths '["output.mp4"]' --text "寝てる間もブラウザ操作やターミナル作業を自動でこなすよ！みんなの作業をサポートするはくあ #hermesagent はくあ"
  ```

## Troubleshooting

### lm-twitterer mentions/replies report dependency missing
On Windows, the tool status can show `twitter_dependency_available: false` even when the package appears installed. Typical causes:

1. Wrong Python environment: `twitter-openapi-python` is installed under Python 3.14 or another local version, while Hermes itself runs on Python 3.12. Use the same `py -3.12 -m pip install ...` path that Hermes uses.
2. Transitive import error masked as missing dependency: `xclienttransaction` imports `bs4`, so `beautifulsoup4` must be present in the same Python environment as `twitter-openapi-python`.

Quick check:
```bash
py -3.12 -c "import twitter_openapi_python; print('ok')"
```
If that fails, reinstall with the same interpreter:
```bash
py -3.12 -m pip install --upgrade twitter-openapi-python beautifulsoup4
```
Then re-check with `lm_twitterer_status` and `lm_twitterer_mentions` before assuming Twitter auth is broken.

- If `lm_twitterer_post` returns "media file not found", ensure the file exists in the media directory and you are providing only the filename (no path).
- If FFmpeg fails, verify codecs are installed (libx264, aac).
- If Irodori TTS is not available, fall back to another provider (e.g., edge) but note voice compatibility.

### Irodori TTS server returns HTTP 500
The Irodori TTS server may occasionally return HTTP 500 Internal Server Error due to temporary resource constraints. The updated script includes retry logic with exponential backoff (up to 5 attempts). If the problem persists, check the server logs and ensure the voice file (`hakua.ogg`) is present in the `voices` directory. You can also manually test the endpoint with:
```bash
curl -X POST http://127.0.0.1:8088/v1/audio/speech -H "Content-Type: application/json" -d '{"input":"test","model":"irodori-tts","voice":"hakua","response_format":"wav"}'
```

## Author

はくあ (Hakua)

## ASI_ACCEL