---
name: dependabot-security-fix
description: Scan and fix Dependabot alerts across npm/pip/go.
version: 0.1.0
author: Hermes
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Dependabot, Security, npm, uv, Go, Dependencies]
---

# Multi-Ecosystem Dependabot Security Fix

Scan GitHub Dependabot alerts across npm, Python (uv), and Go ecosystems,
check upstream repo for existing fixes, apply upgrades, verify builds, and
commit with Conventional Commits. Handles the full flow from alert inspection
to pushed fix.

Supports both manual fix workflows and automated PR auto-merge evaluation
(non-security, all CI pass, patch/minor only — see Auto-Merge PR Evaluation
section). Does NOT auto-deploy — that remains a human decision.

## When to Use

- "Dependabot has X alerts, fix them."
- "Run npm audit fix and update Python/Go deps."
- "Check if upstream already fixed this CVE."
- "Update our lockfiles for security patches."
- "Auto-merge Dependabot PRs that are non-security, CI-passing, patch/minor."
- "Daily Dependabot scan — just report, don't fix."

## Prerequisites

- `gh` CLI authenticated with repo access.
- `npm` / `node` installed for JavaScript projects.
- `uv` installed for Python dependency management.
- `go` installed for Go module updates.
- Working directory: the cloned repo root.

## How to Run

1. Call `terminal` to check Dependabot alerts via `gh api`.
2. Root `npm audit fix` first, then sub-projects.
3. `uv lock --upgrade` then `uv pip compile --upgrade`.
4. `cd` to Go module dir, run `go get -u` on vulnerable packages.
5. Verify each ecosystem builds.
6. `git commit` with `chore(deps):` prefix, push.

## Quick Reference

```sh
# Inspect alerts
gh api repos/<owner>/<repo>/dependabot/alerts --paginate --jq \
  'group_by(.dependency.package.ecosystem)[] | "\(.[0].dependency.package.ecosystem): \(length)"'

# npm
npm audit fix
npm audit fix --force   # when breaking changes are acceptable for dev-only deps

# uv
uv lock --upgrade
uv pip compile pyproject.toml --upgrade -o requirements.txt

# Go
cd path/to/go/module
go get -u golang.org/x/crypto@latest golang.org/x/net@latest
go mod tidy
go build ./...
```

## Procedure

### 1. Inspect Dependabot Alerts

Use the `terminal` tool to fetch alerts grouped by ecosystem:

```sh
cd /path/to/repo
gh api repos/<owner>/<repo>/dependabot/alerts --paginate --jq '
  group_by(.dependency.package.ecosystem)[] |
  "\(.[0].dependency.package.ecosystem): \(length) total"
'
```

For severity breakdown, add `.security_advisory.severity` grouping.

### 2. Check Upstream for Existing Fixes

When the repo is a fork, check if the upstream/official repo has already
addressed the same CVEs:

```sh
# Fetch upstream
git remote add upstream https://github.com/OfficialOrg/repo.git 2>/dev/null
git fetch upstream main

# Check Dependabot-style commits
git log upstream/main --oneline -30 --author=dependabot

# Compare key dependency versions
git show upstream/main:pyproject.toml | grep -E "package-name"
```

### 3. Fix npm Vulnerabilities

Start from the repo root, then fix each sub-project that has a
`package-lock.json` (or `pnpm-lock.yaml`):

```sh
# Root - fix and regenerate lockfile
npm audit fix

# Breaking changes (dev-only deps like concurrently):
npm audit fix --force

# Sub-projects - each has its own package-lock.json
cd scripts/whatsapp-bridge && npm audit fix && cd ../..
cd website && npm audit fix && cd ..

# Photon sidecar plugin - transitive protobufjs often needs override
cd plugins/platforms/photon/sidecar
# 1. Add/ensure override in package.json for protobufjs
# 2. Remove node_modules and package-lock.json for clean reinstall
rm -rf node_modules package-lock.json
npm install --no-fund --ignore-scripts  # avoid postinstall patch failure
# 3. Verify: npm ls protobufjs should show overridden version (8.7.1+)
npm ls protobufjs
cd ../../..
```

