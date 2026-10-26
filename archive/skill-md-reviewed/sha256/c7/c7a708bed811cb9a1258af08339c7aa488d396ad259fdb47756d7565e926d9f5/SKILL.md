---
name: git-pr-fork-routing
description: "Choose the correct target repo when a git checkout has both origin (fork) and upstream remotes; avoid gh pr create silently opening against upstream."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, github, pr, fork, upstream, gh, remote]
    related_skills: [github-pr-workflow, github-auth]
---

# Git PR Fork Routing

Pick the right target repo before opening a pull request in a fork-based workflow. This prevents the common mistake of opening a PR against the **upstream** canonical repo when the user actually wanted it on **their own fork**.

## When this applies

The checkout has two remotes:

```
origin    https://github.com/<YOU>/hermes-agent.git   (your fork)
upstream  https://github.com/<ORG>/hermes-agent.git   (canonical)
```

`gh` resolves its *default* repo from the authenticated account and the checkout, which frequently points at `upstream` — **not** your fork. So `gh pr create` with no `--repo` opens the PR against `upstream` main by default, even though you pushed the branch to `origin`. The result is a cross-repository PR to the wrong repo.

## Steps

1. **Default to the fork (`origin`)** unless the user explicitly asks to contribute upstream. "Open a PR / merge it / create a pull request" normally means the user's own fork main.

2. **Always pin `--repo` to the fork owner/repo.** Derive it from `origin` so it never depends on `gh`'s resolution:

   ```bash
   ORIGIN_URL=$(git remote get-url origin)
   FORK_OWNER_REPO=$(echo "$ORIGIN_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
   gh pr create --repo "$FORK_OWNER_REPO" --base main --head "$(git branch --show-current)" \
     --title "type: short description" --body-file /tmp/pr-body.md
   ```

3. **Verify the landing spot immediately** after creation. A PR that resolved to upstream is `isCrossRepository: true` and shows a different base repo than the fork:

   ```bash
   gh pr view <NUMBER> --json number,title,baseRefName,headRefName,url,state,isCrossRepository
   ```

4. **Wrong repo?** Close it with a short note explaining the re-target (don't just delete — closing keeps the body and the trace), then recreate against the correct fork with `--repo`.

## Pitfalls

- `gh pr create` with no `--repo` is a **hazard** whenever an `upstream` remote exists. Pin `--repo` to the `origin` owner/repo for fork-targeted work.
- Don't assume `gh repo view --json nameWithOwner` reflects where the PR should go — that reports `gh`'s default repo (often upstream), not your fork.
- Closing a mis-targeted PR loses the body unless you re-supply it; use `--body-file` from a saved file so recreation is one command.
- For upstream-targeted contributions, still cherry-pick only the intended commits onto a clean upstream/main branch (see `github-pr-workflow`); that is a different flow from routing a PR to your own fork.
- **A local dir named after the repo may not be the fork at all.** It is often a shallow, detached tag checkout of *upstream* (`origin` = upstream URL, `.git/shallow` present). Confirm with `git remote -v` / `git branch -a` before any push or PR work. For pulling upstream's latest into a fork while preserving fork-only files, see `fork-upstream-sync`.

## Verification checklist

- [ ] `git remote -v` confirms both `origin` (fork) and `upstream` exist.
- [ ] `gh pr create` used explicit `--repo <fork-owner/repo>`.
- [ ] `gh pr view` shows `isCrossRepository: false` (or `true` only if upstream was the deliberate target) and the expected base repo.
