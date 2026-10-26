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

Reference: for image + irodori/Hakua voice MP4 posts and xurl/manual handoff fallback, see `references/voice-video-posting.md`. **X hard cap: videos must be ≤140 seconds** — verify with ffprobe before any upload (see the reference).
For automated daily VRChat photo + Hakua voice cron posts (07:00 JST, random photo, auto-starts irodoriTTS, xurl media upload), see `references/daily-vrchat-photo-cron-post.md`.
If Telegram delivery/download is unreliable for generated media, use `references/telegram-downloadable-media-handoff.md` for the short-Downloads-path plus ZIP fallback pattern.

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

### Prefer `xurl` when available

### Use `lm-twitterer` for Hermes-native posting flows

When the user is already in a Hermes session and wants a normal X post, `lm_twitterer_post` is usually the fastest route. A good live-post pattern is:

1. Draft or confirm the content in chat.
2. Call `lm_twitterer_post` with `dry_run: false` when the user has explicitly approved posting.
3. If the user asks for a specific persona or tone, encode it in the `topic` field so the generator can shape the final tweet.
4. Return the posted text and URL, not just "done".

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

## Voice/audio posts

When the user wants voice in an X post, treat it as a media workflow, not a plain text-post workflow.

Recommended pattern:

1. Generate the voice with the user's configured persona voice, if any. For this user, default to the Hakua Irodori `hakua` reference voice for voice MP4s; do **not** substitute Edge/Nanami or another generic Japanese voice unless explicitly asked or Irodori is unavailable and the fallback is clearly labeled.
2. If the user references a prior approved asset (for example `hakua_release_verification_hakua_voice_LOUD.mp4`), treat that as a voice-identity requirement: synthesize new text with the same persona voice (`Voice hakua`) rather than extracting/reusing the old spoken content.
3. Prefer a short MP4 made from a still image/subtitles/waveform plus the audio; this is usually more portable than trying to attach raw `.ogg`/`.wav` audio.
4. Verify the rendered MP4 exists and plays before discussing posting. Include audio loudness evidence (`volumedetect` mean/max volume) because quiet audio was a real failure mode.
5. If Irodori synthesis fails mid-run, inspect whether the output path contains JSON/text instead of audio, restart duplicate/stale Irodori server processes if needed, and retry once with `Voice hakua`. Do **not** silently fall back to Edge/Nanami or any generic voice.
6. A previously approved `Voice hakua` audio sample may be reused only when the spoken text exactly matches the requested post text; disclose that it is a reuse/fallback rather than fresh synthesis.
7. Use a media-capable X route if available. If the active posting helper is text-only, return the MP4 path and final caption instead of claiming it posted with audio.
8. If the user says the voice identity is wrong, fix the TTS reference voice first and regenerate the media; do not reuse the earlier audio.

See the TTS skill `hermes-tts-plugin-providers` for the Irodori reference-voice pinning pattern. See `references/x-media-audio-video-auth.md` for the media-upload auth preflight and fallback pattern.

For release-news narration videos made from a still image (for example Hermes Agent release highlights), use `references/release-announcement-voice-video.md`: verify the release from primary sources, script a short Hakua/irodori narration, render H.264/AAC MP4 with `+faststart`, verify with ffprobe, and deliver via `MEDIA:` if media-post OAuth is not ready.

## Recurring cron posts

For scheduled public posts:

1. Keep the cron topic public and abstract. Good examples: operational transparency, secret/memory separation, safe automation design. Bad examples: personal details, environment variable names/values, local paths, account IDs, Bitwarden item IDs, keys, passwords, or session material.
2. Put a small validation guard in the script before the live post. Refuse if the topic contains markers such as `TOKEN`, `SECRET`, `PASSWORD`, `.env`, `API_KEY`, local user paths, or known secret variable names.
3. Use a preflight-only mode before enabling live posting, e.g. an environment switch that runs `auth-check` and exits without posting. Report the preflight result separately from live posting.
4. For no-agent cron scripts, make stdout safe: print only success URLs/status or sanitized errors; never dump environment, config, cookies, or raw Bitwarden output.
- If a scheduled post script references a moved checkout path, fix the path but do not encode the old path as a durable lesson; the reusable lesson is to validate script paths during cron setup.
- When a cron job is reconciling X activity into the social ledger (`social_sync.db`, never Ebbinghaus) rather than making a new public post, store only confirmed public artifacts (`action=post`, `ok=true`, `dry_run=false`, `posted=true`, valid `https://x.com/i/web/status/...` URL). Exclude drafts, skipped replies, dry-runs, failures, and reply simulations. URL-only artifact rows are acceptable and safer than storing tweet text when the task is counts/reconciliation.
- When a cron script shells out to Hermes or a repo checkout, resolve the executable/root from `HERMES_PYTHON` and `HERMES_REPO_ROOT` first, then fall back to a local default. See `references/lm-twitterer-cron-path-env.md` for the minimal pattern.

## Pitfalls

