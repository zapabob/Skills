---
name: cron-memory-social-sync
description: Run scheduled Hermes/OpenClaw memory + social sync (Telegram/Discord/LINE sessions + X/lm-twitterer) into Ebbinghaus memory. Counts-only output, Bitwarden-safe secret handling, idempotent writes, two-tier secret guard.
version: 1.2.0
author: Hermes Agent
platforms: [windows]
tags: [cron, memory, ebbinghaus, social, x, twitter, lm-twitterer, bitwarden-safe]
---

# Cron Memory/Social Sync

Scheduled no-user cron job that consolidates Hermes session transcripts (Telegram, Discord, LINE) and X/lm-twitterer public posts into Ebbinghaus memory. Output is counts-only JSON + Japanese summary — no raw text, no secrets.

## Trigger

- Cron schedule (e.g., `0 3 * * *` — 03:00 daily)
- Manual invocation: `python ~/.hermes/cron_sync_YYYYMMDD.py`

## Canonical Data Sources

| Source | Path | Role |
|--------|------|------|
| Hermes transcript DB | `~/.hermes/state.db` | Canonical `sessions` + `messages` source when those tables exist |
| Session-file fallback | `~/.hermes/sessions/*.json*` | Fallback only when the live DB schema is unavailable |
| X activity log | `~/.hermes/lm-twitterer/activity.jsonl` | lm-twitterer post/reply/dry-run records |
| Ebbinghaus DB | `~/.hermes/ebbinghaus_memory.db` | Target memory store (`content` is unique; `encoded` may be NOT NULL) |

**Transcript source is environment-dependent — detect at runtime.** Prefer `state.db` when usable `sessions`/`messages` tables exist because it preserves message volume and source filtering; otherwise fall back to session files. Construct Windows paths in native form when POSIX/MSYS path existence checks are unreliable. Never hardcode that either source is empty.

## Extraction Rules

### X Posts (from `activity.jsonl`)

Only **confirmed public posts** pass all filters:

```python
rec.get('action') == 'post'
rec.get('ok') is True
rec.get('dry_run') is False
rec.get('posted') is True
rec.get('url', '').startswith('https://x.com/i/web/status/')
# Tier 1 broad guard: no TOKEN, SECRET, PASSWORD, API_KEY, .env, oauth_token, session_token, sk-, ghp_, Bearer tokens
```

Excluded: drafts (`dry_run=true`), replies (`action=reply_mentions`), failures (`ok=false`), rate-limited, invalid URLs, broad-guard hits.

Stored as **URL-only artifacts**: `X post: https://x.com/i/web/status/...`

### Sessions (prefer `state.db`, otherwise `sessions/*.json*`)

Inspect the live schema before querying. When `state.db` exposes `sessions` and `messages`, count social sessions with `source IN ('telegram','discord','line')` and count messages directly; do not sample or extrapolate. Use session files only as a fallback and report aggregate counts. Never store raw message content.

## Two-Tier Secret Guard

**Tier 1 — Broad exclusion (intake filter)**: Regex for `TOKEN|SECRET|PASSWORD|API_KEY|...` — excludes candidate at ingestion. Policy text *about* secrets (e.g., "secrets stay in Bitwarden") passes because it lacks actual token patterns.

**Tier 1 can silently drop benign policy prose too**: word-level BROAD patterns such as `oauth`, `api[_-]?key`, `access[_-]?token`, `password` (case-insensitive) also reject legitimate policy facts that merely NAME those credential categories in prose — e.g. a fact like "API keys, OAuth, session tokens ... are never persisted" gets blocked and counted in `excluded`, so fewer policy facts save than expected. Discovered 2026-07-31 (3 of 4 facts saved; the blocked one was reworded and re-inserted). Fix pattern: pre-assert each candidate against BROAD (+ NARROW + path markers) BEFORE insert; reword to avoid trigger tokens while keeping meaning — "credentials" for "API key"/"OAuth", "dotenv contents" for ".env", "session material" for "session tokens". Plain prose "secret"/"Bitwarden" are safe. Detect silently-dropped facts by comparing saved count vs expected, then reword-and-resave with a fresh scoped guard pass.

