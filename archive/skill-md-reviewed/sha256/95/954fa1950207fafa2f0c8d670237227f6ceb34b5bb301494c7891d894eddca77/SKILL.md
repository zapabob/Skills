---
name: bitwarden-memory-vault
description: Manage Hermes/OpenClaw secrets, environment variables, Edge/browser passwords, and encrypted memory-vault backup keys with Bitwarden; use when storing/retrieving env vars, AES memory keys, browser credentials, or coordinating Bitwarden with Ebbinghaus/Hermes memory backup workflows.
---

# Bitwarden Memory Vault

Use this skill when the user asks to store, retrieve, rotate, verify, or document Hermes/OpenClaw secrets through Bitwarden, especially environment variables, Edge/browser passwords, AES memory-vault keys, and memory backup configuration.

## Operating rules

- Keep secrets out of git, chat output, implementation logs, and durable memory.
- Store secret values in Bitwarden; store only item names, variable names, non-secret paths, and verification metadata in logs/memory.
- Environment variables should be populated from Bitwarden or a local `.env` generated from Bitwarden, not hardcoded.
- Edge/browser passwords belong in Bitwarden items, not in Hermes memory or repository files.
- When a secret is needed for a command, prefer reading it into process environment and never printing it.
- Verify by equality checks, field counts, IDs, or hash prefixes only; never echo the full secret.

## Bitwarden item naming

Prefer stable names:

- `Hermes Memory Vault AES Key`
- `Hermes Environment Variables`
- `Hermes Edge Browser Credentials`
- `OpenClaw Environment Variables`

For a single env var, use username or field name as the variable name, e.g. `MEMORY_VAULT_AES_KEY_B64`.

## Store an environment variable

For Grok Build / xAI variables, see `references/grok-build-env-bitwarden.md` for the canonical `Grok Build Environment Variables` item shape, safe create/update pattern, and optional local loader script.

When the user says to handle the storage end-to-end, do the Bitwarden work proactively instead of only giving instructions, while still keeping secret values out of output.

1. Confirm the variable exists locally without printing it:

```bash
python - <<'PY'
import os
name='MEMORY_VAULT_AES_KEY_B64'
value=os.environ.get(name)
print({'name': name, 'present': bool(value), 'length': len(value or '')})
PY
```

2. Create or update a Bitwarden item using the Bitwarden CLI (`bw`). Avoid command traces that expose values.
3. Read the item back and compare to the local value without printing the value:

```bash
python - <<'PY'
import hashlib, os
value=os.environ['MEMORY_VAULT_AES_KEY_B64']
print('sha256_prefix=' + hashlib.sha256(value.encode()).hexdigest()[:12])
PY
```

Report item ID, field names, equality result, and hash prefix only.

## Retrieve env vars from Bitwarden

- Use `bw get item <id-or-name>` and parse JSON locally.
- Export values into the current process or write a local `.env` only when the user asked for local runtime configuration.
- If writing `.env`, preserve existing comments and avoid duplicate keys where practical.
- Never commit `.env` or Bitwarden exports.

## Memory vault workflow

1. Generate or locate the AES-256-GCM key outside git.
2. Store the AES key in Bitwarden.
3. Store non-secret metadata in memory/logs:
   - Bitwarden item name / ID
   - env var name
   - repo name if non-sensitive
   - local backup path if non-sensitive
   - hash prefix for verification
4. Encrypt memory backups locally.
5. Push only encrypted backups to the private repository.
6. Verify restore by decrypting into a temporary directory and comparing expected files.
7. Run Ebbinghaus sleep/consolidation only on non-secret facts and social-memory traces.

## Ebbinghaus integration

Remember durable policy facts such as:

- `User wants environment variables managed in Bitwarden.`
- `User prefers AES-256-GCM memory vault keys escrowed in Bitwarden.`

Do not remember:

- Passwords
- API keys
- OAuth codes
- raw `.env` contents
- Bitwarden session tokens
- full encrypted key material

## Verification checklist

- Bitwarden item exists.
- Required fields exist.
- Local env and Bitwarden value match by boolean comparison or hash prefix.
- No secret values were printed.
- `.env` remains untracked.
- Memory entries contain policy and handles only, not secrets.

