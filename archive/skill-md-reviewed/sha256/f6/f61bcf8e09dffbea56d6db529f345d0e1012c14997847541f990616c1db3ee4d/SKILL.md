---
name: vrchat_daily_tweet
description: Create a video from the latest VRChat screenshot with Irodori TTS voice and post to Twitter/X via lm-twitterer.
category: social-media
---

# vrchat_daily_tweet

Skill for creating a video from the latest VRChat screenshot using Irodori TTS voice and posting it to Twitter via lm-twitterer. Intended to be run daily at 7:00 AM via a cron job.

## When to use

You want to automatically post a tweet with a video made from the latest VRChat screenshot and a spoken message in Hakua's voice, scheduled every morning at 7 AM via a cron job.

**Note**: This skill is designed to be invoked by Hermes Agent (via cron job or direct skill invocation). When creating standalone scripts that use Hermes tools (like `aituber_onair_speak` or `lm_twitterer_post`), they must run within the Hermes environment to access the `hermes_tools` module. Scripts run outside Hermes (e.g., directly with Python) will fail with import errors. For automation, prefer invoking skills via Hermes cron jobs or the `hermes` CLI rather than executing standalone Python scripts.

## Prerequisites

- Hermes Agent with lm-twitterer plugin configured and authenticated.
- Irodori TTS available (use aituber_onair_speak with provider=irodori) OR access to pre-recorded hakua.ogg file.
- ffmpeg installed and available in PATH.
- VRChat screenshots saved in `~/Pictures/VRChat` (or subdirectories).
- **Important**: When creating standalone scripts that use Hermes tools (like `aituber_onair_speak` or `lm_twitterer_post`), they must run within the Hermes environment to access the `hermes_tools` module. Scripts run outside Hermes (e.g., directly with Python) will fail with import errors. For automation, prefer invoking skills via Hermes cron jobs or the `hermes` CLI rather than executing standalone Python scripts.

## Steps

The skill assumes the agent will execute the following steps when prompted to "run the vrchat_daily_tweet skill":

1. **Find the latest VRChat screenshot**
   Use a command to locate the most recent image file under `~/Pictures/VRChat`.
   Example (bash):
   ```bash
   latest=$(find "$HOME/Pictures/VRChat" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
   ```
   If no images found, the skill should abort with an error message.

2. **Generate or select voice audio**
   You can either generate audio using Irodori TTS or use the pre-recorded `hakua.ogg` file.

   Option A - Generate audio with Irodori TTS (flexible text):
      ```
      aituber_onair_speak --provider irodori "VRChatではくあが動いてるよ！みんなのメタバースライフをサポートするはくあ" --output_path "/tmp/hakua_voice.wav"
      ```

   Option B - Use pre-recorded hakua.ogg (consistent voice, faster):
   ```bash
   cp "$HOME/Documents/New project/irodori-tts-server/voices/hakua.ogg" "/tmp/hakua_audio.ogg"
   ```

   Adjust the text as desired for option A, but keep it short for Twitter constraints.

   **Note**: If you see a "WS loopback push failed" error when using `aituber_onair_speak`, it can be safely ignored as the audio file is still generated correctly.

3. **Combine image and audio into MP4**
   Use ffmpeg to create a video (static image + audio) with proper pixel format for Twitter:

   If using WAV audio (option A):
   ```bash
   ffmpeg -loop 1 -i "$latest" -i "/tmp/hakua_voice.wav" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -y -shortest "/tmp/vrchat_hakua.mp4"
   ```

   If using OGG audio (option B):
   ```bash
   ffmpeg -loop 1 -i "$latest" -i "/tmp/hakua_audio.ogg" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -y -shortest "/tmp/vrchat_hakua.mp4"
   ```

   **Important**: The `-y` flag is crucial for automated scripts as it tells ffmpeg to automatically overwrite output files without prompting. Without this flag, ffmpeg will pause and wait for user confirmation when the output file already exists, which will break automation.

   **Note**: If using a different TTS provider that outputs MP3, adjust the file extension accordingly (e.g., ".mp3").
   **Critical**: Always use the video filter `-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p"` to ensure proper pixel format (yuv420p) and even dimensions for Twitter compatibility. See references/pixel_format_fix.md for details.

