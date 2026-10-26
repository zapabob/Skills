---
name: dependabot-fix-and-pr
description: Fix Dependabot alerts and prepare upstream PR with changes.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Security, Dependabit, npm, pip, Go, Dependencies, PR, Upstream]
---

# Dependabot Fix and Upstream PR

Fix Dependabot security alerts in your fork, then prepare a pull request to the upstream repository with your changes (excluding certain files like _docs). This skill covers the full workflow from alert resolution to PR creation.

## When to Use

- Dependabot reports open security alerts on your fork repository
- You want to fix vulnerabilities in npm, pip, and Go dependencies
- After fixing, you need to send a PR to the upstream official repository with your changes (excluding documentation, internal configs, etc.)
- The upstream repository does not have Dependabot enabled, so you must manually apply the fixes

## Prerequisites

- `gh` CLI authenticated with access to both fork and upstream repositories
- `npm` and `uv` available in PATH
- `go` available in PATH (for Go module updates)
- Write access to the fork repository
- Access to create PRs on the upstream repository
- Active virtual environment for Python (`uv`)
- Git configured with user name and email

## How to Run

Invoke through the `terminal` tool with the sequence below, or delegate to a subagent with this prompt.

## Quick Reference

| Task | Command |
|------|---------|
| List open alerts | `gh api repos/FORK_OWNER/FORK_REPO/dependabot/alerts --jq '[.[] \| select(.state=="open")] \| length'` |
| View alert details | `gh api repos/FORK_OWNER/FORK_REPO/dependabot/alerts --jq '.[] \| select(.state=="open") \| {number, package: .dependency.package.name, severity: .security_advisory.severity, manifest: .dependency.manifest_path}'` |
| Update npm dependency | Edit `package.json`, then `npm install` |
| Update pip dependency | Edit `pyproject.toml` [tool.uv] override-dependencies, then `uv lock` |
| Update Go dependency | `go get module@version && go mod tidy` |
| Create branch | `git checkout -b dependabot-fixes` |
| Commit changes | `git commit -m "chore(deps): fix Dependabot security vulnerabilities"` |
| Push branch | `git push origin dependabot-fixes` |
| Create PR | `gh pr create --title "chore(deps): fix Dependabot security vulnerabilities" --body "Fixes for npm/pip/go dependencies"` |
| Prepare upstream PR | Create branch, commit changes (excluding _docs etc.), open PR to upstream |

## Procedure

### 1. Enumerate open alerts in your fork

```bash
gh api repos/OWNER/FORK/dependabot/alerts --jq '.[] | select(.state=="open") | {number: .number, package: .dependency.package.name, severity: .security_advisory.severity, manifest: .dependency.manifest_path, summary: .security_advisory.summary}'
```

Note each alert's package name, severity, and manifest path.

### 2. Fix npm vulnerabilities

For each npm alert:
1. Find the relevant `package.json` (root or workspace)
2. For direct dependencies: add/update in `dependencies` or `devDependencies`
   ```json
   "dependencies": { "vulnerable-package": "fixed-version" }
   ```
3. For transitive dependencies (like protobufjs): use the `overrides` field
   ```json
   "overrides": { "vulnerable-package": "fixed-version" }
   ```
4. Run `npm install` in that directory
5. **For packages with failing postinstall scripts** (e.g., photon/sidecar):
   - Remove `node_modules` and `package-lock.json`
   - Run `npm install --no-fund --ignore-scripts`
   - Verify the fix: `npm ls vulnerable-package` should show the overridden version
6. Commit `package.json` and `package-lock.json`

### 3. Fix pip vulnerabilities

For each pip alert:
1. Edit `pyproject.toml` `[tool.uv] override-dependencies`:
   ```toml
   override-dependencies = [
     "vulnerable-package==fixed-version",
   ]
   ```
2. Run `uv lock` to regenerate `uv.lock`
3. Commit `pyproject.toml` and `uv.lock`

### 4. Fix Go vulnerabilities

For each Go alert:
1. Run `go get vulnerable-module@fixed-version`
2. Run `go mod tidy`
3. Commit `go.mod` and `go.sum`

### 5. Verify resolution in fork

```bash
gh api repos/OWNER/FORK/dependabot/alerts --jq '[.[] | select(.state=="open")] | length'
```

