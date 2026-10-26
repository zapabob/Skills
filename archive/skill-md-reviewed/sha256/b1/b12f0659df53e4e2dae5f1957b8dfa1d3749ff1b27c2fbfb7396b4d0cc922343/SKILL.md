---
name: memory-sleep-diary
description: Run Ebbinghaus sleep cycle and commit to Obsidian wiki. version: 0.1.0 author: Hermes Agent license: MIT platforms: [windows] metadata:
  hermes:
    tags: [memory, sleep, diary, obsidian]
    related_skills: []
---
# Memory Sleep Diary

This skill integrates Ebbinghaus sleep cycles, diary writing, and Obsidian wiki commits. It does not perform raw transcript dumps or arbitrary LLM calls. Depends on the `ebbinghaus_memory` and `memory_llm_wiki_export` Hermes tools.

## When to Use

- `記憶の統合と睡眠` request (Japanese for "memory integration and sleep")
- `dream-synthesizer` or creative insights request — this is a common misnomer for the Ebbinghaus sleep cycle + wiki export flow
- Periodic prune after spikes of cron/social artifacts or UI noise
- User frustration about duplicate cron, noisy social-memory sync, or visible reasoning/thought clutter
- User requests "dream-synthesizer" — redirect to the Ebbinghaus sleep + wiki export flow covered by this skill
- Cron-triggered "daily development summary": collect commits/PRs/issues across repos, summarize key changes, write sanitized markdown to Obsidian vault diary

## Prerequisites

- `ebbinghaus_memory` tool available (fall back to direct SQLite queries via `execute_code` if not discoverable in cron context)
- `memory_llm_wiki_export` tool available for Obsidian wiki export
- Obsidian vault at resolved path — verify via export result's `wiki_root` field (absolute path). Current verified export target (2026-08-15): `%USERPROFILE%\Documents\New project\llm-wiki\Hermes-Memory-Wiki` (branch `master`, remote `zapabob/hermes-memory-wiki.git`)
- Git installed for Obsidian vault commits. Confirm cwd with `git remote -v && git rev-parse --abbrev-ref HEAD`. Only `ObsidianVault/Hermes-Memory-Wiki` (branch `main`, remote `zapabob/hermes-obsidian-vault`) is the live export target. `Obsidian/Hermes` has no remote — local commit only, never push.
- 300ms sleep interval configuration note: The Ebbinghaus sleep parameters control decay (`forget_threshold`, `salience_keep_threshold`, `prune_mode='archive'`), not a fixed 300ms interval. The `300ms` reference in the request may refer to a specific timing setup or hardware parameter; treat as a configurable note rather than a core tool parameter.
- Windows Python venv: use `.venv/Scripts/activate` then `python sync_memory.py ...` — do NOT use `.venv/bin/activate` (does not exist on Windows). `uv run --python 3.12` may trigger first-run interpreter download exceeding 1200s tool timeout; prefer the prebuilt `.venv` instead. `python` on PATH may resolve to C:/Python314 (3.14) — wrong version, will fail on `sync_memory.py`. Use the venv python `%USERPROFILE%\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` or `C:\Python312\python.exe`.

## How to Run

