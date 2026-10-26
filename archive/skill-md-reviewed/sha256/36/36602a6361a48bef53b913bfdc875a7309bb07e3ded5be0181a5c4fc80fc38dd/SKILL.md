---
name: vrchat-hakua-daily-post
description: Create Hakua VRChat videos and post them at 7 AM.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [VRChat, Hakua, IrodoriTTS, XPosting, Cron]
---

# Hakua VRChat Daily Video Post

This skill selects a recent VRChat image, generates a fresh Japanese narration with Hermes, synthesizes it with Irodori-TTS using the `hakua` voice, encodes an X-compatible MP4, and posts it through LM Twitterer at 07:00 JST. It does not guarantee X delivery when authentication or media upload fails, and component tests must not be described as a live post. The workflow uses the existing Windows Hermes, irodoriTTS server, FFmpeg, Python 3.11 LM-Twitterer environment, and cron configuration.

## When to Use

- “朝7時にVRChatの最新写真を動画にしてX投稿”
- “はくあの声でVRChat投稿を復活”
- “VRChatフォルダから最新群をランダム選択して投稿”
- “毎回AIで音声スクリプトを変えて投稿”
- “VRChat daily Hakua post のcronを確認・修正”

## Prerequisites

- Windows Hermes workspace: `%USERPROFILE%\Documents\New project\hermes-agent`
- VRChat images under `%USERPROFILE%\Pictures\VRChat`
- irodoriTTS server repository: `%USERPROFILE%\Documents\New project\irodori-tts-server`
- irodoriTTS health endpoint: `http://127.0.0.1:8088/health`
- Hakua voice reference: `voices\hakua.ogg`
- FFmpeg available through the `terminal` tool
- LM Twitterer configured and authenticated; verify with `lm_twitterer_auth_check`
- Dedicated Python environment: `.venv-vrchat-post311\Scripts\python.exe`
- Hermes cron support and a 07:00 JST job with `no_agent: true`

Do not hardcode X credentials, API keys, or tokens. Keep them in the configured Hermes secret store/environment.

## How to Run

Use the Hermes `terminal` tool from the Hermes repository to syntax-check or component-test the script. Use `cronjob` to inspect or update the scheduled job. Use `aituber_onair_tts_status` or `irodori_tts_status` to verify the irodori backend, and `lm_twitterer_auth_check` to verify X authentication. A normal cron execution invokes the script and performs a live X post.

Canonical script paths:

- Source: `%USERPROFILE%\Documents\New project\hermes-agent\scripts\daily_vrchat_post.py`
- Deployed no-agent copy: `%USERPROFILE%\.hermes\scripts\daily_vrchat_post.py`
- Output: `%USERPROFILE%\Documents\New project\hermes-agent\output\daily_posts`

## Quick Reference

- Schedule: `0 7 * * *`
- TTS URL: `http://127.0.0.1:8088`
- TTS model: `irodori-tts`
- TTS voice: `hakua`
- TTS format: `wav`
- Media format: H.264/AAC MP4
- Video pixel format: `yuv420p`
- Hermes narration command: `hermes -z <prompt> --cli`
- LM-Twitterer command module: `python -m hermes_cli.main lm-twitterer post`
- Required hashtag: `#hermesagent`
- Hermes tools: `terminal`, `read_file`, `patch`, `cronjob`, `aituber_onair_tts_status`, `irodori_tts_status`, `lm_twitterer_auth_check`

## Procedure

1. **Inspect the existing configuration.** Invoke `cronjob` with `action="list"`. Find the job named `Daily VRChat Photo Post - Hakua Morning`, and confirm `schedule` is `0 7 * * *`, `script` is `daily_vrchat_post.py`, `no_agent` is `true`, and `workdir` is `%USERPROFILE%\Documents\New project\hermes-agent`.

2. **Check the backends before editing.** Invoke `aituber_onair_tts_status` or `irodori_tts_status` with the irodori provider. Require HTTP 200 from `http://127.0.0.1:8088/health`, `voice` equal to `hakua`, and a present `hakua.ogg` reference. Invoke `lm_twitterer_auth_check` and require `auth_valid: true` and a matching configured account.