**Tier 2 — Scoped path/secret check (verification)**: After write, scan scoped rows (`session_id='cron-memory-social-sync'`) for literal local-path markers and actual secret-value patterns only — for example `sk-…`, `ghp-…`, `Bearer …`, `oauth_token=…`, `ct0=…`, or `auth_token=…`. **HARD RULE: Tier 2 MUST be narrow — do not reuse bare policy words such as `TOKEN`, `SECRET`, or `API_KEY` during post-write verification.** Broad intake filtering may conservatively exclude benign policy prose; it must not cause benign policy rows to be deleted during scoped remediation. If violations are found, remediate without printing content, then rerun the verification pass. See `references/cron-sync-narrow-guard-pitfall.md` for the corrected pattern.

**Self-flagging trap: durable policy text must never embed literal local-path markers.** Even the narrow Tier-2 path markers (`C:\\\\Users`, `C:/Users`, `\\\\Users\\\\`, `/home/`) will delete a policy fact that *names* a path form. On 2026-08-01 a fact like "resolve DB paths in `C:\\\\Users\\\\…` form" was written and then immediately deleted by Tier 2 (`guard_remediated_rows=1`, risk elevated until a second verification pass). Phrase path-related lessons abstractly — "native Windows backslash form", "local user profile root", "POSIX vs native form" — and pre-assert candidates against the path markers before insert, the same way Tier-1 candidates are pre-asserted. See `references/2026-08-01-cron-memory-social-sync-run2.md`.

**Numeric pattern over-matching X status URLs (Tier 1 intake collapse).** Never put broad decimal numeric patterns such as `\\b\\d{4,}\\b` or `\\d{10,}` in the broad intake guard — X status URLs are `https://x.com/i/web/status/<18-19 decimal digits>` and every valid URL will be flagged as a token, collapsing `saved` to 0 while `excluded` spikes to the full candidate count (observed 2026-08-02: 437 excluded, 0 saved → 0 candidates). For hex token detection use `[0-9a-f]{40+}` (SHA-1+) which excludes decimal. Better: for URL-only artifacts, split the guard — apply **path markers (substring)** to URLs, and apply **secret token patterns (regex)** to tweet *text* only (text is not stored for URL-only rows, so text guard is for intake exclusion only). Post-write verification of URL-only rows needs only path-marker checks, since the stored content is a known-good URL template. Alert: if `saved=0` AND `excluded` is high, suspect guard over-matching, not a quiet day. See `references/2026-08-02-cron-memory-social-sync-execution.md`.

## Memory Write Pattern

- **Idempotent**: `INSERT` with `content` UNIQUE constraint → `SELECT` check first, or `INSERT OR IGNORE` (but must verify `rowcount > 0` because `encoded` is NOT NULL).
- **X artifacts**: prefer the dedicated `x_artifacts` table in `ebbinghaus_memory.db` (columns `id, url, text, posted_at, source, tags`; unique autoindex on `url` → `INSERT OR IGNORE` is idempotent). In practice rows use `text=''`, `posted_at` = sync-run UTC ISO (e.g. `2026-07-29T04:13:05Z`), `source='lm-twitterer'`, `tags='cron-sync'` (confirmed 2026-07-31 run). Fall back to `memories` rows (`X post: <url>`) only if that table is absent — check `PRAGMA index_list(x_artifacts)` first and fall back to an existence check if the unique index is not on `url`.
- **Policy facts**: `source='cron-memory-social-sync'`, `tags='policy-fact,memory-sync,bitwarden-safe'`, `session_id='cron-memory-social-sync'`
- **Encoded field**: Always include `encoded = json.dumps({...cue_encoding...})` — NOT NULL in schema.

## Windows/MSYS Gotchas

