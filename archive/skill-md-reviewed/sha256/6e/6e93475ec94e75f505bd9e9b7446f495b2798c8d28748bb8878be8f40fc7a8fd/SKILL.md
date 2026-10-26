---
name: hermes-a2a-buzz-automation
description: "Multi-agent automation with A2A, Buzz, HyperFrames."
version: 0.1.0
author: Hermes Agent
platforms: [linux, macos, windows]
license: MIT
metadata:
  hermes.tags: [hermes, a2a, buzz, multi-agent, cron, video, automation]
  hermes.related_skills: [buzz-integration-hermes, lm-twitterer-operations, hyperframes, fishaudio-tts, cronjob-management]
---

# Hermes A2A + Buzz + Video Automation

Set up a multi-agent Hermes network where the default profile acts as
orchestrator, A2A peers (job-seeker, secretary, sedori-*, etc.) run as
bot profiles, a master heartbeat cron dispatches tasks, a Buzz Nostr
relay provides inter-agent messaging, and HyperFrames + FishAudio TTS
produce narrated videos posted to X via lm-twitterer.

## When to Use

- "Set up A2A between Hermes profiles"
- "Start a local Buzz relay for Hermes agents"
- "Create a master heartbeat that coordinates all bot profiles"
- "Make a narrated video with Hakua voice and post to X"
- "Wire up multi-agent task automation end to end"

## Prerequisites

- Hermes Agent installed (`hermes --version`)
- Docker Desktop running (for Buzz relay)
- Fish Audio API key (`FISH_AUDIO_API_KEY` in `.env`)
- Hakua cloned voice reference ID (UUID)
- lm-twitterer configured with `LM_TWITTERER_AUTH_TOKEN` + `LM_TWITTERER_CT0`
- Node.js >= 22, FFmpeg, npx (for HyperFrames)

## How to Run

All commands run through the `terminal` tool. Replace `<profile>`,
`<task>`, `<port>` with your values.

### 1. Enable A2A on the Default Profile (Hub)

```bash
hermes config set platforms.a2a.enabled true
hermes config set platforms.a2a.extra.port 9900
hermes config set platforms.a2a.extra.host 127.0.0.1
hermes config set a2a_agents.job-seeker.url "http://127.0.0.1:9901" --force
hermes config set a2a_agents.secretary.url "http://127.0.0.1:9902" --force
hermes config set a2a_agents.sedori-buyer.url "http://127.0.0.1:9903" --force
hermes config set a2a_agents.sedori-ledger.url "http://127.0.0.1:9904" --force
hermes config set a2a_agents.sedori-lister.url "http://127.0.0.1:9905" --force
hermes config set a2a_agents.sedori-researcher.url "http://127.0.0.1:9906" --force
hermes config set a2a_agents.sedori-secretary.url "http://127.0.0.1:9907" --force
hermes config set a2a_agents.sedori-shipper.url "http://127.0.0.1:9908" --force
hermes config set a2a_agents.delivery-worker.url "http://127.0.0.1:9909" --force
hermes config set a2a_agents.self-improver.url "http://127.0.0.1:9910" --force
```

Verify A2A loads on gateway start:
```
A2A: serving Agent Card + JSON-RPC on http://127.0.0.1:9900
```

### 2. Start the Buzz Nostr Relay

```bash
docker compose -f vendor/buzz/deploy/compose/compose.yml up -d
curl -sS --max-time 5 http://localhost:3000/
```

Create a channel:
```bash
BUZZ_RELAY_URL=http://localhost:3000 BUZZ_PRIVATE_KEY=<hex> \
  buzz channels create --name "Hermes Hub" --type stream --visibility open
```

### 3. Create the Master Heartbeat Cron

Use the `cronjob` tool to create a job that runs a Python script like
`scripts/master-heartbeat.py`:

- Schedule: `every 30m`
- Skills: `["ai-employee-org"]`
- Deliver: `origin,telegram`

The script iterates `PROFILES` dict and calls each via:
```bash
hermes -p <profile> --provider nous -m meituan/longcat-2.0:free chat -q '<task>'
```

### 4. Create a HyperFrames Video with Hakua Narration

```bash
cd ~/.hermes/hyperframes && npx hyperframes init my-video --non-interactive --example blank
```

Generate FishAudio narration per slide (via `plugins/fish_audio_tts/core.py`):
```python
from plugins.fish_audio_tts.core import synthesize_text
res = synthesize_text(text="...", voice="25d6710bcdf043a7b7441e58294431f9", model="s2.1-pro-free", output_format="mp3")
```

Render and combine:
```bash
npx hyperframes render --quality standard --output video_only.mp4 --fps 30
ffmpeg -i slide_1.mp3 ... -filter_complex "concat=n=6:v=0:a=1[out]" -map "[out]" narration.m4a
ffmpeg -i video_only.mp4 -i narration.m4a -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4
```

### 5. Post to X via lm-twitterer

```python
import sys; sys.path.insert(0, 'plugins')
# ... load core via importlib with hermes_plugins namespace ...
result = mod.post('', text='...', media_paths=['final.mp4'], dry_run=False)
```

## Quick Reference