3. **Ensure recent-random image selection.** In `daily_vrchat_post.py`, collect files recursively under `VRCHAT_PHOTOS_DIR`, accept `.png`, `.jpg`, and `.jpeg` case-insensitively, sort by `path.stat().st_mtime` descending, take the newest ten, and return `random.choice(recent)`. Do not choose uniformly from the entire archive when the requirement is “latest random.”

4. **Ensure fresh AI narration.** Generate the narration by invoking through the `terminal` tool:

   ```text
   hermes -z '朝7時のVRChat写真投稿用に、はくあが話す日本語ナレーションを1つ作ってください。写真のファイル名から想像できる範囲だけを使い、60文字以内、自然で優しい一文、説明や引用符やハッシュタグは不要です。毎回表現を変えてください。' --cli
   ```

   The script should pass the selected filename in the prompt, join non-empty output lines, strip surrounding quotes, and use a short fallback sentence if the command fails. Append `#hermesagent はくあ` to the post text.

5. **Ensure irodori synthesis uses Hakua.** Send JSON to `http://127.0.0.1:8088/v1/audio/speech` with `input`, `model: "irodori-tts"`, `voice: "hakua"`, `response_format: "wav"`, and `speed: 1.0`. Save the response under the daily output directory.

6. **Encode the video.** Invoke FFmpeg through the `terminal` tool from the script. Use an image loop, WAV input, H.264 video, AAC audio, and the filter `scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p`; include `-shortest` and `-y` for unattended execution.

7. **Post with LM Twitterer.** Copy the MP4 to `Path.home() / ".hermes" / "lm-twitterer" / "media"`. Use the dedicated Python 3.11 executable and invoke through the `terminal` tool:

   ```text
   python -m hermes_cli.main lm-twitterer post --media <media-path> --text <tweet-text> --live
   ```

   Treat nonzero exit status, `"posted": false`, or `"ok": false` as failure.

8. **Prevent duplicate 07:00 posts.** If another enabled job named `vrchat_daily_tweet` performs the same workflow, pause it with `cronjob` and retain only the explicitly configured daily script job. Keep the separate `disaster-news-jp-daily` job independent.

9. **Synchronize source and deployed copies.** Apply the same targeted change to the repository script and `%USERPROFILE%\.hermes\scripts\daily_vrchat_post.py` using `patch`. Do not delete unrelated user changes or reset the repository.

10. **Run non-publishing verification.** Invoke the `terminal` tool from the Hermes repository:

    ```text
    python -m py_compile scripts/daily_vrchat_post.py
    ```

    Then import the module and call only image selection and AI narration generation. Do not invoke the full script for a dry test because the normal path uses `--live` and publishes to X.

11. **Confirm the schedule.** Invoke `cronjob` with `action="list"` again and confirm the daily job is enabled, scheduled for `0 7 * * *`, and points at the correct workdir and script. Report that component verification is not proof of a live X post.

## Pitfalls

- Windows paths with backslashes can be mangled when a cron script is resolved through `/bin/bash`; use a Python script plus an explicit Windows `workdir`, not a malformed absolute `.sh` path.
- The no-agent cron resolver expects the script relative to its configured workdir. Do not assume a repository script is found when `workdir` is absent.
- irodoriTTS may be healthy while VOICEVOX is stopped; that is not a failure when the requested provider is irodori.
- `model_device: auto` does not prove CUDA stability. Prefer the already healthy irodori endpoint and avoid rebuilding environments during the posting run.
- The older implementation selected from the entire image archive and used fixed random templates; that does not satisfy latest-random plus AI-generated narration.
- X authentication checks validate read/auth state but are not proof that a live media post succeeded.
- A full cron run creates audio, MP4, and performs a live post. Never use `cronjob action="run"` merely as a dry test.
- Do not run both the standalone daily script job and the equivalent skill job at 07:00, or duplicate posts can occur.
- Do not commit, reset, or clean unrelated fork changes while synchronizing the two script copies.

## Verification

Invoke the following checks through Hermes tools and require all of them:

```text
python -m py_compile scripts/daily_vrchat_post.py
```

Then confirm `generate_ai_script(selected_photo)` returns non-empty Japanese text, `irodori_tts_status` reports the irodori server as usable with Hakua, `lm_twitterer_auth_check` reports `auth_valid: true`, and `cronjob` shows one enabled 07:00 JST script job. A successful live post is verified only by the LM Twitterer result containing a posted success and URL during the scheduled run.
