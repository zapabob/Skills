---
name: vrchat-fishaudio-posting
description: Use for VRChat posts requiring Fish Audio Hakua voice.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vrchat, fishaudio, hakua, x, video, tts]
    related_skills: [fishaudio-tts, x-video-encode-and-cjk-font]
---

# VRChat Fish Audio Hakua Posting

## When to Use

Use this skill for any VRChat screenshot-to-video post where the user requires
Fish Audio's cloned Hakua voice and verified social delivery.

Class-level workflow for converting a VRChat screenshot into a narrated MP4
and posting it through Hermes LM Twitterer or another approved social adapter.

## User voice contract

For this user, the narration audio must be Fish Audio's cloned Hakua voice.
Pass the cloned-voice `reference_id` explicitly; never rely on a provider
default. Do not silently substitute Irodori-TTS, Edge TTS, or a system voice.
If Fish Audio synthesis fails or the reference ID is absent, stop before video
creation and posting.

Verified configuration:

- provider: `fishaudio`
- model: `s2.1-pro-free`
- format: `mp3`
- Hakua reference ID: `25d6710bcdf043a7b7441e58294431f9`

Never store or print API-key values.

## Procedure

1. Select and validate the VRChat image.
2. Check Fish Audio status: credentials available and `reference_id_configured`
   true.
3. Generate a short Japanese narration. A narration-text timeout may use an
   explicitly approved text fallback, but it must never change the audio
   provider or voice.
4. Use the working Fish Audio core path:
   `plugins.fish_audio_tts.core.settings()` followed by
   `synthesize_text(text=..., voice=cfg.reference_id, model=cfg.model,
   output_format="mp3")`.
5. Verify the result reports `provider=fishaudio`, the expected voice ID and
   model, and a non-empty MP3.
6. Encode the image and MP3 as H.264/AAC MP4 with `yuv420p`. Ensure duration is
   above the destination minimum; X media requires more than 500 ms.
7. Copy the MP4 to the LM Twitterer media directory when required.
8. Post only after local checks pass. Verify structured output has `posted: true`,
   a media ID, and a URL.

## Failure policy

- Missing API key: stop and report configuration status without exposing it.
- Missing or unexpected reference ID: stop; do not use a default Fish voice.
- Fish Audio API/synthesis failure: stop; do not use another TTS provider.
- Encoding failure or ambiguous post response: stop and report the evidence.

## Evidence discipline

Separate voice, media, and delivery evidence. A successful Irodori or Edge
render proves only that another voice worked; it does not satisfy the Fish Audio
Hakua requirement. Report provider/model/reference-ID configuration status,
file existence and size, duration, media ID, and URL, but no secrets.

## References

- `references/verified-pipeline.md` contains the session-verified implementation
  and checks.
- `fishaudio-tts` contains the provider API details and wrapper caveat.
- `x-video-encode-and-cjk-font` contains X encoding guidance.
