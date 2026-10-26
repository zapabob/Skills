---
name: memory-consolidation-sync
description: "統合前の日記作成と睡眠後のWiki同期を行う。"
version: 0.3.2
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Memory, Ebbinghaus, Obsidian, Sync, Git]
    category: devops
    related_skills: [memory-maintenance, cron-recovery]
    config:
      ebbinghaus_rehearse_threshold: 0.45
      ebbinghaus_forget_threshold: 0.08
      ebbinghaus_salience_keep: 0.7
      ebbinghaus_sleep_limit: 200
      obsidian_log_path: "~/Documents/Obsidian/Hermes/Ebbinghaus/YYYY-MM_睡眠ログ.md"
      obsidian_wiki_repo: "runtime value from sync JSON: obsidian.wiki_root"
      local_obsidian_repo: "~/Documents/Obsidian/Hermes"
---

# Memory Consolidation, Pre-Sleep Diary, and Obsidian Sync

This skill runs the verified memory-maintenance workflow: external-memory recall, a sanitized pre-sleep diary, Ebbinghaus sleep, a 300ms pause, sanitized session export, and Git delivery. It does not store raw transcripts, secrets, PINs, credentials, or unredacted personal data. The synchronization target is selected from the exporter’s actual `obsidian.wiki_root`, never guessed from a historical path.

## When to Use

- The user asks for “記憶の統合と睡眠”.
- The user asks to write a diary before sleeping.
- The user asks to commit and push the Obsidian Wiki.
- A scheduled memory-maintenance run needs an auditable diary and export.
- A context handoff needs sanitized external-memory synchronization.

## Prerequisites

- Windows Python launcher `py -3` is available; `python` may be a Windows Store stub.
- `ebbinghaus_memory` is available.
- `sync_memory.py` exists at `%USERPROFILE%/Documents/New project/hermes-agent`.
- The external-memory Wiki may be at `%USERPROFILE%/Documents/ObsidianVault/Hermes-Memory-Wiki` or `%USERPROFILE%/Documents/New project/llm-wiki/Hermes-Memory-Wiki`; determine the real target from sync JSON.
- The local Obsidian repository is `%USERPROFILE%/Documents/Obsidian/Hermes`.
- Git push access is configured for the actual Wiki remote.

## How to Run

Use `search_files` and `read_file` for external recall, `ebbinghaus_memory` for sleep, `terminal` for the 300ms pause, synchronization, and Git, and `write_file`/`patch` for the pre-sleep diary and final sleep log. Run the export through the `terminal` tool from the Hermes-agent root.

## Quick Reference

- Recall: `search_files` then `read_file`
- Sleep: `ebbinghaus_memory(action="sleep", prune_mode="archive", rehearse_threshold=0.45, forget_threshold=0.08, salience_keep_threshold=0.7, limit=200)`
- Pause: `py -3 -c "import time; time.sleep(0.3)"`
- Sync: `py -3 sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep`
- Wiki root proof: `git -C <actual_wiki_root> rev-parse --show-toplevel`
- Wiki verification: `git status --short --branch`, `git diff --check`, `git rev-parse HEAD origin/<branch>`
- Local log: `git add -- Ebbinghaus/2026-08_睡眠ログ.md && git commit -m "sleep log YYYY-MM-DD — Ebbinghaus sleep + memory consolidation"`

## Procedure

1. **Check external memory first.** Search the Wiki with Japanese and English terms such as `Ebbinghaus`, `外部記憶`, `memory`, `Obsidian`, `睡眠`, and `sync`. Read only relevant `index.md`, `concepts/`, `diary/`, or `log.md` files. Prefer the newest sanitized record.

2. **Check capacity and repositories.** Invoke `terminal` with a host-appropriate capacity check and inspect Git status. On Windows, do not assume POSIX `df` is available; if the check fails, report that capacity could not be verified rather than inventing a value. Do not claim delivery if capacity or Git access blocks the run. Preserve unrelated changes.

3. **Write the pre-sleep diary before sleeping.** Create or update `diary/YYYY-MM-DD.md` in the intended Wiki with sanitized sections for the previous result, today’s purpose, unresolved issues, and a pre-sleep note. Do not include raw session logs, secrets, PINs, credentials, or personal identifiers. This diary must exist before the sleep call.

