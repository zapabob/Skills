---
name: multi-agent-showcase-video
description: "Create and post narrated multi-agent showcase videos."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, multi-agent, tts, x-posting, hyperframes, fishaudio, lm-twitterer, buzz]
    category: creative
    related_skills: [hyperframes, fishaudio-tts, lm-twitterer-operations, hermes-a2a-multi-agent]
---

# Multi-Agent Showcase Video

Produce a narrated slideshow video showcasing your multi-agent AI system and post it to X/Twitter. This skill covers the **full pipeline**: HyperFrames slide composition → FishAudio TTS narration → ffmpeg assembly → lm-twitterer posting, plus optional Buzz relay setup for community announcements.

## When to Use

- User wants to create a promo/showcase video about their multi-agent setup
- Combining HyperFrames slides with TTS narration
- Posting a narrated video to X/Twitter via lm-twitterer
- Setting up Buzz relay for community messaging about the system
- End-to-end: "make a video about our AI agents and post it"

## Prerequisites

These skills must be installed and configured:
- `zapabob-skills/hyperframes` — video composition engine
- `fishaudio-tts` — TTS with cloned voice (Hakua)
- `lm-twitterer-operations` — X/Twitter posting
- `hermes-a2a-multi-agent` — A2A multi-agent setup (if showcasing inter-agent comms)

External services:
- FishAudio API key (`FISH_AUDIO_API_KEY` in `.env`)
- FishAudio cloned voice `reference_id` (Hakua: `25d6710bcdf043a7b7441e58294431f9`)
- X/Twitter cookies (`LM_TWITTERER_AUTH_TOKEN`, `LM_TWITTERER_CT0`)
- Docker Desktop (for Buzz relay)

## Procedure

### 1. Plan the Narrative

