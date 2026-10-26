---
name: hermes-cron-operations
description: "Hermes cron ops: pin provider/model to stop drift skips."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cron, scheduler, drift, pin, jobs, ops]
    related_skills: [hermes-agent, windows-local-service-ops]
---

# Hermes Cron Operations

## When to Use

- A cron audit reports jobs were skipped because their config "drifted"
- A job stops running after the default provider/model changes
- You must pin a job's provider/model or inspect cron state across profiles

## Drift guard: why jobs get skipped

Hermes snapshots inference config when a job is created. On each run, if the job is NOT explicitly pinned and the current config differs from the creation-time snapshot, the guard skips the run (the audit/log says something like "inference config drifted since this job was created"). The fix is to explicitly pin provider + model on the job so the snapshot comparison no longer applies.

## Pin a job (verified)

```bash
export HERMES_HOME="%USERPROFILE%/.hermes"          # target profile — cron state is per profile
hermes cron edit <job_id> --provider moa --model hakuapulse-lite-free
```

- Default profile jobs live in `%USERPROFILE%\.hermes\cron\jobs.json`; secretary-profile jobs under `%USERPROFILE%\.hermes\profiles\secretary\cron\`. Set HERMES_HOME to the profile root you want to edit.
- When the pin lands, edit output shows the job name with a "(pinned)" suffix.
- Batch-pin several jobs by looping over job IDs in one shell command.

## Verify

```bash
python3.12 -c "
import json; data=json.load(open(r'%USERPROFILE%\.hermes\cron\jobs.json', encoding='utf-8'))
for j in data['jobs']:
    print(j.get('id'), '|', j.get('name'), '| provider:', j.get('provider'), '| model:', j.get('model'), '| enabled:', j.get('enabled'))
"
```

Confirm provider/model fields are set and `enabled` is True.

## Notes

- Prefer `hermes cron edit` / the cronjob tool over hand-editing jobs.json.
- The cronjob tool and `hermes cron` act on the profile they run under; export HERMES_HOME to target another profile's jobs.
- After pinning, re-run the job once to confirm it executes instead of being skipped.