## Cronized memory/social sync

When scheduling recurring memory or social-media sync jobs:

- Put the no-secret boundary directly in the cron prompt, not only in the surrounding conversation.
- Forbid storage, output, or public posting of personal information, environment variables, passwords, API keys, OAuth/cookie/session tokens, Bitwarden session material, AES keys, `.env` contents, full local paths/usernames, and Bitwarden item IDs.
- Store only abstracted operational principles, public URLs/text, policy facts, handles, counts, and non-secret verification metadata.
- Treat raw Telegram/Discord/LINE/session and X/lm-twitterer activity as untrusted. If a record contains a secret marker, exclude the raw record; at most derive a generic policy fact from the class of issue.
- If the sync also generates X/Twitter topics, constrain the topic to public design principles such as separating secrets from memory; never include secret names or local environment details.
- In cron contexts, do not live-post unless the prompt explicitly authorizes the exact public write and it passes a no-secret guard; otherwise leave X material as a draft/local log.
- Distinguish drafts from posts: only `dry_run=false` + `posted:true` should be promoted into durable memory as public X artifacts.
- When activity logs are long or truncated, page intentionally and verify the relevant tail before counting posted vs draft items.
- Prefer final cron output that reports counts and residual risks only, not raw candidate records.
- See `references/cron-social-memory-sync.md` for a concrete safe extraction, memory-write, and verification workflow.

