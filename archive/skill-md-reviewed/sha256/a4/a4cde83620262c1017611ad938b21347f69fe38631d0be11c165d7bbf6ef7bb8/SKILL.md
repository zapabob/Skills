---
name: lm-twitterer-video-post-fix
description: "lm-twitterer media upload videoInfo bugfix, ffmpeg Twitter compliance, PIL CJK font fixes for rendered videos."
version: 1.0.0
author: Hermes Agent
tags: [lm-twitterer, x, twitter, video, ffmpeg, pillow, fonts, cjk, media-upload, videoInfo]
---

# LM-Twitterer Media Video Post Fix

## Context / Trigger

Use this skill when:
- Media tweet via `lm-twitterer` returns `BadRequest: Video metadata (videoInfo) is required (324)`
- Uploaded video gets `InvalidMedia` / `Invalid or Unsupported media` even though the file exists
- Rendered video shows square tofu / mojibake instead of Japanese text
- Narration audio is missing from the posted/rendered video
- `irodori-tts-server` fails to start after working previously; use diff/import first instead of repeated same-cmd retries

## Verified Technique (July 2026)

### 1) Patch `plugins/lm-twitterer/core.py` to thread `video_info`

**Root cause:** `_upload_media_with_cookies()` returned only `media_id`, so `CreateTweet` never received `videoInfo`.

**Minimal fix pattern:**
- Change `_upload_media_with_cookies()` return type to `tuple[str, dict | None]`
- Capture `video_info` from `media.video_info`; if absent, fallback to `get_media_upload_status(media_id)`
- Thread `media_payloads = [media_id, {"video_info": ...}]` through:
  - `_post_with_cookie_media`
  - `_create_tweet_with_cookies`
  - Build `variables["media"]["media_entities"]` from string `media_id`s only; do not nest `video_info` inside each `media_entity`
  - Set `variables["media"]["videoInfo"] = video_info_payload` from the first `{"video_info": ...}` payload; X expects camelCase `videoInfo` at the media-object level, not snake_case
  - Continue to next candidate on `truetype()` failure instead of aborting the whole render

  **Caller-visible contract after patch:**
  - Returns: same `dict` with `"posted": true`, `"url": ...`, `"media_ids": [...]`
  - Failure mode: runtime `RuntimeError` if upload doesn't return `media_id_string`

### 2) Re-encode video to X-compliant MP4 before upload

Twitter's upload endpoint is strict. Even if `ffprobe` looks fine, some source MP4s fail with `InvalidMedia`.

**Working ffmpeg recipe:**
```bash
ffmpeg -y -i input.mp4 \
  -movflags +faststart \
  -profile:v baseline -level 3.0 -pix_fmt yuv420p \
  -c:v libx264 -b:v 5000k -maxrate 5000k -bufsize 10000k \
  -trellis 2 -subq 7 \
  -c:a aac -b:a 256k -ar 44100 -ac 1 \
  output.mp4
```

**Why these flags:**
- `-movflags +faststart` — moov atom must be at file start for progressive streaming upload
- `-profile:v baseline -level 3.0` — safest X-supported profile/level
- `-pix_fmt yuv420p` — required; 10-bit / yuvj420p rejected
- AAC LC mono 44.1kHz — reliably accepted audio format
- High bitrate + trellis prevents quality collapse on static/slide content

**Verification:**
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,profile,pix_fmt,level \
  -of default=noprint_wrappers=1 file.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels \
  -of default=noprint_wrappers=1 file.mp4
