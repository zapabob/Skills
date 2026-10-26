---
name: github-operations
description: Class-level workflow for GitHub authentication, repository operations, pull-request review, and Actions CI triage.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
category: github
metadata:
  hermes:
    tags: [github, auth, repositories, pull-requests, code-review, actions, ci]
    category: github
---

# GitHub Operations

Use this umbrella for GitHub work across authentication, repository lifecycle, pull-request review, and CI diagnosis. The bundled `github-repo-management` skill remains the canonical repository command reference; this skill adds routing and class-level guardrails.

## Workflow routing

1. Detect auth with `gh auth status`, git credential helper, and SSH without printing secrets.
2. Identify the explicit owner/repository and current branch before mutating anything.
3. For repository lifecycle work, use the bundled repository-management reference.
4. For PR review, gather metadata, changed files, checks, full context, and targeted tests before commenting or approving.
5. For CI failures, inspect `gh run view --log-failed`, distinguish `failure` from `action_required`, reproduce locally, and verify before pushing.
6. Keep tokens out of URLs, prompts, logs, and artifacts; report handles/URLs and statuses, not credentials.

## Support references

- `references/github-auth.md`
- `references/github-code-review.md`
- `references/github-actions-ci-triage.md`

## Fork and repository-target safety

When a checkout has both `origin` (fork) and `upstream` remotes, every `gh pr` read or write must explicitly include `--repo OWNER/REPO` derived from the intended remote. Do not rely on the current directory, `gh` context, or PR number alone.

Before creating or verifying a PR:

1. Parse and record the intended owner/repository from the target remote.
2. Use `gh pr create --repo OWNER/REPO ...`.
3. Use the same explicit `--repo OWNER/REPO` for `gh pr view`, `gh pr checks`, comments, edits, and status queries.
4. Verify that the returned URL, base repository, head branch, and head SHA match the intended fork and local branch.
5. Treat a PR number without its repository as unsafe and non-verifiable.

A PR number is only repository-scoped; `gh pr view 35` can inspect a different repository than the one just pushed.

## Verification

Every completed operation must have a concrete verification: authenticated identity or remote access for auth, a returned PR review/comment handle for GitHub writes, or a successful local/remote CI status for Actions work. Never claim publication, approval, or green CI from an unverified command.

For fork PRs, verification is incomplete until the API or `gh` response confirms the expected `base`, `head`, `head_sha`, repository owner/name, state, mergeability, and check results. Always report the fully qualified PR URL.

See `references/fork-pr-session-pitfalls.md` for a concise record of fork-target and submodule verification pitfalls.
