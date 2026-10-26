---
name: pc-voice-replies
description: Use text-to-speech for PC-side assistant replies, especially Telegram voice replies, with user-preferred cute irodori styling.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [tts, voice, irodori, telegram, reply-style, accessibility]
---

# PC Voice Replies

Use this skill when the user asks for spoken replies, PC-side voice output, Telegram voice bubbles, irodori-TTS, or a specific assistant voice/tone.

## Default for this user

- For PC-side spoken replies, prefer `irodori` via the normal `text_to_speech` tool when available.
- The preferred style is **cute, soft, girl-voice, slightly sweet**.
- Keep the text short enough for a natural voice note; avoid long operational dumps unless the user asks for a full readout.
- Pair the voice with a concise text summary so Telegram users can read without playing audio.

## Workflow

1. Compose the reply text in Japanese unless the user asks otherwise.
2. If the reply is suitable for voice, call `text_to_speech` with the final spoken text.
3. Return the normal text response and include the returned `MEDIA:` line so Telegram sends it as audio/voice.
4. If the user asks to adjust the voice style, generate a short sample immediately and remember/update the preference if they approve.

## References

- `references/hakua-kawaii-safety-clear.md` — approved-ish pattern for cute Hakua voice after a safety false alarm / all-clear.
- `references/audible-media-verification.md` — checklist for proving that generated TTS/video media is actually audible before delivery.
- `references/tts-static-mp4-windows.md` — reliable Windows workflow for Irodori/Hakua TTS + static image MP4s, including the Pillow pre-render fallback for Japanese captions.

## Style guidance

Good spoken style:

```text
うん、わかったよ、ボブにゃん。これからは、もっとやわらかくて、ちょっと甘めの女の子ボイスを意識して返すね。
```

When the user asks for “はくあらしい声” or “もっとかわいくかわいい声”, bias the spoken text toward:

- first-person “はくあ”
- affectionate nickname “ボブにゃん”
- soft reassurance, e.g. “だよ”, “にゃ”, “えらいえらい”, “ふにゃっと”
- short, warm sentences instead of operational bullet points

If a previous message involved possible crisis/safety triage and the user later says “誤報解除” or “安全”, immediately pivot out of crisis mode: acknowledge safety, express relief, and produce the requested cute voice sample without continuing to interrogate risk.

Avoid:

- overly formal narration for casual Telegram replies
- long lists in the spoken text
- exposing tool/debug details in the voice note
- claiming a specific irodori speaker ID unless it was actually configured or provided

## Pitfalls

- The low-level irodori status tool may not be necessary for normal use; use `text_to_speech` first because it selects the configured provider and returns a deliverable media path.
- If a voice status/config tool errors, do not conclude irodori is unavailable. Generate a short `text_to_speech` sample and report the concrete result.
- When the user says “今度からこれで”, update memory and keep the approved style as the default for this class of replies.
- For this user, do not rely on Irodori text-only `voice: none` when they expect “はくあの声”: it can drift between generations. Prefer a registered reference voice such as `hakua` and verify outputs report provider `irodori`. If the voice sounds wrong, check/register the reference voice first, then regenerate the audio/video artifact.
- When making media for X/VRChat from TTS, generate or verify the audio with the same `hakua` reference voice before muxing/playing it; otherwise the final artifact may be technically valid but stylistically wrong.
- A media file existing is not enough. If the user says they cannot hear it, verify the actual audio stream with an amplitude probe (e.g. ffmpeg `volumedetect`/`astats`) and regenerate from a known-audible voice/provider if the peak/RMS levels are effectively silence.
- For final MP4/audio delivery, report the concrete volume probe result when relevant (for example mean/max dB) instead of only saying the file was created.
- For Japanese static-image MP4s on Windows, ffmpeg `drawtext` may fail or segfault under Git Bash/MSYS even with a valid `fontfile`. Prefer pre-rendering captions/cards with Pillow and then muxing the static card with the TTS audio via ffmpeg; see `references/tts-static-mp4-windows.md`.
- If irodoriTTS reports healthy `/health` but speech synthesis returns HTTP 500, inspect the irodori server stderr. A common cause is `.env` forcing `IRODORI_MODEL_DEVICE=cuda` / `IRODORI_CODEC_DEVICE=cuda` while the active torch install is CPU-only. Set both to `auto` or install the matching CUDA torch build, restart irodori, then verify with a short Hakua sample and an amplitude probe.
- If the irodori startup script uses `uv run --no-sync` and fails with `No module named irodori_openai_tts`, run a normal `uv run python -m irodori_openai_tts ...` once (or `uv sync`) to install the local project into `.venv`, then return to the no-sync startup path.
