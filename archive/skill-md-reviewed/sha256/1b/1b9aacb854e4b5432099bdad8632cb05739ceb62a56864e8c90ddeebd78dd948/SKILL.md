---
name: agent-heartbeat-and-memory-ops
description: Run autonomous agent heartbeat, SOUL, and social-memory operations across Discord, LINE, Telegram, X/Twitter, and cron. Use for recurring self-report posts, Ebbinghaus/social memory sync, SOUL.md migration or preservation, and low-noise autonomous status reporting.
---

# Agent Heartbeat and Memory Operations

This umbrella skill covers recurring autonomous-agent status, identity-preservation, and social-memory synchronization patterns.

## Heartbeat reporting

1. Decide the audience and platform first; shared channels require low-noise status formats.
2. Make cron prompts self-contained: role, cadence, destination, reporting style, what to include, and what to omit.
3. Prefer concise reflections with concrete progress/health signals over long diary posts.
4. Verify delivery separately from cron execution.

## Social memory sync

1. Collect social traces only from authorized channels and redact platform identifiers.
2. Distill durable patterns, preferences, or procedures; do not store raw transcript dumps or stale task progress as memory.
3. Use Ebbinghaus-style consolidation only when the output will reduce future steering.
4. For platform bridges, isolate credentials by env-var prefix and verify plugin/tool health before relying on automation.

## SOUL migration

- Treat SOUL.md as portable identity/values/context, not a raw transcript.
- Preserve structure, then adapt to the target runtime/model constraints.
- Verify migration by reading back the installed SOUL.md and running a small behavioral smoke if applicable.

## References

- `references/absorbed-heartbeat-discord-cron.md` — Discord/cron heartbeat patterns and guardrails.
- `references/absorbed-social-memory-soul.md` — social memory sync and SOUL migration details.