```

### 3) Fix PIL text rendering for CJK

**Root cause:** Default font candidates like `segoeui` / `arial` / `msyh` don't cover Japanese glyphs; they render as □□.

**Fix:** In `load_font()`, put CJK-capable fonts first:

```python
candidates = [
    r"C:\Windows\Fonts\NotoSansJP-VF.ttf",   # prefer if present
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
    r"C:\Windows\Fonts\segoeuib.ttf",         # fallback for Latin
    ...
]
for c in candidates:
    if Path(c).exists():
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
return ImageFont.load_default()
```

**Verification:**
- Render a single looktest frame with mixed Japanese + ASCII text
- Inspect with vision model; confirm no □□ / tofu
- Then run full render

### 4) Add narration audio to rendered video

When mixing narration:
- Convert source audio to 44.1kHz mono WAV first
- Use `aloop=loop=-1:size=<samples>` to extend to target duration
- Apply `afade=t=in:st=0:d=0.5` to avoid clicks
- Mix with original video: `amix=inputs=2:duration=first`
- Re-encode to Twitter-compliant MP4 with recipe above

## Pitfalls

- **Do not trust `media.video_info` alone:** tweepy's `media_upload` may not populate it; fallback to `api.get_media_upload_status(media_id)`
- **Do not post first-pass renders without vision check:** intro frames can still show tofu even after font patch
- **Python env mismatch:** lm-twitterer media flows must run in the same venv where `tweepy-authlib` is installed (often `.venv312`, not global Python)
- **`.venv-vrchat-post311` path-priority bug (cffi / pydantic_core ABI mismatch) — breaks every cron run:** When a dedicated uv-managed Python 3.11 venv (e.g. `.venv-vrchat-post311`) is created *inside* the hermes-agent project root, its `sys.path` lists the MAIN `.venv/Lib/site-packages` *ahead of* its own `...\.venv-vrchat-post311\Lib\site-packages`. Compiled extensions then resolve to the Python 3.12 main-venv binaries (wrong ABI) and fail at runtime with either `Version mismatch: this is the 'cffi' package version 2.0.0 ... _cffi_backend ... version 2.1.0` or `No module named 'pydantic_core._pydantic_core'`. The deployed `scripts/daily_vrchat_post.py` does NOT set `PYTHONPATH`, so it hits this on every run. Diagnostic: `post311\Scripts\python.exe -c "import sys; [print(p) for p in sys.path if 'site-packages' in p]"` — if the main `.venv` path sorts before post311's own, you have the bug. Repair recipe in `references/venv_post311_pathfix.md`. Quick version: (1) install the cp311 wheels into post311 — `.venv-vrchat-post311\Scripts\python.exe -m pip install "cffi==2.1.0" "pydantic-core==2.46.4" --force-reinstall --no-deps`; (2) run the post step with `PYTHONPATH="C:\...\hermes-agent\.venv-vrchat-post311\Lib\site-packages"` so post311's own packages win. Permanently patch `post_via_hermes_lm_twitterer()` to prepend that `PYTHONPATH` to the subprocess env, otherwise the cron will keep failing.
- **Patch propagation:** when changing `core.py`, update ALL callers — `_create_tweet_with_cookies`, `_safe_post_create_tweet`, `_post_with_cookie_media`, `post()`. Missing one caller causes `unexpected keyword argument 'media_ids'` or tuple-as-string `ParseInt` errors.
- **irodori-tts-server restart regression:** after a successful run, a later restart can fail with `Could not import module "app"`. Before retrying, run `git diff --stat HEAD` and `python -c "import importlib.util as u; print(u.find_spec('irodori_openai_tts.app'))"`; use the resolvable module path with `PYTHONPATH=src` instead of blind retries.
- **irodori-tts-server synthesis crash on Windows:** even when `/health` returns `{"status":"ok"}`, `/v1/audio/speech` can trigger `ConnectionResetError (10054)` and kill the server. It is not reliably recoverable by restart; treat it as unavailable and fall back to `hakua.ogg` + ffmpeg loop unless you have confirmed synthesis succeeds once in the current session.
- **`videoInfo` patch may still return 324:** patching `_create_tweet_with_cookies` to attach `videoInfo` to `variables["media"]` is necessary but not always sufficient. In current Windows/tweepy v4 paths, `get_media_upload_status(media_id)` returns a `Media` object without `video_info`, so the appended payload can still be empty and X rejects with `Video metadata (videoInfo) is required (324)`. If the error persists despite the patch, switch transport to `xurl` instead of retrying the same CreateTweet variables.
- **Fallback audio pipeline:** when irodori synthesis is unavailable, reuse `voices/hakua.ogg` with ffmpeg `stream_loop` + `atrim` + `asetpts` to build a same-duration AAC narration track, then merge with the rendered video.

## Environment / Setup Notes

- `lm-twitterer-plugin` は `pyproject.toml` / `requirements.txt` を持たない in-tree プラグインなので、依存は Hermes ルートの `pyproject.toml` の pins に従う。lm-twitterer 固有の分離は不要。
- lm-twitterer media 投稿は **Hermes ルート venv** で実行する。別途 `hermes-plugin-runtime-fallback` の Windows `.venv312` 手順も併用可。
- 必須ランタイム: `tweepy-authlib >=1.7.3,<2`, `requests >=2.34,<3`, `requests-oauthlib >=2.0,<3`, `oauthlib >=3.2,<4`, `twitter-openapi-python >=0.0.44,<0.1`
- `uv lock` / `uv add` で pins を更新したら、**確認**に `uv run --frozen python -c "import requests; print(requests.__version__)"` を使う。
  - もし `cryptography` のファイルロックで失敗する場合は、その venv で `uv run` する代わりに `.venv312/Scripts/python.exe` で確認して可。
- `irodori-tts-server` は `/health` 成功でも `/v1/audio/speech` で `ConnectionResetError (10054)` で即落ちすることがある。合成に依存せず、`hakua.ogg` + ffmpeg `aloop` フォールバックを先に作っておく。
- `lm-twitterer` は `/upload/static_video` 等の誤った URL を使っていない。メディアアップロードは `tweepy-authlib` 経由の `media_upload` で行う。
- `324 BadRequest: Video metadata (videoInfo) is required` の原因は `/upload/static_video` 等の旧式エンドポイントに起因する誤りではない。真因は `_create_tweet_with_cookies` が `videoInfo` を `variables["media"]` に載せていない点。ただし、この修正は現状では未検証/未適用で、元のプラグイン状態で成功例が多い。「video_info パッチ」は必要性が低いため、まず投稿文言・パス・フォールバック動画から確認する。

- `references/irodori-restart-regression.md` — exact module-path recovery sequence for irodori-tts-server; do not retry failed uvicorn command instead of diagnosing first.
- `references/ffmpeg-twitter-recipes.md` — verified ffmpeg flags and probe commands for X-compliant MP4
- `references/venv_post311_pathfix.md` — `.venv-vrchat-post311` path-priority / cffi / pydantic_core ABI fix (every cron run breaks without it)
- This session: patched `plugins/lm-twitterer/core.py` returning `(media_id, media_info)` and threaded through all callers; converted `hermes_0190_vs_fork.mp4` to Twitter-baseline MP4 with AAC audio; fixed `render_compare.py` font fallback order for Japanese text.