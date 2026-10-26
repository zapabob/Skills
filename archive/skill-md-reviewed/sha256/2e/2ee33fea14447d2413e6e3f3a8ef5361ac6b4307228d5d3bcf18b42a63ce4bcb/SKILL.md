---
name: lm-twitterer-operations
description: "Complete lm-twitterer plugin guide: posting, reply-to-mentions, mention scanning, SearchTimeline→HomeLatestTimeline fallback (mid-2026), Ebbinghaus memory bridge, cron integration, and known pitfalls."
version: 1.0.0
author: Hermes Agent
tags: [lm-twitterer, x, twitter, social-media, ebbinghaus-memory, xurl]
---

# LM-Twitterer Operations

## Overview

`lm-twitterer` is a Hermes plugin for X/Twitter interactions using cookie-based authentication (GraphQL API, no OAuth). Supports posting, replying to mentions, scanning mention candidates, media uploads, and optional Ebbinghaus memory alignment.

Plugin location: `plugins/lm-twitterer/` (in the Hermes repo).
Core module: `plugins/lm-twitterer/core.py` (~75KB, ~2000 lines).

## Setup & Dependencies

### Python dependencies (in Hermes venv)

```bash
uv pip install 'twitter-openapi-python>=0.0.44,<0.1'
uv pip install 'tweepy-authlib>=1.7.3,<2'  # for media upload
```

### Environment variables (in `~/.hermes/.env`)

```ini
LM_TWITTERER_AUTH_TOKEN=<value>
LM_TWITTERER_CT0=<value>
LM_TWITTERER_BOT_SCREEN_NAME=zapabob_ouj
```

Optional:
```ini
LM_TWITTERER_WHITELIST_FILE=~/.hermes/lm-twitterer/whitelist.txt
LM_TWITTERER_REQUIRED_HASHTAG=hashtag
LM_TWITTERER_SIGNATURE_REPLIES=true
LM_TWITTERER_IDENTITY_NAME=Hakua
LM_TWITTERER_MAX_REPLIES_PER_RUN=3
LM_TWITTERER_REQUIRE_FOLLOWER=false
```

### Whitelist

Whitelist file (default: `~/.hermes/lm-twitterer/whitelist.txt`):
```
user1
user2
```

## Authentication

Cookie-based via `auth_token` + `ct0`. No OAuth required for GraphQL API.

### Verify authentication

```python
def check_auth():
    import sys
    sys.path.insert(0, 'plugins')
    spec = importlib.util.spec_from_file_location('core', 'plugins/lm-twitterer/core.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.auth_check()
    print(mod._json(result))
```

Or via CLI: `hermes lm-twitterer auth-check` (when plugin CLI is registered).

**Note**: `auth_check` shows `v11_verify_credentials_http_status` which may be 404 (v1.1 deprecated). The GraphQL read path is the working auth mechanism.

## Core Operations

### 1. Post a tweet

**Function**: `post(topic, text, dry_run, provider, model, media_paths)`

- `topic`: generation topic (max 240 chars). Empty = configured default.
- `text`: exact text (bypasses generation). Prefer this over `topic` for reliable posting.
- `dry_run`: True = generate without posting. Default: True.
- `provider`/`model`: optional LLM override.
- `media_paths`: optional list of local files for media.

**Pattern**:
```python
result = mod.post("", text="Exact post text", dry_run=False)
```

**Return**: `{"ok": true, "posted": true, "url": "https://x.com/...", "tweet_text": "...", "media_ids": [...]}`

### 2. Reply to mentions

**Function**: `reply_mentions(dry_run, count, mark_seen_on_dry_run, provider, model)`

1. Fetches mentions via `_graphql_search_timeline_items()` (with 404 fallback — see SearchTimeline section)
2. Filters by whitelist and optional `require_follower`
3. For each qualifying mention: fetches thread context → generates reply → posts reply via `_graphql_create_tweet()`
4. Respects `max_replies_per_run` to avoid rate limits

**Limitation**: Since SearchTimeline is deprecated, the HomeLatestTimeline fallback only shows mentions from followed accounts (typically whitelisted users).

### 3. Mention scanning (read-only)

**Function**: `mention_candidates(count, max_text_chars)`

Returns candidates with status: `whitelisted`, `not_whitelisted`, `already_replied`, `not_follower_ignored`.

### 4. Status

