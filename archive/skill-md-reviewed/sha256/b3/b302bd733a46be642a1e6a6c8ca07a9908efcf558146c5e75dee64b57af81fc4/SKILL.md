---
name: windows-hermes-upstream-sync
description: Safely inspect, plan, and carry out upstream synchronization for a Windows-hosted Hermes fork while preserving genuine fork behavior. Use for requests to compare a Hermes fork with its official upstream, run a repository-native Python sync helper, classify official versus fork changes, prepare an isolated merge, publish after CI, or restart and prove a Hermes runtime.
---

# Windows Hermes Upstream Sync

Use this workflow for an actual Git checkout. Do not infer a project, helper, branch, port, or test command from an empty Codex workspace.

## Choose the mode

Default to `inspect` when the request does not explicitly authorize changes.

| Mode | Permitted outcome | Requires direct approval before advancing |
| --- | --- | --- |
| `inspect` | Evidence and a decision matrix only | Any worktree, Git, config, process, or service change |
| `plan` | A concrete command sequence and stop conditions | Creating a branch/worktree or generated report |
| `apply` | An isolated branch/worktree merge and local verification | Merge, commit, or any generated report if not requested |
| `publish` | Remote branch or main update and CI reconciliation | Every push, PR, main promotion, or release/tag action |
| `restart` | Restart/build plus live runtime proof | Every process stop/start, desktop rebuild, or tunnel change |
| `verify` | Live endpoint, listener, PID, and optional local-model proof | Starting a local model or changing service state |

Never treat a successful wrapper, dry run, focused test, or process exit as full delivery. State precisely which later gates remain pending.

## Inspect before changing state

1. Confirm the absolute repository path and that it is a Git worktree. Read the nearest applicable `AGENTS.md`, repository README, contribution policy, package manifests, CI workflows, and any fork policy before selecting commands.
2. Capture the active branch and commit, `git status --short --branch`, `git diff --stat`, remotes, remote default branch, and `git worktree list`. Preserve all tracked, untracked, and sibling-worktree changes. Never use `reset`, `checkout --`, `clean`, `stash`, or a broad delete to make a tree appear clean.
3. Identify the official upstream remote and the repository-native Python sync/merge helper. Read its `--help`, conflict strategy, and generated-report behavior. Do not invent a second merge script when the checkout supplies one.
4. When the request needs current upstream state, fetch the named remote immediately before comparison and again immediately before a publish decision. Record the exact upstream and fork SHAs. Treat `git fetch` as a repository metadata change, not a source merge.
5. Check open pull requests and duplicate issues using the project-authorized forge tooling when authenticated. If issues are disabled or authentication is unavailable, record that condition; do not infer an empty result.

For `inspect`, stop after reporting evidence unless the user has expressly requested a report-producing helper run. Repository dry-run helpers can write inventories and logs, so they are not automatically read-only.

## Classify before merging

Build a compact decision matrix for each material area:

| Area | Official state | Fork state | Decision | Evidence |
| --- | --- | --- | --- |
| path or capability | new, changed, removed, or unaffected | custom behavior and contract | adopt, integrate, preserve, or defer | code, tests, config, and runtime behavior |

Use the official implementation as the base when behavior is materially equivalent. Preserve or reapply only a demonstrated fork advantage. Compare API/config compatibility, error paths, migration impact, security behavior, and real test/runtime evidence; filenames and feature names alone are insufficient.

Do not hand-resolve a path designated as protected by the repository conflict policy. Stop with the helper report if a protected path, unresolved conflict, or unexplained overlay failure remains.

## Apply only in isolation

1. Create or select an isolated feature branch or worktree. Keep the primary checkout and its unrelated dirty state untouched.
2. Use the discovered repository-native helper in its dry-run mode first. Read the complete generated inventory and blocker report. Do not pass a blocker override merely to obtain green-looking output.
3. Run the helper's merge path only after the dry run has no unresolved protected paths, or after the user explicitly accepts each documented blocker and its consequence.
4. Keep repository-specific local documents, secrets, generated files, runtime state, and fork-only material outside the commit unless the decision matrix identifies a required, reviewed change.
5. Record the pre-change SHA so the isolated branch has a clear rollback point.

## Verify the full delivery chain

Use project-native commands discovered during inspection. Run targeted tests for changed behavior, then the appropriate wider tests, lint, type checks, dependency/lock verification, and security checks. On Windows, use the repository virtual environment and set `PYTHONUTF8=1` when the default code page obscures UTF-8 failures.

Before `publish`, re-fetch upstream, repeat PR/issue reconciliation, review the exact commit range and staged paths, then obtain explicit approval for the intended remote and branch. Confirm remote parity and fresh CI for that exact SHA. Do not publish private artifacts, `_docs` reports, local state, secrets, or unrelated worktree files.

For `restart` or `verify`, discover the current backend port from the newest ready log rather than assuming a historical port. Prove the result with all applicable evidence: a successful HTTP request to the exact endpoint, a matching `netstat -ano` listener, PID and command-line ownership, and the current ready log. If local llama or another local model is in scope, apply one explicit policy: `never`, `preserve-existing`, or `ensure-hot-standby`. Never start it by implication.

## Report and stop conditions

Use the evidence fields in [references/evidence-schema.md](references/evidence-schema.md). Mark every gate `pass`, `fail`, `pending`, or `not-run`; do not collapse those states.

Stop and request direction when the repository path, upstream, default branch, applicable fork policy, merge helper, protected-worktree scope, required approval, or runtime identity cannot be determined. Also stop when tests, CI, parity, endpoint checks, or local-model policy are missing or failing.
