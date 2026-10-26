---
name: hermes-x-posting-workflows
description: "Post to X from Hermes safely using xurl or lm-twitterer, with dry-run/confirmation, ledger sync, and robust error handling."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [x, twitter, social-media, lm-twitterer, xurl, ebbinghaus-memory]
---

# Hermes X Posting Workflows

Reference: for image + irodori/Hakua voice MP4 posts and manual handoff fallback, see `references/voice-video-posting.md`.
For automated daily VRChat photo + Hakua voice cron posts (07:00 JST, random photo, auto-starts irodoriTTS, lm-twitterer media upload), see `references/daily-vrchat-photo-cron-post.md`.
For the durable lm-twitterer implementation pattern using Cookie-session media upload via `tweepy_authlib`/`tweepy`, see `references/lm-twitterer-cookie-media-upload.md`.
For the X SearchTimeline deprecation (mid-2026) and the HomeLatestTimeline fallback, see `references/lm-twitterer-searchtimeline-deprecation.md`.
For validated buzz-tweet angle patterns (hot take, numbers-driven, developer empathy, future vision, version-focused rewrite) with templates and multi-tweet strategy, see `references/buzz-tweet-angle-patterns.md`.
For diagnosing `lm_twitterer_post` returning `posted: true` but `url: ""` — the known `_tweet_url_from_result` code-path bug and post-hoc URL recovery methods — see `references/lm-twitterer-empty-url-diagnosis.md`.
If Telegram delivery/download is unreliable for generated media, use `references/telegram-downloadable-media-handoff.md` for the short-Downloads-path plus ZIP fallback pattern.
For cron-driven buzz tweets using agent-crafted exact text (bypassing generation, pre-validating constraints), see `references/cron-buzz-tweet-exact-text.md`.
For topic rotation state management (persistent JSON state file that cycles through a curated topic bank across cron runs, avoiding repeated angles), see `references/topic-rotation-state-management.md`.
For switching an agent-driven X/lm-twitterer cron job to Hermes v0.18+ Mixture-of-Agents, see `references/cron-moa-model-switch.md`.

Use this skill when the user asks Hermes to draft, post, remember, or reconcile X/Twitter content, especially when using the `lm-twitterer` plugin or when posts should stay aligned with the user's agent/persona memory.

## Core safety flow

1. **Draft first for public writes.** For ordinary requests like「ツイートしてみて」, produce a concise draft and ask for explicit confirmation before posting.
1. **Draft first for public writes.** For ordinary requests like「ツイートしてみて」, produce a concise draft and ask for explicit confirmation before posting.
2. **Strip private-by-default details before drafting.** If the source conversation includes medical, travel, parking, home-location, schedule, or other personal logistics, do not carry those details into a public draft unless the user explicitly requests them.
3. **Post only after explicit confirmation.** Treat「投稿して」or equivalent as authorization for the exact draft or a clearly equivalent shortened version.
4. **If the user has multiple candidate drafts, ask them to pick one unless their approval names the variants.** If approval is ambiguous after several options were generated, do not guess which one they meant. Show the short list and ask which draft to publish. If the user explicitly authorizes named variants/styles (for example「強め・エンジニア向け・一般向け投稿許可」), treat that as permission to publish each named variant, while keeping the variants materially distinct.
5. **If posting multiple variants, avoid near-duplicates.** Give each live post a different angle (e.g. strong thesis, engineering/distribution detail, general-reader stability framing) and return every URL with its final posted text.
6. **If shortening is required, preserve intent.** X may reject text that is under Python `len()` but over X's weighted limit. Shorten while preserving the user's stated contrast, tone, and key terms; report that it was shortened.
7. **After successful post, return the URL and final posted text.** Do not merely say it worked.
7. **Record successful posts in the social ledger, not in memory.** Confirmed public posts stay in `~/.hermes/lm-twitterer/activity.jsonl`; `sync_execute.py` copies URL-only artifacts to `~/.hermes/memory-sync/social_sync.db`. Never write X post text or URLs to Ebbinghaus (Memory Source Policy (2026-09-26)), and never save credentials or raw auth details.


