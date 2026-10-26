---
name: cron-repair
description: "Repair Hermes cron jobs with missing/wrong script paths."
---

# cron-repair

Use when a Hermes cron job fails because its configured `script` path is missing, stale, resolved against the wrong profile-local directory, or blocked by the profile-local scripts-directory security boundary.

## Workflow

1. Inspect actual script locations:
   - `~/.hermes/scripts/`
   - repo `scripts/`
   - profile `scripts/`
2. Read the failing job from the relevant `cron/jobs.json`.
3. If the script exists outside the job's profile `scripts/` directory, do NOT use an absolute path in `jobs.json` — that trips the security check `Blocked: script path resolves outside the scripts directory`. Instead:
   - copy the script into the profile `scripts/` directory
   - keep the `script` value as the bare filename so it resolves inside that directory
4. If the script is genuinely missing from all script roots, patch `script` to a real path, preferring an absolute Windows path in JSON.
5. Verify the script runs directly.
6. If `cronjob list` shows 0 jobs while a failure notification mentions one, that usually means the visible tool is reading a different profile than the job's `jobs.json`. Inspect and patch the JSON directly; do not keep querying the wrong profile.

## Pitfalls

- Windows `jobs.json` often stores relative script names that resolve against a profile `scripts/` directory missing the file. Always switch to an absolute path only when the file can live there.
- Cron has a security boundary: script paths must resolve inside the job's profile `scripts/` directory. Absolute paths outside that tree are rejected at runtime even when the file exists.
- Repo scripts and `.hermes/scripts/` can drift. Reconcile by copying missing scripts into the profile `scripts/` directory, not by recreating jobs blindly.
- Do not trigger live cron sends as part of repair unless the user explicitly asks. Repair, verify by direct script execution, and report.

## References

- `references/cron-script-path-repair.md`
- `references/cron-profile-scripts-boundary.md`
- `scripts/verify_cron_script.py`