4. **Run one sleep cycle.** Invoke `ebbinghaus_memory` with `action="sleep"`, `prune_mode="archive"`, `rehearse_threshold=0.45`, `forget_threshold=0.08`, `salience_keep_threshold=0.7`, `limit=200`, `max_sleep_rehearsals=2`, and `max_negative_sleep_rehearsals=1`. Record actual counts; never invent them.

5. **Pause for 300ms.** Invoke through `terminal`: `py -3 -c "import time; time.sleep(0.3)"`. Confirm exit code 0.

6. **Synchronize without a second sleep.** From `%USERPROFILE%/Documents/New project/hermes-agent`, invoke through `terminal`:
   `py -3 sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep`
   Require `success: true` and record the JSON values for `sessions_seen`, `x_events_seen`, `memories_written`, `obsidian.items`, `obsidian.groups`, `obsidian.files`, and `obsidian.wiki_root`.

7. **Resolve the actual Wiki repository.** Use the returned `obsidian.wiki_root`, then invoke `terminal` with `git -C <wiki_root> rev-parse --show-toplevel`, `git status --short --branch`, and `git remote -v`. If multiple candidate vaults exist, only the Git repository actually written by the exporter is authoritative. Do not assume `main` or `master`; use the reported branch.

8. **Audit before staging.** Invoke `terminal` with `git diff --check` and inspect changed Markdown. Search added lines for private keys, API keys, tokens, passwords, PINs, webhooks, local absolute paths, and raw personal data. Replace detected values with `[REDACTED]` using `patch`. Raw private transcripts must not be committed.

9. **Stage only intended Wiki files.** Explicitly stage the exporter’s Markdown files and the pre-sleep diary. Leave unrelated changes unstaged. Re-run `git diff --cached --check`.

10. **Commit and push the Wiki.** Commit with `sync: Ebbinghaus sleep + session-memory export YYYY-MM-DD`, push to the actual remote and current branch, then verify `git rev-parse HEAD` equals `git rev-parse origin/<branch>`, `git diff --check` succeeds, and status is clean.

11. **Complete the diary after synchronization.** Append the actual sleep result, 300ms exit status, sync counts, resolved Wiki root, Wiki commit ID, and residual risks to the same `diary/YYYY-MM-DD.md`. Keep it sanitized. If the diary changed after the Wiki commit, make a second intended Wiki commit and push it.

12. **Update the local sleep log.** Preserve existing entries and append actual results to `%USERPROFILE%/Documents/Obsidian/Hermes/Ebbinghaus/2026-08_睡眠ログ.md`. In `%USERPROFILE%/Documents/Obsidian/Hermes`, stage only that file and commit locally. Do not push the local vault without explicit instruction.

13. **Final verification.** Confirm the Wiki’s current `HEAD == origin/<branch>`, clean status, and successful `git diff --check`; confirm the local vault has the dated sleep-log commit and no unintended changes. Report successes, blockers, counts, commit IDs, and residual risks separately.

## Pitfalls

- The diary must be created before `ebbinghaus_memory`; writing it only after sleep violates the workflow.
- `sync_memory.py` uses dynamic Wiki discovery. `ObsidianVault` and `New project/llm-wiki` can be different repositories with different remotes and branches. Never push a historical path merely because it is familiar.
- The sync JSON is the source of truth for counts and `obsidian.wiki_root`; do not infer missing values.
- `--no-sleep` is mandatory after the explicit sleep to prevent a second cycle.
- On Windows, `python` can be a Store stub; use `py -3`.
- Do not use `git add -A` when unrelated changes are present.
- Do not hard-code `main`; verify the current branch and push that branch.
- A clean `git diff --check` does not prove that secrets are absent; perform the explicit added-line audit.
- Current observed capacity risk: approximately 7.1GB free with C: at 100% usage. If capacity is insufficient, report the blocker honestly.
- Existing cron jobs must be listed with `cronjob(action="list")` before creating another. Reuse `memory-consolidation-sync-daily` when it exists; never create duplicates.

## Verification

Run these checks through `terminal` after delivery:
`git -C <wiki_root> status --short --branch && git -C <wiki_root> diff --check && git -C <wiki_root> rev-parse HEAD origin/<branch> && git -C %USERPROFILE%/Documents/Obsidian/Hermes status --short --branch && git -C %USERPROFILE%/Documents/Obsidian/Hermes log -1 --oneline --decorate`

Success requires the actual Wiki repository to be clean and synchronized with its remote, the final diary and sanitized export to be present, and the local repository to contain only the intended dated sleep-log commit.