**Function**: `status()`

Reports: state dir, whitelist count, bot screen name, auth_token/ct0 presence, effective provider/model, media upload capability.

## SearchTimeline → HomeLatestTimeline Fallback (mid-2026)

### Background

In mid-2026, X **deprecated** the SearchTimeline GraphQL endpoint (`queryId: Yw6L66Pw54NHKuq4Dp7b4Q`). Both v1.1 `/1.1/search/tweets.json` and v2 `/2/tweets/search/recent` were also unavailable (404 or OAuth-required).

**Impact**: `lm_twitterer_mentions` and `lm_twitterer_reply_mentions` returned HTTP 404.

### Diagnosis Technique

When an X GraphQL endpoint returns 404 or unexpected data, probe the raw API with `urllib` to discover the actual response structure. See `references/x-api-graphql-probing.md` for the exact technique.

Key finding from this session: the HomeLatestTimeline response lives at `data.home.home_timeline_urt.instructions[]`, NOT `home_timeline_u` as some code assumed. Dumping the full JSON response revealed the real path.

### Verified Endpoint Status

| Endpoint | Status |
|----------|--------|
| `CreateTweet` | ✅ |
| `HomeLatestTimeline` | ✅ |
| `TweetDetail` | ✅ |
| `UserByScreenName` | ✅ |
| `SearchTimeline` | ❌ 404 |
| v1.1 `search/tweets.json` | ❌ 404 |
| v2 `tweets/search/recent` | ❌ 403 (needs OAuth) |

### Code Change (applied to `plugins/lm-twitterer/core.py`)

**New function**: `_graphql_home_timeline_items(cfg, count)`
Fetches authenticated user's home timeline via `HomeLatestTimeline` GraphQL.

- queryId: `0dateTVgvXjpkf7kyBZy0g`
- Response path: `data.home.home_timeline_urt.instructions[]`
- Variables: `{"count": N, "includePromotedContent": false}`

**Modified function**: `_graphql_search_timeline_items()`
Wraps SearchTimeline call in `try/except HTTPError(404)`:

```python
try:
    data = _placeholder_graphql_get(cfg, "SearchTimeline", variables)
except urllib.error.HTTPError as exc:
    if exc.code == 404:
        all_items = _graphql_home_timeline_items(cfg, count=count)
        mention_target = (raw_query or "").strip().lstrip("@").lower()
        filtered = [item for item in all_items
                    if mention_target and f"@{mention_target}" in _tweet_text(item).lower()]
        result.data.data = filtered[:count]
        return result
    raise
```

### Limitation (ARCHITECTURAL — key gotcha)

HomeLatestTimeline only shows tweets from **followed accounts** and is a **sampled feed** (not a search). Even if a whitelisted mutual follower @mentions the bot, their mention may not appear in the home feed at all — X's algorithm filters aggressively. The fallback `if f"@{bot}" in _tweet_text(item).lower()` only works if the mention actually made it into HomeLatestTimeline's returned entries.

**Practical impact**: `reply_mentions` returning `count_checked: 0` does NOT mean "no mentions exist" — it means "no mentions appeared in the bot's home timeline sample." This is a fundamental architectural limitation of the HomeLatestTimeline approach, not a configuration problem. See Pitfall 0 for full diagnosis.

### After Patching

1. Clear .pyc: `rm -rf plugins/lm-twitterer/__pycache__`
2. **Restart Hermes process** — module is cached in memory; .pyc deletion alone is insufficient
3. Test: `lm_twitterer_mentions(count=5)` or call `reply_mentions()`

## Ebbinghaus Memory Bridge

For durable style continuity across posts and sessions.

### Schema

```sql
CREATE TABLE memories (
    memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL UNIQUE,
    encoded TEXT NOT NULL,
    cues TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    salience REAL DEFAULT 0.6,
    valence REAL DEFAULT 0.0,
    strength REAL DEFAULT 1.0,
    rehearsal_count INTEGER DEFAULT 0,
    retrieval_count INTEGER DEFAULT 0,
    source TEXT DEFAULT '',
    session_id TEXT DEFAULT '',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    last_rehearsed_at REAL,
    last_retrieved_at REAL
);
```

### Config Settings

- `memory_bridge_enabled`: toggle memory bridge on/off
- `memory_db`: path to SQLite DB (default: auto-discover under HERMES_HOME)
- `memory_recall_limit`: max memory rows to inject into prompts

