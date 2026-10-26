---
name: akari-video-english-release-pipeline
description: Create English videos via akari-video and FishAudio Hakua.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags:
      - AkariVideo
      - FishAudio
      - Hakua
      - ReleaseVideo
      - LmTwitterer
---

# Akari Video English Release Pipeline

Produce English-language release or intro videos using the `akari-video` kaisetsu-short template, FishAudio Hakua narration, and `lm_twitterer_post` for X/Twitter posting. This skill captures the exact headless workflow from project setup to social posting, including the synthetic VOICEVOX query generation required for English lip-sync.

## When to Use

- User wants an English intro or release video built with the `akari-video` kaisetsu-short template
- User wants FishAudio Hakua voice narration for English text (not VOICEVOX)
- User wants to post the resulting MP4 to X/Twitter via `lm_twitterer_post`
- User needs a reproducible headless pipeline that skips the full akari-video app

## Prerequisites

- `akari-video` monorepo at `%USERPROFILE%/Documents/New project/akari-video`
- Hermes fork venv Python (`py -3` inside `%USERPROFILE%/Documents/New project/hermes-agent`)
- FishAudio API key configured (`FISH_AUDIO_API_KEY` in `.env` or env var); verify with `fish_audio_tts_status`
- Hakua voice UUID: `25d6710bcdf043a7b7441e58294431f9`
- `puppeteer` installed in an ancestor `node_modules` of the akari-video repo
- Chrome installed via puppeteer: run `npx puppeteer browsers install chrome` in the akari-video dir
- `ffmpeg` on PATH
- `lm_twitterer` plugin configured with valid X cookies

## How to Run

1. Create a project dir under `templates/kaisetsu-short/<name>/` and add `project.json`, `script.json`, `channel.json`
2. Generate English WAVs by invoking `terminal` with a `py -3` snippet that calls `plugins.fish_audio_tts.core.synthesize_text`
3. Generate synthetic `query.json` files for lip-sync (VOICEVOX structure, English vowels mapped to `a/e/i/o/u`)
4. Run `generate-timeline.mjs` via `node -e "..."` inside the akari-video dir
5. Render with `render.mjs` (puppeteer + ffmpeg mux)
6. Copy the MP4 to `~/.hermes/lm-twitterer/media/`
7. Post with `lm_twitterer_post`

## Quick Reference

- Narration: `py -3 -c "from plugins.fish_audio_tts.core import synthesize_text; ..."`
- Query gen: `py -3 -c "import json, re; ..."` (synthetic VOICEVOX structure)
- Timeline: `node -e "import('./templates/kaisetsu-short/tools/generate-timeline.mjs').then(...)"`
- Render: `node templates/kaisetsu-short/tools/render.mjs <proj> --timeline <path> --out <path>`
- Post: `lm_twitterer_post(text=..., media_paths=[...], dry_run=false)`

## Procedure

### 1. Project Setup

Invoke through the `terminal` tool. Working directory: `%USERPROFILE%/Documents/New project/akari-video`.

```bash
cd "%USERPROFILE%/Documents/New project/akari-video"
mkdir -p templates/kaisetsu-short/<project-name>/{narration,assets,out}
```

Create three JSON files with `write_file` (or `terminal`). Representative contents:

**project.json**
```json
{"aspect":"portrait","fps":30,"script":"./script.json","channel":"./channel.json","narrationDir":"./narration","outDir":"./out","timing":{"leadIn":0.8,"beatGap":1.4,"tailHold":4.5}}
```

