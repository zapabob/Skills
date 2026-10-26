---
name: git-delivery-verification
description: Verify scoped Git commits and remote pushes on Windows.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [git, github, commit, push, verification, windows]
    related_skills: [github-pr-workflow, github-operations, verification-gated-github-delivery]
---

# Git Delivery Verification Skill

Use this skill when the user asks to commit and push a completed change, especially from a Windows checkout with unrelated working-tree files or multiple modules.

## When to Use

- The user asks to commit and push changes.
- A repository has unrelated untracked files that must not be included.
- The checkout has `origin`/`upstream` remotes or a non-default branch.
- Local tests need to run per module rather than from the repository root.

## Prerequisites

- Confirm the repository root, branch, status, recent HEAD, and `origin` URL.
- Confirm GitHub authentication without printing credentials.
- Identify the exact files in scope; never infer that every working-tree change belongs to the request.

## Procedure

1. **Inspect current state** with `git status --short --branch`, `git branch --show-current`, `git log -5 --oneline`, and `git remote -v`.
2. **Inspect and validate the diff** with `git diff --check`, `git diff --stat`, and a targeted diff. Scan for credential-shaped values; classify ordinary words such as `secretary` or `token` in documentation before treating them as secrets.
3. **Choose the branch safely.** If the user says only “commit and push” without naming `main`/`master`, create a short-lived feature branch. Push the default branch only when explicitly requested.
4. **Stage explicitly.** Use `git add` with the named files. Do not use `git add .` when unrelated untracked scripts or generated files exist. Inspect `git diff --cached --name-status`, `--stat`, and `--check`.
5. **Run verification before commit.** For a Go repository with a root `go.work`, run `go test ./...`, `go vet ./...`, and builds separately inside each module; a root-level `go test ./...` may be invalid even when modules pass.
6. **Commit conventionally** with a message explaining the change, then inspect `git show --stat --name-status HEAD`.
7. **Push and verify.** Run `git push -u origin <feature-branch>`, then compare `git rev-parse HEAD` with `git ls-remote origin refs/heads/<feature-branch>`. Confirm `git status --short --branch` shows the branch tracking its remote.
8. **Report scope honestly.** Include commit SHA, branch, remote verification, tests, PR URL if emitted by GitHub, and any intentionally excluded/untracked files. Do not claim a PR was created unless a PR handle/URL was actually returned.

## Windows Notes

- Use POSIX syntax in Hermes `terminal`, but pass native Windows paths to native tools.
- Use `py -3` rather than a Python Store stub.
- Do not expose tokens from `gh auth status`; it may print masked token metadata.
- Preserve unrelated working-tree files and do not clean them up unless explicitly requested.

## Verification Checklist

- [ ] Correct repository and remote confirmed.
- [ ] Intended files only are staged.
- [ ] Tests/build/vet pass at the correct module scope.
- [ ] Commit SHA is recorded.
- [ ] Remote branch SHA matches local HEAD.
- [ ] Branch tracking and remaining untracked files are reported.

## Related Skills

`github-pr-workflow` and `github-operations` cover the broader GitHub lifecycle; use this skill for scoped delivery and post-push evidence.
