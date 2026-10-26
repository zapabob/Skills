---
name: x-automation-operations
description: "Use for authenticated X automation and safe reply reporting."
version: 1.0.0
author: Hermes Agent
tags: [x, twitter, automation, lm-twitterer, replies, cron, privacy]
---

# X Automation Operations

Use this class-level skill for authenticated X/Twitter automation from Hermes, especially scheduled posts, mention replies, and operational verification. Prefer the Hermes-native lm-twitterer route when configured; use xurl or a direct plugin invocation only as an explicit fallback.

## Execution workflow

1. Identify the requested operation and whether it is read-only, dry-run, or live.
2. Preserve explicit user parameters exactly, including `dry_run=false`, count limits, provider, and model.
3. Prefer a registered Hermes tool when available.
4. If the tool is not exposed in the current surface, inspect the registered CLI help and use the equivalent nested command rather than inventing a top-level command.
5. Run the operation once with the requested limit and mode.
6. Verify the structured result's `ok`/status and aggregate counters.
7. For unattended jobs, return only safe aggregate status; never emit raw candidates or authentication material.

## lm-twitterer reply workflow

The registered CLI spelling for live mention replies is:

```bash
hermes lm-twitterer replies --live --count 50 --provider moa --model hakuapulse-orchestrator
```

Important details:

- `--live` enables publication; omitting it is a dry run.
- `--count` is the maximum number of candidates to inspect, not a promise that that many mentions exist.
- `--mark-seen-on-dry-run` is opt-in and should not be added unless requested.
- Pass explicit provider/model overrides only when the user requests them and the plugin allowlist accepts them.
- A successful no-op (`count_checked: 0`, zero replies, and a message such as `no new whitelisted mentions`) is valid and should not be misreported as failure.

## Safe reporting contract

For cron or unattended delivery, report only:

- candidates/messages checked (count)
- replies posted (count)
- sanitized status/message

Do not report or persist cookies, tokens, environment variables, raw candidate records, tweet text from private records, thread contents, or raw API responses. Do not infer that zero surfaced candidates proves that no mentions exist when the backend uses a sampled home timeline fallback; report the observed count and status only.

## Rotation state drift (topic-bank cron posts)

When a cron job rotates through a curated topic bank (`topics_*.json` + `rotation_state.json` + `_rotation_picker.py` under `~/.hermes/lm-twitterer/`), the state files can drift out of sync with reality: posts made outside the picker, state resets, or manual edits leave `used_ids`/`posted` lists stale, and the picker re-picks an already-posted angle.

Verified 2026-08-01 (`hermes-viral-tweets-v018`): picker returned ID 13 even though it was posted two days earlier. Recovery pattern:

1. **Ground truth is `~/.hermes/lm-twitterer/activity.jsonl`** — filter `action=post`, `posted:true`, `dry_run:false`, then match `tweet_text` against the topic bank's feature details to determine which IDs are genuinely used.
2. Cross-check against `topics_*.json` `posted` list — it may also be missing entries (e.g. an ID posted via a different flow that was never recorded).
3. After each post, update BOTH `topics_*.json` `posted` (id/date/url) AND `rotation_state.json` `used_ids` so the next run's picker excludes it.
4. On this Windows host, `python` may resolve to the WindowsApps stub (prints "Python", exit 49) — invoke the repo venv explicitly (`/c/Users/<user>/Documents/New project/hermes-agent/.venv/Scripts/python`).

## Failure handling

- If a command name is rejected, use `hermes lm-twitterer --help` and then `hermes lm-twitterer replies --help` to discover the registered spelling.
- If the CLI is unavailable but the repository plugin is present, use the documented direct `core.reply_mentions(...)` path with the same arguments, keeping stdout sanitized.
- For a direct `importlib` bootstrap, register the module in `sys.modules` before `spec.loader.exec_module(mod)`. Dataclass-decorated plugin modules can otherwise fail during import with `AttributeError: 'NoneType' object has no attribute '__dict__'`.
- On Windows, invoke the repository's Hermes venv interpreter explicitly (for example `.venv/Scripts/python.exe`); the `python` command may resolve to a Windows Store stub or a different environment.
- In unattended/cron execution, avoid inline `python -c`/arbitrary-script paths that require interactive approval. Prefer the registered Hermes CLI or a pre-deployed standalone script, and verify its sanitized output.
- Do not treat an empty candidate set as an auth failure without checking the structured `ok` and status fields.
- Do not expose secrets while debugging; inspect only boolean readiness fields and aggregate errors.

## Related skills

Existing X skills overlap with this one: `lm-twitterer-operations`, `hermes-x-posting-workflows`, and `x-twitterer-posting`. Those skills contain broader posting/media/history material; this skill concentrates on live automation command discovery, reply execution, and safe aggregate reporting.

## References

See `references/live-reply-cli-and-safe-reporting.md` for the session-derived command mapping and sanitized result contract.
See `references/windows-direct-core-bootstrap.md` for the Windows venv, `sys.modules` import bootstrap, and approval-safe direct invocation pattern.