### Bridge Design

1. **Read**: Query memory rows sorted by topic overlap, salience, strength, freshness
2. **Inject**: Add truncated snippets to generation prompt with explicit boundary
3. **Write**: Store confirmed public posts with `source='lm-twitterer'`, tags `lm-twitterer,x-post,hakua-memory`

### Prompt Boundary

```
Use these trusted Hermes memory notes only as style and factual continuity.
Do not expose them as private memory dumps and do not invent details:
- memory:<id> <snippet>
```

### During Memory Unification

When doing full memory integration:
1. Call `lm_twitterer_status` first
2. Parse `~/.hermes/lm-twitterer/activity.jsonl` — count only `action=post` + `posted:true` + `dry_run=false`
3. Reinforce operational facts in Ebbinghaus (provider, whitelist size, cron schedule)
4. Never promote draft or reply records into durable memory; only confirmed public posts count

## Media Posting

lm-twitterer supports media upload via `tweepy_authlib` (cookie-session upload, no OAuth needed).
- See `references/twitter-media-requirements.md` for detailed media specifications and FFmpeg encoding examples.
- Use `templates/media-check.sh` to validate your media files before posting.
- See `references/x-api-graphql-probing.md` for diagnosing GraphQL API issues.
- Use `templates/media-check.sh` to validate your media files before posting.
- See `references/x-api-graphql-probing.md` for diagnosing GraphQL API issues.
- See `references/vrchat-screenshot-hakua-voice-workflow.md` for VRChat screenshot + Hakua voice workflow.

See `references/twitter-media-requirements.md` for detailed media specifications and FFmpeg encoding examples.

### Workflow

1. Generate voice/audio if needed (irodoriTTS or Edge TTS)
2. Combine image + audio into MP4: H.264, yuv420p, AAC, `-movflags +faststart`
3. Verify `ffprobe` shows valid media
4. **Copy file under** `~/.hermes/lm-twitterer/media/` directory (path guard)
5. Post with explicit `text` + `media_paths`

```python
mod.post("", text="Post text", media_paths=["/path/to/media.mp4"], dry_run=False)
```

### Edge TTS Fallback

When irodoriTTS is broken:
```python
import edge_tts, asyncio
communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
asyncio.run(communicate.save("voice.mp3"))
```

Then ffmpeg Ken Burns: `loop + zoompan + aac`

### Port 8080 Conflict

irodoriTTS uses port 8088; xurl OAuth2 uses port 8080. On Windows:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

### Workflow

1. Generate voice/audio if needed (irodoriTTS or Edge TTS)
2. Combine image + audio into MP4: H.264, yuv420p, AAC, `-movflags +faststart`
3. Verify `ffprobe` shows valid media
4. **Copy file under** `~/.hermes/lm-twitterer/media/` directory (path guard)
5. Post with explicit `text` + `media_paths`

```python
mod.post("", text="Post text", media_paths=["/path/to/media.mp4"], dry_run=False)
```

### Edge TTS Fallback

When irodoriTTS is broken:
```python
import edge_tts, asyncio
communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
asyncio.run(communicate.save("voice.mp3"))
```

Then ffmpeg Ken Burns: `loop + zoompan + aac`

### Port 8080 Conflict

irodoriTTS uses port 8088; xurl OAuth2 uses port 8080. On Windows:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

1. Generate voice/audio if needed (irodoriTTS or Edge TTS)
2. Combine image + audio into MP4: H.264, yuv420p, AAC, `-movflags +faststart`
3. Verify `ffprobe` shows valid media
4. **Copy file under** `~/.hermes/lm-twitterer/media/` directory (path guard)
5. Post with explicit `text` + `media_paths`

```python
mod.post("", text="Post text", media_paths=["/path/to/media.mp4"], dry_run=False)
```

### Edge TTS Fallback

When irodoriTTS is broken:
```python
import edge_tts, asyncio
communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
asyncio.run(communicate.save("voice.mp3"))
```

Then ffmpeg Ken Burns: `loop + zoompan + aac`

### Port 8080 Conflict

irodoriTTS uses port 8088; xurl OAuth2 uses port 8080. On Windows:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

### Workflow