**script.json** (English example — note `sentenceOverride` is mandatory for English)
```json
{"speaker":{"engine":"fishaudio","voice":"hakua"},"titleCard":{"kicker":"Hermes Agent","main":"v0.20.3\nPatch Release","sub":"~125 PRs merged since v0.20.2"},"beats":[{"id":"s1-title","scene":"title","text":"Hermes Agent version 0.20.3 is here.","sentenceOverride":[{"text":"Hermes Agent version 0.20.3 is here.","t0":0.0,"t1":3.5}],"expression_plan":[{"expr":"surprised","holdCap":1.0},{"expr":"neutral"}],"visual":"Title card"},{"id":"s2-features","scene":"diagram","text":"Highlights: MCP 2.x SDK, Bot Mode plugin, CommandCode provider, Cua Driver 0.20, kanban/cron self-heal, session handoff fix.","sentenceOverride":[{"text":"Highlights:","t0":0.0,"t1":1.2},{"text":"MCP 2.x SDK,","t0":1.2,"t1":2.8},{"text":"Bot Mode plugin,","t0":2.8,"t1":4.4},{"text":"CommandCode provider,","t0":4.4,"t1":5.8},{"text":"Cua Driver 0.20,","t0":5.8,"t1":7.2},{"text":"self-healing fixes.","t0":7.2,"t1":9.0}],"expression_plan":[{"expr":"neutral"}],"visual":"Feature bullets","diagram":{"eyebrow":{"text":"Key Features","reveal":{"at":{"sentence":0,"offset":0},"dur":0.4}},"blocks":[{"id":"f1","type":"bullet-row","display":"flex","collapseWhenHidden":true,"mark":"✓","text":"MCP 2.x SDK","reveal":{"at":{"sentence":1,"offset":0},"dur":0.4}},{"id":"f2","type":"bullet-row","display":"flex","collapseWhenHidden":true,"mark":"✓","text":"Bot Mode plugin","reveal":{"at":{"sentence":2,"offset":0},"dur":0.4}},{"id":"f3","type":"bullet-row","display":"flex","collapseWhenHidden":true,"mark":"✓","text":"CommandCode provider","reveal":{"at":{"sentence":3,"offset":0},"dur":0.4}},{"id":"f4","type":"bullet-row","display":"flex","collapseWhenHidden":true,"mark":"✓","text":"Cua Driver 0.20","reveal":{"at":{"sentence":4,"offset":0},"dur":0.4}},{"id":"f5","type":"bullet-row","display":"flex","collapseWhenHidden":true,"mark":"✓","text":"Self-healing fixes","reveal":{"at":{"sentence":5,"offset":0},"dur":0.4}}]}},{"id":"s3-ending","scene":"ending","text":"Update now with hermes update.","sentenceOverride":[{"text":"Update now with hermes update.","t0":0.0,"t1":3.0}],"expression_plan":[{"expr":"happy"},{"expr":"neutral"}],"visual":"Follow CTA","endingReveal":{"at":{"sentence":0,"offset":1.0},"dur":0.5}}]}
```

**channel.json**
```json
{"character":{"assetsDir":"../../channel-sample/assets","files":{"neutral-closed":"fullbody-neutral-closed.png","neutral-half":"fullbody-neutral-half.png","neutral-open":"fullbody-neutral-open.png","happy":"fullbody-happy.png","sad":"fullbody-sad.png","angry":"fullbody-angry.png","surprised":"fullbody-surprised.png","laugh":"fullbody-laugh.png"},"sourceSize":{"width":1024,"height":1536},"personBBox":{"x":182,"y":70,"w":661,"h":1431}},"background":{"src":"../../channel-sample/assets/bg.png"},"brand":{"accent":"#cc6b49","accentDark":"#a04f34","ink":"#221f1f","inkSoft":"#6b625c","line":"#e2ddd6"},"sns":[{"icon":"x","caption":"@zapabob_ouj"},{"icon":"youtube","caption":"Hermes Agent"}]}
```

NOTE: `sentenceOverride` is mandatory for English. Without it the auto mora-based sentence splitter yields 0 sentences per beat and `generate-timeline.mjs` throws `sentence anchor index X が範囲外（文数=Y）`.

### 2. FishAudio Hakua English Narration

Invoke through `terminal`. Working directory: `%USERPROFILE%/Documents/New project/hermes-agent`.

