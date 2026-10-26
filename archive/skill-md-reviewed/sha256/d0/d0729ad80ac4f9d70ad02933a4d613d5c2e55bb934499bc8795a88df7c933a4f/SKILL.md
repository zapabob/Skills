---
name: windows-hermes-cron-delivery
description: Debug Windows Hermes cron scripts and notification delivery.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Windows, Cron, Telegram, Notifications, Hermes]
---

# Windows Hermes Cron Delivery

This skill diagnoses and repairs Windows Hermes no-agent cron jobs that execute scripts and deliver stdout to Telegram or another channel. It focuses on the durable boundary between the configured `script`, `workdir`, Hermes home, and the scheduler's subprocess environment; it does not replace channel authentication troubleshooting when the job itself executes successfully. Prefer direct, end-to-end repair and verification over giving the user a list of commands to run.

## When to Use

- A cron job says `ok` but no Telegram message arrives.
- A no-agent job reports `No such file or directory` for a Windows path.
- A script exists under `~/.hermes/scripts` but the cron workdir points at the repository.
- A notification job is paused, duplicated, or has no output.
- The user asks to restore a Hermes Telegram cron.

## Prerequisites

- Windows Hermes installation with `cronjob` available.
- Access to the current profile's `~/.hermes/scripts` and configured workspace.
- The job name or ID and its intended delivery target.
- Credentials remain in Hermes configuration; never request or print Telegram tokens.

## How to Run

Use `cronjob` to list, update, pause, resume, and run jobs. Use `read_file` to inspect the script and `search_files` to locate candidate copies. Use `terminal` only for bounded syntax or existence checks. Always verify the job again after an update. See `references/warashibe-telegram-cron.md` for the session-derived path-mismatch example.

## Quick Reference

- List jobs: `cronjob(action="list")`
- Run one job: `cronjob(action="run", job_id="<id>")`
- Update workdir: `cronjob(action="update", job_id="<id>", workdir="C:\\Users\\<user>\\.hermes")`
- Resume a paused job: `cronjob(action="resume", job_id="<id>")`
- Hermes script directory: `C:\Users\<user>\.hermes\scripts`
- Typical no-agent fields: `script`, `no_agent: true`, `workdir`, `deliver`

## Procedure

1. **Identify the exact job.** Invoke `cronjob` with `action="list"`. Match by job name, not a guessed ID. Record `enabled`, `state`, `script`, `workdir`, `deliver`, `last_status`, `last_delivery_error`, and `next_run_at`.

2. **Locate the actual script.** Use `search_files` for the script basename under the profile's `~/.hermes/scripts` and the configured repository. If the file is under `~/.hermes/scripts`, the canonical no-agent configuration is a relative script basename plus `workdir` set to the Hermes home directory. Do not infer that a repository copy exists.

3. **Read the script.** Use `read_file`. Confirm it emits a useful message to stdout on every intended notification path. A no-agent job with empty stdout is correctly treated as “nothing to deliver,” even when its exit code is zero.

4. **Fix path resolution.** If the script is in `C:\Users\<user>\.hermes\scripts` but `workdir` points elsewhere, invoke `cronjob` with `action="update"` and set the workdir to `C:\Users\<user>\.hermes`. Keep `script` as the basename unless the job's existing convention proves otherwise. Avoid `.sh` wrappers containing unescaped Windows paths; they can become malformed when interpreted by `/bin/bash`.

5. **Fix paused jobs only when the user's request implies restoration.** If a related notification job is paused, inspect its name, schedule, script, and delivery target. Resume it with `cronjob(action="resume", job_id=...)` only when it is part of the requested notification family. Do not resume unrelated jobs.

6. **Prevent duplicate notifications.** Look for multiple enabled jobs with the same purpose and delivery schedule. Keep the intended canonical job enabled and pause obsolete duplicates; do not delete jobs merely to make the list clean.

7. **Run a bounded test.** Invoke `cronjob` with `action="run"` after correcting the path. If the scheduler reports the job is already being fired, wait briefly through `terminal` and retry once. Treat `executed: true` and `execution_success: true` as proof that the script ran, not proof that the user visually received Telegram delivery.

8. **Verify delivery evidence.** Re-list the job and inspect `last_status` and `last_delivery_error`. A Telegram timeout or delivery error requires channel/gateway investigation; an `ok` result with empty script output requires changing the script's notification behavior rather than the Telegram target.

9. **Handle missing or broken auxiliary jobs conservatively.** If a job's configured script cannot be found in either the declared workdir or the known Hermes/repository script roots, do not invent a replacement from the prompt. Pause the job to stop repeated errors, record the missing path, and only resume after a real script is restored and tested. For duplicate jobs with one healthy canonical replacement, pause the obsolete erroring duplicate rather than running both.

10. **Report concretely.** State the root cause, exact job(s) changed, workdir/script mapping, test result, and next scheduled run. Do not claim message receipt unless the tool provides delivery evidence.

## Pitfalls

- A Windows path such as `%USERPROFILE%\.hermes\scripts\file.py` can be mangled into `C:Usersdownl.hermescriptsfile.py` when passed through Bash. Prefer a relative script and explicit Windows `workdir`.
- `last_status: ok` only proves the script process succeeded; it does not prove Telegram accepted or displayed the message.
- `no_agent: true` jobs deliver stdout. A script that intentionally prints nothing for “no opportunities” will produce no Telegram message by design.
- A manual `cronjob run` may be skipped while the scheduler is already executing the same job. Retry after the active run finishes; do not create a duplicate job.
- A script in `~/.hermes/scripts` should not be assigned a repository workdir unless the file is actually present there.
- Keep the user's existing workspace changes intact; do not reset, clean, commit, or delete unrelated files while repairing cron configuration.

## Verification

Invoke `cronjob(action="run", job_id="<target>")`, then require `executed: true`, `execution_success: true`, and a follow-up `cronjob(action="list")` showing the intended `script`, `workdir`, enabled state, and no new delivery error. If delivery is still absent despite successful execution, report that the remaining boundary is Telegram/gateway delivery or empty stdout, not script path resolution.
