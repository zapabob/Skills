---
name: telegram-cron-failure
description: Telegram cron job failure detection and prevention.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, cron, failure-handling]
    category: devops
    related_skills: [hermes-agent]
---
# Telegram Cron Job Failure Handling

When Hermes Telegram cron jobs report error status, the agent skips sending Telegram messages until the job's `last_status` returns to `ok`. Only jobs with `last_status: ok` proceed to Telegram delivery.

## Failure Patterns (from this session)

| Job | Error | Fix Note |
|-----|-------|----------|
| �every morning Gmail/面談チェック | Interrupted before terminal completion | Re-run after fixing terminal config |
| security-audit-weekly | Config drift since job creation | Pin provider/model and re-run |
| warashibe穴場価格スキャン (pinned) | Interrupted before terminal completion | Re-run after fixing terminal config |
| Master Heartbeat (Bot Coordination) | Python SyntaxError in script | Fix script and re-run |
| SitDeck OSINT monitor | Never executed (last_status=None) | Check and fix scheduling |

## Audit Guard

Only `last_status: ok` jobs proceed to Telegram delivery. Failed jobs have `fix_note` in jobs.json documenting the error and remediation path. Re-run with `hermes cronjob run` after fixing to restore normal status.