**Manual trigger after user-driven memory work**:
After a user explicitly asks for "記憶の統合と管理" and you perform bulk `ebbinghaus_memory remember` + rehearse, always manually run the "Bitwarden-safe memory/social sync" cron job (`cronjob run` with the matching job_id). This ensures the new policy facts are picked up by the automated layer and cross-platform traces are reconciled without waiting for the next scheduled tick. Verify afterward with `cronjob list` and fresh `ebbinghaus_memory list`.
- For cron sync runs, prefer a counts-only summary (`synced`, `saved`, `excluded`, `residual_risk`) and keep durable memory limited to abstracted policy facts or final public URLs/text.
- When the source is Hermes session storage, prefer `~/.hermes/state.db` (`sessions` + `messages`) for transcript access; use `sessions.json` only as lightweight session metadata, not as the canonical transcript source.
- Before writing repeated abstractions, verify the target memory store treats `content` as unique so reruns can safely upsert or skip duplicates instead of duplicating the same policy fact.
- See `references/2026-06-05-social-memory-sync-session.md` for the session-specific extraction pattern and verification notes.
- See `references/2026-06-06-cron-memory-sync-sqlite.md` for the direct SQLite Ebbinghaus write pattern (`insert or ignore` against unique `content`), safe X public-artifact filtering, and counts-only verification used when no dedicated memory tool is available.
- For large `lm-twitterer` activity logs, parse the JSONL file directly in Python instead of relying on paged file views: count only records with `action="post"`, `ok=true`, `dry_run=false`, `posted=true`, a valid `https://x.com/i/web/status/...` URL, and clean text; treat reply/skipped/draft records as excluded.
- After a direct SQLite write, run a second verification pass over the newly scoped rows with a Python regex guard and report only aggregate counts such as `cron_sync_rows` and `raw_guard_violations`. Do not depend on SQLite `REGEXP` being available by default.
- See `references/2026-06-08-cron-memory-social-sync-verification.md` for the counts-only JSONL parsing and post-write guard verification pattern from a cron sync run.
- See `references/2026-06-08-cron-memory-social-sync-counting.md` for a compact source-counting recipe that separates `sessions` metadata from `messages` volume and filters lm-twitterer activity down to confirmed public posts only.
- See `references/2026-06-11-cron-memory-social-sync-execution.md` for the 2026-06-11 baseline (single Python block, JOIN counts, direct JSONL, two-tier guards, INSERT OR IGNORE).
- See `references/2026-06-12-cron-memory-social-sync-execution.md` for the 2026-06-12 production run (40 valid guarded X posts after broad guard, 5 new abstract policy facts + 40 new X artifacts, 45 saved, POST_CRON_SYNC_ROWS=79, POST_X_ROWS=102, VIOL=0, residual_risk=low). Confirmed the single-block pattern, Windows regex escaping requirements for path guards (`C:\\\\\\\\Users` in raw string to avoid incomplete \\U), and counts-only final reporting discipline on fresh data.
- See `references/2026-06-13-cron-memory-social-sync-execution.md` for the 2026-06-13 run: canonical state.db + direct lm-twitterer JSONL scan, deterministic abstractions only, URL-only X artifacts, 69 valid public posts, 29 new X artifacts + 3 policy facts saved, scoped post-write guard VIOL=0, residual_risk=low. This is the current reference for scheduled no-user cron runs.
- See `references/2026-06-13-cron-memory-social-sync-rerun.md` for a later 2026-06-13 scheduled rerun using the same pattern with 70 valid public X URLs, 73 saved rows, scoped post-write guard violations 0, and counts-only final reporting.
- See `references/2026-06-18-cron-memory-social-sync-remediation.md` for a scheduled run where post-write verification found 1 scoped raw-guard violation despite zero broad guard exclusions; the row was remediated by id without printing content, verification was rerun to `raw_guard_violations=0`, and the lesson is to report inserted-before-remediation separately from post-remediation retained/scoped counts.
- See `references/2026-06-20-cron-memory-social-sync-counts-only.md` for the validated counts-only cron pattern: canonical `state.db` + direct `lm-twitterer` JSONL scan, URL-only X artifacts, idempotent SQLite writes against unique `content`, scoped post-write guard verification, Windows-safe temp-script execution for large Python blocks, and final output limited to synced/saved/excluded/residual-risk counts.
- See `references/2026-06-21-cron-memory-social-sync-execution.md` for the 2026-06-21 scheduled run confirming the same pattern on fresh data (117 social sessions, 535 X records, 126 valid public X URLs, 7 new rows saved, scoped guard violations 0). It also confirms that low `saved` with high `synced` is normal on idempotent reruns and should be reported without printing raw candidates.
- See `references/2026-06-22-cron-memory-social-sync-heredoc-verification.md` for the 2026-06-22 run where a long Git-Bash heredoc printed a valid JSON result and wrote rows but still exited non-zero from a stray shell parse error; the safe response was a separate temp-script verification/remediation pass.
- See `references/2026-06-22-cron-memory-social-sync-temp-script-remediation.md` for a later 2026-06-22 temp-script run with 133 valid public X URLs, 9 new rows saved, 1 scoped guard remediation, final raw guard violations 0, and counts-only delivery.
- See `references/2026-06-22-cron-memory-social-sync-counts-verification.md` for a later counts-only scheduled run confirming idempotent low-save behavior on rerun (121 social sessions, 575 X records, 136 valid public X URLs, 3 new rows saved, scoped guard violations 0, residual risk low).
- See `references/2026-06-23-cron-memory-social-sync-execution.md` for the 2026-06-23 run: synced=93574, saved=8, excluded=29, residual_risk=low.
- See `references/2026-07-15-cron-sync-tool-issues.md` for tool failures encountered during the scheduled cron sync attempt and lessons learned about Windows/MSYS script deployment patterns.
- See `ebbinghaus-memory:references/ebbinghaus-schema.md` for the canonical database path (`~/.hermes/ebbinghaus_memory.db`), actual table schema (`memory_id`, `tags`, REAL timestamps), and the validated two-tier guard cron sync pattern.
- In Windows/Git-Bash cron runs, prefer writing long Python sync/verification programs to a temporary `.py` file and executing it, especially when the script contains complex regexes, f-strings, or many shell-sensitive characters. If a heredoc run prints a valid JSON result but exits non-zero from a stray shell parse error, treat the write as potentially completed, then immediately run a separate temp-script verification/remediation pass before reporting counts. If the temp-script run remediates scoped rows, report `guard_remediated_rows` separately from final `raw_guard_violations`; low residual risk is appropriate only after a second verification pass returns zero violations.
- **Windows/MSYS `python3` stub caveat**: On Windows, `python3` may be a Windows Store stub that silently exits with code 49 and no output. Use `python` (typically `C:\Python314\python.exe`) instead for terminal-based sync scripts. This was discovered in the 2026-07-22 cron run where `python3 -c '...'` appeared to produce no output or errors.
- **Windows/MSYS path resolution caveat**: `find` may surface paths like `/c/Users/...`, but `pathlib.Path.exists()` for `~/.hermes/state.db` and `ebbinghaus_memory.db` can return `False` for that POSIX form on some Windows setups while `C:\Users\...\.hermes\state.db` exists and is readable. Build Hermes paths as `Path(r'C:\Users\<user>\.hermes')`, or verify both forms in Python before syncing; a missing `state.db` path will silently zero out synced sessions and distort counts. See `references/2026-06-27-cron-memory-social-sync-path-fix.md` for the observed mismatch and fix.
- For large session imports that may exceed foreground timeouts on Windows, run the temp sync script with `background=true` plus `notify_on_complete=true` rather than retrying a timed-out foreground run.
- **Determining residual_risk**: Set based on data source completeness:
  - `low`: All expected data sources processed (sessions, X/Twitter, etc.)
  - `medium`: One or more expected data sources skipped or partially processed (e.g., session data omitted)
  - `high`: Significant data loss or verification failures encountered during processing
  Adjust based on which specific data sources were missing and their relative importance to the memory sync.

