---
name: x-video-encode-and-cjk-font
description: Encode MP4 for X video posts and render CJK text safely with Pillow on Windows.
version: 0.1.0
author: Hermes
metadata:
  hermes.tags:
    - Windows
    - X
    - Video
    - Fonts
    - Media
---

# X Video Encode and CJK Font Rendering

Encode MP4 files for X/Twitter media uploads and render Japanese/CJK text with Pillow without tofu. This skill captures the verified re-encode recipe and CJK font fallback order from an end-to-end media-post workflow.

## When to Use

- X/Twitter media upload fails with `Video metadata (videoInfo) is required` after `media_upload` succeeds
- Pillow renders Japanese text as squares on Windows
- Need a repeatable ffmpeg command to make MP4s acceptable to X's uploader

## Prerequisites

- `ffmpeg` on PATH
- Python `pillow` available in the active `.venv`
- For lm-twitterer fixes: edit `plugins/lm-twitterer/core.py` so upload returns `(media_id, media_info)` and `CreateTweet` receives `media_entities` with `video_info`.

## How to Run

Use the `terminal` tool. On Windows, prefer `cmd /c` for `ffmpeg` and absolute paths.

## Quick Reference

| Task | Command/Path |
|------|--------------|
| Verify source stream | `ffprobe -v error -show_entries stream=codec_name,profile,pix_fmt -of csv=s=x:p=0 INPUT.mp4` |
| Twitter-compatible encode | ffmpeg recipe in Procedure |
| CJK font test frame | `python -m py_compile render_compare.py && python render_compare.py` |
| Actual post | `.venv312/Scripts/hermes.exe lm-twitterer post ... --live` |

## Procedure

### 1. Encode MP4 for X

```bash
ffmpeg -y -i INPUT.mp4 \
  -movflags +faststart \
  -profile:v baseline -level 3.0 -pix_fmt yuv420p \
  -c:v libx264 -b:v 5000k -maxrate 5000k -bufsize 10000k \
  -c:a aac -b:a 256k -ar 44100 -ac 1 \
  OUTPUT.mp4
```

Key constraints captured from live posting:
- baseline profile + level `3.0`
- yuv420p pixel format
- moov atom at file start: `-movflags +faststart`
- audio mono 44.1kHz AAC; omit audio only if the source truly has none

### 2. CJK-safe Pillow font fallback

Use this `load_font()` fallback order. Earlier entries win if they exist.

Bold:
```text
C:\Windows\Fonts\NotoSansJP-VF.ttf
C:\Windows\Fonts\meiryob.ttc
C:\Windows\Fonts\msgothic.ttc
C:\Windows\Fonts\segoeuib.ttf
C:\Windows\Fonts\segoeui-bold.ttf
C:\Windows\Fonts\arialbd.ttf
```

Regular:
```text
C:\Windows\Fonts\NotoSansJP-VF.ttf
C:\Windows\Fonts\meiryo.ttc
C:\Windows\Fonts\msgothic.ttc
C:\Windows\Fonts\segoeui.ttf
C:\Windows\Fonts\arial.ttf
C:\Windows\Fonts\msyh.ttc
```

Implementation notes:
- Wrap `ImageFont.truetype()` in `try/except` and continue to the next candidate.
- Final fallback: `ImageFont.load_default()`.

### 3. lm-twitterer media payload threading

If `CreateTweet` returns `Video metadata (videoInfo) is required`:
1. Make `_upload_media_with_cookies` return `tuple[str, dict[str, Any] | None]`.
2. Extract `video_info` from `media.video_info`, or from `media_upload_status(media_id)` when missing.
3. Pass a flat `media_payloads` list of `str | dict` through `_post_with_cookie_media`, `_create_tweet_with_cookies`, and `_safe_post_create_tweet`.
4. Build `media_entities` from string ids only, attach `video_info` to matching entities, and set `variables["media"]["video_info"]` from the first available dict.

## Pitfalls

- `segoeui`/`arial` do not render Japanese glyphs; they produce tofu even if the font loads.
- One bad candidate can crash `truetype()`; swallow the exception and fall back.
- `tweepy.API` does not expose `media_upload_status`; use `get_media_upload_status(media_id)` if needed.
- Do not pass `media_ids=` to `_create_tweet_with_cookies`; it now expects `media_payloads=`.

## Verification

```bash
cd PROJECT && python -m py_compile render_compare.py
ffprobe -v error -show_entries format=format_name:stream=codec_name,codec_type,sample_rate,channels -of default=noprint_wrappers=1 OUTPUT.mp4
```

Expected:
- `format_name=mov,mp4,m4a,3gp,3g2,mj2`
- `codec_name=h264`
- `codec_name=aac`, `sample_rate=44100`, `channels=1`
