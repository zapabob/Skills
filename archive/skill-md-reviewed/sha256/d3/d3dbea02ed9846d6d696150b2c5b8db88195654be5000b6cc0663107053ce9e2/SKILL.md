---
name: music-audio-production
description: Create, analyze, and package music/audio artifacts, including songwriting, AI music prompts, HeartMuLa/Suno-like generation, spectrogram or feature visualization, and audio-output verification. Use for lyrics, parody, AI music generation, mel/chroma/MFCC visualizations, and checking that generated media is actually audible.
---

# Music and Audio Production

This umbrella skill covers music/audio creation and analysis workflows that are not specifically Hermes runtime TTS-provider engineering.

## Choose the sub-workflow

- **Songwriting / AI music prompt:** write lyrics, structure sections, tune rhyme/meter, provide Suno-style tags/metatags, and include phonetic tricks for AI singers when needed.
- **Open-source music generation:** use HeartMuLa when the user wants local/open-source song generation from lyrics and tags; verify hardware/Python constraints before installing.
- **Audio visualization/analysis:** use Songsee or Python audio tooling for spectrograms, mel, chroma, MFCC, or multi-panel feature grids.
- **Voice/audio reply packaging:** when the final deliverable must be heard by a user, verify the file is playable and delivered in the platform-compatible format.

## Quality rules

1. For songs, make the structure explicit (`[Verse]`, `[Chorus]`, `[Bridge]`, etc.) unless the target tool prefers prose prompt fields.
2. For AI music prompts, separate style/genre instructions from lyric content.
3. For generated files, report the actual path/URL and any real verification performed.
4. For local model generation, check disk/GPU/Python-version constraints before starting large downloads.

## References

- `references/absorbed-songwriting-heartmula-songsee.md` — songwriting craft, HeartMuLa bring-up notes, and Songsee CLI patterns.
- `references/absorbed-audio-voice-replies.md` — PC-side audible media verification and voice-reply packaging notes.
- `references/absorbed-aituber-hakua-audio.md` — AITuber OnAir, Hakua voice, and phone/VRM audio-routing setup notes.
