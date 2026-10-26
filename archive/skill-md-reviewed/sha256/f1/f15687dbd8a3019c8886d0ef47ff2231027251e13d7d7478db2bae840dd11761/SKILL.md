---
name: social-publishing-video-repair
description: "Class-level workflow for diagnosing X/Twitter video media failures in agent plugins, creating a minimal compatibility patch, and verifying with a real live post."
---

# Social Publishing Video Repair

## Use this skill when
- media upload succeeds but `CreateTweet` rejects video with: `Video metadata (videoInfo) is required`.
- a plugin's media helper's return type was changed, but call sites still pass the old shape.
- you need a real live-post verification after a plugin-side media metadata fix.

## Outcome
- minimal plugin patch for video metadata threading
- encoded MP4 that meets X's baseline compatibility requirements
- verified successful media-attached post URL

## Steps

### 1. Reproduce / classify the failure
Run `post(..., dry_run=False, media_paths=[abs_path_under_media_dir], text="short")`.
Record the exact error text and `code`. If `code` is 324 and the message mentions `videoInfo`, continue.
If the error text shows a tuple like `('208018...', None)` being parsed as `media_id`, that means a function`s return type changed from `str` to `tuple[str, dict]` but some caller path still passes the raw tuple.

### 2. Keep the patch minimal
Do not introduce broad refactors. A sound minimal patch usually touches only:
- `_upload_media_with_cookies()` → return `(media_id, media_info)`.
- `_post_with_cookie_media()` and `post()` → flatten into `media_payloads`.
- `_create_tweet_with_cookies()` and `_safe_post_create_tweet()` → consume `media_payloads`, inject `video_info` into `variables["media"]` when present.

### 3. Encode a compatible MP4
```bash
ffmpeg -y -i input.mp4 \
  -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 192k -ar 44100 -ac 1 \
  output.mp4
```
Baseline profile + yuv420p + faststart is the most compatible combination for X uploads.

### 4. Verify with a real live post
```bash
cp output.mp4 ~/.hermes/lm-twitterer/media/output.mp4
.venv312/Scripts/hermes.exe lm-twitterer post "topic" \
  --text "88..271 chars" \
  --media "<media_dir>/output.mp4" \
  --live
```
Short text is more likely to pass first-time validation while validating the media path.

### 5. Record the evidence
- final tweet URL
- exact ffmpeg encode line
- exact plugin callsite changes made
- any remaining caveats

### Pitfalls
- Changing `_upload_media_with_cookies()` return type is a breaking API change; every caller must be updated in the same patch.
- Long Japanese posts with media may fail validation independently of video metadata. If 186/324 combinations persist, shorten the text and retry.
- `.pyc` removal alone does not reload a patched plugin; spawn a fresh process.
- Some users have `js2py_` / dependency issues in their default Python 3.13+ venv; a separate Python 3.12 env with `twitter-openapi-python`, `tweepy-authlib`, `tweepy`, `curl-cffi` can resolve live posting.

## References
- `references/media-video-info-fix-2026-07.md` — exact patch sites, error text, and successful live-post URLs for `videoInfo` repair.
- `references/ffmpeg-baseline-mp4.sh` — re-encode script for X-compatible MP4:
  - `libx264`, `baseline`, `level 3.0`, `yuv420p`, `+faststart`, `aac 192k`, `44100 Hz`, `mono`
