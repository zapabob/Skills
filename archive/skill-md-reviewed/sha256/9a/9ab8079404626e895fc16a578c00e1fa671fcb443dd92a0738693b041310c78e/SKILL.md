---
name: sillytavern-roleplay
description: "CLI and slash-command roleplay using SillyTavern-native features."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [SillyTavern, Roleplay, CLI, SlashCommand]
    category: devops
---

# SillyTavern Roleplay for Hermes Agent

Run SillyTavern-style roleplay directly from Hermes CLI or slash commands,
using the native ST features (characters, lorebook, personas, sessions)
without a separate SillyTavern server. All data lives in Hermes' SQLite
and bridges to ebbinghaus memory.

## When to Use

- User types `/rp start <character>` or `/rp say <message>` in chat
- User runs `hermes rp ...` from CLI
- Want ST-style roleplay with memory bridge to Hermes

## Prerequisites

- Hermes with `plugins/sillytavern` loaded (provides `st_*` tools)
- At least one character created via `st_character_create`
- Default persona created via `st_persona_create`

## How to Run

### Slash Commands (in Hermes chat)

```
/rp list                    # list characters
/rp start はくあ            # start session with character
/rp say こんにちは          # send user turn, get ST-style prompt
/rp reply "そうだね"        # record assistant reply
/rp summary 今日は森を探検した # set running summary
/rp memory                 # emit session to ebbinghaus memory
/rp lore                   # ingest memories back to lorebook
/rp status                 # show current session
/rp end                    # close session
```

### CLI (terminal)

```bash
hermes rp list
hermes rp start はくあ
hermes rp say "森に入る"
hermes rp reply "木々が囁く"
hermes rp summary "古の森を発見"
hermes rp memory
hermes rp lore
```

## Quick Reference

| Slash | CLI | Action |
|-------|-----|--------|
| `/rp list` | `hermes rp list` | List characters |
| `/rp start <name>` | `hermes rp start <name>` | Start session |
| `/rp say <msg>` | `hermes rp say <msg>` | User turn |
| `/rp reply <msg>` | `hermes rp reply <msg>` | Assistant reply |
| `/rp summary <text>` | `hermes rp summary <text>` | Set summary |
| `/rp memory` | `hermes rp memory` | Push to ebbinghaus |
| `/rp lore` | `hermes rp lore` | Memories → lorebook |
| `/rp status` | `hermes rp status` | Show session |
| `/rp end` | `hermes rp end` | Close session |

## Procedure

### 1. Create a character (once)

```bash
# via slash
/rp create はくあ --first "ボブにゃん！" --personality "元気で忠実"
# or CLI
hermes rp create はくあ --first "ボブにゃん！" --personality "元気で忠実"
```

### 2. Create default persona (once)

```bash
/rp persona ボブにゃん --desc "上田市の開発者"
```

### 3. Add lorebook entries

```bash
/rp lore add world --keys "eldoria,forest" --content "Eldoriaは魔法の森"
```

### 4. Start a session

```bash
/rp start はくあ
# or: hermes rp start はくあ
# returns session_id
```

### 5. Roleplay loop

```bash
# User turn → get ST-style prompt (system + lore + history)
/rp say 森に入る

# Model generates reply → record it
/rp reply "森は静かだ…"

# Optional: set running summary
/rp summary 古の森を発見した

# Push to ebbinghaus memory
/rp memory

# Ingest memories back as lore triggers
/rp lore
```

### 6. Check status / end

```bash
/rp status
/rp end
```

## Pitfalls

- **No session started**: `say`/`reply`/`summary`/`memory`/`lore` require active session
- **Lore not firing**: keys are case-insensitive substring match; check `st_lore_add` keys
- **Memory not persisting**: `st_session_to_memory` only emits records; agent must call `ebbinghaus_memory` tool to actually store
- **First message missing**: `st_session_start` auto-seeds `first_mes` from character

## Verification

```bash
# Smoke test full loop
hermes rp create テストキャラ --first "テスト！"
hermes rp persona ユーザー --desc "テストユーザー"
hermes rp lore add test --keys "test" --content "テスト世界"
hermes rp start テストキャラ
hermes rp say "こんにちは"
hermes rp reply "こんにちは！"
hermes rp summary "挨拶した"
hermes rp memory
hermes rp lore
hermes rp end
```

All steps should succeed with `ok: true` responses.