Before touching tools, define:
- **Duration**: 120 seconds is the X video limit (2min 20s absolute max, but 120s is safe)
- **Slides**: 6 scenes × 20 seconds each works well
- **Script**: Write narration text per slide (approx. 150-180 words per 20s slot at natural pace)
- **Visual identity**: Dark canvas (#0a0a0f) with purple accent (#6c5ce7) is the Hakua palette

### 2. Create HyperFrames Composition

```bash
cd ~/.hermes/hyperframes
npx hyperframes init <project-name> --non-interactive --example blank
```

**CRITICAL**: Every timed element MUST have `class="clip"` — HyperFrames uses this class to control visibility based on `data-start`/`data-duration`. Using any other class (e.g. `class="slide"`) triggers the `timed_element_missing_clip_class` lint error and the element stays visible for the entire composition.

```html
<!-- WRONG: class="slide" -->
<div id="slide1" class="slide" data-start="0" data-duration="20" data-track-index="1">

<!-- RIGHT: class="clip" -->
<div id="slide1" class="clip" data-start="0" data-duration="20" data-track-index="1">
```

**Animation pattern** (deterministic, paused timeline):

```javascript
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const slides = ["slide1","slide2","slide3","slide4","slide5","slide6"];
slides.forEach((id, i) => {
  const start = i * 20;
  tl.to("#" + id, { opacity: 1, visibility: "visible", duration: 0.5 }, start + 0.5);
  tl.from("#" + id + " .title", { y: 30, opacity: 0, duration: 0.8 }, start + 0.8);
  tl.from("#" + id + " .subtitle", { y: 20, opacity: 0, duration: 0.8 }, start + 1.2);
  tl.from("#" + id + " .card", { y: 40, opacity: 0, duration: 0.6, stagger: 0.1 }, start + 1.5);
  if (i < slides.length - 1) {
    tl.to("#" + id, { opacity: 0, visibility: "hidden", duration: 0.5 }, start + 19);
  }
});
window.__timelines["main"] = tl;
```

Render to video (no audio yet):

```bash
npx hyperframes render --quality standard --output video_only.mp4 --fps 30
```

### 3. Generate TTS Narration

**Use the core function directly** — the `fish_audio_tts_synthesize` tool wrapper is broken.

```bash
cd <hermes-fork>
py -3 <<'PY'
from plugins.fish_audio_tts.core import synthesize_text
import os, shutil

slides = ["Slide 1 text...", "Slide 2 text...", ...]

output_dir = os.path.expanduser("~/.hyperframes/<project>/audio")
os.makedirs(output_dir, exist_ok=True)

for i, text in enumerate(slides, 1):
    res = synthesize_text(
        text=text,
        voice="25d6710bcdf043a7b7441e58294431f9",
        model="s2.1-pro-free",
        output_format="mp3"
    )
    shutil.copy(res["file_path"], os.path.join(output_dir, f"slide_{i}.mp3"))
PY
```

**NOTE**: The keyword is `output_format`, not `format`. Using `format` raises `TypeError: synthesize_text() got an unexpected keyword argument 'format'`.

### 4. Combine Audio + Video

Concatenate per-slide audio files, pad to 120s, then mux with video:

```bash
cd ~/.hyperframes/<project-name>

# Concatenate all slide audio files
ffmpeg -y -i audio/slide_1.mp3 -i audio/slide_2.mp3 -i audio/slide_3.mp3 \
  -i audio/slide_4.mp3 -i audio/slide_5.mp3 -i audio/slide_6.mp3 \
  -filter_complex "[0:a][1:a][2:a][3:a][4:a][5:a]concat=n=6:v=0:a=1[out]" \
  -map "[out]" -c:a aac -b:a 192k narration.m4a

# Pad to exactly 120 seconds
ffmpeg -y -i narration.m4a -af "apad=whole_dur=120" -c:a aac -b:a 192k narration_120s.m4a

# Mux video + audio
ffmpeg -y -i video_only.mp4 -i narration_120s.m4a -c:v copy -c:a aac -b:a 192k \
  -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

### 5. Post to X/Twitter

Copy video to lm-twitterer media directory and post:

```bash
mkdir -p ~/.hermes/lm-twitterer/media
cp final.mp4 ~/.hermes/lm-twitterer/media/final.mp4
```

Then post via core module:

```bash
cd <hermes-fork>
py -3 <<'PY'
import os
os.environ['SSL_CERT_FILE'] = r'%USERPROFILE%\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem'
os.environ['REQUESTS_CA_BUNDLE'] = r'%USERPROFILE%\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem'
import sys
sys.path.insert(0, 'plugins')
import importlib.util

# Load plugin module chain
spec = importlib.util.spec_from_file_location('hermes_plugins', 'plugins/__init__.py')
mod0 = importlib.util.module_from_spec(spec); sys.modules['hermes_plugins'] = mod0; spec.loader.exec_module(mod0)
spec = importlib.util.spec_from_file_location('hermes_plugins.lm_twitterer', 'plugins/lm-twitterer/__init__.py')
mod0_5 = importlib.util.module_from_spec(spec); sys.modules['hermes_plugins.lm_twitterer'] = mod0_5; spec.loader.exec_module(mod0_5)
spec = importlib.util.spec_from_file_location('hermes_plugins.lm_twitterer.core', 'plugins/lm-twitterer/core.py')
mod = importlib.util.module_from_spec(spec); sys.modules['hermes_plugins.lm_twitterer.core'] = mod; spec.loader.exec_module(mod)

result = mod.post(
    '',
    text='Your post text here #hashtag',
    media_paths=[r'%USERPROFILE%\.hermes\lm-twitterer\media\final.mp4'],
    dry_run=False
)
print(mod._json(result))
PY
```

## SSL Certificate Workaround (Windows)

lm-twitterer fails with `Could not find a suitable TLS CA certificate bundle` because the cert path gets mangled (`C:Usersdownl...`). Fix by setting env vars before the request:

```python
import os
os.environ['SSL_CERT_FILE'] = r'%USERPROFILE%\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem'
os.environ['REQUESTS_CA_BUNDLE'] = r'%USERPROFILE%\AppData\Local\Programs\Python\Python312\Lib\site-packages\certifi\cacert.pem'
```

Verify certifi location: `py -3 -c "import certifi; print(certifi.where())"`

## Buzz Relay Setup (Optional)

If announcing via Buzz Nostr relay:

1. Start Docker Desktop
2. Set `RELAY_URL=ws://localhost:3000` in `vendor/buzz/deploy/compose/.env`
3. Reset DB volumes if switching from a previous community (ngrok URL is baked into Postgres): `docker compose -f vendor/buzz/deploy/compose/compose.yml down -v`
4. Start: `docker compose -f vendor/buzz/deploy/compose/compose.yml up -d`
5. Verify: `curl -sS http://localhost:3000/` (should return JSON relay info)

**NIP-98 auth error** (`URL mismatch: event has http://... expected https://...`): The community was seeded with a different `RELAY_URL`. Reset DB volumes and restart with consistent URL.

## Hub-Spoke A2A Pattern (for reference)

When showcasing multi-agent communication, use the hub-spoke pattern:

```
[default :9900] ← A2A server (hub)
    ├─ hermes -p job-seeker --provider nous -m meituan/longcat-2.0:free chat -q '<task>'
    └─ hermes -p secretary --provider nous -m meituan/longcat-2.0:free chat -q '<task>'
```

Same-machine multi-gateway is blocked by PID file — one profile runs A2A server, others are invoked one-shot. See `hermes-a2a-multi-agent` skill for details.

## Pitfalls

- **HyperFrames `class="clip"`**: Timed elements without this class stay visible for the entire composition. Always add `class="clip"` to elements with `data-start`/`data-duration`.
- **FishAudio kwarg**: Use `output_format="mp3"`, not `format`.
- **SSL cert on Windows**: Always set `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` before lm-twitterer posting.
- **Profile provider mismatch**: When invoking other profiles, pair `-m <model>` with `--provider <provider>`. Using `-m` alone routes to the default provider and may 404.
- **Buzz community binding**: Changing `RELAY_URL` after first start creates a new community — old channels vanish. Reset DB (`down -v`) when switching URLs.
- **Video duration**: X enforces 2min 20s max. Keep videos at 120s for safety margin.

## References

- `references/hyperframes-class-clip.md` — why `class="clip"` is required and the lint error it prevents
- `references/ssl-cert-fix.md` — Windows SSL cert workaround for lm-twitterer
- `references/buzz-relay-local-setup.md` — Docker compose, community binding, NIP-98 auth
