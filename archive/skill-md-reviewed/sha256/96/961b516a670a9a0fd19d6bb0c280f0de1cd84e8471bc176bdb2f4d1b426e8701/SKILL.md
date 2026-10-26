---
name: verification-gated-github-delivery
description: "Use when shipping unverified changes through a Draft PR."
version: 1.0.0
author: Hermes Agent
license: MIT
category: github
metadata:
  hermes:
    tags: [github, draft-pr, verification, release-gates, security]
---

# Verification-Gated GitHub Delivery

Use this class-level skill when local checks pass but live, production, compatibility, security, operational, or review gates remain open. Default to a feature branch plus Draft PR, not direct `main` publication.

## Workflow

1. Confirm repository identity, current branch, HEAD, remotes, clean status, and the exact commit under consideration. Do not infer state from an earlier turn.
2. Inspect the commit with `git show --stat`, `git show --name-status`, and `git ls-files "_docs/*<topic>*"` to detect omitted files and near-identical path variants. A file-mutation warning can indicate an unapplied patch or filename mismatch; it does not invalidate an existing commit.
3. Compare with `origin/main`, run `git diff --check origin/main...HEAD`, and scan the diff for workstation/model-cache paths, authorization headers, bearer tokens, API keys, refresh tokens, and model credentials. Manually classify intentional redaction fixtures; a grep hit alone is not proof of a secret leak.
4. Keep evidence classes separate: local tests/lint/compile/clean tree; remote branch publication; PR metadata; CI; live probes; review; mergeability; production readiness.
5. Push only the named feature branch. Do not push directly to `origin/main` unless explicitly authorized.
6. Verify publication by matching `git rev-parse HEAD` with `git ls-remote origin refs/heads/<branch>`. This proves branch publication only.
7. Create a repository-qualified Draft PR with explicit base, head, title, and `--body-file`. Separate Summary, Included, Invariants, Verification, and Not yet verified sections; avoid shell interpolation hazards from inline Markdown.
8. Verify PR URL, repository, base/head branches, head SHA, open state, draft flag, mergeability, and merge state. Query checks separately. Pending checks and `UNSTABLE` are pending, not PASS.
9. Keep the PR Draft while live compatibility, production backend behavior, long-run soak, A/B quality, restart recall, security review, or other claimed gates remain unverified.

## Semantic Graph invariants

For Semantic Graph retrieval changes, state explicitly:

- Semantic Graph is the canonical source of truth.
- Vector indexes are reproducible derived data.
- Embedding retrieval is a candidate generator only.
- Embeddings cannot promote nodes, merge nodes, confirm `same_as`, supersede nodes, change authority or graph confidence, or rewrite answers.
- Production recall remains lexical-first with lexical-only degradation unless a separate production gate proves otherwise.

## Reporting contract

Use compact bullets or a table with: **Observed** (command/result and commit or PR identity), **Pending** (not performed or still running), **Not claimed** (readiness/compatibility not established), and **Next gate** (smallest concrete action advancing review). Never call a PR production-ready merely because local tests pass, the remote SHA matches, or GitHub reports it mergeable.

## References

- `references/feature-branch-draft-pr-verification.md` — concrete commands, evidence boundaries, path/credential scan handling, and Draft PR body contract.