- If a media post is approved, preflight the media route separately: `xurl auth status && xurl whoami`, then upload with `xurl media upload` and attach `--media-id`. Do not assume `lm-twitterer` text-post cookies are sufficient for X media upload; if media auth is missing, return the MP4 path and caption and offer OAuth setup.
- **lm-twitterer does not support media upload**. The `core.post()` function only accepts `topic`, `dry_run`, `provider`, `model`, `cfg` — no `media_paths` parameter exists. For media posts (images, videos, GIFs), use **xurl** which supports `xurl media upload` + `xurl post --media <id>`.
- **xurl media upload requires manual OAuth2 authentication**. The `xurl auth oauth2 --app <name>` command opens a browser for user consent — this cannot be automated in a headless/cron context. The user must complete this once manually. After auth, `xurl auth status` should show `oauth2: <username>` for the default app.
- **Two cron patterns for daily VRChat photo posts exist** (2026-06-18):
  - **Script-based (07:00)**: `no_agent: true` cron running `/c/Users/downl/.hermes/scripts/daily_vrchat_post.py` — uses xurl for media upload, requires xurl OAuth2 pre-auth.
  - **Agent-based (08:00)**: Agent-driven cron with `hermes-x-posting-workflows` skill — currently text-only via lm-twitterer, can be extended for media via xurl subprocess.
  Both pick random photos from `Pictures/VRChat`, generate Hakua voice via irodoriTTS, create MP4 with ffmpeg. Choose based on whether xurl OAuth2 is set up.
- If `lm_twitterer_post` reports missing Python dependencies after you installed them, do not retry the same tool call unchanged. Check whether the tool and terminal are using different Python environments; import `plugins/lm-twitterer/core.py` with the terminal Python, run `core.status()`, and if dependencies/cookies are available, use the direct raw-post `without_preload_content` pattern from this skill.
- X's weighted character limit can reject a post even when Python `len(text)` is under 280. If X returns `code 186`, shorten and retry once with the same meaning.
- Do not preserve accidental quote/attachment state unless the user requested a quote or reply. In `twitter-openapi-python`, the default `CreateTweet` variables can contain `attachment_url?` pointing at an Elon Musk tweet; clear nullable fields such as `variables.attachment_url = None` and `variables.reply = None` (unless explicitly replying). **Do not assign `variables.media = None` on newer pydantic clients**; the generated media object may be required even for text-only posts, and setting it to `None` can raise a validation error before the request is sent. Leave the empty media object intact unless intentionally posting media. Verify the final response URL and final text.
- Treat dependency installation or missing `xurl` as setup state, not as evidence that X posting is impossible.
- If `lm_twitterer_post` fails with a dependency/runtime error, do **not** retry the same tool call unchanged. Install the documented dependencies, then verify which Python can import `twitter_openapi_python`, `twitter_openapi_python_generated`, and `tweepy_authlib`. If the plugin dependencies are available to the repo/shell Python but not to the tool sandbox, use the robust posting pattern in this skill directly from `plugins/lm-twitterer/core.py` and return the real post URL. Also check `xurl auth status && xurl whoami`; a present `xurl` binary may still be unauthenticated.
- If `lm_twitterer_post` fails during response deserialization with a pydantic error such as `ValidationError: ErrorExtensions tracing Input should be a valid dictionary ... input_value=None`, treat it as a wrapper/client parsing failure, not proof that posting is impossible. Use the raw `post_create_tweet_without_preload_content` pattern above, parse the returned JSON for `rest_id`, append the lm-twitterer activity log when available, and report the real `https://x.com/i/web/status/<id>` URL.
- **`topic` + `dry_run=false` validation error**: When passing a non-empty `topic` parameter with `dry_run: false`, the plugin can fail with `ValidationError: ErrorExtensions.tracing Input should be a valid dictionary ... input_value=None` during response deserialization even though `dry_run: true` with the same topic succeeds. Workaround: (a) generate the tweet with `dry_run: true` first, then (b) post using an empty `topic` (which uses the configured default topic) or a simple emoji-free Japanese topic. This appears to be a GraphQL variable serialization issue with certain tweet content (emojis, special characters) in the non-dry-run path. Verified 2026-06-16: empty topic succeeded; emoji-containing topics failed; simple Japanese text succeeded.
- If `lm_twitterer_post` rejects a provider override such as `xai-oauth` because it is not in `plugins.entries.lm-twitterer.llm.allowed_providers`, retry once without the override before escalating. The default Hermes generation path can still publish successfully.
- **Plugin allowlists are strict and independent of global Hermes defaults.** The plugin's `allowed_models` / `allowed_providers` (in `~/.hermes/config.yaml` under `plugins.lm-twitterer.llm`) must match the `provider` + `model` you pass. The global `hermes config show` model/provider are often NOT in those lists. **Always pass explicit `provider` + `model` from the plugin's allowlists** — do not rely on defaults. See `references/lm-twitterer-allowed-models-providers.md` for the full diagnostic and workaround.
- For this user, maintain the safe public-write flow: **draft → user confirmation → post → URL + final text + ledger sync (`social_sync.db`, not Ebbinghaus)**.
- See `references/lm-twitterer-provider-override.md` for a real provider-override pitfall and the safer fallback when the plugin rejects an override.
- See `references/lm-twitterer-allowed-models-providers.md` for the plugin allowlist vs global defaults mismatch and the mandatory explicit-override pattern.
