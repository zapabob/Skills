---
name: lightweight-repo-handoff-zip
description: Use when the user wants to hand a repo to GPT Pro or another external reviewer as a ZIP plus prompt, especially when they care about keeping code/config/tests and excluding heavy results, caches, or history artifacts.
argument-hint: "[repo-path] [consult-focus]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Lightweight Repo Handoff ZIP

## When to use

Use this when the user asks for a repo snapshot they can send elsewhere for review, redesign, or implementation help.

Typical triggers:
- make a zip for GPT Pro
- package the current repo for external review
- include the current diff/status too
- make a lightweight handoff bundle

Non-goals:
- shipping full experiment outputs, caches, or history by default
- relying on chat-only summaries when the user explicitly wants a transferable artifact
- bundling secrets or runtime-only local state

## Inputs / context to gather

1. Confirm the repo root and the consult target:
- repo path
- what the external reviewer should focus on

2. Inspect current state:
- `git status --short --branch`
- whether the worktree is noisy enough that `CURRENT_DIFF.patch` and `CURRENT_GIT_STATUS.txt` should be included

3. Identify must-include surfaces:
- code directories
- config files
- tests
- project manifest files
- any existing AGENTS/SOP/readme files that explain the repo

4. Identify default exclusions:
- `.git`
- virtual environments
- caches
- build outputs
- `results/`
- large history/docs folders such as `_docs`
- heavy media/data unless the consult explicitly needs them

## Procedure

1. Create a handoff folder inside the repo or an existing `_handoff` area.

2. Write a paste-ready prompt file that includes:
- the design or bugfix goal
- explicit constraints from the user
- files/folders the reviewer should inspect first
- the expected answer shape

3. Export current context:
- save `git status` to `CURRENT_GIT_STATUS.txt`
- save the current diff to `CURRENT_DIFF.patch` when local modifications matter

4. Stage a clean package directory.
- Copy only the approved code/config/tests/docs surfaces.
- Add the prompt and context files explicitly.
- Exclude `.git`, venvs, caches, large docs/history, results, and heavy media/data unless requested.

5. Create the ZIP from the staged package directory.
- If shell/pathspec exclusion attempts are brittle, fall back to a staged directory plus .NET `System.IO.Compression.ZipFile` on Windows.

6. Validate the archive.
- Confirm expected roots are present.
- Confirm excluded roots are absent.
- Record quick size and entry-count proof.

## Efficiency plan

- Decide include/exclude rules once before copying files.
- Prefer staging a clean temp package over fighting exclusion syntax on a noisy worktree.
- Keep the prompt concrete so the external consult does not need a second packaging pass.
- Stop after the ZIP contents, size, and exclusions are verified.

## Pitfalls and fixes

- Symptom: the ZIP is far too large.
- Likely cause: `_docs`, `results`, venvs, caches, or media/data were copied blindly.
- Fix: exclude them by default and only add them back if the consult truly needs them.

- Symptom: `Compress-Archive` or pathspec exclusions behave unreliably.
- Likely cause: Windows tooling and noisy worktree paths are brittle.
- Fix: assemble a clean staged directory, then compress it with .NET `ZipFile`.

- Symptom: the external review comes back vague.
- Likely cause: the prompt omitted the user's exact constraints.
- Fix: preserve concrete constraint wording and requested output structure in the prompt file.

- Symptom: the bundle lacks the local context needed to understand uncommitted work.
- Likely cause: diff/status were omitted.
- Fix: include `CURRENT_DIFF.patch` and `CURRENT_GIT_STATUS.txt` when the working tree is not clean.

## Verification checklist

- ZIP contains the intended code/config/tests surfaces.
- ZIP excludes `.git`, venvs, caches, results, and heavy docs/media unless explicitly requested.
- Prompt file exists and reflects the user's exact focus/constraints.
- `CURRENT_GIT_STATUS.txt` exists, and `CURRENT_DIFF.patch` exists when local modifications matter.
- Archive size and a quick content check look reasonable for transfer.