- Through Hermes: invoke the skill by name (ensure it is loaded in the active profile)
- Directly via tools:
  1. `ebbinghaus_memory(action='stats')` to inspect current state
  2. `ebbinghaus_memory(action='sleep', forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode='archive')` — note: `prune_mode`, NOT `prune`; invalid args fail silently
  3. Identify targeted cleanup candidates: low-salience duplicates, execution-record noise, repeated social-memory session summaries, `CONTEXT COMPACTION — REFERENCE ONLY` clots, UI/prompt-injection clots
  4. Remove them in small explicit `forget` batch calls
  5. If cron is producing the noise, pause duplicate sync/sleep/dream jobs first so cleanup does not immediately re-pollute memory
  6. Export with `memory_llm_wiki_export(dry_run=true)` first. If the candidate count is substantially smaller than the existing Wiki's Ebbinghaus rows, do **not** perform a full export; append a dated, sanitized aggregate inventory page and `log.md` entry instead, preserving the larger Wiki
  7. Commit and push to Obsidian vault following the auth fallback chain:
     1. SSH first — if remote is `[REDACTED_EMAIL]:...` and push gives `Permission denied (publickey)`, switch to HTTPS + `gh`
     2. Check `gh auth status`; this machine is logged in as `zapabob` over HTTPS. Switch remote: `git remote set-url origin https://github.com/zapabob/<repo>.git` then `gh auth setup-git` and retry push
     3. If `Repository not found` on HTTPS, the remote repo does not exist yet. Verify with `gh repo view zapabob/<repo>` and `gh repo list zapabob --limit 200 | grep -i <name>`
     4. Token scope gate: `gh auth status` often shows `Token scopes: none`. Creating a repo (`gh repo create`) then fails with `requires ['public_repo'] but granted ['']`. Fix by `gh auth refresh -h github.com -s repo` — this prints a one-time device code + `https://github.com/login/device`. Hand the code to the user to approve in a browser
     5. If push still can't complete (no repo, no scope), the local commit is done — report clearly and offer: (A) refresh scope + create repo, or (B) user supplies the correct existing repo URL to re-point origin. Never claim a push succeeded when only the local commit landed
  8. Verify the remote commit hash and clean working tree after push. Ensure `HEAD` equals `origin/main` on the vault repo

## Quick Reference

- `ebbinghaus_memory(action='stats')` — inspect memory state
- `ebbinghaus_memory(action='sleep', forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode='archive')` — sleep cycle
- `memory_llm_wiki_export(dry_run=true)` — dry-run comparison before full export
- `git commit -m "chore(memory): sleep-cycle consolidation export $(date '+%Y-%m-%d')"` — local commit
- `git push` — push (follow auth fallback chain)
- `git status --short` and `git rev-parse --short HEAD` — verify after push

## Procedure

1. Run `ebbinghaus_memory(action='stats')` to inspect current state (total sessions/messages, source distribution, role distribution, active/compacted counts, date range)
2. Run one sleep cycle with `ebbinghaus_memory(action='sleep', forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode='archive')`, then compare before/after counts from the sleep result itself — end-of-pipeline stats include new rows added by later sync, so use the sleep result's active_count delta: `len(archived)` equals the forgotten/archived count
3. Identify targeted cleanup candidates: low-salience duplicates, execution-record noise, repeated social-memory session summaries, `CONTEXT COMPACTION — REFERENCE ONLY` clots, UI/prompt-injection clots
4. Remove them in small explicit `forget` batch calls. If cron is producing the noise, pause duplicate sync/sleep/dream jobs first so cleanup does not immediately re-pollute memory
5. **Session log inventory** (optional but recommended): Check `_docs/` for implementation logs (`*.md`) and merge reports. Check `output/logs/` for runtime/build logs. Check `output/obsidian-memory-graph.html` for WebXR graph freshness. For Hermes SQLite inventory, inspect `PRAGMA table_info(sessions)` and `PRAGMA table_info(messages)` before writing SQL; use the live schema (session timestamps are commonly `started_at`/`ended_at`, not assumed names), then emit aggregate counts only
6. Run `python scripts/obsidian_memory_graph.py --output output/obsidian-memory-graph.html` to regenerate the 3D graph if stale
7. Export with `memory_llm_wiki_export(dry_run=true)` first. If the candidate count is substantially smaller than the existing Wiki's Ebbinghaus rows, do **not** perform a full export; append a dated, sanitized aggregate inventory page and `log.md` entry instead, preserving the larger Wiki
8. Before pushing, inspect `git status`, `git diff --stat`, `git diff --check`, and staged content for secret-like values. Commit only after confirming redaction and push the verified branch
9. Verify the remote commit hash and clean working tree after push. Ensure `HEAD` equals `origin/main` on the vault repo

## Pitfalls

