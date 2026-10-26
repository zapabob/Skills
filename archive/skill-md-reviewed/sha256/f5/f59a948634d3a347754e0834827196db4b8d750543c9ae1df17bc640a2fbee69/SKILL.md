---
name: codex-workflow-subagents
description: Use when a user asks to delegate work to subagents, run parallel reviewers, check why CI failed, review a PR, trace a bug, audit a diff, or draft changelog text from evidence.
---

# Codex Workflow Subagents

## Overview

Use this skill to dispatch repeatable engineering sidecars. Subagents are useful for bounded read-only analysis, independent review, or a disjoint write scope while the main session keeps the immediate critical path moving.

## Dispatch Rules

- First decide the immediate local task. Do that locally when the next step depends on it.
- Delegate sidecar work that can run in parallel and has a concrete output.
- Give each subagent only the context it needs: repo path, relevant diff range, logs, command output, file ownership, and output format.
- Default to read-only. Grant write authority only for a named file/module set.
- Tell workers that other edits may exist and that they must not revert unrelated changes.
- When the result returns, review it before using it. Close the agent when finished.

## Prompt Selection

| Request | Prompt |
| --- | --- |
| Check why CI failed | `prompts/ci-failure-triager.md` |
| Review this PR or diff | `prompts/pr-reviewer.md` |
| Trace this bug or log bundle | `prompts/log-root-cause-investigator.md` |
| Clean up or audit this diff | `prompts/diff-scope-auditor.md` |
| Draft changelog/release notes | `prompts/changelog-drafter.md` |
| Check long job or monitor artifacts | `prompts/monitor-artifact-triager.md` |

## Codex Framing

Spawn a `worker` for write-capable bounded tasks and an `explorer` for read-only investigation. Wrap the selected prompt like this:

```text
Your task is to perform the following. Follow the instructions exactly.

<agent-instructions>
[filled prompt content]
</agent-instructions>

Execute this now. Output only the requested structured result.
```

## Main-Session Duties

- Do not duplicate the subagent's exact investigation while it runs.
- Continue with non-overlapping work.
- Integrate only evidence-backed findings.
- Keep final ownership of staging, commit, push, user-facing claims, and destructive cleanup.

## Common Mistakes

- Delegating the next blocking task and then waiting idly.
- Asking two subagents to inspect the same thing.
- Sending secrets, tokens, private env values, or unnecessary session history.
- Accepting a subagent success report without checking the files or commands it references.
