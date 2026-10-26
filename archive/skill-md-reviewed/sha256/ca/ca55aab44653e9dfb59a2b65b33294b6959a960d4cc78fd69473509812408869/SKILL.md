---
name: obsidian-memory-sync
description: Run Ebbinghaus sleep then sync and push the Obsidian Wiki.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Memory, Ebbinghaus, Obsidian, Sync, Wiki, Routing]
    category: devops
    related_skills: [memory-consolidation-sync, obsidian-memory-wiki-routing, memory-maintenance]
---

# Obsidian Memory Sync (consolidated)

Runs the full nightly memory pipeline: Ebbinghaus sleep → session-memory sync
to the Obsidian Wiki → git commit/push. It consolidates the older
`memory-consolidation-sync` and `obsidian-memory-wiki-routing` skills and adds
two hard-won lessons: auto-resolving the user's typo'd/stale path, and checking
for an already-committed previous run after an interrupted session.

What it does NOT do: it does not push the local `Obsidian/Hermes` vault (no
remote), and it does NOT write to the legacy `New project/llm-wiki/...` repo.

## When to Use

- "記憶の統合と睡眠" / "memory maintenance" / "Ebbinghaus sleep"
- "Obsidian にコミットプッシュ" / "push memory wiki"
- User names a path like `/newproject/Obdisian`, `/newproject/Obsidian`,
  `~/Documents/Obsidian` for the memory wiki — these are often typos or stale.

## Prerequisites

- `ebbinghaus_memory` tool available (Hermes plugin).
- `sync_memory.py` at hermes-agent repo root:
  `%USERPROFILE%\Documents\New project\hermes-agent\sync_memory.py`
- Windows venv: `.venv/Scripts/activate` (NOT `bin/activate`). `python` on PATH
  is C:/Python314 (wrong); always use the venv.
- Git push access to `github.com/zapabob/hermes-obsidian-vault.git`.

## How to Run

1. Ebbinghaus sleep (Hermes tool):
   `ebbinghaus_memory(action="sleep", prune_mode="archive")`
