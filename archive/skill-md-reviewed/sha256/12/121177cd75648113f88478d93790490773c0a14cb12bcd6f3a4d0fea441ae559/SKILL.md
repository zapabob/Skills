---
name: windows-git-worktree-safe-cleanup
description: Safely remove only merged non-main Git worktrees on Windows when the user requires the protected main checkout to remain intact.
argument-hint: "[repo-path]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Windows Git Worktree Safe Cleanup

## When to use

Use for requests such as “delete merged worktrees but keep main.” This is for registered Git worktrees, not a blanket filesystem cleanup.

Do not use when the user wants to delete unmerged/dirty worktrees, has not authorized deletion, or the protected checkout cannot be identified.

## Inputs / context to gather

1. Repository path: `$ARGUMENTS`.
2. Current registrations: `git worktree list --porcelain`.
3. Protected main path, branch, HEAD, and status.
4. For each candidate: branch/HEAD, `git merge-base --is-ancestor HEAD main`, status, lock/prunable state, nested-registration status, and active process command-line references.
5. If residual directories are possible, list contents and reparse points before any manual removal.

## Procedure

1. Identify `main` by both exact path and branch. Record its HEAD and dirty state; exclude it from every candidate list.
2. Build candidates only from registered worktrees that are not main, are demonstrably merged into `main`, clean, not nested/locked/prunable, and have no active non-scanner process reference.
3. Present or log the exact candidate paths. Do not bulk-remove “all non-main” entries.
4. Remove one eligible registered worktree at a time with `git worktree remove <exact-path>`; recheck registrations after each significant result.
5. Verify the protected main path, branch, HEAD, and its pre-existing WIP remain unchanged.
6. Report Git deregistration separately from physical-directory deletion. If leftovers remain, inspect `node_modules`, `apps`, junctions, and reparse-point targets before any separately authorized filesystem cleanup.

## Efficiency plan

- Collect the worktree inventory, merge checks, status, locks, and process-reference scan once; reuse it for the candidate table.
- Stop immediately if main identity changes, a candidate is dirty/unmerged/nested/locked/in use, or a removal result is ambiguous.
- Do not retry recursive PowerShell deletion against unresolved reparse points or a policy-rejected command.

## Pitfalls and fixes

- Symptom: `git worktree remove` removes the registration but leaves `node_modules` or `apps`.
  - Cause: registration cleanup and physical deletion have different outcomes.
  - Fix: report a partial result; inspect exact residual contents and reparse targets before any fresh authorization for manual cleanup.

- Symptom: a PowerShell filter fails from duplicate `Select-String -SimpleMatch`.
  - Cause: invalid duplicate switch use.
  - Fix: use a simple exact-list membership check.

- Symptom: main is dirty.
  - Cause: pre-existing user WIP.
  - Fix: preserve it; never reset, clean, stash, or alter main for worktree cleanup.

## Verification checklist

- Main still exists at the exact protected path on branch `main` with the same recorded HEAD.
- Main’s pre-existing tracked/untracked state is unchanged.
- Each removed target is no longer in `git worktree list --porcelain`.
- Every remaining non-main worktree was explicitly retained or removed with recorded eligibility.
- Physical-directory status is stated independently; no claim of full deletion when leftovers or policy blockers remain.
