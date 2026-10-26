---
name: cron-script-sync-repair
description: Repair Windows cron paths and sync script deployments.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Windows, Cron, Synchronization, Telegram, Verification]
---

# Windows Cron Script Sync Repair

This skill repairs Windows Hermes cron jobs whose scripts, workdirs, or delivery targets drift out of sync, and keeps approved operational scripts synchronized between the repository and `.hermes`. It does not invent missing business logic or claim delivery from an exit code alone. The workflow prefers deterministic no-agent scripts, explicit Windows workdirs, and hash-based verification.

## When to Use

- A Hermes cron reports `last_status: error`.
- A cron is `ok` but its Telegram message does not arrive.
- A script exists in `.hermes\scripts` but the cron points at the repository.
- Repository and `.hermes` copies of an operational script diverge.
- Several jobs perform the same notification and one is failing.
- A cron references a script that no longer exists.

## Prerequisites

- Windows Hermes profile with the `cronjob` tool available.
- Repository at `%USERPROFILE%\Documents\New project\hermes-agent` or an explicitly confirmed alternative.
- Operational scripts under `%USERPROFILE%\.hermes\scripts`.
- A known Telegram destination when Telegram delivery is intended.
- Do not request, print, or copy credentials, cookies, tokens, or `.env` contents.

## How to Run

Use `cronjob` to inspect and modify scheduler state, `read_file` and `search_files` to inspect script placement, `patch` to make minimal code fixes, and `terminal` to run bounded syntax, preflight, hash, or direct-script checks. Use `delegate_task` only when the user explicitly wants a subagent to investigate. Use `write_file` only for a new sync helper or report artifact.

## Quick Reference

- Inspect jobs: `cronjob(action="list")`
- Run a job: `cronjob(action="run", job_id="<id>")`
- Update a job: `cronjob(action="update", job_id="<id>", ...)`
- Pause an obsolete/error duplicate: `cronjob(action="pause", job_id="<id>")`
- Repository scripts: `%USERPROFILE%\Documents\New project\hermes-agent\scripts`
- Deployed scripts: `%USERPROFILE%\.hermes\scripts`
- Sync helper: `scripts/sync-hermes-operational-scripts.py`
- Sync report: `%USERPROFILE%\.hermes\sync-reports\latest-operational-script-sync.json`

## Procedure

1. **Inventory the scheduler.** Invoke `cronjob(action="list")`. Filter attention to enabled jobs with `last_status: error`, missing `script`, suspicious `workdir`, `deliver: local` where Telegram is expected, or duplicated purpose. Record the job ID, schedule, `script`, `workdir`, `no_agent`, `deliver`, `last_status`, and `last_delivery_error`.

2. **Locate the real script.** Use `search_files` under both known script roots. Then use `read_file` on the exact deployed copy. Do not assume a repository copy exists, and do not repair a missing script by inventing a replacement.

3. **Separate execution from delivery.** A no-agent job delivers stdout. `last_status: ok` proves the process completed, not that Telegram displayed a message. Check whether the script prints useful output on both hit and no-hit paths, and confirm that `deliver` is an explicit target such as `telegram:7201110294` when required.

4. **Repair Windows path resolution.** For a script under `%USERPROFILE%\.hermes\scripts`, prefer a relative `script` basename with `workdir: %USERPROFILE%\.hermes` or `%USERPROFILE%\.hermes\scripts`, according to the script's path assumptions. Avoid Bash `.sh` wrappers containing unescaped Windows paths; they can become `C:Users...` and fail with `No such file or directory`.

5. **Repair import-path failures minimally.** If a deployed wrapper imports a repository plugin directly and fails with `ModuleNotFoundError` for a repository module, patch the wrapper to add its confirmed repository root to `sys.path` before loading the plugin. Apply the same change to the repository copy and deployed copy, then run a non-posting preflight.

6. **Handle duplicates conservatively.** If two jobs have the same purpose, keep the verified canonical script-based job and pause the obsolete or erroring duplicate with `cronjob(action="pause", job_id="...")`. Do not delete jobs or resume unrelated paused jobs.

7. **Handle missing scripts conservatively.** If the configured script is absent from both known roots, pause the job to stop repeated errors. Report the missing absolute path. Resume only after a real script is restored and syntax/preflight checks pass.

8. **Synchronize approved operational scripts.** Invoke through `terminal` from the repository root:

   ```text
   python scripts/sync-hermes-operational-scripts.py
   ```

   The helper's approved allowlist is the synchronization boundary. It imports deployed-only operational scripts on first setup, then treats the repository as the source of truth and deploys changes to `.hermes`. Do not use a broad recursive copy that overwrites unrelated user scripts.

9. **Verify the sync report.** Use `read_file` on `%USERPROFILE%\.hermes\sync-reports\latest-operational-script-sync.json`. Require `ok: true`, `missing: []`, and no unexpected entries in `imported_to_repo` or `deployed_to_hermes`. The normal steady state reports `unchanged: 14` for the configured allowlist, but do not hard-code that count as a permanent invariant.

10. **Run a bounded test.** Use `terminal` for `python -m py_compile` or a non-posting preflight. Use `cronjob(action="run", job_id="...")` only when the job's external side effect is intended. Never repeatedly trigger a live post or purchase workflow while testing.

11. **Re-list and report.** Invoke `cronjob(action="list")` after changes. Confirm the intended job is enabled, has the correct `script`, `workdir`, and `deliver`, and that a manual run returns `executed: true` and `execution_success: true`. Report remaining delivery uncertainty separately from script execution success.

## Pitfalls

- `deliver: local` intentionally does not send to Telegram.
- Empty stdout can correctly mean “no notification”; it is not automatically a scheduler failure.
- A successful script run does not prove Telegram delivery; inspect the cron job's `deliver`, `last_delivery_error`, and `last_status` after a real run.
- If a secondary target is malformed or a placeholder such as `discord:*`, remove it or replace it with a real numeric Discord channel snowflake. Discord requires a snowflake ID; a successful Telegram leg can coexist with a Discord HTTP 400 failure.
- After removing a bad secondary target, avoid an immediate duplicate rerun if the primary delivery already succeeded; let the next scheduled run validate the repaired route, or rerun only with explicit duplicate-delivery approval.
- Do not infer that `last_status: ok` means every delivery target succeeded; verify each configured platform separately.
- Never claim that a message arrived unless the platform delivery result or gateway log confirms it.
- A manual run can be skipped while the same job is already executing. Wait and retry once rather than creating a duplicate.
- A script copied only to `.hermes` will be overwritten or become stale unless it is also added to the approved repository source and sync allowlist.
- The sync helper must not be allowed to overwrite unrelated scripts, generated media, credentials, logs, or runtime state.
- A successful direct script run does not prove the Telegram channel delivered the message; inspect `last_delivery_error` and channel evidence separately.
- Do not reset, clean, or rewrite unrelated repository changes while fixing cron operations.
- Disk-full errors can make a correct cron update fail to persist. Check system disk state with `terminal` before retrying; delete only explicitly approved temporary caches, never source or auth data.

## Verification

Run the following through `terminal` from the repository root, then inspect the JSON report with `read_file`:

```text
python scripts/sync-hermes-operational-scripts.py
```

The repair is verified when the command exits successfully, the report has `ok: true` and `missing: []`, and a follow-up `cronjob(action="list")` shows the intended script/workdir/delivery mapping with no new error for the repaired job.