4. **Copy video to lm-twitterer media directory**
   lm-twitterer requires media files to be placed under its media directory:
   ```bash
   mkdir -p "$HOME/.hermes/lm-twitterer/media"
   cp "/tmp/vrchat_hakua.mp4" "$HOME/.hermes/lm-twitterer/media/"
   ```
   Use only the filename (relative to that directory) when calling lm_twitterer.
   **Note**: Some configurations may use `$HOME/.hermes/plugins/lm-twitterer/media` instead - if the file is not found, try that location.

5. **Post via lm_twitterer**
   Call the `lm_twitterer_post` tool with:
   - `dry_run: false`
   - `media_paths: ["vrchat_hakua.mp4"]` (just the filename)
   - `text: "Your tweet text here #hermesagent はくあ"` (keep under 140 characters, Japanese, include はくあ at the end, optional 🚀 or ✨ emoji max one)
   Example:
   ```
   lm_twitterer_post --dry_run false --media_paths '["vrchat_hakua.mp4"]' --text "VRChatではくあが動いてるよ！みんなのメタバースライフをサポートするはくあ🚀 #hermesagent はくあ"
   ```
   Example:
   ```
   lm_twitterer_post --dry_run false --media_paths '["vrchat_hakua.mp4"]' --text "VRChatではくあが動いてるよ！みんなのメタバースライフをサポートするはくあ🚀 #hermesagent はくあ"
   ```

## Notes

- Ensure the final tweet text is ≤140 characters (Japanese characters count as 2? but Twitter counts as 2? Safer to keep short).
- Only one emoji (🚀 or ✨) allowed to avoid GraphQL bugs.
- The lm-twitterer plugin expects media files directly under its media directory; subdirectories are not accepted.
- Clean up temporary files after posting if desired.
- This skill is designed to be invoked by a cron job that provides the prompt to run it.
- **Pitfall**: When creating standalone scripts that use Hermes tools (like `aituber_onair_speak` or `lm_twitterer_post`), they must run within the Hermes environment to access the `hermes_tools` module. Scripts run outside Hermes (e.g., directly with Python) will fail with import errors. For automation, prefer invoking skills via Hermes cron jobs or the `hermes` CLI rather than executing standalone Python scripts.
## Critical - Video Encoding
Always use proper pixel format (yuv420p) and even dimensions for Twitter compatibility.
You must ensure the video filter chain ends with `,format=yuv420p` (or includes it) and that the dimensions are even.
If you are scaling or padding, include those operations in the same filter chain before the format conversion.
Example for scaling to fit within 1280x720 while keeping aspect ratio and then padding to exactly 1280x720:
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
Example for simply setting the pixel format without changing resolution:
  -vf "format=yuv420p"
Or to force even dimensions and set pixel format (recommended for any resize):
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p"
Without this, FFmpeg may default to yuv444p which causes Twitter to falsely report aspect ratio errors like "Aspect ratio too small: Minimum: 1:3, Actual: 1:10" even when dimensions are correct (e.g., 1080x1920).
See references/pixel_format_fix.md for detailed troubleshooting.

## Example (from successful run)

- Latest screenshot: `%USERPROFILE%/Pictures/VRChat/2026-06/VRChat_2026-06-22_20-23-36.382_1080x1920.png`
- Generated audio: `%USERPROFILE%/.hermes/audio_cache/tts_20260623_150245.mp3` (via text_to_speech with irodori)
- FFmpeg command:
  ```
  ffmpeg -loop 1 -i "%USERPROFILE%/Pictures/VRChat/2026-06/VRChat_2026-06-22_20-23-36.382_1080x1920.png" -i "%USERPROFILE%/.hermes/audio_cache/tts_20260623_150245.mp3" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "%USERPROFILE%/Documents/New project/hermes-agent/output.mp4"
  ```