## Reach optimization for buzz-oriented posts

When the user is explicitly chasing reach, prefer posts that are:
- **utility-driven**: explain what changes for the reader
- **proof-driven**: cite visible signals like an official repo, active forks, working code, or real usage
- **contrast-driven**: use a clear opposition such as hype vs utility, chat vs execution, demo vs shipping
- **materially distinct** across variants: do not generate near-duplicate paraphrases when the user wants multiple options
- **single-language when requested**: keep English posts fully English and Japanese posts fully Japanese unless the user asks for a hybrid style
- **language-fixed before posting**: if the user asks for an English-only or Japanese-only post, verify the final generated text matches that language before publishing; if it does not, regenerate or explicitly restate the mismatch before posting
- **Hakua-branded but not over-explained**: when the user asks for「はくあらしく」or「もっと可愛く、鋭く」, keep the voice cute, concise, and a little sharp; do not over-justify the tone inside the post

For this user, the highest-performing angles in this session were utility + proof + contrast. Fork-specific posts should emphasize the *gap the fork closes* rather than branding alone; see `references/2026-06-03-fork-differentiation-and-language-control.md` for the distilled pattern.

### Tone micro-guidance for public drafts
- Prefer short sentences and one strong thesis.
- Use a cute/self-aware opener only if it does not dilute the claim.
- Keep the edge in the contrast, not in overlong explanation.
- If the user says「バズ狙い」, default to a sharper, more compressible version before asking for permission.
- If the model outputs the wrong language, correct it before publishing rather than assuming the tool will preserve the requested language.
- If the user explicitly asks for English, state the language requirement in the prompt twice if needed (title/topic + final text constraint), and verify the generated tweet is actually English before posting. If the model returns Japanese or mixed-language output, regenerate once with a stricter English-only instruction rather than publishing the mismatch.

See `references/2026-06-03-fork-differentiation-and-language-control.md` for the distilled pattern.
For cron-driven batches where the agent crafts the text (with constraint validation) and posts via the `text` parameter instead of generation, see `references/cron-buzz-tweet-exact-text.md`.
See `references/private-info-guard.md` for the public-post privacy guard and rewrite pattern.

## Source gathering for X-linked posts

For repo/latest-commit announcement posts, see `references/repo-latest-commit-announcement.md`: verify the commit from git/remote, inspect touched files or diff context, translate the raw commit into a user-facing benefit, and immediately honor a mid-turn route correction such as switching from WSL2/xurl to `lm-twitterer`.

When drafting from or verifying an existing X/Twitter status URL, first try the lightweight direct-reader path before reaching for broad X search:

1. Normalize direct status URLs to `https://x.com/<handle>/status/<id>` and drop tracking query parameters.
2. Read the status through `r.jina.ai` when credentials for broad X search are unavailable or unnecessary.
3. Use the returned Markdown as source context only; still follow the public-write flow: draft → explicit confirmation → post → URL + final text.
4. If you are changing Hermes tool defaults so this route works without xAI credentials, preserve explicit opt-outs such as `platform_toolsets: {cli: []}`. Auto-enable only for missing/default config, not for an intentionally empty selection.

See `references/r-jina-x-status-source.md` for the distilled implementation and test pitfall.

## Tool choice

### Use `lm-twitterer` for Hermes-native posting flows (preferred)

### Use `xurl` as fallback when lm-twitterer unavailable

When the user is already in a Hermes session and wants a normal X post, `lm_twitterer_post` is usually the fastest route. A good live-post pattern is:

1. Draft or confirm the content in chat.
2. Call `lm_twitterer_post` with `dry_run: false` when the user has explicitly approved posting.
3. If the user asks for a specific persona or tone, encode it in the `topic` field so the generator can shape the final tweet.
4. Return the posted text and URL, not just "done".