**Important:** If a sub-project has a failing `postinstall` script (e.g., photon/sidecar's `patch-spectrum-mixed-attachments.mjs`), use `npm install --ignore-scripts` to update the lockfile without running the patch. The patch can be run manually later if needed.

### 4. Fix Python Dependencies (uv)

```sh
# Upgrade lockfile to latest compatible versions
uv lock --upgrade

# Regenerate requirements.txt
uv pip compile pyproject.toml --upgrade -o requirements.txt
```

Check key security-relevant packages were updated:

```sh
grep -E "(aiohttp|tornado|starlette|python-multipart)" requirements.txt
```

### 5. Fix Go Dependencies (watchdog, etc.)

```sh
cd scripts/windows/watchdog-go   # or path to Go module
go get -u golang.org/x/crypto@latest
go get -u golang.org/x/net@latest
go mod tidy
go build ./...
```

If `go build` fails due to Windows resource limits on large transitive deps
(e.g. Tailscale), verify just your module compiles:

```sh
go build -v . 2>&1 | tail -5
```

### 6. Commit and Push

```sh
git add -A
git commit -m "chore(deps): fix Dependabot security vulnerabilities across npm/pip/go

npm:
- npm audit fix [--force]: resolved CVE-* in <pkg>

Python (uv):
- uv lock --upgrade: <pkg> <old> -> <new> (CVE-*)

Go:
- golang.org/x/crypto <old> -> <new> (CVE-*)
- golang.org/x/net <old> -> <new>
"
git push origin main
```

### 7. Verify Dependabot Refresh

Dependabot rescans automatically after push (may take minutes to hours).
Check the GitHub Security → Dependabot tab after a few minutes. The alert
count should decrease.

## Pitfalls

- **npm audit fix --force** downgrades packages if the fix requires a breaking
  SemVer change. Only safe for dev dependencies (concurrently, etc.). Check
  `git diff package.json` before committing.
- **protobufjs transitive dependencies** (e.g. in photon/sidecar) may show moderate alerts even after upstream fixes. Resolve by adding an override in the appropriate package.json (root package.json for workspace-wide, or specific plugin's package.json) setting `"protobufjs": "^8.7.1"`, then run `npm install` to update lockfiles. Verify with `npm ls protobufjs` that the overridden version is active.
- **npm min-release-age blocking fixed versions**: Many repos use `.npmrc` with `min-release-age=14` to avoid brand-new packages. This BLOCKS installation of freshly-published security fixes (e.g., undici 6.28.0, brace-expansion 5.0.9, fast-uri 4.1.2, postcss 8.5.25 published within 14 days). **Fix**: Add `min-release-age-exclude[]=<package>` to each workspace's `.npmrc` (root, website/, ui-tui/, plugins/platforms/photon/sidecar/, etc.) before running `npm install`. This is the #1 cause of "npm audit fix does nothing" on this repo.
- **Multiple npm workspaces**: This repo has 6+ workspaces (root, website/, ui-tui/, apps/desktop/, apps/bootstrap-installer/, plugins/platforms/photon/sidecar/) each with independent package-lock.json. Must run `npm install` (with overrides + min-release-age-exclude) in EACH workspace. Use `npm audit` per workspace to verify.
- **Photon sidecar postinstall failure**: The `patch-spectrum-mixed-attachments.mjs` postinstall script fails on Windows. Use `npm install --ignore-scripts` to update lockfile without running patch; run patch manually later if needed.
- **ui-tui direct undici dependency**: ui-tui/package.json declares `"undici": "6.27.0"` directly (not transitive). Must edit package.json to `"6.28.0"` THEN run `npm install` in ui-tui/.
- **`go build ./...`** on Windows may hit page-file limits with large
  Tailscale transitive deps. Fall back to `go build -v .` for just your module.
- **uv exclude-newer blocking fixed versions**: `[tool.uv]` in pyproject.toml has `exclude-newer = "14 days"` and `exclude-newer-span = "P14D"`. This BLOCKS freshly-published security fixes (e.g., aiohttp 3.14.3 published 2026-07-23). **Fix**: Add the package to `exclude-newer-package` in `[tool.uv]`: `exclude-newer-package = { ..., aiohttp = false }`. Then `uv lock --upgrade`.
- **uv.lock** is the canonical lock file; `requirements.txt` is a generated
  artifact. Always update both, but only mark `uv.lock` as the intent.
- **Transitive dependency conflicts may be unresolvable**: cryptography CVE-2026-69247 (GHSA-g6cj-pr64-35w5) requires `cryptography>=50.0.0` but `msal` and `alibabacloud-tea-openapi` cap at `<49`. This is a hard constraint conflict. Document the mitigation (OpenSSL 3.2+ implicit rejection in wheels) and accept remaining alerts.
- **Upstream may be ahead** — always `git fetch upstream main` before
  concluding "not fixed yet." The upstream may have bumped the dep in a
  non-Dependabot commit.
- **CRLF warnings** on Windows are cosmetic — `git add` may warn about LF→CRLF
  conversion. These are safe to ignore.
- **Dependabot alert deduplication**: Dependabot creates multiple alerts for the same package across different version ranges and manifest paths (uv.lock, requirements.txt, pyproject.toml). Deduplicate by `(ecosystem, package, summary)` for accurate counts.

## Fork Workflow (NousResearch/hermes-agent fork — e.g. zapabob)

When the repo is a fork whose **official Dependabot is closed** (alerts never
auto-fix) and `upstream/main` itself still ships vulnerable lockfiles:

1. **Branch from `upstream/main`, not fork `main`.** The fork `main` may carry
   stale or conflicting pins. `git fetch upstream main && git switch -c
   chore/... upstream/main`.
2. **Layer patches ON TOP of upstream — do not "sync to upstream and call it
   done".** Syncing alone leaves every CVE upstream never fixed still open.
   Run `uv lock --upgrade` + `npm audit fix` on the upstream-based branch so the
   patched versions actually land in the lockfiles.
3. **Exclude fork-only assets from the PR.** Do NOT include `scripts/windows/`,
   `vendor/`, or `_docs/` (these are fork operational assets, not upstream
   deps). Stage only the lockfile/manifest changes explicitly:
   `git add pyproject.toml uv.lock package-lock.json website/package-lock.json`.
4. **Go advisories (e.g. `gorilla/csrf` in `scripts/windows/watchdog-go`) are
   fork-only — skip them.** They are not part of the upstream dependency
   surface.
5. **Do NOT revert intentional security pins.** This fork pins
   `starlette==1.3.1` as the patched version for CVE-2026-48710 (BadHost);
   upstream's `1.0.1` is the VULNERABLE one. Never "align to upstream" on that.
   Also `npm audit fix --force` may downgrade `concurrently ^10 -> ^9` in app
   manifests (e.g. `apps/desktop/package.json`) — revert those with
   `git checkout -- apps/desktop/package.json`.
6. **Check for duplicates before opening an upstream PR.** The official repo
   often already has 10+ open CVE-fix PRs (e.g. Pillow 12.3.0, tornado 6.5.7,
   cbor2 bumps) and issues (#60841, #47997). If a same-scope PR/issue exists,
   **do not open a duplicate** — report it and stop. The fork PR is still valid.
7. **Write PR/issue bodies in clear, correct, professional English** (accurate
   technical detail, no colloquialisms). State the scope note (official
   Dependabot closed; patches layered on upstream/main; fork dirs excluded).

See `references/fork-workflow.md` for the exact command sequence and the
`gh api` alert-grouping / duplicate-check recipes.

See `references/daily-vuln-scan-recipe.md` for the read-only multi-repo
Dependabot + local pip-audit scanning recipe used by the daily cron job.

See `references/auto-merge-evaluation.md` for the Dependabot PR auto-merge
evaluation procedure (deep security cross-referencing, CI check methods,
major version detection, merge state evaluation).

## Auto-Merge PR Evaluation

Evaluate open Dependabot PRs for safe auto-merge: non-security, all CI
checks pass, version bump is patch/minor only. Skip major bumps and
security-related PRs.

### Key Technique: Deep Security Cross-Reference

Group-bump Dependabot PRs (e.g. "bump npm_and_yarn group with 11 updates")
touch many transitive deps in lockfiles. A simple title-based check is
**insufficient**. Must:

1. Fetch open alert package names for the repo (`gh api` dependabot/alerts).
2. Fetch the PR diff (`gh pr diff`).
3. Extract changed package names from lockfile paths (`node_modules/X`) and
   package.json keys.
4. Intersect the two sets. If any changed package matches an open alert
   package → security-related → skip auto-merge.

### CI Check Methods

`gh pr checks --json` field names differ by gh CLI version (`state` vs
`conclusion`). Use `gh api repos/{repo}/commits/{sha}/check-suites` as a
more reliable fallback. See `references/auto-merge-evaluation.md` for both
methods and bot check-suite handling.

### Criteria

- Non-security (deep cross-reference, not title-based)
- All CI checks pass (or no CI configured)
- Version bump is patch/minor only (check PR body for "from X to Y" major jumps)
- Merge state is CLEAN or similar (not DIRTY/BLOCKED/CONFLICTING)

## Daily Vulnerability Scan (Read-Only Report)

For scheduled cron jobs or manual audit-only runs — no fixes applied, just
scan all repos and produce a concise severity-grouped report.

### Multi-Repo Dependabot Scan

1. List all repos: `gh repo list --limit 50 --json nameWithOwner`
2. For each repo, fetch alerts: `gh api repos/<repo>/dependabot/alerts --paginate`
3. Parse JSON with `execute_code` (jq may be unavailable on Windows/MSYS; use
   Python `json.loads` on the `gh api` stdout instead of `--jq`)
4. Extract: `state`, `security_advisory.severity`, `dependency.package.name`,
   `dependency.package.ecosystem`, `security_vulnerability.vulnerable_version_range`,
   `security_vulnerability.first_patched_version.identifier`,
   `security_advisory.summary`
5. Deduplicate by `(repo, package, summary)` — Dependabot creates duplicate
   alerts for the same package across different version ranges
6. Group by repo, then severity (HIGH → MEDIUM → LOW)
7. Summarize: total open / fixed, per-repo breakdown, top fixes by impact

### Local pip-audit (hermes-agent fork)

Run alongside the Dependabot scan for packages not tracked by GitHub:

```sh
py -3 -m pip_audit --desc --format=json
```

Parse the JSON: `dependencies[].vulns[]` yields individual CVE/PYSEC IDs.
Deduplicate by `vuln.id` (same vuln hits multiple packages). Group by package,
list fix versions. Flag `NO FIX` entries for monitoring.

On Windows: use `py -3 -m pip_audit` (not `pip-audit` directly — `python` is
the WindowsApps stub). If `pip_audit` is not installed: `py -3 -m pip install
pip-audit`.

### Report Format

Keep it concise and actionable for the user:
- **Summary table**: repo → open count (H/M/L breakdown)
- **HIGH severity section**: grouped by repo, one line per unique vuln with
  package, fix version, and one-line description
- **Local pip-audit**: top packages with most vulns, critical fixes first
- **NO FIX watchlist**: CVEs with no upstream patch yet
- **Remediation priorities**: immediate (this week), short-term (2 weeks),
  ongoing monitoring

### Cron-Mode Notes

- This scan is safe to run autonomously — read-only, no git changes
- `execute_code` is the preferred tool for parsing large `gh api` JSON outputs
  (avoids context flooding from 100K+ char API responses)
- `gh api --paginate` returns a JSON array directly; `json.loads(stdout)` works
- Some repos may return 404 (no Dependabot enabled) — catch and skip
- Total runtime for 20 repos: ~15-30 seconds

## Verification

After the fix is pushed, run this from the repo root to confirm clean builds:

```sh
# npm
npm audit 2>&1 | tail -3

# Python
uv pip compile pyproject.toml -o /dev/null 2>&1 | tail -3

# Go (watchdog)
cd scripts/windows/watchdog-go && go build . 2>&1
```

All three should exit 0 with no vulnerability output.

### Stronger import-level proof (recommended for CVE patches)
`uv lock --check` only proves the lockfile is consistent, not that the patched
versions actually import. Prove it without disturbing a live `.venv` (which a
running Hermes/gateway process may have locked — `uv sync` can fail with
`os error 5: Access is denied` on a `.pyd`):

```sh
# 1. Confirm PyPI actually serves the patched versions (Windows: use a temp
#    file, NOT process substitution — `uv pip compile - <(...)` fails).
printf 'Pillow>=12.2.0,<12.4\ncbor2\nmsgpack\n' > _tmp_reqs.txt
uv pip compile -q --no-deps _tmp_reqs.txt
rm -f _tmp_reqs.txt

# 2. Install the patched set into an ISOLATED temp venv and import it.
uv venv --python 3.13 _tmp_v
uv pip install --python _tmp_v Pillow==12.3.0 cbor2==6.1.3 ...
_tmp_v/Scripts/python -c "import PIL, cbor2, tornado; print(PIL.__version__)"
rm -rf _tmp_v
```

**Caveat:** `cbor2` exposes NO `__version__` attribute — `print(cbor2.__version__)`
raises `AttributeError` even on a successful import. Check its version via
`importlib.metadata.version("cbor2")` or just rely on the `uv pip compile`
output. A successful `import cbor2` with no error IS the proof.