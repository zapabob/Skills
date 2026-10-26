---
name: log-root-cause-tracing
description: Use when a user pastes logs, stack traces, startup warnings, TypeScript or test errors, CI snippets, runtime crashes, or multiple failures that may belong to different layers.
---

# Log Root Cause Tracing

## Overview

Use this skill to turn noisy pasted failures into a bounded root-cause investigation. Keep the exact error text central, split layered failures, and prove the fix against the smallest reliable runtime or test surface.

## Workflow

1. Preserve the exact signals:
   - copy the error strings, codes, file paths, command names, process names, and timestamps
   - separate symptoms that may belong to different layers
   - do not merge auth, liveness, gateway, cache, config, packaging, and runtime errors into one diagnosis without evidence
2. Map each signal to a concrete surface:
   - search exact strings with `rg`
   - inspect matching source, generated/runtime entrypoints, config, package metadata, and docs
   - check whether the running process uses built output, source, a copied install, or a skip-worktree local config
3. Narrow the failure lane:
   - prefer file-scoped type checks, targeted tests, parser checks, or live smoke tests over broad noisy suites
   - when broad lanes are already red for unrelated reasons, keep that separate from the reported failure
   - on Windows, account for encoding, timeout, shell, and path quirks before blaming production code
4. Repair the concrete cause:
   - keep the patch in the files implicated by the failing stack unless evidence widens scope
   - update generated/runtime files only when the runtime actually executes them
   - avoid speculative refactors during crash cleanup
5. Verify live enough:
   - rerun the targeted failing lane
   - run syntax/type checks for touched files
   - restart only the affected local process when proving a runtime fix
   - record any broad suite noise as residual risk, not as proof of failure

## Delegation

Use `codex-workflow-subagents/prompts/log-root-cause-investigator.md` when a sidecar can inspect logs and source paths while the main session continues with non-overlapping work. Keep secrets and local tokens out of the delegated prompt.

## Report Shape

- Root cause: the smallest proven cause, with file/path references.
- Evidence: exact log strings and commands checked.
- Fix: files changed and why those files are the runtime surface.
- Verification: command output summary and any live smoke proof.
- Residual risk: broad lanes not run, unrelated red tests, stale running processes, or unverified current external behavior.

## Common Mistakes

- Treating a pasted log bundle as one fault when it contains independent layers.
- Editing TypeScript source while the app runs checked-in JavaScript.
- Using a broad failing suite as the only regression signal for a narrow runtime bug.
- Ignoring local config or installed package drift when source code looks correct.
