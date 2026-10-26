---
name: windows-git-clean-scope
description: Use when the user asks to clean a dirty Windows worktree, preserve specific files (like _docs logs), and keep commit scope limited to included changes.
argument-hint: "[repo-path] [mode]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Windows Git Clean Scope

## When to use

Use this when a repository is dirty and the user asks for one or more of:
- commit/push only included changes
- clean tracked and ignored clutter
- preserve specific artifacts (for example `_docs/*.md` logs)
- keep env files ignored

Non-goals:
- blind `git clean -fdx` without inventory
- committing every dirty file by default

## Inputs / context to gather

1. Current branch and cleanliness:
- `git status --short --branch --untracked-files=all`

2. Ignored clutter inventory (if user asked for full cleanup):
- `git status --ignored=matching --short`

3. User keep/exclude constraints:
- preserve paths (for example `_docs/*.md`)
- exclude generated/runtime/local state
- env ignore expectations (`.env.*` vs `!.env.example`)

## Procedure

1. Classify paths into three buckets before editing:
- included (intended commit scope)
- excluded tracked (restore to HEAD)
- generated/ignored (cleanup candidates)

2. For commit-scope requests:
- stage only included files
- verify staged scope with `git diff --cached --name-status`
- when the publish target is `main` or another tracked branch, verify divergence with `git rev-list --left-right --count origin/main...HEAD` (or branch-specific equivalent) before and after push
- if user asked for no-verify, commit with `--no-verify`; otherwise use normal commit

3. For tracked cleanup:
- restore excluded tracked files with explicit paths using:
- `git restore --worktree --source=HEAD -- <paths...>`

4. For ignored cleanup:
- start with inventory and bounded deletes
- use `git clean -fd` first
- use `git clean -fdx` only when user explicitly asks for ignored cleanup
- on Windows long-path failures, switch to targeted deletion of known heavy roots (for example `node_modules`, build caches), then re-check status

5. Preserve requested logs/artifacts:
- if user asked to keep `_docs` markdown logs, ensure they are excluded from destructive cleanup path lists
- if `_docs/` is ignored but one specific implementation log should ship, force-add only that file with `git add -f <path>`

6. Env file policy:
- ensure `.gitignore` patterns keep runtime env files ignored while preserving examples:
- `.env.*`
- `!.env.example`

## Efficiency plan

- Do one inventory pass up front and reuse it for all cleanup/commit decisions.
- Prefer focused restore/delete commands over repeated trial-and-error cleans.
- Stop once `git status` matches user target state (clean tracked only, or clean tracked+ignored as requested).

## Pitfalls and fixes

- Symptom: `git clean -fdx` times out or fails with `Filename too long`.
- Likely cause: deep nested Windows paths (often `node_modules`).
- Fix: run targeted path cleanup for the deepest roots, then rerun status checks.

- Symptom: agent accidentally removes useful implementation logs.
- Likely cause: no explicit preserve list before cleanup.
- Fix: create preserve list first (for example `_docs/*.md`) and exclude it from cleanup command paths.

- Symptom: broad commit includes generated/local state.
- Likely cause: staging without bucket classification.
- Fix: require included/excluded/generated classification before any `git add`.

## Verification checklist

- `git diff --cached --name-status` contains only intended included files.
- preserved files (for example `_docs` logs) still exist when requested.
- if a publish was requested, `git rev-list --left-right --count origin/main...HEAD` (or branch equivalent) matches the intended clean alignment.
- env ignore behavior matches expectation (`.env.*` ignored, example files preserved).
- final status aligns with requested endpoint:
  - tracked-clean: `git status --short --untracked-files=all` empty (or expected untracked only)
  - full-clean: `git status --ignored=matching --short` has no unexpected clutter
