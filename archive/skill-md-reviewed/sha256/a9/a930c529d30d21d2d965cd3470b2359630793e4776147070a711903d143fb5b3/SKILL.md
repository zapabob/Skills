---
name: fishaudio-tts
description: FishAudio TTS with a cloned voice (Hakua) in Hermes fork.
---

# FishAudio TTS (Hermes fork)

Use the bundled `fish-audio-tts` plugin to synthesize speech via Fish Audio's
REST API, including a cloned custom voice such as **Hakua (はくあ)**.

## When to use
- User wants Hakua / a specific FishAudio cloned voice in Hermes TTS output.
- Wiring FishAudio as the `tts.provider` in `config.yaml`.
- The `fish_audio_tts_synthesize` tool errors out and you need the working path.

## Prerequisites
- `FISH_AUDIO_API_KEY` present. Verify with `fish_audio_tts_status` →
  `credentials.api_key_present: true` (the status tool itself works fine).
  Set it in `.env` (or env var). The plugin reads `FISH_AUDIO_API_KEY` then
  `FISH_API_KEY`. The key is NOT a config.yaml key.
- A cloned voice on Fish Audio → its `reference_id` (UUID). Find it at
  https://fish.audio/ja/app/ (My Voices). **Without `reference_id` the plugin
  uses the model's default voice, NOT Hakua.**

**Verified Hakua voice UUID (2026-08-09):** `25d6710bcdf043a7b7441e58294431f9`

## Setup (config.yaml)
Set the provider and the `fishaudio` section. See `templates/config-snippet.yaml`
for a paste-ready block. Key facts (mirrored from `plugins/fish_audio_tts/core.py`):
- Section key: `tts.fishaudio` (alias `tts.fish_audio` is also read).
- `reference_id` (or `voice`) = cloned voice UUID. **Required for Hakua.**
- `model` default `s2.1-pro-free` (also `s2.1-pro`, `s2-pro`, `s1`).
- `format` ∈ {mp3, wav, opus, pcm}, default mp3.
- `speed` 0.5–2.0, default 1.0. `mp3_bitrate` ∈ {64,128,192}.
- `base_url` default `https://api.fish.audio`.

After editing, verify:
```
fish_audio_tts_status
```
Expect `provider: fishaudio`, `reference_id_configured: true`, and the chosen model.

## Known pitfall: `fish_audio_tts_synthesize` tool wrapper is broken
As observed in-session, calling the `fish_audio_tts_synthesize` tool (even with a
valid `text`) raises `AttributeError: 'dict' object has no attribute 'strip'` —
the tool wrapper passes a dict where the underlying function expects a `str`.
**Do not loop on the tool.** Use the working path instead (the core function is sound):

```bash
cd <hermes-fork>
python - <<'PY'
from plugins.fish_audio_tts.core import synthesize_text
res = synthesize_text(
    text="こんにちは、ボブにゃん！",
    voice="<HAKUA_REFERENCE_ID>",
    model="s2.1-pro-free",
)
print(res["file_path"])
PY
```
`synthesize_text` writes the audio file and returns
`{ok, file_path, format, voice, model, media_tag}`. The `media_tag` is
`MEDIA:<path>` for inline delivery. CLI `fish-audio-tts` is also provided by the plugin.

## User preference: FishAudio Hakua is an approved voice
For this user, FishAudio's cloned Hakua (はくあ) voice is an explicitly approved
TTS option for VRChat おはツイ, reminder audio, and Hakua-persona posts. Treat it
as a first-class option alongside irodori-TTS Hakua, not merely a fallback.

## Workflow pitfall: check status before requesting a voice UUID
When the user approves FishAudio Hakua, first run `fish_audio_tts_status` and
inspect `reference_id_configured` plus the configured `reference_id`/`voice`.
Do not immediately ask the user to paste a UUID: it may already be configured.
Proceed with the configured cloned voice when present. Ask for the UUID only when
status confirms it is absent and a default FishAudio voice is not acceptable.
An API key alone is not proof that the output uses Hakua; the cloned voice
reference ID must also be verified.

## VRChat Hakua posting requirements

For the VRChat screenshot-to-video workflow, Fish Audio's cloned Hakua voice is mandatory: pass the configured cloned-voice `reference_id` explicitly and abort rather than falling back to Irodori-TTS, Edge TTS, or another voice. See `references/vrchat-hakua-posting-requirements.md` for the verified pipeline and checks.

## References
- `references/config-schema.md` — full config key table mirrored from core.py.
- `references/vrchat-fishaudio-hakua-video-pipeline.md` — complete working pipeline: VRChat screenshot → FishAudio Hakua voice → MP4 → lm-twitterer post (verified 2026-08-09).
- `templates/config-snippet.yaml` — paste-ready TTS config.
