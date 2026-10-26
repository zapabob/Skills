---
name: workspace-diff-cleanup
description: Use when a user asks to clean a diff, clean a dirty worktree, commit and push, use no-verify, suppress local runtime noise, preserve _docs logs, or leave a repo clean on Windows.
---

# Workspace Diff Cleanup

## Overview

Use this skill for scope-safe cleanup and closeout in dirty local repositories. The default expectation is not just "make the status short"; it is to classify the tree, preserve user/local state, verify the intended change, and end with evidence.

## Workflow

1. Read the local instructions first: project `AGENTS.md`, repo docs for generated paths, and relevant SOP notes when present.
2. Inventory without changing files:
   - `git status --short --branch --untracked-files=normal`
   - `git worktree list`
   - `git remote -v`
   - `git rev-list --left-right --count @{upstream}...HEAD` (when upstream is configured)
   - `git diff --name-only`
   - `git diff --cached --name-only`
   - `git ls-files -o --exclude-standard`
3. Classify paths before staging or deleting:
   - Included: files required for the requested change.
   - Excluded tracked: existing unrelated edits that must remain untouched.
   - Local/runtime noise: credentials, env files, app state, generated caches, build residue, desktop runtime state.
   - Protected artifacts: `_docs` implementation logs, release reports, evidence bundles, tracked examples.
4. Pick the cleanup mechanism by intent:
   - Use `.git/info/exclude` for machine-local noise that should not become repo policy.
   - Use `.gitignore` when the pattern is generally repo-local noise and should protect future runs.
   - Use `git add -f` only for a specific intended ignored artifact, commonly a durable `_docs` implementation log.
   - Use bounded deletion only after absolute target paths are verified.
5. Stage only the requested scope. If the user asks to publish `main` and this worktree cannot switch because another worktree owns `main`, use `git worktree list` and publish from the real `main` worktree.
6. Verify before commit/push:
   - Always run `git diff --check` or `git diff --cached --check` for staged changes.
   - Run the strongest practical targeted tests for behavior changes.
   - If the user explicitly says `no-verify`, use `git commit --no-verify` after manual verification instead of debating the hook.
7. Close with proof:
   - commit hash and pushed branch, if published
   - `git status --short --branch`
   - `git rev-list --left-right --count @{upstream}...HEAD` (or `origin/<branch>...HEAD`) when parity is relevant
   - `git ls-files -o --exclude-standard`
   - verification commands and their result

## Windows Guardrails

- Before recursive delete or move, resolve the absolute path and confirm it is inside the intended workspace or explicitly named target directory.
- Long `node_modules` paths and generated package trees should be removed with bounded, path-checked cleanup. Avoid broad `git clean -fdx` unless the user explicitly requested it and the protected set was reviewed.
- Treat junction-like skill folders carefully. Apparent deletions may be broken targets rather than files that should be removed.
- Preserve `.env.*`, credentials, tokens, desktop runtime state, and tracked example env files unless the user explicitly widens scope.

## Delegation

When the cleanup has a large diff or unclear ownership, use `codex-workflow-subagents/prompts/diff-scope-auditor.md` as a read-only sidecar review. Keep the actual staging, deletion, commit, and push in the main session unless the subagent receives a disjoint write scope.

## Common Mistakes

- Treating ignored files as disposable without checking whether they are durable `_docs` logs or release evidence.
- Folding unrelated dirty files into a convenient commit.
- Claiming a worktree is clean without checking both tracked status and untracked files.
- Running broad cleanup before discovering the repo's local runtime paths.
