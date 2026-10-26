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

Does NOT auto-merge PRs or deploy — those remain a human decision.

## When to Use

- "Dependabot has X alerts, fix them."
- "Run npm audit fix and update Python/Go deps."
- "Check if upstream already fixed this CVE."
- "Update our lockfiles for security patches."

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
# Root
npm audit fix

# Breaking changes (dev-only deps like concurrently):
npm audit fix --force

# Sub-projects
cd scripts/whatsapp-bridge && npm audit fix && cd ../..
cd website && npm audit fix && cd ..
cd plugins/platforms/photon/sidecar && npm audit fix && cd ../../..
```

After each, confirm `found 0 vulnerabilities` in the output. If moderate
transitive deps remain blocked by an upstream package, note it for the commit
message.

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

- **CRITICAL: A repo can have 100+ Dependabot alerts that are ALL ONE stale
  lockfile.** Before triaging per-CVE, check whether `pyproject.toml`/`uv.lock`
  already carries the fixed pin while `requirements.txt` (a uv-generated
  artifact) lags. Regenerate instead of hand-editing:
  `uv pip compile pyproject.toml -o requirements.txt`. Verify drift with
  `grep -iE '^(pyjwt|urllib3|cryptography)' pyproject.toml requirements.txt`
  and confirm the real installed version in `.venv/Lib/site-packages/*-*.dist-info`.
  A CRITICAL PyJWT/urllib3 alert on `requirements.txt` while `uv.lock` shows a
  fixed version is stale-artifact noise, not an unpatched dependency — but it
  still matters if any bootstrap script does `pip install -r requirements.txt`.
- **`security_and_analysis.dependabot_security_updates.status` returning `none`
  does NOT mean "no alerts"** — it usually means Dependabot is disabled, and
  the alerts endpoint returns HTTP 403 "Dependabot alerts are disabled". Only
  `gh api repos/<o>/<r>/dependabot/alerts` returning a number is authoritative.
- **Paginate or undercount.** `--per_page=100` alone silently truncates:
  hermes-agent-windows showed exactly 100 with `--paginate` revealing 123.
  Always pass `--paginate` and count the TSV rows, never trust `length` on a
  single page.
- **Forks inherit upstream advisories.** `zapabob/codex` (fork of
  `openai/codex`) carries 288 alerts in `codex-rs/Cargo.lock`, `pnpm-lock.yaml`
  etc. that belong to upstream. Check `gh api repos/<o>/<r> --jq .fork`
  before triaging; don't chase vendor-tree alerts you can't push upstream.
- **npm audit `--json` cannot be parsed with `python -c` in cron.** Security
  Center blocks `-c`/heredoc/execute_code. Use `grep -o '"severity": "..."'`
  for counts and `sed -n '/"metadata"/,/^  }/p'` for the summary block.
- **govulncheck indirect ≠ exploitable.** watchdog-go reports
  GO-2025-3607 (gorilla/csrf v1.7.2) as reachable only through
  `tailscale.com/tsnet -> ipnlocal -> client/web -> gorilla/csrf`. Confirm with
  `go mod why <module>` and note it as transitive-without-local-call rather
  than fixing directly.
- **npm audit fix --force** downgrades packages if the fix requires a breaking
  SemVer change. Only safe for dev dependencies (concurrently, etc.). Check
  `git diff package.json` before committing.
- **photon/sidecar protobufjs** moderate alerts may be blocked by
  `@photon-ai/whatsapp-business` not releasing a fix — these are transitive
  and upstream-version-gated, not fixable without an override or fork.
- **`go build ./...`** on Windows may hit page-file limits with large
  Tailscale transitive deps. Fall back to `go build -v .` for just your module.
- **uv.lock** is the canonical lock file; `requirements.txt` is a generated
  artifact. Always update both, but only mark `uv.lock` as the intent.
- **Upstream may be ahead** — always `git fetch upstream main` before
  concluding "not fixed yet." The upstream may have bumped the dep in a
  non-Dependabot commit.
- **CRLF warnings** on Windows are cosmetic — `git add` may warn about LF→CRLF
  conversion. These are safe to ignore.

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