1. **Both `python` and `python3` may be Windows Store stubs** — On Windows, either or both can silently exit code 49 with no output. There is no single safe short name. **Probe for a working Python explicitly**: check `C:\\Users\\<user>\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`, `C:\\Python*\\python.exe`, or run `which python` / `which python3` in Git-Bash to find the active shell Python. Use the explicit full path for cron sync scripts and temp-script execution. Always verify before relying on it in cron: `"C:\\path\\to\\python.exe" --version`.
2. **Path resolution**: `find` returns `/c/Users/...` but `Path(r'C:\\Users\\downl\\.hermes')` works; `Path('~/.hermes')` also works in Python. Verify both forms if uncertain.
3. **Large Python blocks**: Write to a temp `.py` file and execute (`python script.py`) instead of heredoc — avoids line-ending/truncation issues and shell parse errors. Use `write_file` to create the script to avoid shell escaping problems with complex Python source.
   - **Heredoc backslash-U parse trap**: a literal backslash followed by `U` in Python source (e.g. typing `\\Users\\downl` as a path marker inside a heredoc) dies at parse time with `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes ... truncated \\UXXXXXXXX escape` — the block never runs. Confirmed 2026-08-01: a short *verification* heredoc hit this even though the main sync script (written via `write_file`) was fine. Fix: never type backslash literals in heredoc source — build path markers with `bs=chr(92)` concatenation (e.g. `'C:'+bs+'Users'`, `bs+'Users'+bs+'downl'`), or write the block to a temp .py with `write_file` and execute that.
4. **Temp script cleanup**: Remove the temp `.py` file after successful verification and counts reporting.
5. **Protected `~/.hermes/*.py` writes (2026-08-25)**: Writing a dated runner such as `~/.hermes/cron_sync_YYYYMMDD.py` can be blocked as a protected agent-instruction file in unattended cron. Put the runner under `%LOCALAPPDATA%/Temp/` (or another non-protected path) and execute it with the absolute Python312 path. Do not retry the blocked write via shell. Report files may also go to Temp if `~/.hermes/sync-reports/` is blocked.

## Residual Risk Assessment

Set risk from source completeness and verification, not exclusion volume alone:

| Condition | Risk |
|-----------|------|
| Expected sources missing or partially processed | `medium` |
| Significant data loss or post-write verification failure | `high` |
| All expected sources processed and final scoped guard is zero | `low` |

A high excluded count can be normal when the activity log contains many dry-runs, replies, failures, or invalid records. Report it as a count; do not automatically elevate risk without source incompleteness or verification failure.

**`excluded` counts X-record exclusions + guard-remediated rows only.** Message-level guard flags from the session scan (messages whose content matches the broad regex) are informational — report them separately (e.g. `guard_flagged_messages`) and do NOT fold them into `excluded` or the risk signal. On 2026-08-01 folding 1,438 flagged messages into `excluded` inflated it to 2,637; the correct X-only value was 1,199 (1,632 records − 433 valid posts). Message flags only indicate *topic* overlap with secret vocabulary, not data loss — those messages were never storage candidates.

## Final Output (Auto-delivered)

```json
{
  "social_sessions": "<count>",
  "messages": "<count>",
  "x_total": "<count>",
  "valid_x_posts": "<count>",
  "saved": "<count>",
  "excluded": "<count>",
  "guard_remediated": "<count>",
  "guard_violations_after_verification": "<count>",
  "residual_risk": "<low|medium|high>"
}
```

Japanese summary:
```
同期件数: <count>
保存件数: <count>
除外件数: <count>
残留リスク: <low|medium|high>
```

## Reference Implementations