1. Generate voice/audio if needed (irodoriTTS or Edge TTS)
2. Combine image + audio into MP4: H.264, yuv420p, AAC, `-movflags +faststart`
3. Verify `ffprobe` shows valid media
4. **Copy file under** `~/.hermes/lm-twitterer/media/` directory (path guard)
5. Post with explicit `text` + `media_paths`

```python
mod.post("", text="Post text", media_paths=["/path/to/media.mp4"], dry_run=False)
```

### Edge TTS Fallback

When irodoriTTS is broken:
```python
import edge_tts, asyncio
communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
asyncio.run(communicate.save("voice.mp3"))
```

Then ffmpeg Ken Burns: `loop + zoompan + aac`

### Port 8080 Conflict

irodoriTTS uses port 8088; xurl OAuth2 uses port 8080. On Windows:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

## Cron Integration

### Safe Script Pattern

For no-agent cron jobs (`no_agent: true`):
1. Use direct `plugins/lm-twitterer/core.py` import, not CLI
2. Keep stdout clean: only success URLs/status, no cookie/secret dumps
3. Validate path env vars (`HERMES_REPO_ROOT`, `HERMES_PYTHON`) before shelling out
4. When the launcher lives under `~/.hermes/scripts` but imports a plugin from the repository, insert the repository root into `sys.path` before loading `core.py`; otherwise imports such as `hermes_constants` fail even when the plugin itself is healthy.
5. After changing the deployed script, apply the same change to the repository copy and run the operational-script sync before the next cron tick.
6. **Topic bank versioning**: Store topics in `~/.hermes/lm-twitterer/topics_v<NN>.json` (versioned by campaign, e.g. `topics_v026.json`). Store rotation state in `~/.hermes/lm-twitterer/rotation_state_v<NN>.json`. Each campaign (version intro, workstation harness, etc.) gets its own versioned files to avoid confusion when pivoting campaigns.

### Provider/Model in Cron

**Dynamic resolution pattern (preferred for no-agent scripts):**
- no-agent cron scripts (`no_agent: true`) run as standalone processes and do NOT inherit the Hermes session's current provider/model.
- **Best practice**: at cron execution time, read `config.yaml`'s `model.provider` and `model.default` dynamically, so every cron tick uses whatever the user has set as their main AI.
- Resolution order:
  1. Explicit env var override (e.g. `LM_TWITTERER_PROVIDER` / `LM_TWITTERER_MODEL`)
  2. `config.yaml` → `model.provider` + `model.default` (read at runtime)
  3. Sensible hardcoded fallback (e.g. `openai-codex` / `gpt-5.5`)
- **Do NOT** hardcode a static provider/model string in the prompt template — that locks the cron to a model that may not match the user's active configuration.
- Example pattern: a `_resolve_provider_model()` function that checks `yaml.safe_load(config_path.read_text())` for `raw["model"]["provider"]` and `raw["model"]["default"]`.

**Legacy guidance (outdated — avoid):**
- Previously recommended "omit provider/model entirely." This does not work well for no-agent cron because the spawned process has no session context and may fall back to a stale default or fail entirely.

### Cron Troubleshooting

- If `lm_twitterer_mentions` crashes with `AttributeError: 'NoneType' object has no attribute 'group'`: the `twitter-openapi-python` read path is broken by an X web change. `auth_check` and exact-text posting may still work. Pause mention-reply cron.
- If 404 persists after patching: restart Hermes process (module cache).
- Verify the cron Python has `twitter_openapi_python` installed in its venv.

### Reply-Cron Diagnosis Order

When Hakua's automatic replies are not appearing, inspect the scheduler before changing credentials:

1. Call `cronjob(action='list')` and find every reply-mentions job. Keep one canonical live job; duplicate jobs can produce conflicting results and hide failures.
2. Check `last_status`, `last_delivery_error`, `enabled`, `script`, `workdir`, and whether `provider`/`model` are null. A no-agent reply cron should use a standalone script that resolves an explicit provider/model at runtime, or the cron must set them explicitly.
3. Run the standalone script with `LM_TWITTERER_CRON_PREFLIGHT_ONLY=1` through the `terminal` tool, then call `lm_twitterer_mentions(count=20)`. Keep this read-only during diagnosis.
4. Interpret `auth_valid: true`, configured cookies, dependency availability, and `candidate_count: 0` separately. Healthy auth plus zero candidates points to the X read path, not credentials.
5. If `SearchTimeline` is returning 404, treat `HomeLatestTimeline` fallback results as a sampled home feed, not exhaustive mention search. A missing candidate does not prove that no mention exists.
6. Do not lower `require_follower` as the first fix when the candidate list is empty; that setting only affects filtering after a mention is surfaced.

