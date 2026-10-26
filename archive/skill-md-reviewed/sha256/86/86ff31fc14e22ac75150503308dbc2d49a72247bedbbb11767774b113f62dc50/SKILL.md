---
name: windows-ebbinghaus-cron-verification
description: "Use for Windows Ebbinghaus sleep cron verification."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [memory, ebbinghaus, cron, obsidian, windows, verification]
    related_skills: [ebbinghaus-memory, agent-memory-consolidation, obsidian]
---

# Windows Ebbinghaus Cron Verification

Use when a scheduled or manual Windows job must run the Ebbinghaus memory sleep cycle and write a sanitized Obsidian summary. Keep the operation non-recursive: never create, edit, delete, or invoke cron jobs from inside the sleep job.

## Workflow

1. Get the local/JST timestamp with `date` before choosing the monthly note name.
2. Prefer the exposed `ebbinghaus_memory` tool. If it is unavailable, use the direct provider fallback in `references/windows-ebbinghaus-cron-verification.md`.
3. For the direct provider, invoke the project Python explicitly from `.venv/Scripts/python.exe`; the Windows Store `python` shim may exit without running Python. Call `initialize(session_id, hermes_home=...)` — `session_id` is the FIRST POSITIONAL arg and the signature is fully synchronous (do not await). Use a stable non-empty session id. A ready-made runner exists at `scripts/ebbinghaus_stats_cron.py` in the Hermes checkout: `.venv/Scripts/python.exe scripts/ebbinghaus_stats_cron.py stats`.
   - Correct import: `from plugins.memory.ebbinghaus import EbbinghausMemoryProvider` (the class lives in `plugins/memory/ebbinghaus/__init__.py`; there is **no** `plugins.memory.ebbinghaus.provider` module).
4. Capture `stats` before sleep, run sleep with explicit thresholds (`prune=true`, `rehearse_threshold=0.45`, `forget_threshold=0.08`, `salience_keep_threshold=0.7`, `limit=200`), then capture `stats` again.
5. Treat provider responses as possibly JSON-encoded strings. Decode them before reading fields. Verify the sleep effect from the before/after `stats.count`; do not trust a sleep response's processed count as the resulting database count. Use the `pruned` list length for the reported prune count.
6. Resolve the fixed or configured Obsidian vault path. Create the output directory if needed. Read the monthly note first; when appending to an existing note, anchor the edit on a unique dated section because generic memo lines repeat.
7. Create the bridge note only when it does not exist. Never overwrite it during routine sleep.
8. Write only timestamp, counts, thresholds, and a statement that raw logs/secrets/private text were excluded. Do not persist API keys, tokens, OAuth values, environment values, or raw session messages.
9. Read the written note back and run a targeted secret-pattern search. Report the saved path, before/after count, and prune count concisely in Japanese.

## Verification commands

- `".venv/Scripts/python.exe" -m py_compile <fallback-script>`
- `git diff --check` when a repository helper was edited
- direct `stats` invocation after writing the note
- note read-back plus secret-pattern search

## Pitfalls

- **`hermes -z` CLI times out in cron/no-user contexts (120s+).** Do not attempt `hermes -z "Use the ebbinghaus_memory tool ..."` for cron jobs on this Windows host — it hangs and never returns. Go directly to the Python provider fallback.
- Do not use the Microsoft Store `python` alias when a project `.venv` exists.
- **`py -3` works as a fallback when `.venv` is unavailable.** If `.venv/Scripts/python.exe` does not exist or the venv is broken, `py -3` (the system Python launcher, 3.12.x) can run the provider directly from the repo root with `py -3 -c "..."` or `py -3 script.py`. The `sys.path.insert(0, '.')` from the repo root makes `plugins.*` and `hermes_constants` importable.
- `EbbinghausMemoryProvider.initialize()` requires `session_id` in current Hermes versions.
- A provider warning about SQLite WAL should be reported as an operational warning, not copied into Obsidian.
- A repeated append anchor can cause a patch to fail or append in the wrong section; widen it with the complete final dated section.
- A no-op count change does not mean sleep failed: rehearsal counters can increase while total count remains stable.
- Full repository tests may be blocked by unrelated optional dependencies or Windows-specific failures; report focused verification separately and do not modify unrelated code merely to force the whole suite green.