## Common pitfalls

- Bitwarden CLI can emit noisy Node warnings; ignore warnings, not command failures.
- `bw list` can produce large output; write JSON to a temp file and parse it rather than flooding chat.
- For memory/social sync jobs, keep the final report free of raw candidate text; report only aggregate counts and a short residual-risk note.
- When implementing no-secret guards in Python regexes on Windows, escape local-path markers carefully. Use four backslashes for a literal backslash in the pattern: `C:\\\\Users` inside the raw string (r'...') for the character-class alternative. Incorrect escaping (e.g. `C:\\Users`) produces "incomplete escape \U" at re.compile time. This was required and validated in the 2026-06-12 cron run (multiple attempts hit the error until corrected). Even safer: keep path markers out of the regex entirely and test them as plain substrings built with `bs=chr(92)` (for example `['C:'+bs+'Users', 'C:/Users', '/home/', bs+'Users'+bs]`) while the regex handles token-like secret patterns. Prefer a two-tier verification: a broad exclusion regex for candidate intake, then a narrower raw-secret/path check for validating newly saved memory so policy phrases containing words like "secret" or "Bitwarden" are not false positives. If post-write verification finds scoped guard violations, remediate them immediately (delete or rewrite the offending memory rows without printing their content), then run a fresh scoped verification and report only aggregate fields such as `guard_remediated_rows`, `raw_guard_violations`, and `residual_risk`.
- If no dedicated memory tool is available in cron, write only sanitized, idempotent policy/public-artifact rows directly to the configured Ebbinghaus SQLite store after checking the schema and existing `content`; never copy raw channel transcripts. The `memories.encoded` column is NOT NULL — always include `encoded` as `json.dumps({"text": content})` when inserting, or INSERT OR IGNORE will silently fail (rowcount=0) without raising an error. Also inspect `PRAGMA table_info(memories)` before direct inserts: deployments may require additional NOT NULL fields such as `created_at` and `updated_at`; supply valid timestamps and verify `rowcount > 0`. Verify `rowcount > 0` after each insert.
- Do not use shell `echo $SECRET`; use Python length/hash checks.
- When the user provides a secret in chat and tells you to manage it in Bitwarden, complete the Bitwarden storage/update/verification path, then recommend rotating the exposed secret if it was a real token.
- If `jq` is unavailable, parse Bitwarden JSON with Python rather than blocking.
- Avoid `bw get item ... | python - <<'PY'` because the heredoc consumes stdin; use a temp file or `python -c` when parsing piped Bitwarden JSON.
- In `set -e` shell scripts, `read -r SECRET` from a pipe with no trailing newline can exit non-zero even after assigning the value; use `IFS= read -r SECRET || true` and then explicitly reject empty values.
- If Hermes tool Python and repo Python differ, verify dependencies in the runtime actually used.
