---
name: vrchat-photo-hakua-post
description: Post VRChat photo with Hakua voice to X.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [VRChat, Hakua, IrodoriTTS, XPosting, LM-Twitterer]
---

# VRChat Photo Hakua Post

Select a random photo from a VRChat month folder, generate a fresh Japanese narration with Hermes, synthesize is with Irodori-TTS using the `hakua` voice, encode an X-compatible MP4, and post it through LM-Twitterer. This is the interactive step-by-step workflow; the automated no-agent cron variant lives at `scripts/daily_vrchat_post.py`.

## When to Use

- "VRChatの写真をはくあの声でXに投稿して"
- "先月のVRChatフォルダーからランダムに一枚選んで投稿"
- "朝7時のVRChat写真投稿を手動で実行"
- "VRChatの思い出を動画にしてツイート"

## Prerequisites

- VRChat screenshots under `%USERPROFILE%\Pictures\VRChat` (with month subdirectories like `2026-06`)
- irodoriTTS server repo at `%USERPROFILE%\Documents\New project\irodori-tts-server`
- irodoriTTS venv: `.venv\Scripts\python.exe` in that repo
- FFmpeg installed and in PATH
- LM-Twitterer configured (Python 3.11 venv at `.venv-vrchat-post311` in the Hermes repo)
- Hermes CLI available

## How to Run

Invoke each step through the `terminal` tool in sequence: pick a photo, generate narration, start irodoriTTS, generate audio, encode MP4, post to X.

## Quick Reference

| Step | Tool / Endpoint |
|------|------------|
| Photos directory | `/c/Users/downl/Pictures/VRChat/<YYYY-MM>/` |
| irodoriTTS health | `curl http://127.0.0.1:8088/health` |
| irodoriTTS synthesis | `POST http://127.0.0.1:8088/v1/audio/speech` |
| irodoriTTS startup CPU mode | `IRODORI_MODEL_DEVICE=cpu IRODORI_CODEC_DEVICE=cpu IRODORI_PRELOAD=false HF_HUB_ENABLE_HF_TRANSFER=0` |
| Narration prompt | `hermes -z '<prompt>' --cli` (60-char max, unique each time) |
| FFmpeg stillimage loop | `-loop 1 -i photo -i audio -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -c:v libx264 -tune stillimage -c:a aac -shortest` |
| LM-Twitterer post | `.venv-vrchat-post311/Scripts/python.exe -m hermes_cli.main lm-twitterer post --media <path> --text "<text>" --live` |
| Output directory | `output/daily_posts/` |
| Tweet suffix | `#hermesagent はくあ` |

## Procedure

1. **Select a random photo** from the desired month folder:
   ```text
   python -c "import random, os; files=[f for f in os.listdir('/c/Users/downl/Pictures/VRChat/2026-06') if f.startswith('VRChat_') and f.endswith('.png')]; print(random.choice(files))"
   ```

2. **Generate a fresh narration** via Hermes. Pass the selected filename in a prompt like:
   ```text
   hermes -z '朝7時のVRChat写真投稿用に、はくあが話す日本語ナレーションを1つ作ってください。写真のファイル名から想像できる範囲だけを使い、60文字以内、自然で優しい一文、説明や引用符やハッシュタグは不要です。毎回表現を変えてください。写真ファイル名: <filename>' --cli
   ```

3. **Start irodoriTTS** (if not running). Set CPU env vars to avoid GPU crashes:
   ```text
   IRODORI_MODEL_DEVICE=cpu IRODORI_CODEC_DEVICE=cpu IRODORI_PRELOAD=false HF_HUB_ENABLE_HF_TRANSFER=0 /c/Users/downl/Documents/New\ project/irodori-tts-server/.venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
   ```
   Verify with `curl http://127.0.0.1:8088/health`. Wait until `"loaded": true`.

4. **Generate TTS audio** via the HTTP API:
   ```python
   payload = {"input": "<narration>", "model": "irodori-tts", "voice": "hakua", "response_format": "wav", "speed": 1.0}
   # POST to http://127.0.0.1:8088/v1/audio/speech with Content-Type: application/json
   # Save response bytes to an output .wav file
   ```
   The synthesis can take 1-5 minutes on first request (model loading). Timeout should be at least 900 seconds.

5. **Encode MP4** with FFmpeg using Windows paths (avoid MSYS path mangling):
   ```text
   ffmpeg -y -loop 1 -i '%USERPROFILE%\Pictures\VRChat\2026-06\<photo>' -i '<audio>.wav' -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest '<output>.mp4'
   ```

6. **Post via LM-Twitterer**. Copy the MP4 to `~\.hermes\lm-twitterer\media\`, then invoke:
   ```text
   cd /c/Users/downl/Documents/New\ project/hermes-agent && .venv-vrchat-post311/Scripts/python.exe -m hermes_cli.main lm-twitterer post --media "%USERPROFILE%\.hermes\lm-twitterer\media\<video>.mp4" --text "<narration> #hermesagent はくあ" --live
   ```
   Verify `"posted": true` in the JSON response.

## Pitfalls

- **irodoriTTS GPU crash**: On RTX 5060 Ti / CUDA, the server segfaults (exit 139) during model load. Always use CPU mode (`IRODORI_MODEL_DEVICE=cpu IRODORI_CODEC_DEVICE=cpu`).
- **hf_transfer error**: HF download defaults to `hf_transfer` which can corrupt partial downloads. Set `HF_HUB_ENABLE_HF_TRANSFER=0` in the environment.
- **preload=false**: Keep `IRODORI_PRELOAD=false` so the server starts quickly; the model loads on first synthesis request.
- **First synthesis is slow**: Expect 60-120s for model loading on first request. The synthesis timeout should be 900s.
- **LM-Twitterer Python version**: js2py dependency breaks on Python 3.13/3.14. Use the dedicated `.venv-vrchat-post311` environment.
- **LM-Twitterer direct import fails**: Don't `import plugins.lm_twitterer.core` directly — use the CLI via `python -m hermes_cli.main lm-twitterer post`.
- **FFmpeg path quoting**: File paths with dots (e.g. `21-00-04.175` in filenames) confuse MSYS/bash. Use single-quoted Windows paths (`'C:\...'`) instead of MSYS-style paths for ffmpeg.
- **Media dir constraint**: The MP4 must be copied under `~/.hermes/lm-twitterer/media/` before posting; files outside this dir are rejected.
- **Dots in filenames**: Some shell commands interpret multiple dots as extension boundaries. Use `test -f "..."` to verify file existence before passing to ffmpeg.

## Verification

After completing the workflow, confirm the lm-twitterer CLI output contains `"posted": true` and a `"url"` field. The tweet appears on the configured X account. Optionally run `cronjob action=list` to confirm the existing daily cron `Daily VRChat Photo Post - Hakua Morning` at schedule `0 7 * * *` is enabled.