- **Windows Python venv**: the hermes-agent checkout on this machine ships a Windows venv at `.venv/Scripts/activate` (Python 3.12.9). `source .venv/Scripts/activate` then `python sync_memory.py ...` — do NOT use `.venv/bin/activate` (does not exist). `uv run --python 3.12` triggers a first-run interpreter download that can exceed the 1200s tool timeout; prefer the prebuilt `.venv` instead. `python` on PATH resolves to C:/Python314 (3.14) — wrong version, will fail on `sync_memory.py`. Use the venv python.
- **Three samey Obsidian repos**: before any `git push`, confirm cwd: `git remote -v && git rev-parse --abbrev-ref HEAD`. Only `ObsidianVault/Hermes-Memory-Wiki` (branch `main`, remote `zapabob/hermes-obsidian-vault`) is the live export target. `Obsidian/Hermes` has no remote — local commit only, never push.
- **Ebbinghaus sleep param name**: sleep takes `prune_mode='archive'`, not `prune`. An unknown kwarg is ignored or errors — verify the tool schema if unsure.
- **Dream apply salience cap (verified 2026-08-06)**: `ebbinghaus_memory(action="dream", mode="apply")` rejects salience values exceeding `source_max_salience + 0.15` with error `salience X exceeds source max Y + 0.15`. The cap is dynamic — it depends on the maximum salience of the source memories in the cluster, not a fixed threshold. If the error fires, lower the dream salience to at most `source_max + 0.15` and retry. Default to 0.5 when unsure; the dream is still persisted as a semantic memory regardless of salience. Always run `action="dream", mode="preview"` first to inspect the cluster's source IDs and themes before composing the apply payload.
- **Monthly sleep log filename (verified 2026-08-06)**: The Obsidian sleep log file is named `YYYY-MM_睡眠ログ.md` (e.g. `2026-08_睡眠ログ.md`). When the month changes, create a new file — do not append to the previous month's file. Do not attempt to read the file as text first if BOM-encoded UTF-8 triggers binary detection — `write_file` directly to the new path.
- **Sleep result arrays (verified 2026-07-31)**: with `prune_mode='archive'`, the `forgotten` and `archived` arrays hold the SAME IDs and `pruned` is empty — archive is the disposal action for forgotten items, so the sleep result's active_count delta equals `len(archived)`. Read before/after counts from the sleep result or a stats call IMMEDIATELY after sleep: a later `sync_memory.py` run adds new rows (active can tick up by a few), so end-of-pipeline stats are NOT the sleep delta.
- **Windows launcher verification for large syncs**: Do not assume the PATH `python`/`python3` aliases are real interpreters. A Windows Store redirector can exit with code 49 without useful output. Before launching a long SQLite sync, run `where python` and `py -3 --version`; if the PATH alias is a stub, execute the verified script with `py -3 <temp-script.py>` or an explicit venv interpreter. Keep the run counts-only and perform an independent post-write guard verification. As of 2026-08-01, BOTH `python` and `python3` on PATH can be Windows Store stubs simultaneously. `where python` may show the stub first under `WindowsApps`. Use the full installation path directly: `%USERPROFILE%\AppData\Local\Programs\Python\Python3XX\python.exe` or `%USERPROFILE%\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`. Previous `C:\Python314` paths may no longer exist.
- **Windows path translation for script arguments (verified 2026-08-01)**: When passing a script path as argv to a Windows-native Python from Git-Bash, use the Windows-native backslash form (`%USERPROFILE%\...`), NOT the POSIX `/c/Users/...` form. Windows Python interprets `/c/Users` as `C:\c\Users` (a literal `c` directory). Shell builtins and MSYS tools accept POSIX paths, but native Windows binaries do not for argv.
- **Idempotent social reconciliation**: A high source count with `saved=0` is a valid success when candidates already exist. Report source counts, exclusions, post-write guard status, and residual risk separately; do not interpret zero new rows as data loss.
- **Ebbinghaus tool not discoverable in cron context (verified 2026-08-03)**: `tool_search("ebbinghaus memory")` returns empty when running as a scheduled cron job. The `ebbinghaus_memory` tool may not be registered in the cron tool registry. Fall back to direct SQLite queries via `execute_code` against `~/.hermes/ebbinghaus_memory.db` (schema: `memories` table with `state`, `salience`, `memory_type`, `source` columns) and `~/.hermes/state.db` (schema: `sessions` table with `source`, `started_at`, `message_count`; `messages` table with `role`, `timestamp`, `active`, `compacted`). Always run `PRAGMA table_info` first — schema may evolve.