2. Session sync (terminal, venv, `--no-sleep` so sleep isn't doubled):
   `python sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep`
3. Commit & push the ACTUAL wiki repo (ObsidianVault, branch `main`).
4. Append a sleep-log entry to `Obsidian/Hermes` and commit locally (no push).

## Quick Reference

| Target | Path | Remote / branch | Action |
|--------|------|-----------------|--------|
| Wiki export (real) | `Documents/ObsidianVault/Hermes-Memory-Wiki` | `zapabob/hermes-obsidian-vault` / `main` | push |
| Local vault (sleep log) | `Documents/Obsidian/Hermes` | none / `master` | local commit |
| Legacy/stale repo | `Documents/New project/llm-wiki/Hermes-Memory-Wiki` | `zapabob/hermes-memory-wiki` / `master` | SKIP |

## Procedure

1. **Auto-resolve the target repo (trust-but-verify).** The user's path
   (`/newproject/Obdisian`, etc.) may not exist. Locate the real repo:
   ```bash
   find "/c/Users/downl/Documents" -maxdepth 3 -type d -name ".git" 2>/dev/null \
     | xargs -I{} dirname {} | while read d; do
       if git -C "$d" remote -v 2>/dev/null | grep -q "hermes-obsidian-vault"; then
         echo "WIKI REPO: $d"; git -C "$d" rev-parse --abbrev-ref HEAD
       fi
     done
   ```
   Confirm `origin` = `hermes-obsidian-vault` and branch = `main`. Push only there.

2. **Ebbinghaus sleep.** Use `ebbinghaus_memory(action="sleep",
   prune_mode="archive")`. Defaults used this run: candidate_window 3000,
   rehearse_threshold 0.35, forget_threshold 0.10, salience_keep_threshold 0.80.
   Record before/after `active_count` / `archived_count` from the result.

3. **Check for an already-committed previous run (interrupted sessions).**
   After an interruption the prior turn may have already committed/pushed.
   Before re-pushing, inspect state:
   ```bash
   cd "/c/Users/downl/Documents/ObsidianVault/Hermes-Memory-Wiki"
   git fetch --dry-run 2>/dev/null
   git rev-list --left-right --count HEAD...@{u}   # 0 0 = in sync
   git log --oneline -1                            # last commit date
   ```
   If `HEAD` already contains today's "chore(memory): ..." export, do NOT
   re-commit the same content — just proceed to the local-vault sleep log.

4. **Session sync (no second sleep).** Run from hermes-agent root with venv:
   ```bash
   cd "/c/Users/downl/Documents/New project/hermes-agent"
   source .venv/Scripts/activate
   python sync_memory.py --max-sessions 80 --max-x-events 80 --no-sleep
   ```
   It prints absolute `files:` paths — confirm they land in `ObsidianVault/...`,
   not `New project/llm-wiki/...`. Expect a new
   `raw/memory/hermes-memory-sanitized-YYYY-MM-DD.md`.

5. **Secret-leak scan (mandatory before push).** Grep the repo for real
   secrets; allow only `[..._REDACTED]` markers and policy sentences:
   ```bash
   grep -rInE "sk-[a-z0-9]{20,}|api[_-]?key|password|token|secret" \
     --include=*.md . | grep -vE "_REDACTED\]|no-secret|keep secrets|secret-boundary" \
     && echo "LEAK" || echo "clean"
   ```
   Treat any non-marker hit as a REAL leak and stop the push.

6. **Commit & push the wiki.** Only if changes exist:
   ```bash
   cd "/c/Users/downl/Documents/ObsidianVault/Hermes-Memory-Wiki"
   git add -A
   git commit -m "chore(memory): Ebbinghaus sleep + session-memory export $(date +%F)"
   git push origin main
   ```

7. **Update local vault sleep log (no remote).** Prepend an entry to
   `Documents/Obsidian/Hermes/Ebbinghaus/2026-07_睡眠ログ.md` with date,
   before/after counts, thresholds, exported group counts, and the wiki commit
   SHA. Then:
   ```bash
   cd "/c/Users/downl/Documents/Obsidian/Hermes"
   git add -A && git commit -m "sleep log $(date +%F)"
   ```
   Do NOT `git push` (vault has no remote).

## Pitfalls

- **User path is usually wrong.** `/newproject/Obdisian` (Obsidian typo) and
  `/newproject/Obsidian` do not exist here. The real repo is
  `Documents/ObsidianVault/Hermes-Memory-Wiki`. Always auto-locate + verify.
- **Three samey repos.** `ObsidianVault` (push), `New project/llm-wiki` (stale,
  skip), `Obsidian/Hermes` (local only). Confirm `remote -v` + branch every run.
- **Stale-path push.** Pushing from `New project/llm-wiki/...` sends an
  untouched repo. `sync_memory.py` resolves the path via the `memory_llm_wiki`
  plugin (`vaults` config → `~/Documents/ObsidianVault`), NOT a hardcoded path.
- **Double sleep.** Run sleep once via the tool, then sync with `--no-sleep`,
  or you double-count/alter retention.
- **Interrupted re-runs.** A prior turn may have already committed today's
  export (this happened 2026-08-03: commit `7dfa843` predated the re-run, so
  the second push only carried 7 changed files). Check `git log` first.
- **Windows venv.** `.venv/Scripts/activate`, not `bin/`. `python` on PATH is
  3.14 — wrong; the venv pins 3.12.
- **Secrets.** Sanitized dumps use `[LONG_TOKEN_REDACTED]` /
  `[PRIVATE_IP_REDACTED]` markers — grep hits on those are SAFE.

## Verification

```bash
# Wiki repo pushed + clean
cd "/c/Users/downl/Documents/ObsidianVault/Hermes-Memory-Wiki"
git log --oneline -1        # today's "chore(memory): ..."
git status -sb              # "## main...origin/main" (clean)

# Local vault committed (no remote)
cd "/c/Users/downl/Documents/Obsidian/Hermes"
git log --oneline -1        # "sleep log YYYY-MM-DD"
grep -q "$(date +%F)" Ebbinghaus/2026-07_睡眠ログ.md && echo "log updated"
```
