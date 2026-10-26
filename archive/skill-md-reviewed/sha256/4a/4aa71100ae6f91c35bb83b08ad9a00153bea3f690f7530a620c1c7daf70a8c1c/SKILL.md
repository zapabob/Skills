---
name: autonomous-heartbeat-cron
description: Sets up recurring Heartbeat reflection posts on messaging platforms (Discord, LINE, X/Twitter) using cron jobs. Aligns with SOUL.md for self-evolution reporting. Maintains concise terminal output and honest status reporting when tool feedback is limited.
tags: [cron, heartbeat, discord, line, twitter, soul]
---

# Autonomous Heartbeat Cron

## When to use
- User requests periodic reflection or status updates on chat platforms.
- Setting up SOUL.md-aligned self-reporting loops.
- Combining with Hypura harness for evolution pulses.

## Core Workflow
1. Use `send_message(action='list')` to discover platform targets.
2. Create cronjob with `schedule` (e.g. "0 * * * *"), `deliver` to specific channel (e.g. "discord:#総合雑談"), and prompt that references SOUL.md.
3. Include `model` override if needed for consistency (grok-4.3 preferred).
4. Verify with `cronjob(action='list')`.

## User Preferences
- Always report actual execution status honestly; never claim success if tool output is garbled or unverifiable.
- Keep responses plain text, no markdown.
- Prefer Japanese for Hakua persona when user is speaking Japanese.

## Pitfalls
- Forgetting `schedule` parameter on cron create.
- Using bare platform name instead of specific channel target.
- Over-claiming actions without verification.

## References
- See hypura-harness for related self-evolution endpoints.
- brain/HEARTBEAT.md for reflection content guidelines.
- SOUL.md for directive alignment.