---
name: cloudflare-workers-repository-maintenance
description: Maintain Cloudflare Workers repositories and pinned forks.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Cloudflare, Workers, GitHub, Submodules, Verification]
---

# Cloudflare Workers Repository Maintenance

Maintain Cloudflare Workers applications and pinned upstream forks without confusing deployment configuration with upstream source changes. This skill covers capability orientation, safe fork and remote setup, submodule commit propagation, platform-specific build fixes, and evidence-based verification; it does not authorize production deployment, billing changes, or secret disclosure. Invoke repository commands through the `terminal` tool and inspect sources with `read_file` and `search_files` before editing.

## When to Use

- Explaining what Cloudflare OS or a Workers-based workspace can do.
- Forking an upstream Cloudflare repository for durable local changes.
- Updating a pinned upstream submodule and its parent repository.
- Fixing cross-platform local development or build command resolution.
- Preserving changes in a reviewable branch without merging to `main`.
- Verifying tests, diffs, remotes, submodule pointers, and pushed commits.

## Prerequisites

- GitHub-authenticated account with permission to create forks and push branches.
- Git and the repository-declared Node/package-manager versions for JavaScript or TypeScript Workers code.
- Upstream repository URL, parent repository URL, and submodule mapping.
- Project-local `AGENTS.md`, README, SOPs, and build/test instructions read with `read_file`.
- Secret-redaction policy. Never commit tokens, credentials, private keys, `.env` values, local databases, media, or unrelated generated artifacts.
- Explicit approval before deployment, DNS changes, production changes, paid services, or Cloudflare billing actions.

## How to Run

Use the `terminal` tool for GitHub/Git operations and test commands. Use `read_file` to inspect README, `AGENTS.md`, `.gitmodules`, manifests, and diffs; use `search_files` for secret-pattern and generated-artifact review; use `patch` for focused changes. Keep `upstream` canonical and `origin` pointed at the user's fork.

## Quick Reference

```text
git status --short --branch
git remote -v
git diff --check
git submodule status
git diff --submodule=log

gh repo fork <owner>/<repo> --clone=false
git remote set-url origin <fork-url>
git remote add upstream <upstream-url>
git add <changed-files>
git commit -m "<focused message>"
git push -u origin <review-branch>
```

## Procedure

1. **Establish scope and capabilities.** Describe the product from project material: Workers runtime, browser workspace, AI agents, integrations, authentication/access controls, storage, observability, customization, and deployment boundaries. Distinguish open-source code from hosted or paid services.

2. **Read before mutation.** Inspect project instructions, README, `.gitmodules`, manifests, relevant source files, current branch, remotes, submodule state, and working-tree status. Treat generated files and unrelated untracked files as untrusted until their provenance is known.

3. **Create or confirm forks.** Confirm exact upstream repositories before forking. Invoke `gh repo fork <owner>/<repo> --clone=false` through `terminal`, then verify fork URL and default branch. Do not assume fork ownership or name.

4. **Configure remotes safely.** Set `origin` to the fork and `upstream` to the official repository. For a parent with a submodule, configure both repositories independently. Record branch names before commits.

5. **Separate intended from incidental changes.** Review `git diff`, `git diff --stat`, `git diff --check`, and submodule diffs. Generated route trees, caches, local media, credentials, and unrelated files must not enter a focused commit unless explicitly required. Restore incidental generated changes only after confirming their provenance.

6. **Implement the smallest platform fix.** Prefer repository-relative, runtime-portable commands over shell-specific package-manager spawning. For Node-based Workers builds, when a package-manager shim is the incompatibility, invoke the checked-in package binary through Node and use the same command in generated development configuration. Preserve existing build steps and working directories.

7. **Commit the submodule first.** In the submodule, create a focused review branch, stage only intended files, run `git diff --cached --check`, commit with a specific message, and push to the fork. Capture the resulting SHA and URL.

8. **Pin the parent repository.** In the parent, update only the submodule gitlink, review `git diff --submodule=log`, commit the pointer update, and push a separate review branch. The parent commit is incomplete if its referenced submodule SHA is not reachable from the fork.

9. **Run proportionate verification.** Execute the repository's canonical test command and focused checks for modified paths. Report pass/fail counts and distinguish unrelated or pre-existing golden-file failures from patch failures. Never call a failing test run successful.

10. **Verify remote evidence.** Confirm local and remote branch SHAs match, both working trees are clean, the parent gitlink resolves to the pushed submodule commit, and fork URLs are correct. Keep branches unmerged unless explicitly asked to merge.

11. **Record an implementation note.** For substantive work, use `write_file` under `_docs` with scope, changed files, commands, test results, known failures, commit SHAs, branch URLs, and residual risk. Redact secrets and note skipped deployment checks.

## Pitfalls

- Committing only the parent gitlink does not preserve submodule changes; commit and push the submodule first.
- A detached submodule `HEAD` is normal for a pinned checkout, but create a named branch before committing.
- A clean parent tree can hide dirty submodule content; inspect both levels.
- Generated files may become modified after tests or dev-server startup. Determine provenance before staging; never use broad `git add .` for a focused change.
- A successful fork command does not guarantee the local remote changed; verify `git remote -v`.
- A release-manifest golden-file failure is a mismatch, not proof that the platform fix works or fails. Preserve the exact failure and do not update goldens without review.
- Do not claim deployment, hosted activation, billing status, DNS changes, or production safety from local tests and GitHub pushes alone.
- Do not expose authentication output, tokens, environment values, or secret-pattern matches in logs.
- Do not merge to `main` as part of preservation unless explicitly requested.

## Verification

Through the `terminal` tool, require all of the following before reporting completion:

```text
git status --short --branch
git -C <submodule> status --short --branch
git -C <submodule> rev-parse HEAD
git -C <submodule> rev-parse origin/<submodule-branch>
git rev-parse HEAD
git rev-parse origin/<parent-branch>
git submodule status
git diff --check
```

The parent gitlink SHA must equal the pushed submodule SHA, both branch SHAs must match their remotes, working trees must be clean, and test results must be stated exactly.

Load `references/cloudflare-os-fork-session.md` with `skill_view` when a session-specific worked example, route map, Windows build adjustment, or test caveat is needed.
