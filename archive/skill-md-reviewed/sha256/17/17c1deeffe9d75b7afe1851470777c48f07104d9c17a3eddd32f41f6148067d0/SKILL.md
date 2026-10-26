---
name: autonomous-heartbeat-cron
description: "Recurring heartbeat reflection posts via cron."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, heartbeat, discord, line, twitter, soul, reflection]
    category: devops
    related_skills: [hypura-harness, discord-heartbeat, hermes-agent]
---

# Autonomous Heartbeat Cron

## When to use
- User requests periodic reflection or status updates on chat platforms.
- Setting up SOUL.md-aligned self-reporting loops.
- Combining with Hypura harness for evolution pulses.

## Core Workflow
1. Discover platform targets with `hermes gateway status` or check the gateway channel configuration for active outgoing destinations (Discord, LINE, X/Twitter).
2. Create a cron job:
   ```bash
   hermes cron create "0 * * * *" \
     -p "<profile>" \
     -q "Write a concise heartbeat reflection based on brain/HEARTBEAT.md and brain/SOUL.md. Report current status, recent activity, and next actions." \
     --deliver <channel>
   ```
3. Verify with `hermes cron list`.
4. Check execution history: `hermes cron log <job-id>`.

## User Preferences
- Always report actual execution status honestly; never claim success if tool output is garbled or unverifiable.
- Keep responses concise (10 lines or fewer for Telegram/LINE delivery, plain text).
- Prefer Japanese for Hakua persona when user is speaking Japanese.

## Pitfalls
- Forgetting `--schedule` (or positional schedule) on cron create — job silently never runs.
- Using bare platform name instead of specific channel target (e.g. `discord:#general` not just `discord`).
- Over-claiming actions without verification — always verify with `hermes cron list` and check delivery status.
- If the cron job's delivery channel requires a specific profile, use `-p <profile>` explicitly.
- Use `no_agent=True` in the cron job when the job only posts static content without needing agent reasoning — this avoids unnecessary LLM calls and 429 rate limits.

## References
- `brain/HEARTBEAT.md` for reflection content guidelines.
- `brain/SOUL.md` for directive alignment.
- `hermes-agent` skill for cron CLI reference.
- `discord-heartbeat` skill for Discord-specific heartbeat setup.
- `hypura-harness` for related self-evolution endpoints.