## Verification

- `ebbinghaus_memory(action='stats')` before and after sleep — review/rehearsed/forgotten/pruned counts, before/after memory count and average salience
- `memory_llm_wiki_export(dry_run=true)` candidate count vs existing Wiki rows — if candidates are materially fewer, do not perform full export; append dated aggregate-only inventory instead
- `git status --short` and `git rev-parse --short HEAD` after push — verify clean status and exact equality of HEAD and origin/main
- `git diff --check` — verify no trailing whitespace or mixed-line-ending issues in staged content

## Reference

- `references/external-memory-recall-and-journals.md` — reusable layout and verification pattern
- `references/sync_memory_orchestration.md` — full parameter map, cron wrapper, watermark index, and manual flow
- `references/obsidian_sleep_log_vault.md` — dual-vault layout (Hermes-Memory-Wiki + Ebbinghaus sleep log), sleep log format, bridge note, and local commit pattern
- `references/wiki-destination-integrity.md` — reusable verification and redaction checklist
- `references/windows-audited-export-gate.md` — detailed reusable checklist
- `references/daily-development-summary-pattern.md` — multi-repo git scan, Ebbinghaus cron fallback to direct SQLite, diary entry format for dev summaries
- `references/forget-safety-gate.md` — forget-safety-gate.md, decay-candidate-triage.md, ebbinghaus-cue-integrity-corrections.md (the latter supersedes stale conclusions in ebbinghaus-retrieval-and-cue-integrity.md §3/§4)
- `references/2026-08-15_memory-integration-sleep-obsidian-sync.md` — Direct tool pattern (no sync_memory.py): `ebbinghaus_memory` sleep + `memory_llm_wiki_export` + git push. 943 archived, 158 items exported.
- `references/2026-08-06_memory-consolidation-sleep-dream-obsidian-sync.md` — Dream apply salience cap (`source_max + 0.15`), monthly sleep log creation, stable sleep with zero archive/rehearse
- `references/2026-08-02_memory-consolidation-sleep-obsidian-sync.md`
- `references/daily-development-summary-pattern.md` — multi-repo git scan, Ebbinghaus cron fallback to direct SQLite, diary entry format for dev summaries
- `references/2026-08-01-cron-memory-social-sync-execution.md` — both `python` and `python3` are now Windows Store stubs; use full installation path; POSIX-to-Windows path translation pitfall for script argv
- `references/wiki-destination-integrity.md` — verify actual export destination from `memory_llm_wiki_export` result's `wiki_root` field; confirm git repo path, remote, and branch
- `references/2026-07-17_memory-consolidation-session.md`
- `references/2026-07-26_memory-consolidation-sleep-obsidian-sync.md`
- `references/2026-07-28_memory-consolidation-sleep-obsidian-sync.md`
- `references/2026-07-30-windows-social-memory-sync.md`
- `references/2026-07-31-memory-consolidation-sleep-obsidian-sync.md`
- `references/2026-08-06_memory-consolidation-sleep-dream-obsidian-sync.md`
- `references/2026-08-02_memory-consolidation-sleep-obsidian-sync.md`
- `references/2026-08-15_memory-integration-sleep-obsidian-sync.md`
- `references/2026-08-01-cron-memory-social-sync-execution.md`
- `references/daily-development-summary-pattern.md`
- `references/ebbinghaus-cron-runtime.md`
- `references/ebbinghaus-cue-integrity-corrections.md`
- `references/ebbinghaus-cue-writer-integrity.md`
- `references/ebbinghaus-retrieval-and-cue-integrity.md`
- `references/export-gate-corrections.md`
- `references/external-memory-recall-and-journals.md`
- `references/forget-safety-gate.md`
- `references/obsidian_sleep_log_vault.md`
- `references/sync_memory_orchestration.md`
- `references/wiki-destination-integrity.md`
- `references/windows-audited-export-gate.md`