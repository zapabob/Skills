---
name: git-submodule-integration
description: "Use when adding external repos as verified git submodules."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Git, Submodule, Node.js, pnpm, TypeScript, Verification]
---

# Git Submodule Integration

Integrate a forked or third-party repository as an independently versioned submodule while preserving isolated dependency resolution, fresh verification evidence, and a clean parent gitlink.

## When to use

- Add an external repository under `vendor/` or another submodule path.
- The parent is a workspace/monorepo but the submodule has its own lockfile and package manager.
- Verify the nested project before committing the parent integration.

## Workflow

### 1. Inspect before changing

Check the parent branch, remotes, existing submodules, repository instructions, and the external repository's default branch and package-manager requirements. For a fork, read fork-specific merge/submodule guidance. Do not assume the parent workspace can safely install or build the nested project.

### 2. Fork and add

With authenticated GitHub CLI:

```bash
gh repo fork upstream-owner/repo-name --clone=false
git submodule add https://github.com/your-owner/repo-name.git vendor/repo-name
```

Prefer the user's fork as the submodule URL when tracking user-owned changes. Add `branch = main` in `.gitmodules` when branch tracking is useful, while remembering that the parent pins an exact commit.

### 3. Isolate dependency installation

Run package-manager commands from inside the submodule, never from the parent root. For a nested pnpm project:

```bash
cd vendor/repo-name
pnpm install --frozen-lockfile --ignore-workspace
```

This prevents parent workspace metadata from contaminating dependency resolution. Respect the submodule lockfile and avoid changing source/config to mask a transient workspace problem.

### 4. Verify independently

Run the external project's documented checks from its own directory. For Node/TypeScript projects:

```bash
pnpm run test
pnpm run typecheck
pnpm run build
```

Use real output and report warnings separately. Windows typecheck/build/test does not prove macOS Electron packaging or runtime behaviour; state that platform boundary explicitly.

### 5. Windows Git Bash command resolution

If a globally installed npm command is missing from Git Bash PATH, prepend the npm global directory or invoke the `.cmd` executable directly:

```bash
export PATH="/c/Users/<user>/AppData/Roaming/npm:$PATH"
pnpm run test
# preferred for unambiguous evidence
/c/Users/<user>/AppData/Roaming/npm/pnpm.cmd run test
```

A `pnpm: command not found` result from an unprepared PATH is not evidence that pnpm is unavailable.

### 6. Handle compiler mismatches conservatively

Check the actually installed compiler version before changing configuration. Do not add TypeScript 6-only options such as `ignoreDeprecations: "6.0"` to a project resolved to TypeScript 5.x; that can produce `TS5103`. First correct workspace isolation and reinstall from the lockfile. Revert temporary probes unless upstream requires them.

### 7. Commit only the parent integration

Verify both worktrees independently:

```bash
git -C vendor/repo-name status --short --branch
git status --short --branch
git submodule status vendor/repo-name
git diff --cached --check
```

Generated outputs such as `dist/` belong to the submodule's ignore rules or its own repository, not the parent commit. Stage only `.gitmodules` and the gitlink:

```bash
git add .gitmodules vendor/repo-name
git commit -m "feat: add repo-name vendor submodule"
```

Afterward verify the commit, push destination, branch tracking, and clean status. Do not recreate a parent commit solely to refresh verification when the gitlink is unchanged.

## Pitfalls

- Workspace leakage: install inside the submodule with `--ignore-workspace`.
- PATH false negatives: Git Bash may omit the npm global directory; use an absolute `.cmd` path for fresh evidence.
- Premature tsconfig edits: transient TypeScript 6 diagnostics do not justify TS 6 flags when the lockfile resolves TypeScript 5.x.
- Stale evidence: rerun canonical checks with an absolute executable path, then recheck both worktrees; never infer success from old output.
- Platform boundary: Windows web/type/build checks do not constitute macOS Electron packaging or runtime validation.

## Supporting references

- `references/submodule-dependency-pitfalls.md` — workspace isolation, compiler compatibility, and Windows command resolution.
- `references/verification-recovery.md` — refreshing stale evidence and confirming the fixed gitlink without unnecessary commits.