Should return `0`. If not, repeat for remaining alerts.

### 6. Commit and push fixes to your fork

```bash
git add -A
git commit -m "chore(deps): fix Dependabot security vulnerabilities across npm/pip/go" -m "List each CVE addressed with GHSA/CVE IDs"
git push origin HEAD
```

### 7. Prepare changes for upstream PR

1. Fetch upstream main to ensure you are up to date:
   ```bash
   git remote add upstream https://github.com/UPSTREAM_OWNER/UPSTREAM_REPO.git 2>/dev/null
   git fetch upstream main
   ```
2. Create a new branch for upstream PR based on upstream main:
   ```bash
   git checkout upstream/main
   git checkout -b dependabot-fixes-upstream
   ```
3. Cherry-pick or merge the commits from your fork that contain the fixes. Alternatively, you can apply the same changes manually to the upstream branch. A common approach is to merge your fork's fix branch:
   ```bash
   git merge --no-ff origin/main   # assuming your fixes are on your fork's main
   ```
   Or, if you have a separate branch with fixes:
   ```bash
   git merge --no-ff origin/dependabot-fixes
   ```
4. **Exclude certain files** from the PR as requested (e.g., `_docs` directory, any internal configuration files that are fork-specific). You can reset those files to upstream state:
   ```bash
   git checkout upstream/main -- path/to/excluded_dir/
   git checkout upstream/main -- path/to/excluded_file
   ```
   Or, if you want to keep your changes but exclude them from the PR, you can amend the commit to remove those files, or use `.gitattributes` with export-ignore, but simpler is to reset them.
5. Verify that the changes you want to include are only the dependency fixes and any other unique features you want to contribute.
6. Commit the changes:
   ```bash
   git add -A
   git commit -m "chore(deps): fix Dependabot security vulnerabilities across npm/pip/go" -m "List each CVE addressed with GHSA/CVE IDs"
   ```
7. Push the branch to your fork:
   ```bash
   git push origin dependabot-fixes-upstream
   ```

### 8. Create pull request to upstream

```bash
gh pr create \
  --base UPSTREAM_OWNER/UPSTREAM_REPO:main \
  --head OWNER:dependabot-fixes-upstream \
  --title "chore(deps): fix Dependabot security vulnerabilities" \
  --body "This PR fixes the following Dependabot security vulnerabilities:\n\n- npm: package1 (CVE-XXXX-XXXX)\n- pip: package2 (CVE-XXXX-XXXX)\n- Go: module1 (CVE-XXXX-XXXX)\n\n*Changes excluded: _docs/, internal configs, etc.*"
```

### 9. Verify the PR

Check that the PR shows up in the upstream repository and that the changes are correct.

## Pitfalls

- **Lockfile not updated**: `npm install`/`uv lock` must run after manifest changes; otherwise GitHub still sees old versions
- **Workspace packages**: Vulnerabilities in workspace subdirectories (e.g., `apps/`, `plugins/`) need their own dependency updates
- **Transitive deps**: Overrides only work for direct dependencies; transitive fixes require updating the direct dependency that pulls them in or using override fields
- **Go module proxy**: `GOPROXY` may cache old versions; use `go get module@version` to force refresh
- **Postinstall scripts**: Some packages fail on `npm install` due to postinstall; use `npm install --no-fund --ignore-scripts` if needed (but verify the package works)
- **Upstream divergence**: If upstream has changed significantly, merging may cause conflicts. Resolve conflicts carefully.
- **Excluding files**: Be careful not to accidentally include fork-specific configuration that should not be sent to upstream. Use `git checkout upstream/main -- <file>` to revert to upstream version for excluded items.
- **PR title and body**: Follow the project's contribution guidelines for PR formatting.

## Verification

After the fix is pushed to your fork, run this from the repo root to confirm clean builds:

```bash
# npm
npm audit 2>&1 | tail -3

# Python
uv pip compile pyproject.toml -o /dev/null 2>&1 | tail -3

# Go (watchdog)
cd scripts/windows/watchdog-go && go build . 2>&1
```

All three should exit 0 with no vulnerability output.

After creating the PR to upstream, ensure that the PR only includes the intended changes and that CI passes (if applicable).