```bash
cd "%USERPROFILE%/Documents/New project/hermes-agent"
py -3 -c "
from plugins.fish_audio_tts.core import synthesize_text
beats = [('s1-title','Hermes Agent version 0.20.3 is here.'),('s2-features','Highlights include MCP 2.x SDK migration, the bundled Bot Mode plugin, CommandCode provider, Cua Driver 0.20 runtime, kanban fixes, desktop remote-gateway healing, cron scheduler self-heal, and session handoff data-loss fixes.'),('s3-ending','Update now with hermes update.')]
out_dir = '%USERPROFILE%/Documents/New project/akari-video/templates/kaisetsu-short/<project-name>/narration'
for beat_id, text in beats:
    res = synthesize_text(text=text, voice='25d6710bcdf043a7b7441e58294431f9', model='s2.1-pro-free', output_path=f'{out_dir}/{beat_id}.wav')
    print(f'{beat_id}: {res[\"file_path\"]}')
print('ALL DONE')
"
```

### 3. Synthetic VOICEVOX query.json for lip-sync

The akari-video timeline generator requires `.query.json` for each beat even when narration is from FishAudio. Invoke through `terminal`.

```bash
cd "%USERPROFILE%/Documents/New project/hermes-agent"
py -3 -c "
import json, re
VOWEL_MAP = {'a':'open','e':'open','i':'half','o':'open','u':'half','ay':'open','ey':'open','oy':'open','aw':'open','ow':'open','iy':'half','uw':'half','ae':'open','ao':'open','aa':'open','ah':'half','eh':'half','ih':'half','oh':'open','uh':'half'}
def text_to_moras(text):
    words = re.findall(r'[a-zA-Z]+', text.lower())
    moras = []
    for word in words:
        i = 0
        while i < len(word):
            cons = ''
            while i < len(word) and word[i] not in 'aeiou': cons += word[i]; i += 1
            vowel = ''
            while i < len(word) and word[i] in 'aeiou': vowel += word[i]; i += 1
            if vowel:
                vl = vowel.lower()
                mouth = VOWEL_MAP.get(vl, 'open' if vl[0] in 'aeo' else 'half')
                moras.append({'text':(cons+vowel) if cons else vowel,'vowel':vowel[0].lower(),'consonant':cons[0] if cons else None,'consonant_length':0.05 if cons else None,'vowel_length':0.08,'pitch':5.0,'mouth_state':mouth})
    return moras
beats = [('s1-title','Hermes Agent version 0.20.3 is here.'),('s2-features','Highlights include MCP 2.x SDK migration, the bundled Bot Mode plugin, CommandCode provider, Cua Driver 0.20 runtime, kanban fixes, desktop remote-gateway healing, cron scheduler self-heal, and session handoff data-loss fixes.'),('s3-ending','Update now with hermes update.')]
for beat_id, text in beats:
    moras = text_to_moras(text)
    query = {'prePhonemeLength':0.1,'postPhonemeLength':0.1,'accent_phrases':[{'moras':moras,'accent':len(moras),'pause_mora':None,'is_interrogative':False}]}
    with open(f'narration/{beat_id}.query.json','w') as f: json.dump(query, f, indent=2, ensure_ascii=False)
    print(f'{beat_id}: {len(moras)} moras')
print('DONE')
"
```

NOTE: Valid vowels are `a`, `e`, `i`, `o`, `u`, `N`, `pau`, `cl`. Invalid vowels throw `未知の母音種別`.

### 4. Generate Timeline

Invoke through `terminal`. Working directory: `%USERPROFILE%/Documents/New project/akari-video`.

```bash
cd "%USERPROFILE%/Documents/New project/akari-video"
node -e "
import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import('./templates/kaisetsu-short/tools/generate-timeline.mjs').then(async m => {
  const r = await m.generateTimeline('templates/kaisetsu-short/<project-name>');
  const outDir = 'templates/kaisetsu-short/<project-name>/out';
  await mkdir(outDir, { recursive: true });
  await writeFile(path.join(outDir, 'timeline.json'), JSON.stringify(r.timeline, null, 2));
  console.log('Wrote timeline.json — beats:', r.timeline.beats.length, 'total:', r.timeline.total);
}).catch(e => { console.error('ERROR:', e.message); });
"
```

### 5. Render Video

Before first render, install Chrome:

```bash
cd "%USERPROFILE%/Documents/New project/akari-video"
npx puppeteer browsers install chrome 2>&1
```

Invoke through `terminal`:

