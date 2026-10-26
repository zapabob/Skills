---
name: hermes-cron-admin
description: Repair Hermes cron jobs, script path blocks, and bot naming.
triggers:
  - cron failed
  - Script not found
  - cronjob error
  - telegram bot name
---

# Hermes Cron Admin

Use when diagnosing, editing, or repairing Hermes cron jobs, especially when jobs span profiles or reference script files. Covers script path resolution, cross-profile edits, and bot-name configuration.

## Core Model

- Cron jobs live in profile-specific `cron/jobs.json` files, but **some shared job tables also exist at `~/.hermes/cron/jobs.json`**.
- The `cronjob` tool is **profile-scoped**: it only lists/manages jobs visible to the current profile. Jobs owned by another profile (e.g. `delivery-worker`) will not appear when running as `job-seeker`.
- When `no_agent: true`, the cron runner executes `script` directly. The runner enforces a **scripts-directory security check**: the resolved script path must stay inside the profile’s `scripts/` directory.

## Script Path Resolution

| `script` form | Resolution |
|---|---|
| Relative filename (`disaster-news-jp.py`) | Resolved against `HERMES_HOME/profiles/<profile>/scripts/` |
| Absolute path (`C:\...\scripts\foo.py`) | Blocked if it resolves outside the profile `scripts/` directory |
| Bare name with no `profile` set | May fall back to `HERMES_HOME/scripts/`, but this often trips the security check |

**Pitfall:** Setting `script` to an absolute path under `~/.hermes/scripts/` will fail with `Blocked: script path resolves outside the scripts directory (...delivery-worker\scripts)`. The fix is to copy the script into the profile’s `scripts/` directory and use a relative filename.

**Pitfall:** `workdir` does not change where the runner looks for the script. `workdir` only sets the cwd for execution.

## Cross-Profile Editing

- When editing another profile’s `cron/jobs.json` from the current session, pass `cross_profile=True` to `patch` / `write_file`.
- Always verify by re-reading the file after editing, because the runner may have cached the old jobs.json.

## Diagnosing Failures

1. Check `last_error` and `last_delivery_error` in the job record.
2. `Script not found`:
   - Read the job’s `script` field.
   - Check whether the file exists at the resolved path inside `profiles/<profile>/scripts/`.
   - If missing, copy from `~/.hermes/scripts/` or the repo’s `scripts/` directory into the profile scripts dir.
   - Ensure `script` is a bare filename, not an absolute path outside the profile.
3. `RuntimeError: Connection error.`:
   - Usually a provider/network issue, not a script issue.
   - Re-run is usually sufficient; do not change script paths for this error.
4. `drift_skip`:
   - The job’s pinned provider/model no longer matches global config.
   - Fix with: `cronjob action=update job_id=<id> provider=<provider> model=<model>`

## Telegram Bot Name

Bot-name changes require edits in multiple places:

| Location | What it controls |
|---|---|
| `hermes_cli/telegram_managed_bot.py` `DEFAULT_BOT_NAME` | Default bot name for new Telegram pairings |
| `hermes_cli/web_server.py` `start_telegram_onboarding` | Web dashboard onboarding fallback |
| `hermes_cli/skins/<skin>.yaml` `branding.agent_name` | CLI/skin display name (persona) |

**Pitfall:** Bot name and persona name are separate. `DEFAULT_BOT_NAME` / onboarding `bot_name` control the Telegram bot account name. Skin `branding.agent_name` controls what the CLI prints. Keep them independent unless the user explicitly wants them unified.

## Verification

After edits:
1. Re-read the job from `jobs.json` to confirm the field actually changed.
2. Run the script directly with Python to confirm it executes.
3. Check `last_status` flips to `ok` on the next cron tick.
