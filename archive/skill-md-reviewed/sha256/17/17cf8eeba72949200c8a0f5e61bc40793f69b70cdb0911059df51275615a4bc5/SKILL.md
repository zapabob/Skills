---
name: vrchat-daily-post-cron-troubleshooting
description: Troubleshooting guide for the daily VRChat daily VRChat photo post cron job (07:00 JST) using Irodori-TTS (Hakua voice) and LM Twitterer. Covers TTS server issues, Python version incompatibilities, cron scheduling conflicts, and verification steps.
version: 1.0.0
author: Hermes Agent
tags: [VRChat, Hakua, IrodoriTTS, XPosting, Cron, Troubleshooting]
---

# VRChat Daily Post Cron Troubleshooting

This skill documents the proven working configuration and troubleshooting steps for the daily 07:00 JST VRChat photo post with Hakua voice (Irodori-TTS) posted via LM Twitterer.

## When to Use

- "朝7時のVRChat投稿が失敗する" / "Daily VRChat post failing at 7 AM"
- "Irodori-TTSでタイムアウトする" / "Irodori-TTS timeout"
- "lm-twittererがPython 3.13で動かない" / "LM Twitterer broken on Python 3.13"
- "cronの重複投稿を防ぎたい" / "Prevent duplicate cron posts at 07:00"
- "VRChat写真投稿の動作確認手順が知りたい" / "Verification steps for VRChat daily post"

## Proven Working Configuration (Session 2026-07-21)

### Irodori-TTS Server

- **URL**: `http://127.0.0.1:8088`
- **Model**: `Aratako/Irodori-TTS-500M-v3` (auto-loaded on first request, lazy loading)
- **Voice**: `hakua` (references `voices/hakua.ogg`)
- **Health endpoint**: `GET /health` → HTTP 200, `{"status":"ok","voices":{"files":1}}`
- **Synthesis endpoint**: `POST /v1/audio/speech` with `{"input":"...","model":"irodori-tts","voice":"hakua","response_format":"wav","speed":1.0}`
- **Critical timeout**: 900 seconds (model loads on first request, takes 2-5 minutes)

### LM Twitterer

- **Python**: `.venv-vrchat-post311\Scripts\python.exe` (Python 3.11 — **required**, 3.13/3.14 fail with dataclass/KW_ONLY error)
- **Command**: `python -m hermes_cli.main lm-twitterer post --media <path> --text "<text>" --live`
- **Auth**: Cookie-based (`auth_token` + `ct0`), verified via GraphQL
- **Media path guard**: Must copy MP4 to `~/.hermes/lm-twitterer/media/` before posting

### Cron Job (07f62cef0201)

- **Name**: `Daily VRChat Photo Post - Hakua Morning`
- **Schedule**: `0 7 * * *` (07:00 JST)
- **Script**: `daily_vrchat_post.py`
- **Workdir**: `%USERPROFILE%\Documents\New project\hermes-agent`
- **No-agent**: true
- **Deliver**: local

### Video Encoding (FFmpeg)

```bash
ffmpeg -y -loop 1 -i <image> -i <audio.wav> \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest <output.mp4>
```

## Common Issues and Solutions

### 1. Irodori-TTS Server Not Running

**Symptom**: `curl http://127.0.0.1:8088/health` fails with "Failed to connect to host"

**Solution**:
```bash
cd "%USERPROFILE%\Documents\New project\irodori-tts-server"
.venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
```
Wait for "Application startup complete", then verify with `/health`.

### 2. Port 8088 Already in Use

**Symptom**: Server fails to start with `ERROR: [Errno 10048] ...`

**Solution**: Server is already running. Verify with `curl http://127.0.0.1:8088/health`.

### 3. Voice File Missing

**Symptom**: TTS generation fails

**Check**: `%USERPROFILE%\Documents\New project\irodori-tts-server\voices\hakua.ogg` exists (136963 bytes)

### 4. TTS Generation Timeout (Most Common Cron Failure)

**Symptom**: `urllib.request.urlopen` times out after 60-120 seconds

**Root Cause**: Irodori-TTS loads the model on first request (lazy loading). First request takes 2-5 minutes.

**Solution**: Use 900 second timeout in cron script. The `daily_vrchat_post.py` already uses 900 seconds:
```python
with urllib.request.urlopen(req, timeout=900) as response:
    output_path.write_bytes(response.read())
```

### 5. Python Version Incompatibility (LM Twitterer + js2py)

**Symptom**: `AttributeError: 'NoneType' object has no attribute '__dict__'` when importing `core.py` in Python 3.13/3.14

**Root Cause**: `dataclass` decorator fails with `KW_ONLY` in Python 3.13+ due to `twitter-openapi-python` dependency issues.

**Solution**: Use dedicated Python 3.11 virtual environment for LM Twitterer:
- Path: `%USERPROFILE%\Documents\New project\hermes-agent\.venv-vrchat-post311\Scripts\python.exe`
- Already configured in `daily_vrchat_post.py` as `HERMES_POST_PYTHON`

### 6. Cron Job Last Status: Error

**Diagnosis**: Check cron job `07f62cef0201`
- If `last_status: error` but no `last_delivery_error`, script failed silently
- Common causes: TTS timeout, model loading, media path issues
- Script logs to stdout/stderr which cron captures

### 7. Duplicate 07:00 Posts Prevention

**Prevention**: Ensure only ONE job runs at 07:00 JST:
- Keep `07f62cef0201` (Daily VRChat Photo Post - Hakua Morning) **enabled**
- Pause `8836c500a031` (morning-vrchat-hakua-post) and `80b6cac36fc5` (vrchat_daily_tweet)

## Verification Checklist Before Cron Run

1. `curl http://127.0.0.1:8088/health` → HTTP 200, `"status":"ok"`, `"voices":{"files":1}`
2. `ls "%USERPROFILE%\Documents\New project\irodori-tts-server\voices\hakua.ogg"` → exists
3. `.venv-vrchat-post311\Scripts\python.exe -m hermes_cli.main lm-twitterer auth-check` → `"auth_valid": true`
4. `python -m py_compile scripts/daily_vrchat_post.py` → no errors
5. Cron job `07f62cef0201` enabled, schedule `0 7 * * *`, workdir correct

## Live Post Verification (2026-07-21)

- **Tweet URL**: https://x.com/zapabob_ouj/status/2079350054184476940
- **Text**: "朝5時のVRChat、静かな世界で深呼吸して目覚めました #hermesagent はくあ"
- **Media ID**: 2079350022819479552
- **Status**: Successfully posted via cron script (manual test run)

## Related Skills

- `lm-twitterer-operations` — LM Twitterer plugin guide, cron integration, media posting
- `vrchat-hakua-daily-post` — Daily post workflow and procedure
- `hermes-x-posting-workflows` — General X posting workflows