```bash
cd "%USERPROFILE%/Documents/New project/akari-video"
node templates/kaisetsu-short/tools/render.mjs \
  templates/kaisetsu-short/<project-name> \
  --timeline templates/kaisetsu-short/<project-name>/out/timeline.json \
  --out templates/kaisetsu-short/<project-name>/out/final.mp4
```

Output: `final.mp4` ~45 sec, ~1.4MB (H.264 CRF 18, AAC 192k).

NOTE: If channel assets are missing (`ERR_FILE_NOT_FOUND` in page console), the render still succeeds but frames render with the CSS background color (white). Fix by ensuring `channel.json` `assetsDir` points to a directory that contains the PNG files listed in `character.files`.

### 6. Post to X via lm-twitterer

```bash
mkdir -p ~/.hermes/lm-twitterer/media
cp "%USERPROFILE%/Documents/New project/akari-video/templates/kaisetsu-short/<project-name>/out/final.mp4" \
   ~/.hermes/lm-twitterer/media/<project-name>.mp4
```

Post with `lm_twitterer_post`:

```
lm_twitterer_post(
    text="Hermes Agent v0.20.3 (2026.8.16.2) 🚀 ~125 PRs since v0.20.2\n\nMCP 2.x SDK • Bot Mode plugin\nCommandCode provider • Cua Driver 0.20\nKanban/cron/desktop self-heal\nSession handoff data-loss fix\n\nUpdate: hermes update\n\n#hermesagent はくあ",
    media_paths=["~/.hermes/lm-twitterer/media/<project-name>.mp4"],
    dry_run=false
)
```

NOTE: Tweet text must be under 280 characters (Japanese characters count as 2). If `CreateTweet returned errors: [{'code': 186...` appears, shorten the text.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `sentence anchor index X が範囲外（文数=Y）` | Missing `sentenceOverride` or wrong sentence count in `script.json` | Add `sentenceOverride` with explicit `t0`/`t1` for each beat |
| `AttributeError: 'NoneType' object has no attribute '__dict__'` on `core.py` import | System Python used instead of Hermes venv Python, or stale `.pyc` | Use Hermes fork `.venv` Python for plugin imports; clear `__pycache__` |
| Render succeeds but frames are blank/white | `ERR_FILE_NOT_FOUND` for channel assets (`assetsDir` path wrong or PNG files missing) | Verify `channel.json` `assetsDir` relative path; ensure PNG files exist |
| Tweet fails with error 186 (too long) | Tweet text exceeds 280 characters | Shorten text; Japanese characters count as 2 |
| `ENOENT: ... timeline.json` on `render.mjs` | `timeline.json` not written to the expected path | Write `timeline.json` explicitly to the project `out/` dir after `generate-timeline.mjs` |
| puppeteer `executablePath` points to a missing binary | Chrome not installed via puppeteer | `npx puppeteer browsers install chrome` (full Chrome, not just headless-shell) |
| FishAudio narration succeeds but `query.json` missing | `generate-timeline.mjs` requires both `.wav` AND `.query.json` per beat | Generate both; `query.json` can be synthetic (not from VOICEVOX) |
| `puppeteer` module not found | `puppeteer` absent from ancestor `node_modules` | Set env var `KAISETSU_PUPPETEER_PKG` to a `package.json` path that has `puppeteer`, or ensure akari-video's `node_modules` has it |

## Verification

- [ ] `narration/*.wav` files exist for all 3 beats
- [ ] `narration/*.query.json` files exist for all 3 beats
- [ ] `generate-timeline.mjs` outputs 3 beats with total ~45s
- [ ] `render.mjs` completes and `ffprobe` confirms duration ≈ timeline.total
- [ ] `final.mp4` exists under project `out/`, ~1-2MB
- [ ] `lm_twitterer_post` returns `posted: true` with a URL
- [ ] X post is visible at the returned URL with video attached

## See Also

- Parent pipeline concepts: `hyperframes-video-production` (shared TTS, posting, media path rules)
- `references/hakua-tts-integration.md` — FishAudio provider setup for the Hakua voice
- `references/v0202-release-workaround.md` — drive space / output fallback notes
