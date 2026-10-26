---
name: ebbinghaus-memory
description: "Use Ebbinghaus memory sleep, recall, and decay."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, ebbinghaus, sleep, recall, forgetting]
    related_skills: [hermes-agent]
    plugin: plugins/memory/ebbinghaus
    tools: [ebbinghaus_memory]
---

# Ebbinghaus Memory Skill

Use this skill to operate the bundled Ebbinghaus memory plugin as an agent memory routine. It covers durable recall, rehearsal-based consolidation, and idle sleep cleanup.

This skill does not replace other memory providers. Use it when the active memory provider is `ebbinghaus` or when you are helping a user configure that provider.

## Cron Memory/Social Sync (Bitwarden-Safe Pattern)

When the user asks to run a scheduled or manual memory/social sync job (e.g., "記憶の統合と管理", cron jobs), follow the counts-only, Bitwarden-safe pattern implemented in `scripts/cron-memory-s