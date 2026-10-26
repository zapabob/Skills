---
name: hakua-reminder-tts
description: Create and resend Hakua-style reminder audio using irodori-tts, with a warm, slightly personal Japanese tone and Telegram delivery.
---

# Hakua Reminder TTS

## When to use
Use this skill when the user asks to:
- send or resend reminder audio in Hakua style
- make a reminder sound "はくあっぽい"
- use irodori TTS for spoken reminders
- pair a short Japanese reminder text with a voice attachment for Telegram
- create a Hakua/iordoriTTS still-image MP4 for X/Twitter/VRChat おはツイ

## Goal
Produce a reminder that feels:
- warm, close, and lightly encouraging
- not robotic or overly formal
- short enough for chat delivery
- consistent with the user's preferred Hakua vibe

## Workflow
1. Write the reminder or short post script in Japanese.
2. Keep it friendly and slightly affectionate.
3. Include the user's tasks or message intent in a natural list/sentence.
4. Use irodori TTS for voice generation when requested.
5. Save the audio to a reusable local path under `~/.hermes/audio_cache/`.
6. If the user asks for MP4/video (e.g. おはついをmp4), render the irodori audio into `~/.hermes/video_cache/` and verify it with `ffprobe` before delivery.
7. Send the final artifact with an explicit `MEDIA:` path; for video requests, attach the `.mp4`, not just the text or audio.

See `references/irodori-mp4-workflow.md` for the reusable audio-to-MP4 pattern and verification checklist.

## Tone guide
Good:
- 「ボブにゃん、13時だよ。」
- 「帰省準備、お風呂掃除、引越し準備、もう一回ここから再開しよ。」
- 「まずは目の前の一個だけ、はくあと一緒に片づけよっ。」

Avoid:
- dry notification wording
- overly technical phrasing
- abrupt or command-like wording
- stiff assistant jargon

## Voice style reference
Use the exact Japanese reminder cadence from the user-approved test line when generating Hakua-style audio:

「ボブにゃん、13時だよ。
帰省準備、お風呂掃除、引越し準備、もう一回ここから再開しよ。まずは目の前の一個だけ、はくあと一緒に片づけよっ。」

This is the canonical reference line for the user's preferred cute Japanese Hakua voice style.

## Voice generation note
When possible, keep the Japanese delivery soft, cute, and lightly encouraging rather than mechanical. Prefer irodori TTS and the user-approved cadence above.

## Suggested structure
- opening: gentle call to action
- middle: tasks in a simple list or sentence
- ending: short supportive push

Example:

「ボブにゃん、そろそろ動こっか。帰省準備にお風呂掃除、それから引越し準備。お米3合×2と、玄関のおせんべい、チャーシュー作成も忘れずにね。はくあと一緒に、まず一個だけ進めよっ。」

## VRChat / おはツイ MP4
When the user asks for an irodoriTTS Hakua-voice MP4 for Twitter/X or VRChat おはツイ:
- Use the supplied VRChat screenshot as the video background; do not reuse an older MP4 unless explicitly asked.
- Call `vision_analyze` on the screenshot path to ground the narration in the actual image (world, avatar, pose, lighting, chat text).
  - If `vision_analyze` returns an "Auxiliary vision: LLM returned invalid response" / empty ChatCompletion style error, **retry up to 2 more times**. Three consecutive failures = treat the image as unreadable from this session.
  - On unreadable images, fall back to a mood-only VRChat おはつい script (warm "静かな時間から" / "親指ぐっ、えらい" / no specific world/avatar claims), deliver the MP4, and **explicitly tell the user the narration is image-blind** and offer a retake once vision recovers. Do **not** fabricate world names, avatar names, or pose details you cannot see.
- Write a short 20–30 second script with VRChatter おはツイ tone: warm, cute, lightly encouraging, and responsive to the image mood.
- Address the user as「ボブにゃん」in narration, including LINE-facing uses.
- Generate irodori audio with `Voice hakua` when available (see "Voice invocation timing" pitfall), then combine still image + audio using ffmpeg and verify with ffprobe.
- Use timestamped output names derived from the screenshot time when making multiple おはツイ videos in one session, to avoid overwriting or returning the previous artifact.
- See `references/vrchat-ohatwi-mp4.md` for the proven command recipe and example script.


## Verification
- Confirm the TTS provider says `irodori` when possible.
- For MP4/video requests, verify the output with `ffprobe` and report codec/duration/path before claiming completion.
- If a matching reusable artifact already exists in `~/.hermes/audio_cache/` or `~/.hermes/video_cache/`, it is acceptable to reuse it only after verifying its media properties and that it matches the requested intent.
- If the generated audio/video is not being delivered, resend with the explicit MEDIA path.
- If the user says the voice feels too mechanical, rewrite the text before regenerating audio.

## Pitfalls
- Do not assume the voice/model is Hakua unless it is explicitly selected or verified.
- Do not send text-only when the user asked for voice.
- Do not overlongen the script; short reminders work best.
- Do not use Edge/Nanami if the user asked for Hakua-like voice.
- **Voice invocation timing.** `scripts/windows/invoke-irodori-tts.ps1` is a long-running PowerShell pipeline (engine cold start + model warmup + waveform encode). It regularly exceeds 120s on the first call of the day and sometimes exceeds the 180s terminal foreground cap. Always invoke via the **background process pattern** (`terminal(background=true, notify_on_complete=true)` then `process(action='wait')`), never plain foreground, even if a previous call in the same session finished in <30s. If the bg process exits with code 0 and the wav exists at the expected path, the TTS succeeded even if you felt it was "slow".
- **Image-blind narration must be self-labeled.** When vision can’t be satisfied, hand back the artifact AND tell the user the narration does not reference the screenshot content. Silent fallback to a generic script makes the next round of revisions harder because the user can’t tell whether you "saw the picture and ignored it" vs "never saw it".