For the full reproduction and evidence pattern from the X timeline change, see `references/reply-cron-diagnosis.md`.

### Campaign Pivot Pattern

When the user asks to discontinue old version introductions and start a new campaign (e.g., "Windows native AI workstation harness"), follow the procedure in `references/campaign-pivot-pattern.md`. Key points:
- Pause ALL old-version crons (don't delete — preserve history)
- Create versioned topic bank: `~/.hermes/lm-twitterer/topics_v<NN>.json`
- Create versioned rotation state: `~/.hermes/lm-twitterer/rotation_state_v<NN>.json`
- 15-25 angles per campaign, each under 270 chars (script appends hashtag)
- Angles should be verifiable facts (port numbers, file counts, concrete capabilities), not marketing fluff

+### Feature Rotation for Automated Tweets
+
+For the user's specific cron job (every 6 hours) that posts buzzworthy tweets about Hermes v0.18.0 features, we implemented a feature rotation system. The lm-twitterer plugin already provides a rotation mechanism via `~/.hermes/lm-twitterer/rotation_state.json` which tracks used feature IDs. Each execution:
+
+1. Reads the rotation state from `~/.hermes/lm-twitterer/rotation_state.json` (contains `used_ids` array and `last_updated` timestamp).
+2. Selects an unused feature ID from the v0.18.0 features list (1-13 as defined in the task description).
+3. Marks the selected ID as used in the rotation state.
+4. If all features have been used, resets the tracking (optional: based on configuration).
+5. Forms the tweet text by appending " #hermesagent はくあ" and truncating to 140 characters if needed.
+6. Posts the tweet via `lm_twitterer_post` with `dry_run=false` (explicit text, so provider/model are ignored).
+
+This ensures each tweet features a different aspect of the release while preserving state between executions using the plugin's built-in rotation tracking.
+
+Alternative approaches include storing state in a custom file (e.g., `last_index.txt` or `tweet_index.txt`) and selecting from a template file (e.g., `topics.txt`), as shown in the pseudocode examples below.

 ## v0.18.2 Patch-Release Feature Rotation

For recurring release-buzz cron posts, treat v0.18.2 as a patch release rather than replaying the v0.18.0 feature list. The durable factual anchors are: v2026.7.7.2 (July 7, 2026), same-day patch on v0.18.1, WhatsApp Baileys moved from a Git commit pin to published npm `7.0.0-rc13`, and improved tagged-release installation/Docker build reliability. v0.18.1 context may be used as secondary scale—about 660 PRs, 667 commits, and about 990 files—but do not attribute that whole change volume to v0.18.2 itself.

Recommended rotation angles include dependency reproducibility, Docker downstream reliability, WhatsApp pairing, Windows updater/self-healing, dashboard/gateway/MCP/provider stabilization, and the release philosophy of fixing “can install/build” before adding flashy features. Keep v0.18.0 features such as MoA, `/learn`, `/journey`, Projects, and evidence-based completion as background only; do not present them as new in v0.18.2.

For a 6-hour live-post cron, update the existing job in place rather than creating a duplicate. Preserve the schedule and `dry_run=false` behavior. Store selected angle IDs in `~/.hermes/lm-twitterer/rotation_state.json`, prefer unused IDs, reset only after the complete angle set is consumed, and pass the final copy through `lm_twitterer_post(text=..., dry_run=false)` so provider generation cannot silently rewrite the facts. After a manual test run, verify the cron execution reports success and inspect the resulting activity/output for a real post URL; do not infer a URL from execution success alone.

## v0.19.0 Feature Rotation (Quicksilver) — ID Mapping

The 6-hourly `hermes-viral-tweets-v018` cron rotates 13 feature angles for Hermes v0.19.0. The canonical list with details lives at `~/.hermes/lm-twitterer/topics_v019.json` (IDs 1-13). Confirmed from past run logs: **ID 10 = new providers** (Fireworks/DeepInfra/Upstage Solar), **ID 13 = session export** (`sessions export` MD/Quarto/HTML/HF + `--redact`). IDs 1-9 were reconstructed from the 07-31/08-01 overview posts. When all 13 are consumed, reset `rotation_state.json` to start a fresh cycle; prefer unused IDs. Recent posts to avoid immediate duplication: 2026-08-01 posted ID 4 (`/subscription`・`/topup` ターミナルでのサブスク管理). Always verify copy against the release notes before posting (GitHub release page 404s publicly — use the cached copy in `~/.hermes/cache/web/github.com-792184261a.md` or the skill reference).

## Provider/Model Override Rules

1. Plugin allowlists (`plugins.entries.lm-twitterer.llm.allowed_providers` / `allowed_models`) are **strict** and independent of global Hermes defaults
2. Global defaults are often NOT in plugin allowlists
3. **Always pass explicit `provider` + `model` from the allowlists** when overriding; don't rely on defaults
4. For this user's cron jobs, omit overrides unless explicitly specified

## Known Pitfalls

### 0. Zero Candidates / Mentions Not Surfacing

Symptom: `count_checked: 0`, `candidate_count: 0`, despite expecting recent mentions.

Diagnostic sequence:
1. `lm_twitterer_status` — verify `bot_screen_name_set`, `auth_token_set`, `ct0_set`, `whitelist_count`.
2. `lm_twitterer_mentions(count=10)` — inspect `candidates[]` presence, not just counts.
3. If `candidates` is empty but the bot was recently @mentioned: the mentioning account may not be followed, and the active timeline source may not surface their mention.
4. If candidates exist but are skipped: check `not_follower_ignored` counts vs `whitelist_count` to separate "no mention data" from "filtered out".

**Critical root cause (mid-2026+):** `SearchTimeline` is deprecated (404). The `HomeLatestTimeline` fallback is a **home timeline feed**, not a mention search. It returns ~20-100 tweets from the bot's home feed. The fallback filter then checks `if f"@{bot}" in _tweet_text(item).lower()` — but if the @-reply to the bot never appeared in the bot's home feed (even from a followed/whitelisted account), it will **never be detected**. Key reasons a mention may not appear in HomeLatestTimeline:
   - The tweet was algorithmically suppressed (low engagement signals)
   - The mention was a reply in a chain the bot doesn't follow
   - The mention was posted while the bot's timeline was idle
   - HomeLatestTimeline is a **sample**, not exhaustive — X's algorithmic feed filters aggressively

**Definitive diagnosis**: patch `_graphql_home_timeline_items()` temporarily to log or return the raw tweet IDs/texts it fetched. If `@zapabob_ouj` appears nowhere in those raw entries, the HomeLatestTimeline simply did not surface the mention — not a permission/whitelist/config issue.

Fix patterns:
- Confirm the mentioning account is in `whitelist.txt`.
- **Preferred (フォローバック運用):** If `require_follower: true` and the mention comes from a whitelisted mutual follower who the bot follows back, but HomeLatestTimeline still doesn't surface it, the limitation is architectural. Consider a periodic `UserByScreenName` + `TweetDetail` probe for the whitelisted accounts' most recent tweets, or explore X v2 API (OAuth 2.0) for real mention search.
- _Alternative:_ Set `require_follower: false` — this removes the follower check but does NOT fix the HomeLatestTimeline sampling issue. The mention still needs to appear in the home feed to be detected.
- After any `core.py` patch, restart Hermes (module cache).

### 1. Module Cached in Process

After patching `core.py`, the running Hermes process still has old code. You MUST restart Hermes or spawn a fresh process. `.pyc` deletion is NOT enough.

### 2. Response Deserialization Failures

`twitter-openapi-python` can raise `ValidationError` during response parsing even when X returned a valid response. Use raw `post_create_tweet_without_preload_content` to bypass wrapper and parse JSON directly.

### 3. URL After Successful Post

`_tweet_url_from_result()` can return `""` even though the tweet IS live. Recovery:
- `_find_recent_tweet_url_by_text(client, cfg, text[:80])` from core.py
- Check `~/.hermes/lm-twitterer/activity.jsonl`
- Visit `https://x.com/<screen_name>` manually

### 4. `topic` + `dry_run=false` Validation Error

The generation path can fail with pydantic `ValidationError`. Workaround:
```python
# Prefer this pattern:
result = mod.post("", text="Exact draft text", dry_run=False)
```

### 5. Accidental Quote State

The CreateTweet default variables can contain an Elon Musk `attachment_url?`. Clear it:
```python
variables.attachment_url = None
variables.reply = None  # unless replying
```
DO NOT set `variables.media = None` on newer pydantic clients (required model field).

### 6. Whitelist Follower Requirement — フォローバック運用 優先

If `require_follower: true` and a whitelisted user doesn't follow back, their mention is skipped.

**User preference (this Hermes instance):** prefer **フォローバック運用** (follow-back operation) over lowering `require_follower=false`. The bot should follow whitelisted accounts whose mentions should be replied to. Only set `require_follower: false` as a fallback when following back is not possible or the whitelisted user explicitly unfollowed.

Even with フォローバック運用 (`require_follower=true` + mutual follow), mentions can still be missed if HomeLatestTimeline does not surface them (see Pitfall 0).

**User preference**: when mentions are blocked by follower checks, prefer **フォローバック運用** over lowering `require_follower`. The bot should follow whitelisted accounts whose mentions should be replied to. Only set `require_follower: false` when following back is not possible.

**Cron prompt clause for follow-back operation** (example wording to include when creating a reply-mentions cron job under this policy):
`フォローバック維持: 返信したいメンションが発生した場合、まず対象アカウントをフォローしてから返信する運用とする。`

### 7. Two Python Environments

`lm_twitterer_status` probes the tool wrapper's Python, NOT the terminal Python. A `twitter_dependency_available: false` status doesn't mean posting is impossible — verify by importing the plugin from terminal.

**Windows / Python 3.13 `js2py_` repair:** If live posting returns `No module named 'js2py_'`, check the exact Hermes venv rather than the global interpreter. `tweepy-authlib` expects the Python-3.13-compatible distribution `Js2Py_3.13`:

```bash
HERMES_VENV="C:/Users/<user>/Documents/New project/hermes-agent/.venv/Scripts/python.exe"
uv pip install --python "$HERMES_VENV" "Js2Py_3.13==0.74.1"
"$HERMES_VENV" -c "import js2py_; print(js2py_.__file__)"
```

Then retry the live post in a fresh Hermes tool call. Do not install the package only into the global Python, because the plugin may execute in the repository `.venv`.

### 8. Media File Path Issues (Error Code 3)

When posting media returns error code 3 ("media file not found") despite the file existing:
- Verify the file is under `~/.hermes/lm-twitterer/media/` directory (path guard)
- Ensure the filename contains only ASCII characters and no spaces
- Check that the file is a valid MP4 with H.264 video and AAC audio (use `ffprobe` to verify)
- Try copying the file again to the media directory - sometimes the plugin watches for new files
- The `media_paths` argument must be a path relative to the media directory (e.g., `myvideo.mp4`) or an absolute path that lies inside the media directory. Paths outside will be rejected with error code 3.
- As a workaround, test with a simple generated video first:
  ```bash
  ffmpeg -f lavfi -i color=c=black:s=320x240:d=1 -f lavfi -i sine=frequency=440:duration=1 -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest /tmp/test.mp4
  cp /tmp/test.mp4 ~/.hermes/lm-twitterer/media/test.mp4
  ```
- If basic test works but your file doesn't, re-encode your video with standard settings:
  ```bash
  ffmpeg -i input.mp4 -vf "scale=480:-2,format=yuv420p" -c:v libx264 -preset ultrafast -tune stillimage -c:a aac -b:a 128k -movflags +faststart -shortest output.mp4
  ```

### 9. Video Duration Too Short (Error Code 324 masquerading as 3)

Twitter/X requires videos to be at least 500 milliseconds long. If your video is shorter (common when converting a static image to video with very short audio), the API returns error code 324 ("Duration too short"), which the lm-twitterer plugin may surface as error code 3.

**Symptoms**:
- Error message contains "Duration too short, minimum:500.milliseconds"
- `ffprobe` shows video duration < 0.5 seconds
- Post fails despite file existing and being valid format

**Fix**: Ensure your video meets the minimum duration requirement:
- For static images: use `-loop 1` with sufficient audio duration or explicitly set duration
- Example ffmpeg command for image + audio:
  ```bash
  ffmpeg -loop 1 -i image.png -i audio.wav -c:v libx264 -tune stillimage -c:a aac -shortest -pix_fmt yuv420p -vf "scale=480:854:force_original_aspect_ratio=decrease,pad=480:854:(ow-iw)/2:(oh-ih)/2" output.mp4
  ```
- Alternatively, explicitly set duration with `-t` or ensure audio is long enough
- Always verify output with `ffprobe -show_entries format=duration -v quiet -of csv="p=0" output.mp4`

### Workflow

#### Automated Tweet Generation for Cron Jobs

For automated tweet generation (e.g., every 6 hours), implement feature and provider rotation to ensure varied content:

1. Maintain a list of feature-based tweet templates (Japanese, under 140 chars, with emoji, #hermesagent, ending with "はくあ")
2. Maintain a list of free tier providers to rotate (e.g., freebuff, opencode-zen)
3. Store rotation state in persistent storage (file or memory)
4. For each post:
   - Increment feature index and provider index (with wraparound)
   - Select tweet template and provider
   - Post using lm_twitterer_post with dry_run=false
   - Update rotation state

Example implementation in execute_code context:
```python
# Pseudocode for state management
state = read_state()  # Returns {"feature_index": int, "provider_index": int} or default {-1, -1}
next_feature = (state["feature_index"] + 1) % len(features)
next_provider = (state["provider_index"] + 1) % len(providers)
tweet_text = features[next_feature]
provider = providers[next_provider]
result = lm_twitterer_post(text=tweet_text, dry_run=False, provider=provider)
save_state({"feature_index": next_feature, "provider_index": next_provider})
```

**Concrete implementation example** (based on actual session):
- Store feature templates in a file (e.g., `templates/topics.txt`)
- Store current index in a file (e.g., `tweet_index.txt`)
- On each execution:
  ```bash
  # Read current index (default to 0 if file doesn't exist)
  idx=$(cat "/c/Users/downl/tweet_index.txt" 2>/dev/null || echo 0)

  # Read all topics into array
  lines=($(cat "/c/Users/downl/topics.txt"))
  total=${#lines[@]}

  # Select topic based on index
  selected_topic="${lines[$idx]}"

  # Post the tweet
  result=$(hermes lm-twitterer_post --text "$selected_topic" --dry_run false)

  # Update index for next time (with wraparound)
  next_idx=$(( (idx + 1) % total ))
  echo $next_idx > "/c/Users/downl/tweet_index.txt"
  ```
This approach ensures each tweet uses a different feature template while maintaining state between executions.
```

### Quick smoke test

```python
import sys
sys.path.insert(0, 'plugins')
spec = importlib.util.spec_from_file_location('core', 'plugins/lm-twitterer/core.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Status
print(mod._json(mod.status()))

# Auth check
print(mod._json(mod.auth_check()))

# Mention candidates
print(mod._json(mod.mention_candidates(count=3)))

# Post (dry-run)
print(mod._json(mod.post("test topic", dry_run=True)))
```

### Expected results after SearchTimeline fix
- `mention_candidates()` / `reply_mentions()` → returns data (may be empty if no whitelisted users have mentioned recently)
- `auth_check()` → `ok: true, auth_valid: true`
- `status()` → `twitter_dependency_available: true`
- `post(dry_run=True)` → generates text without posting

### 10. Irodori TTS HTTP 500 Internal Server Error

When the Irodori-TTS server returns HTTP 500 during TTS generation (as seen in the daily VRChat post cron job), check the server logs for details. Common causes include missing voice files, model loading issues, or port conflicts.

**Troubleshooting steps:**
1. Verify the Irodori-TTS server is running: `curl http://127.0.0.1:8088/health`
2. Check the server's stderr/logs for error details (if running in foreground).
3. Ensure the voice file (e.g., `hakua.ogg`) exists in the voices directory.
4. If the server fails to start, try starting it manually to see the error:
   ```bash
   cd /path/to/irodori-tts-server
   .venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
   ```
5. As a fallback, consider using Edge TTS (see the Edge TTS Fallback section elsewhere in this skill).

## Memory Source Policy (2026-09-26)

Follow the Memory Source Policy in the `ebbinghaus-memory` skill: X / lm-twitterer posts and raw SNS message mirrors are NOT written to Ebbinghaus any more; they stay in `activity.jsonl` / `social_sync.db`. Only distilled first-hand facts (user conversations, work logs and decisions, sleep/health summaries) are memories. Report sync counts in the cron output instead of storing them.