**`topic` field character limit**: The `topic` parameter is capped at **240 characters** (X's posting limit). If your topic is longer, the call will fail with `"Topic too long for public posting: N chars (max 240)"`. Shorten the topic, or bypass entirely by using the `text` parameter instead (which can be up to 240 chars but has no topic-length restriction).

If the user says 「そのまま投稿」 or an equivalent explicit approval after seeing a draft, publish the same draft or a minimally adjusted version that preserves the original intent and key terms.

See `references/2026-06-02-xai-oauth-and-prompt-to-post.md` for a concise session note on the xAI OAuth + prompt-to-post flow.

Use the official `xurl` workflow for standard X API posting:

```bash
xurl auth status
xurl whoami
xurl post "..."
```

Do not read or print `~/.xurl`, and do not use verbose flags or inline secrets.

### Use `lm-twitterer` when this Hermes checkout has it configured

If `xurl` is unavailable but the repo/plugin has `plugins/lm-twitterer/core.py` and status shows cookies configured, use the plugin path instead. Check status without revealing secrets:

```bash
python - <<'PY'
import importlib.util, sys
from pathlib import Path
plugin=Path('plugins/lm-twitterer/core.py')
spec=importlib.util.spec_from_file_location('lm_twitterer_core', plugin)
core=importlib.util.module_from_spec(spec); sys.modules['lm_twitterer_core']=core; spec.loader.exec_module(core)
print(core._json(core.status()))
PY
```

If dependencies are missing, install the plugin's documented dependencies rather than declaring the route broken:

```bash
python -m pip install 'twitter-openapi-python>=0.0.44,<0.1' 'tweepy-authlib>=1.7.3,<2'
```

## lm-twitterer robust posting pattern

The generated client can sometimes raise during response deserialization even when X returned a structured API error. For diagnosing write failures, use the `without_preload_content` call to inspect the raw JSON response. This is useful for errors such as `code 186` (tweet needs to be shorter).

See also:

- `references/lm-twitterer-dependency-fallback.md` for the recovery path when the tool wrapper's Python environment lacks the installed dependencies but the repo/shell Python can run the plugin directly.
- `references/accidental-quote-state-twitter-openapi.md` for the CreateTweet template-state bug where ordinary posts can accidentally inherit an Elon Musk `attachment_url?` quote unless quote/reply/media fields are explicitly cleared.

Minimal pattern:

```python
import importlib.util, json, sys
from pathlib import Path
import twitter_openapi_python_generated as twitter
from twitter_openapi_python.utils import non_nullable
from twitter_openapi_python.utils.api import get_headers

plugin = Path('plugins/lm-twitterer/core.py')
spec = importlib.util.spec_from_file_location('lm_twitterer_core', plugin)
core = importlib.util.module_from_spec(spec)
sys.modules['lm_twitterer_core'] = core
spec.loader.exec_module(core)

text = 'FINAL POST TEXT'
cfg = core.settings()
client = core._twitter_client(cfg)
post_api = client.get_post_api()
variables = non_nullable(twitter.PostCreateTweetRequestVariables.from_dict(post_api.flag['CreateTweet']['variables']))
features = non_nullable(twitter.PostCreateTweetRequestFeatures.from_dict(post_api.flag['CreateTweet']['features']))
variables.tweet_text = text
# Clear accidental quote/reply state. Do NOT set variables.media = None on newer
# pydantic-generated clients: media may be a required model field and assigning
# None raises a validation error. Leave the generated empty media object intact
# unless you are intentionally attaching uploaded media.
for field in ('attachment_url', 'reply'):
    try:
        setattr(variables, field, None)
    except Exception:
        pass
req = twitter.PostCreateTweetRequest(
    queryId=post_api.flag['CreateTweet']['queryId'],
    variables=variables,
    features=features,
)
resp = post_api.api.post_create_tweet_without_preload_content(
    path_query_id=post_api.flag['CreateTweet']['queryId'],
    post_create_tweet_request=req,
    _headers=get_headers(post_api.flag['CreateTweet'], post_api.ct),
)
body = resp.data.decode('utf-8', errors='replace')
data = json.loads(body)
rest_id = data.get('data', {}).get('create_tweet', {}).get('tweet_results', {}).get('result', {}).get('rest_id', '')
if not rest_id:
    raise RuntimeError(body[:2000])
url = f'https://x.com/i/web/status/{rest_id}'
result = {'ok': True, 'posted': True, 'dry_run': False, 'tweet_text': text, 'chars': len(text), 'url': url}
core._append_log({'action': 'post', **result}, cfg)
if hasattr(core, '_remember_generated_post'):
    core._remember_generated_post(text, cfg, dry_run=False, topic='manual post')
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## Memory alignment with Ebbinghaus / Hakua memories

When the user's goal is for posts to match a persistent assistant/persona context:

- Read prior `lm-twitterer` activity from `~/.hermes/lm-twitterer/activity.jsonl` (or `social_sync.db`) as read-only context. Do not import it into Ebbinghaus memory.
- Do not create Ebbinghaus rows for public posts (no `x-post` / `source='lm-twitterer'` memories). The plugin's generated-post writeback stays off unless `plugins.entries.lm-twitterer.memory_writeback: true` is set in config.yaml.
- The ledger keeps the final public URL; never store credentials or raw API responses anywhere.
- In future drafts, blend memories as continuity/style context, not as private memory dumps.

**During memory unification passes**:
When the user requests full memory integration ("記憶の統合と管理"), always:
- Call `lm_twitterer_status` early.
- Parse `~/.hermes/lm-twitterer/activity.jsonl` (count only `action=post` + `posted:true` + `dry_run=false`).
- Reinforce in Ebbinghaus the lm-twitterer operational facts (identity, hashtag, whitelist size, active provider, cron schedule) as durable policy memory.
- Never promote draft or reply-simulation records into durable memory. Only confirmed public posts count as artifacts, and artifacts live in `social_sync.db`, not Ebbinghaus.
This was executed successfully in the 2026-06-11 unification session (68 confirmed public posts surfaced).

### Voice/audio posts

When the user wants voice in an X post, treat it as a media workflow, not a plain text-post workflow.

**Current implementation: `lm-twitterer` supports media posts via `core.post(..., text=..., media_paths=[...])`.** It keeps lm-twitterer generation/policy/logging/memory semantics and uploads media with the existing lm-twitterer X cookie session (`auth_token`/`ct0`), so `xurl` OAuth is not required for this path.

Troubleshooting: if live posting fails with `AttributeError: 'NoneType' object has no attribute 'group'`, inspect `plugins/lm-twitterer/core.py`. The upstream `twitter_openapi_python.get_tid()` path may scrape `https://x.com` and fail before posting; a robust cookie-session CreateTweet fallback should generate `x-client-transaction-id` from `https://x.com/home` plus the current `ondemand.s` bundle, then POST to `https://x.com/i/api/graphql/{queryId}/CreateTweet`. Without that transaction header, X can reject with code `226`. Also ensure relative media names resolve under `~/.hermes/lm-twitterer/media` and still reject paths outside that directory.

Recommended pattern for media posts:
1. Generate the voice with the user's configured persona voice (for this user: Hakua Irodori `hakua` reference voice) - if irodoriTTS unavailable, use edge-tts from Hermes venv
2. Combine the still image and audio into an X-compatible MP4 with ffmpeg: H.264 video, yuv420p, AAC audio, `-movflags +faststart`
3. Verify the rendered MP4 exists, is small enough (<512MB, <140s), and plays before claiming it is ready
4. Ensure the media file is physically under the lm-twitterer media root (`~/.hermes/lm-twitterer/media/...`). If a render lives in `~/.hermes/video_cache/` or another cache, copy it into a topic subdirectory under the media root, then ffprobe the copied file.
5. Dry-run through `lm_twitterer_post` with the exact text and copied media path. Treat `media file must be under lm-twitterer media dir` as a path-placement guard, not an auth/media failure: copy under the media root and retry the dry-run once.
6. Publish through `lm-twitterer` with exact text and media paths:
   ```python
   core.post("", text=post_text, media_paths=[str(mp4_path)], dry_run=False)
   ```
7. Return the real X URL and final posted text. If the post response lacks a URL, recover it by checking the account's recent tweets and matching the exact text prefix.
8. If live media upload fails, provide a manual-post handoff package: MP4 path, exact post text, and optional Telegram media delivery.
Always verify that the media file resides inside the lm-twitterer media directory (e.g., `~/.hermes/lm-twitterer/media/`) and use an absolute path when calling `lm_twitterer_post`. This avoids `media file not found` errors.

### Edge TTS fallback when irodoriTTS is unavailable

When irodoriTTS is broken (missing module `irodori_openai_tts`, dependency resolution failure, or server won't start), use `edge-tts` directly from the Hermes venv instead:

```python
import edge_tts, asyncio
text = "Your narration text here"
communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")  # Use Japanese voice for Hakua
asyncio.run(communicate.save("voice.mp3"))
```

`edge-tts` is typically already installed in the Hermes venv (check with `pip list | grep edge-tts`). Use any Edge voice from `edge_tts.list_voices()`.

After generating the MP3, combine with an image via ffmpeg Ken Burns effect:

```bash
# 1. Get audio duration in seconds
duration=$(ffprobe -i voice.mp3 -show_entries format=duration -v quiet -of csv="p=0")

# 2. Calculate frame count: duration * fps
frames=$(python -c "import math; print(math.ceil(float('$duration') * 24))")

# 3. Create video with Ken Burns slow zoom + audio
ffmpeg -y -loop 1 -i "input_image.png" -i voice.mp3 \\
  -vf "zoompan=z='min(zoom+0.002,1.1)':d=$frames:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=24" \\
  -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k \\
  -shortest -pix_fmt yuv420p final.mp4
```

**Pitfalls**:
- The `d` (duration in frames) parameter in zoompan must be an integer; calculate as `ceil(audio_duration * fps)`.
- Ensure the image is the right aspect ratio (1920x1080 for landscape) or add scale/pad filters.
- Use `-shortest` so video ends when audio ends.
- X/YouTube accept H.264 + AAC in MP4 container.
- For portrait images (1080x1920), adjust `s` to `1080x1920` and the image path.

### Port 8080 Conflict Troubleshooting (Windows)

During this session, we encountered an error when running `xurl auth oauth2 --app hermes`:
```
OAuth2 authentication failed: Auth Error: ListenerError (cause: Auth Error: ServerError (cause: listen tcp 127.0.0.1:8080: bind: Only one usage of each socket address (protocol/network address/port) is normally permitted.))
```

**Root cause**: irodoriTTS server was running on port 8088, but some process was already listening on port 8080 (which xurl uses for its OAuth2 callback).

**Windows-specific resolution**:
1. Identify the process using port 8080: `netstat -ano | findstr :8080 | findstr LISTENING`
2. Note the PID (Process ID) from the output
3. Kill the process: `taskkill /PID <PID> /F`
   - Alternatively, use PowerShell: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force`
4. Retry xurl OAuth2: `xurl auth oauth2 --app hermes`
5. After successful auth, you can restart irodoriTTS if needed

**Verification**: After completing the above, `xurl auth status` should show `oauth2: <username>` for the default app, and `xurl whoami` should return your profile information without error.

## Recurring cron posts

For scheduled public posts:

1. Keep the cron topic public and abstract. Good examples: operational transparency, secret/memory separation, safe automation design. Bad examples: personal details, environment variable names/values, local paths, account IDs, Bitwarden item IDs, keys, passwords, or session material.
2. Put a small validation guard in the script before the live post. Refuse if the topic contains markers such as `TOKEN`, `SECRET`, `PASSWORD`, `.env`, `API_KEY`, local user paths, or known secret variable names.
3. Use a preflight-only mode before enabling live posting, e.g. an environment switch that runs `auth-check` and exits without posting. Report the preflight result separately from live posting.
4. For no-agent cron scripts, make stdout safe: print only success URLs/status or sanitized errors; never dump environment, config, cookies, or raw Bitwarden output.
- If a scheduled post script references a moved checkout path, fix the path but do not encode the old path as a durable lesson; the reusable lesson is to validate script paths during cron setup.
- For no-agent cron scripts that shell out to `hermes lm-twitterer ...`, verify the plugin CLI is registered in the exact cron Python (`python -m hermes_cli.main lm-twitterer auth-check`). If the CLI route is flaky, prefer direct `plugins/lm-twitterer/core.py` import for status/auth/exact-text posts; avoid generation unless the plugin LLM facade is bound.
- If `lm_twitterer_mentions` / `reply_mentions` fails with `AttributeError: 'NoneType' object has no attribute 'group'`, the upstream `twitter-openapi-python` read path is broken by an X web change. `auth-check` and exact-text posting may still work. Pause mention-reply cron instead of letting it fail hourly. See `references/lm-twitterer-mentions-attributeerror.md` for the exact failing code path and the placeholder-GraphQL bypass pattern already present in the plugin.
- When a cron job is reconciling X activity into the social ledger (`social_sync.db`, never Ebbinghaus) rather than making a new public post, store only confirmed public artifacts (`action=post`, `ok=true`, `dry_run=false`, `posted=true`, valid `https://x.com/i/web/status/...` URL). Exclude drafts, skipped replies, dry-runs, failures, and reply simulations. URL-only artifact rows are acceptable and safer than storing tweet text when the task is counts/reconciliation.
- When a cron script shells out to Hermes or a repo checkout, resolve the executable/root from `HERMES_PYTHON` and `HERMES_REPO_ROOT` first, then fall back to a local default. See `references/lm-twitterer-cron-path-env.md` for the minimal pattern.

## Provider/model override guidance for cron & tool calls

When the user explicitly provides a `provider` + `model` override for lm-twitterer calls, honor it.

### For agent-driven cron jobs
- If the user says the **execution model** should be MoA, update the cron job's model override to `provider: moa` and `model: default` (or the named MoA preset they specify). Do not approximate MoA with `auto-free`, `freebuff`, `opencode-zen`, or a prompt instruction about provider rotation.
- First locate the target job with `cronjob(action="list")`; never guess job IDs.
- After updating, verify the returned job object shows `provider: "moa"` and `model: "default"` (or the requested preset). See `references/cron-moa-model-switch.md`.
- Remember: `no_agent: true` cron scripts ignore agent model settings; convert to an agent-driven job if MoA reasoning is required.

### For interactive/tool calls
- **Do NOT add** explicit provider/model overrides on your own initiative — the default provider chain is preferred.
- Only hardcode a provider/model override when:
  1. The user explicitly asks for a specific model
  2. You have verified the override is in the plugin's `allowed_providers`/`allowed_models` allowlists
  3. A default-provider call has already failed and the failure was due to the provider, not the API endpoint

### For no-agent cron scripts
- **Do NOT hardcode** a static provider/model string in the prompt template. no-agent cron scripts run as standalone processes without session context; static overrides lock them to a stale model and do not track the user's active config.
- **Preferred pattern**: read `config.yaml`'s `model.provider` and `model.default` dynamically at execution time.
- Resolution order for no-agent scripts:
  1. Explicit env var override (e.g. `LM_TWITTERER_PROVIDER` / `LM_TWITTERER_MODEL`)
  2. `config.yaml` → `model.provider` + `model.default`
  3. Sensible hardcoded fallback
- A `_resolve_provider_model()` function calling `yaml.safe_load()` on `config.yaml` is the canonical implementation.

See `references/lm-twitterer-allowed-models-providers.md` for the plugin allowlist check.

## SearchTimeline deprecation (mid-2026)

X has deprecated the SearchTimeline GraphQL endpoint. `_graphql_search_timeline_items()` now falls back to **HomeLatestTimeline** when SearchTimeline returns 404, filtering results for `@bot_screen_name` mentions.

See `references/lm-twitterer-searchtimeline-deprecation.md` for the full technical details.

> **Consolidated**: The lm-twitterer plugin operations, memory bridge, and the SearchTimeline fix are now documented together in the `lm-twitterer-operations` skill. Load it with `skill_view(name='lm-twitterer-operations')` for the complete reference.

## Pitfalls

- If a media post is approved, preflight the media route with `lm_twitterer_status` / `core.status()` first. For this user's current path, `lm-twitterer` Cookie-session media upload via `tweepy_authlib` is preferred and `xurl` OAuth is not required. Use `xurl` only as a fallback/manual handoff route when the Cookie-session upload path is unavailable.
- **Port 8080 conflict**: irodoriTTS uses port 8088 for its server, while xurl OAuth2 callback uses port 8080. If port 8080 is busy (e.g., irodoriTTS is running), xurl auth will fail with "Only one usage of each socket address" error. To resolve on Windows: open PowerShell as administrator and run `Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force` to kill the process using port 8080, then retry xurl OAuth2 authentication.
- **lm-twitterer media upload uses the lm-twitterer cookie session**. `core.post(..., text=..., media_paths=[...], dry_run=false)` uploads media with the configured `auth_token`/`ct0`, posts with media IDs, and records the lm-twitterer activity/memory row.
- **xurl OAuth is not needed for the lm-twitterer media path**. If xurl OAuth fails due to app permission or port 8080 issues, keep using lm-twitterer cookie media upload instead.
- **Two cron patterns for daily VRChat photo posts exist** (2026-06-18):
  - **Script-based (07:00)**: `no_agent: true` cron running `/c/Users/downl/.hermes/scripts/daily_vrchat_post.py` — uses xurl for media upload, requires xurl OAuth2 pre-auth.
  - **Agent-based (08:00)**: Agent-driven cron with `hermes-x-posting-workflows` skill — currently text-only via lm-twitterer, can be extended for media via xurl subprocess.
  Both pick random photos from `Pictures/VRChat`, generate Hakua voice via irodoriTTS, create MP4 with ffmpeg. Choose based on whether xurl OAuth2 is set up.
- If `lm_twitterer_post` reports missing Python dependencies after you installed them, do not retry the same tool call unchanged. Check whether the tool and terminal are using different Python environments; import `plugins/lm-twitterer/core.py` with the terminal Python, run `core.status()`, and if dependencies/cookies are available, use the direct raw-post `without_preload_content` pattern from this skill.
- X's weighted character limit can reject a post even when Python `len(text)` is under 280. If X returns `code 186`, shorten and retry once with the same meaning.
- Do not preserve accidental quote/attachment state unless the user requested a quote or reply. In `twitter-openapi-python`, the default `CreateTweet` variables can contain `attachment_url?` pointing at an Elon Musk tweet; clear nullable fields such as `variables.attachment_url = None` and `variables.reply = None` (unless explicitly replying). **Do not assign `variables.media = None` on newer pydantic clients**; the generated media object may be required even for text-only posts, and setting it to `None` can raise a validation error before the request is sent. Leave the empty media object intact unless intentionally posting media. Verify the final response URL and final text.
- Treat dependency installation or missing `xurl` as setup state, not as evidence that X posting is impossible.
- If `lm_twitterer_post` fails with a dependency/runtime error, do **not** retry the same tool call unchanged. Install the documented dependencies, then verify which Python can import `twitter_openapi_python`, `twitter_openapi_python_generated`, and `tweepy_authlib`. If the plugin dependencies are available to the repo/shell Python but not to the tool sandbox, use the robust posting pattern in this skill directly from `plugins/lm-twitterer/core.py` and return the real post URL. Also check `xurl auth status && xurl whoami`; a present `xurl` binary may still be unauthenticated.
- **`lm_twitterer_status` may report `twitter_dependency_available: false` even when the repo/shell Python has all deps.** The status check probes the tool wrapper's Python, not the terminal Python. Do NOT treat a `false` status as proof that posting is impossible. Verify by importing the plugin from terminal: `cd` to repo root, insert repo root + venv site-packages into `sys.path`, and run `core.status()`. If that report shows `twitter_dependency_available: true`, proceed with the direct posting pattern. See `references/lm-twitterer-dependency-fallback.md` for the exact recovery steps.
- If `lm_twitterer_post` fails during response deserialization with a pydantic error such as `ValidationError: ErrorExtensions tracing Input should be a valid dictionary ... input_value=None`, treat it as a wrapper/client parsing failure, not proof that posting is impossible. Use the raw `post_create_tweet_without_preload_content` pattern above, parse the returned JSON for `rest_id`, append the lm-twitterer activity log when available, and report the real `https://x.com/i/web/status/<id>` URL.
- **`topic` + `dry_run=false` validation error**: When passing a non-empty `topic` parameter with `dry_run: false`, the plugin can fail with `ValidationError: ErrorExtensions.tracing Input should be a valid dictionary ... input_value=None` during response deserialization even though `dry_run: true` with the same topic succeeds. Workarounds (prefer #1):
  1. **(Best)** Use the `text` parameter directly with `dry_run: false` — bypasses the generation path entirely, no serialization issue. Draft first with `dry_run: true`, then post with `text="<exact draft>"` and `dry_run: false`.
  2. Post with an empty `topic` (uses the configured default topic) or a simple emoji-free Japanese topic.
  3. Generate with `dry_run: true` first, then post the same topic again with `dry_run: false` (may still fail intermittently).
  This appears to be a GraphQL variable serialization issue with the generation-only path. Verified 2026-06-16 & 2026-06-19: `text` parameter direct posting always succeeds.
- If `lm_twitterer_post` returns `{"posted": true, "url": ""}`, the tweet IS live on X — URL extraction failed, not the actual posting. Recovery options in order of preference:
  1. Call `_find_recent_tweet_url_by_text(client, cfg, tweet_text[:80])` from `plugins/lm-twitterer/core.py` to search the user's last 20 tweets.
  2. Use the `without_preload_content` raw-response pattern to inspect the actual JSON.
  3. Check `~/.hermes/lm-twitterer/activity.jsonl` — if `posted: true`, the tweet exists.
  4. Visit `https://x.com/<screen_name>` in a browser.
  See `references/lm-twitterer-empty-url-diagnosis.md` for the full debugging walkthrough and a known code-path bug in `_tweet_url_from_result`.
- If `lm_twitterer_post` rejects a provider override such as `xai-oauth` because it is not in `plugins.entries.lm-twitterer.llm.allowed_providers`, retry once without the override before escalating. The default Hermes generation path can still publish successfully.
- **Plugin allowlists are strict and independent of global Hermes defaults.** The plugin's `allowed_models` / `allowed_providers` (in `~/.hermes/config.yaml` under `plugins.lm-twitterer.llm`) must match the `provider` + `model` you pass. The global `hermes config show` model/provider are often NOT in those lists. **Always pass explicit `provider` + `model` from the plugin's allowlists** — do not rely on defaults. See `references/lm-twitterer-allowed-models-providers.md` for the full diagnostic and workaround.
- For this user, maintain the safe public-write flow: **draft → user confirmation → post → URL + final text + ledger sync (`social_sync.db`, not Ebbinghaus)**.
- See `references/lm-twitterer-provider-override.md` for a real provider-override pitfall and the safer fallback when the plugin rejects an override.
- See `references/lm-twitterer-allowed-models-providers.md` for the plugin allowlist vs global defaults mismatch and the mandatory explicit-override pattern.
