---
name: hermes-memory-obsidian-sync
description: Sync Hermes social memory + Ebbinghaus sleep to Obsidian LLM Wiki vault.
version: 0.1.0
author: Hermes
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [Memory, Obsidian, Ebbinghaus, Sync, Wiki, Social]
---

# Hermes Memory → Obsidian LLM Wiki Sync

Run the social-memory sync (LINE, Discord, Telegram, X) + Ebbinghaus sleep cycle,
then export curated memories to the Obsidian vault. The export target is resolved by the
`memory_llm_wiki` plugin (`~/Documents/ObsidianVault/Hermes-Memory-Wiki`, remote `zapabob/hermes-obsidian-vault`, branch `main`).
Does NOT cover cron job migration or README translation — separate skills.

## When to Use

- Daily/weekly memory consolidation run
- After significant conversations that should be searchable in Obsidian
- Before backups or when switching workstations
- Manual trigger when `cronjob 1fe5b2fda4d0` (Ebbinghaus sleep) missed its window

## Prerequisites

- Hermes repo at `%USERPROFILE%/Documents/New project/hermes-agent` (or `HERMES_REPO_ROOT` env)
- `sync_memory.py` at repo root (bundled)
- Obsidian wiki vault at `%USERPROFILE%/Documents/ObsidianVault/Hermes-Memory-Wiki`
  (resolved by `memory_llm_wiki` plugin `core.py`: Obsidian `vaults` config → fallback `~/Documents/ObsidianVault`, then `/Hermes-Memory-Wiki`. Remote: `zapabob/hermes-obsidian-vault`, branch `main`.)
- `plugins/memory_llm_wiki` plugin installed and enabled
- State DB: `~/.hermes/state.db`
- Ebbinghaus DB: `~/.hermes/ebbinghaus_memory.db`
- X activity log: `~/.hermes/lm-twitterer/activity.jsonl` (optional)

## How to Run

**Full rescan (non-incremental):**
```
python sync_memory.py --full --no-sleep
```

**Incremental (default):**
```
python sync_memory.py
```

**Dry-run Obsidian export only:**
```
python sync_memory.py --dry-run --no-obsidian=false
```

**Via Hermes cron (Ebbinghaus sleep + export):**
```
cronjob action=run job_id=1fe5b2fda4d0
cronjob action=run job_id=705be17677d0
```

## Quick Reference

| Action | Command |
|--------|---------|
| Full sync + Obsidian export | `python sync_memory.py --full --no-sleep` |
| Incremental sync | `python sync_memory.py` |
| Dry-run export | `python sync_memory.py --dry-run` |
| Ebbinghaus sleep only | `cronjob action=run job_id=1fe5b2fda4d0` |
| Obsidian summary only | `cronjob action=run job_id=705be17677d0` |
| View last export | `cat ~/.hermes/memory_sync_last_index.json` |

## Procedure

1. **Optional: Run Ebbinghaus sleep** (prunes low-value, rehearses important memories)
   ```bash
   cronjob action=run job_id=1fe5b2fda4d0
   ```
   Wait for completion (check `cronjob action=list`).

2. **Run full memory sync with Obsidian export**
   ```bash
   cd %USERPROFILE%/Documents/New project/hermes-agent
   python sync_memory.py --full --no-sleep
   ```
   This:
   - Scans `state.db` for sessions from sources: `line`, `line-personal`, `discord`, `telegram`
   - Extracts social memories + X activity (`lm-twitterer/activity.jsonl`)
   - Writes to `ebbinghaus_memory.db` (129 memories in last run)
   - Calls `memory_llm_wiki` plugin `handle_export` with `include_curated=true`, `include_ebbinghaus=true`
   - Writes concept pages to `ObsidianVault/Hermes-Memory-Wiki/concepts/*.md`
   - Writes raw sanitized dump to `raw/memory/hermes-memory-sanitized-YYYY-MM-DD.md`

3. **Verify export**
   - Check `obsidian.success == true` in JSON output
   - Verify `items` count (152 in last run)
   - Open `ObsidianVault/Hermes-Memory-Wiki/index.md` in Obsidian
   - Confirm concept pages updated (8 concept groups)

4. **Push to Git** (wiki repo has remote `zapabob/hermes-obsidian-vault`, branch `main`)
   ```bash
   cd "%USERPROFILE%/Documents/ObsidianVault/Hermes-Memory-Wiki"
   git add -A
   git commit -m "chore(memory): sync Hermes memories $(date +%F)"
   git push origin main
   ```

## Pitfalls

- **`--full` ignores watermark**: Re-scans all recent sessions; slower but catches missed incremental runs.
- **`memory_llm_wiki` plugin missing**: Export returns `skipped: true` with error; install plugin via `hermes plugins install memory_llm_wiki`.
- **Wiki path resolution**: `sync_memory.py` does NOT hardcode the path — the `memory_llm_wiki` plugin's `core.py` resolves it via Obsidian `vaults` config (fallback `~/Documents/ObsidianVault`), then appends `Hermes-Memory-Wiki`. Override via `--wiki_root` arg or `WIKI_PATH` env if needed.
- **X activity log format changes**: `lm-twitterer` JSONL schema drift breaks parsing; update `SocialMemorySync` if needed.
- **Concurrent runs**: Don't run two syncs simultaneously; state DB lock contention.

## Verification

After run, check JSON output:
```json
{
  "success": true,
  "social": { "memories_written": 129, "sessions_seen": 78 },
  "obsidian": {
    "success": true,
    "items": 152,
    "groups": { "identity-persona": 52, "user-profile": 47, ... }
  }
}
```
Then open `ObsidianVault/Hermes-Memory-Wiki/concepts/identity-persona.md` and confirm today's date appears in the raw log.