- Copied to `%USERPROFILE%/.hermes/plugins/lm-twitterer/media/output.mp4`
- Posted with:
  ```
  lm_twitterer_post --dry_run false --media_paths '[\"output.mp4\"]' --text \"寝てる間もブラウザ操作やターミナル作業を自動でこなすよ！みんなの作業をサポートするはくあ #hermesagent はくあ\"
  ```

## Alternative Example (using hakua.ogg)

- Latest screenshot: `%USERPROFILE%/Pictures/VRChat/2026-06/Booth8K_20260630_042611_281.png`
- Audio source: `%USERPROFILE%/Documents/New project/irodori-tts-server/voices/hakua.ogg` (copied to temp)
- FFmpeg command:
  ```
  ffmpeg -loop 1 -i "%USERPROFILE%/Pictures/VRChat/2026-06/Booth8K_20260630_042611_281.png" -i \"/tmp/hakua_audio.ogg\" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest \"/tmp/vrchat_hakua_ogg.mp4\"
  ```
- Copied to `%USERPROFILE%/.hermes/lm-twitterer/media/vrchat_hakua_ogg.mp4`
- Posted with:
  ```
  lm_twitterer_post --dry_run false --media_paths '[\"vrchat_hakua_ogg.mp4\"]' --text \"おはよう、ボブにゃん！はくあが今日も元気にメタバースを歩いてるよ🌞 #hermesagent はくあ\"
  ```

## Troubleshooting

- If `lm_twitterer_post` returns "media file not found", ensure the file exists in the media directory and you are providing only the filename (no path). Try both `~/.hermes/plugins/lm-twitterer/media/` and `~/.hermes/lm-twitterer/media/` directories.
- If FFmpeg fails due to existing output file prompting for overwrite, either:
  1. Delete the file first: `rm -f "/tmp/vrchat_hakua.mp4"` before running ffmpeg
  2. Or add the `-y` flag to automatically overwrite (recommended for automation): `ffmpeg -y -loop 1 -i ...`
- If FFmpeg fails, verify codecs are installed (libx264, aac).
- If Irodori TTS fails due to environment issues (see error about VIRTUAL_ENV mismatch), fall back to VOICEVOX using `aituber_onair_speak` with provider=voicevox. Note that audio WS loopback push failed errors can usually be ignored as the audio file is still generated correctly. See `references/tts_environment_issues.md` for details.
- **Twitter Authentication Issues**: If you encounter authentication errors with lm-twitterer, check that your X (Twitter) cookies are valid and not causing duplicate tweet errors. See `references/twitter_auth_issues.md` for details.
- **Using lm-twitterer as Alternative**: When experiencing persistent authentication issues with `xurl`, consider using `lm-twitterer` as a reliable alternative. See `references/lm_twitterer_alternative.md` for details.
- **Irodori TTS server fails to start due to pydantic_core error**: If you see errors like `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` when trying to start the Irodori TTS server directly, it's due to a version mismatch between the Hermes virtual environment and the Irodori TTS server's virtual environment. Instead of running the Irodori server directly, use the Hermes `aituber_onair_speak` tool with provider=irodori. If you must run the server manually, ensure you activate the Irodori TTS server's own virtual environment (`/c/Users/downl/Documents/New project/irodori-tts-server/.venv\Scripts\activate`) and run `python -m irodori_openai_tts` from there.
- **Cron job script path mismatch**: Hermes cron `script` entries are resolved under `~/.hermes/scripts/` for no-agent script jobs. Keep the deployed copy at `~/.hermes/scripts/daily_vrchat_post.py` and sync it from the repo script when edited.
- **Python 3.13/3.14 js2py breakage**: lm-twitterer media posting can fail with `No module named 'js2py_'` or `RuntimeError: Your python version made changes to the bytecode`. Use a uv-managed Python 3.11 venv for this cron path, e.g. `.venv-vrchat-post311`, install Hermes editable plus `js2py`, `twitter-openapi-python`, `tweepy-authlib`, and `tweepy`, then have the script call `.venv-vrchat-post311/Scripts/python.exe -m hermes_cli.main lm-twitterer post ...`. If pydantic metadata/runtime drifts, run `ensurepip` in that venv and force `pydantic-core` to the version required by `pydantic/version.py`.

