---
name: obsidian-memory-wiki-routing
description: Correct Obsidian Wiki export-target routing for Hermes memory sync — which of the 3 similarly-named repos sync_memory.py actually writes to, and the exact commit/push targets. CORRECTS the stale paths recorded in memory-consolidation-sync and hermes-memory-obsidian-sync.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Memory, Ebbinghaus, Obsidian, Sync, Wiki, Routing]
    category: devops
    related_skills: [memory-consolidation-sync, hermes-memory-obsidian-sync, memory-maintenance]
---

# Obsidian Memory Wiki Routing (corrected)

Routing map for Hermes memory → Obsidian Wiki export and git push. The older
`memory-consolidation-sync` and `hermes-memory-obsidian-sync` skills document a
**stale** export path (`~/Documents/New project/llm-wiki/Hermes-Memory-Wiki`).
This skill records the **actual** layout, verified 2026-07-24.

## Critical fact

`sync_memory.py` (run from the hermes-agent repo root) writes the Wiki export to:

```
%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki
```

NOT the legacy `%USERPROFILE%\Documents\New project\llm-wiki\Hermes-Memory-Wiki`
path the other skills mention. Always push from the **ObsidianVault** copy.

> Full repo table + push rules: `references/obsidian-repo-map.md`

## Repo map (3 repos — do not confuse them)

See `references/obsidian-repo-map.md` for the full table. Summary:

| Repo path | Role | Remote | Branch | Push? |
|-----------|------|--------|--------|-------|
| `Documents/ObsidianVault/Hermes-Memory-Wiki` | **Actual export target** (concepts/, raw/, index.md) | `github.com/zapabob/hermes-obsidian-vault.git` (`origin`) | `main` | ✅ `git push origin main` |
| `Documents/New project/llm-wiki/Hermes-Memory-Wiki` | Legacy/stale path (NOT written by sync_memory.py) | `zapabob/hermes-memory-wiki` | `master` | ❌ skip |
| `Documents/Obsidian/Hermes` | Local Obsidian vault + sleep log (`Ebbinghaus/2026-07_睡眠ログ.md`) | none | `master` | local commit only |

## Procedure (verified working)

The canonical Git root is `%USERPROFILE%/Documents/ObsidianVault`; `Hermes-Memory-Wiki/` and `Hermes-Memory/` are tracked subdirectories of that one repository. Run Git commands from the vault root and stage prefixed paths. Do not assume the Wiki subdirectory is an independent Git repository.

```bash
# 1. Ebbinghaus sleep (already done separately if using --no-sleep in step 2)
ebbinghaus_memory(action="sleep", prune_mode="archive",
  rehearse_threshold=0.45, forget_threshold=0.08,
  salience_keep_threshold=0.7, limit=200)

# 2. Session/social memory inventory + Obsidian export (NO second sleep)
cd "/c/Users/downl/Documents/New project/hermes-agent"
source .venv/Scripts/activate          # Windows venv: Scripts/, NOT bin/
python sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep

# 3. Commit & push the ACTUAL wiki repo (ObsidianVault, branch main)
cd "/c/Users/downl/Documents/ObsidianVault/Hermes-Memory-Wiki"
git add -A
git commit -m "chore(memory): Ebbinghaus sleep + session-memory export $(date +%F)"
git push origin main

# 4. Update sleep log + commit local vault (no remote)
cd "/c/Users/downl/Documents/Obsidian/Hermes"
# prepend entry to Ebbinghaus/2026-07_睡眠ログ.md
git add -A && git commit -m "sleep log $(date +%F)"
```

## Pitfalls

- **Export-target mismatch (the big one)**: `sync_memory.py` does NOT hardcode the path — the `memory_llm_wiki` plugin (`plugins/memory_llm_wiki/core.py`) resolves it via Obsidian `vaults` config (fallback `~/Documents/ObsidianVault`), then appends `Hermes-Memory-Wiki`. If you `cd` into `New project/llm-wiki/...` to push, you push an untouched/stale repo. Always verify which dir `sync_memory.py` wrote to by reading its stdout `files:` list (it prints absolute paths).
- **User-supplied path does not exist (trust-but-verify)**: when the user names a path
  like `/newproject/Obsidian` or `/newproject/Obdisian`, do NOT assume it exists. A typo'd
  or stale path will fail `cd` with "No such file or directory". Auto-locate the real repo
  before committing: (1) probe `find ~/Documents -maxdepth 3 -iname "*obsidian*"` ; (2) for
  each candidate, test `-d <dir>/.git` to find the actual git repo ; (3) confirm via
  `git remote -v` that it points at `github.com/zapabob/hermes-obsidian-vault.git`
  (`origin`) on branch `main`. Then push from THAT dir. In the 2026-08-03 run the user's
  `/newproject/Obsidian` was absent; the real target was `Documents/ObsidianVault` (confirmed
  by `.git` + `origin` remote).
- **Windows venv activation**: `.venv/bin/activate` does NOT exist on this
  Windows checkout — use `.venv/Scripts/activate` (bash can `source` it).
  `python` on PATH resolves to C:/Python314 (3.14) — wrong; use the venv.
- **Three samey repos**: before any `git push`, confirm cwd via
  `git remote -v && git rev-parse --abbrev-ref HEAD`.
- **Secrets**: the sanitized dump (`raw/memory/hermes-memory-sanitized-YYYY-MM-DD.md`)
  contains NO real tokens/keys/passwords — only structural config (ports, MIDs) and
  redacted placeholders. The sanitizer replaces secrets with literal markers
  `[LONG_TOKEN_REDACTED]` and `[PRIVATE_IP_REDACTED]` — grep hits on these markers are
  SAFE, not leaks. Still grep `token|api[_-]?key|password|secret|sk-[a-z0-9]{20,}` before
  every push; treat any hit that is NOT wrapped in `[..._REDACTED]` and is NOT part of a
  known policy sentence ("keep secrets out of memory", etc.) as a REAL leak and stop the push.

## Verification

```bash
cd "/c/Users/downl/Documents/ObsidianVault/Hermes-Memory-Wiki"
git log --oneline -1            # expect today's "chore(memory): ..."
git status -sb                  # expect "## main...origin/main" (clean)
```