| Tool | Command |
|------|---------|
| `a2a_list` | List configured peers + metrics |
| `a2a_discover(url)` | Fetch Agent Card from peer |
| `a2a_call(agent, message)` | Send task to peer |
| `a2a_orchestrate(capability, message)` | Fan-out by capability |
| `buzz_channel_create` | Create NIP-29 channel |
| `buzz_message_send` | Send message to channel |
| `buzz_relay_status` | Probe relay health |
| `hyperframes render` | Render HTML→MP4 |
| `fish_audio_tts_synthesize` | Generate Hakua voice |
| `lm_twitterer_post` | Post text+media to X |
| `cronjob` | Create/update scheduled jobs |

## Procedure

### A2A Peer Registration

1. Edit `~/.hermes/config.yaml` → add each profile under `a2a_agents`
2. Enable `platforms.a2a.enabled: true` on the hub profile
3. Restart gateway (`hermes gateway restart`)
4. Verify with `a2a_list` or curl `http://127.0.0.1:9900/.well-known/agent-card.json`

### Multi-Profile Orchestration

1. Create `scripts/master-heartbeat.py` with `PROFILES` dict mapping
   profile names to task lists
2. Create cron job via `cronjob` tool with `schedule: "every 30m"`
3. Script runs `hermes -p <profile> chat -q '<task>'` for each
4. Results aggregated as JSON and delivered to Telegram

### A2A Feedback Loop

After bot profiles complete tasks, they report results back to the
default profile via A2A. The default profile aggregates, then triggers
deep research via OpenManus / Research Desk.

1. Bot profiles write results to `~/.hermes/a2a_results/<profile>.json`
2. Default profile polls `a2a_list` for completed tasks
3. Interesting findings trigger `openmanus_run` or `research_desk_run`
4. Deep research results stored in Obsidian / Ebbinghaus memory
5. Summary posted to Buzz channel + Telegram

The **A2A Feedback** pane in hermes-bot-mode displays:
- Real-time status of the Master Heartbeat cron
- Results from each bot profile (click to expand)
- Deep research triggers (🔍 badge)
- Success/fail counts per run

### hermes-bot-mode Integration

The `hermes-bots` desktop plugin (at `~/.hermes/desktop-plugins/hermes-bots/`)
provides the UI for multi-agent coordination:

1. **Bots pane** (left): profile roster with avatars, click to chat
2. **Cronjobs pane** (right): per-profile scheduled routines
3. **A2A Feedback pane** (right): heartbeat results + deep research status

After editing `plugin.js`, the desktop app hot-reloads on save.
Fallback: Ctrl+K → "Reload desktop plugins".

### Deep Research Integration (OpenManus + Research Desk)

Use OpenManus for autonomous multi-step research. Use Research Desk
for structured reports with citations.

**OpenManus** — autonomous agentic research:
```bash
hermes openmanus run "Research <topic> and report findings"
```

**Research Desk** — structured reports with citation discipline:
```bash
hermes research-desk run --query "<topic>" --depth deep
```

**When to deep-dive:**
- Job-seeker finds promising role → Research Desk for company analysis
- Sedori-buyer finds arbitrage → OpenManus for market price verification
- Secretary flags important email → Research Desk for context research
- Self-improver finds skill gap → OpenManus for learning path research

### Video Production Pipeline

1. Scaffold HyperFrames project: `npx hyperframes init`
2. Write `index.html` with GSAP timeline (120s total, 20s per slide)
3. Generate narration: `synthesize_text()` per slide via Python import
4. Concatenate audio: `ffmpeg -filter_complex concat`
5. Render video: `npx hyperframes render --quality standard`
6. Merge: `ffmpeg -i video.mp4 -i audio.m4a -shortest`
7. Copy to `~/.hermes/lm-twitterer/media/` and post via `mod.post()`

### Buzz Channel Setup

1. Ensure Docker Desktop running: `docker info`
2. Start relay: `docker compose -f vendor/buzz/deploy/compose/compose.yml up -d`
3. Verify: `curl http://localhost:3000/` returns JSON
4. Create channel: `buzz channels create --name "Hermes Hub" --type stream --visibility open`
5. Post: `buzz messages send --channel <UUID> --content "..."`

## Pitfalls

- `hermes gateway run` is single-instance — cannot start multiple gateways simultaneously
- A2A `a2a_agents` keys are custom top-level keys (use `--force` with `hermes config set`)
- FishAudio `synthesize_text()` requires Python import, NOT the tool wrapper (tool wrapper has a dict/str bug)
- lm-twitterer media must live under `~/.hermes/lm-twitterer/media/` (path guard)
- X video limit is 2m20s (140s); trim if needed
- `hyperframes render` requires `chrome-headless-shell` (run setup.sh first)
- Buzz relay binds to community from `RELAY_URL` host; changing URL requires recreating channels
- A2A inbound text is filtered for prompt-injection (peers cannot invoke slash commands)

## Verification

- A2A: `curl http://127.0.0.1:9900/.well-known/agent-card.json` returns JSON
- Buzz: `curl http://localhost:3000/` returns relay info JSON
- Heartbeat: `cronjob(action='list')` shows job with next_run_at
- Video: `ffprobe -show_entries format=duration -of default=nw=1:nk=1 final.mp4` shows 120.0
- Post: `mod.post()` returns `{"ok": true, "posted": true, "url": "..."}`