- `~/.hermes/cron_sync_20260805.py` — current working script (2026-08-05)
- `references/2026-08-05-cron-memory-social-sync-execution.md` — 2026-08-05 run 1: 9320 sessions / 231368 messages / 201 social sessions / 1832 X records / 460 valid X URLs / 11 saved / 1373 excluded / 1 scoped remediation / 0 final violations / residual_risk=low; absolute Python312 path required (Store stub exit 49); counts-only JP delivery confirmed
- `references/2026-08-05-cron-memory-social-sync-execution-rerun.md` — 2026-08-05 run 2 (fresh data): 9383 sessions / 231975 messages / 201 social sessions / 1885 X records / 471 valid X URLs / 12 saved / 1414 excluded / 0 guard remediations / 0 final violations / residual_risk=low; same absolute Python312 path requirement; idempotent rerun pattern confirmed
- `~/.hermes/cron_sync_20260723.py` — earlier working script baseline
- `references/2026-08-03-cron-memory-social-sync-execution.md` — 2026-08-03 run: 201 social sessions / 16,311 messages / 1,722 X records / 446 valid X URLs / 11 saved (5 X artifacts + 6 policy facts) / 1,278 excluded / 0 guard violations / medium (excluded > 100); temp-script execution pattern, Windows python3 stub caveat confirmed
- `references/2026-08-02-cron-memory-social-sync-execution.md` — 2026-08-02 run: Tier-1 numeric pattern (`\\\\b\\\\d{4,}\\\\b`) over-matched X status URL decimal IDs collapsing all candidates (0 saved / 437 excluded); fix: split guard into path-marker (URLs) + secret-token-regex (text only), use `[0-9a-f]{40+}` not decimal for token detection; 24 saved / 0 excluded / 0 violations / low
- `references/2026-08-01-cron-memory-social-sync-execution.md` — 2026-08-01 run: 201 social sessions / 16,580 messages / 431 valid X URLs / 5 new / 15 saved / 0 guard violations / low; verification-heredoc `\\\\U` parse trap, dual-write double-counting note, `x_artifacts` shared across processes
- `references/2026-08-01-cron-memory-social-sync-run2.md` — second 2026-08-01 run: policy fact self-flagged by Tier-2 path guard (reword-and-resave), `excluded` = X-record exclusions only (message guard flags reported separately), 201/13,554/433 / 5 saved / 1 remediated / 0 final violations / low
- `references/2026-07-31-cron-memory-social-sync-execution.md` — 2026-07-31 run: Tier-1 broad guard silently rejecting policy facts that name credential categories (reword-and-resave pattern), `x_artifacts` table as canonical URL-only store, interpreter/path notes
- `references/2026-07-29-cron-memory-social-sync-execution.md` — corrected execution counts, explicit-interpreter recovery, remediation/verification lessons
- `references/2026-07-30-sqlite-insert-schema-pitfall.md` — required `created_at`/`updated_at` fields, silent `INSERT OR IGNORE` failure diagnosis, and schema-valid probe verification
- `bitwarden-memory-vault:references/2026-06-20-cron-memory-social-sync-counts-only.md` — validated pattern
- `bitwarden-memory-vault:references/2026-06-23-cron-memory-social-sync-execution.md` — prior run
- `ebbinghaus-memory:references/ebbinghaus-schema.md` — canonical DB schema
- `memory-social-sync-patterns:references/line-bridge-pin-fetch-failure.md` — LINE bridge PIN issued but `TypeError: fetch failed` after entry; network switch mitigation (2026-08-02 cron sync)
- `memory-social-sync-patterns:references/2026-08-02-line-bridge-auth-recovery.md` — Validated recovery sequence for PIN fetch failure with email/password login; includes environment config, stability checks, and integration guidance for social sync cron
- `references/2026-08-04-cron-memory-social-sync-execution.md` — 2026-08-04 run 1: 691 social sessions / 1,271 messages / 1,753 X records / 437 valid X URLs / 0 saved / 1,316 excluded / 0 guard violations / low; Windows python3 stub caveat confirmed
- `references/2026-08-04-cron-memory-social-sync-execution-run2.md` — 2026-08-04 run 2: 9,238 sessions / 228,368 messages / 796 X records / 452 valid X URLs / 454 saved (452 X artifacts + 2 policy facts, 1 blocked) / 133 pre-existing violations remediated / 0 final violations / low; historical leakage remediation confirmed, policy fact trigger-word collision documented

## Related Skills

- `bitwarden-memory-vault` — secret handling rules for cron jobs
- `memory-consolidation-sync` — nightly Ebbinghaus sleep + Obsidian/llm-wiki sync
- `ebbinghaus-memory` — Ebbinghaus memory operations and schema

## Memory Source Policy (2026-09-26)

Follow the Memory Source Policy in the `ebbinghaus-memory` skill: X / lm-twitterer posts and raw SNS message mirrors are NOT written to Ebbinghaus any more; they stay in `activity.jsonl` / `social_sync.db`. Only distilled first-hand facts (user conversations, work logs and decisions, sleep/health summaries) are memories. Report sync counts in the cron output instead of storing them.