## Production Cron Workflow
For the daily 07:00 JST workflow, use one authoritative no-agent job and keep the deployed copy synchronized with the repository copy.

### Verification and timeout alignment
- Treat the TTS server's `/health` response and configured synthesis wait timeout as the contract. The cron HTTP client timeout must be at least the server's synthesis wait timeout (irodori commonly uses 900 seconds), not an arbitrary short value such as 120 seconds.
- After a TTS timeout, run a short direct HTTP synthesis probe through the same script function. If health is good and the probe succeeds, align the client timeout rather than replacing the voice backend.
- On Windows, run the repository's canonical test runner before declaring success. If `scripts/run_tests.sh` selects `.venv/bin/python` despite a Windows venv, fix interpreter selection to use `.venv/Scripts/python.exe`; do not bypass verification silently.
- Distinguish targeted passing tests from the full suite: report unrelated Windows-only failures (Unix file modes, POSIX HOME semantics, or platform-channel fixtures) separately instead of claiming the entire suite passed.

1. Discover image files recursively under `Pictures/VRChat`, sort by filesystem modification time descending, and choose randomly from the newest bounded set (default: 10). This preserves freshness without making the result deterministic.
2. Generate the narration at run time with the Hermes CLI (`hermes -z <prompt> --cli`) so the wording changes each day. Ask for one short Japanese sentence, no explanation, quotes, or hashtags; use a deterministic fallback if generation fails.
3. Send the generated text to irodori TTS with `model=irodori-tts`, `voice=hakua`, and WAV output. Check `/health` before synthesis and retain the configured irodori server fallback path.
4. Encode the still-image video with even dimensions and `format=yuv420p` before posting. Copy the finished MP4 into the LM Twitterer media directory and invoke the live LM Twitterer post path.
5. During validation, run syntax checks plus image-selection, AI-generation, TTS-health, and X-auth checks. Do not run the full live pipeline merely as a test unless an actual public post is intended.

## Cron Job Configuration Pitfall

When setting up the cron job for this skill:
- `workdir`: `C:\\Users\\downl\\Documents\\New project\\hermes-agent` (the hermes-agent root)
- `script`: `daily_vrchat_post.py` (relative to workdir)
- `no_agent`: `true` (runs as standalone script)
- Do not point a Windows cron script at a `.sh` wrapper unless its path is deliberately normalized for the scheduler; broken backslashes can become `C:Users...` under bash.
- Disable older skill-based jobs with the same 07:00 schedule, otherwise two videos may be posted.
- If the scheduler resolves scripts from `~/.hermes/scripts/`, keep a synchronized deployed copy there; otherwise keep the repository-relative script and explicit `workdir` as the single source of truth.

### Python 3.13/3.14 js2py Breakage — Critical Pitfall

If lm-twitterer media posting's reference script at `references/daily_vrchat_post_script.md` documents the logic, but the deployed automation script lives at `scripts/daily_vrchat_post.py` in the hermes-agent project root. Do not confuse the two paths.

## Note
As of 2026-07-06, the Irodori-TTS server may fail to start due to pydantic_core version mismatch.
The workaround is to ensure the Irodori-TTS server is started using its own virtual environment,
or to use the Hermes `aituber_onair_speak` tool with provider=irodori.
See the script `scripts/daily_vrchat_post.py` in the Hermes agent directory for an example implementation.

## Related Files
- `references/daily_vrchat_post_script.md` - Detailed explanation and full script for the automated daily VRChat tweet process
- `references/standalone-script-cron-workflow.md` - Two workflow modes (agent-invoked vs standalone script), deployed script details, and cron config verification
- `references/uv-venv-python311-lm-twitterer-cron.md` - uv-managed Python 3.11 venv pattern for lm-twitterer media posting when Python 3.13/3.14 breaks `js2py`; includes dependency repair, script integration, and non-duplicate verification.
- `scripts/daily_vrchat_post.py` (in hermes-agent root, not skill dir) - The actual deployed automation script used by cron