---
name: dependabot-security-updates
description: Standard procedure for responding to Dependabot security alerts and running weekly security audits (Dependabot + pip-audit + npm audit + Go + code patterns + config hardening) in the Hermes Agent fork (zapabob/hermes-agent). Cron-safe read-only scan mode available.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Dependabot Security Updates Response Skill

## Purpose
Standard procedure for responding to Dependabot security alerts in the Hermes Agent fork (zapabob/hermes-agent). This skill ensures CVEs are addressed promptly by updating dependencies in lockfiles and configuration files, then verifying the alert count decreases.

## When to Use
- When Dependabot alerts appear for the repository
- After a security scan reveals new CVEs in dependencies
- As part of routine security maintenance

## Steps

### 1. Check Current Alerts
```bash
gh api repos/zapabob/hermes-agent/dependabot/alerts --jq '[.[] | select(.state == "open")] | length'
```
*Note the count and details of open alerts.*

### 2. Examine Specific Alerts (Optional)
To get details on a specific alert number:
```bash
gh api repos/zapabob/hermes-agent/dependabot/alerts/<NUMBER> --jq '{number:.number, package:.dependency.package.name, severity:.security_advisory.severity, summary:.security_advisory.summary}'
```

### 3. Update Python Dependencies (if any alerts involve pip packages)
- Edit `pyproject.toml`:
  - For packages in `[project.dependencies]`: bump version directly.
  - For packages in `[tool.uv] override-dependencies`: change to exact patched version (e.g., `"pillow==12.3.0"`).
- Run `uv lock` to update `uv.lock`.
- Commit changes:
  ```bash
  git add pyproject.toml uv.lock
  git commit -m "chore(deps): fix CVE-XXXX-XXXX by updating <package> to <version>"
  ```

### 4. Update JavaScript/TypeScript Dependencies (if any alerts involve npm packages)
- Identify which workspace/package.json contains the vulnerable package (commonly `apps/`, `web/`, `ui-tui/`, or plugins).
- Update the version in the appropriate `package.json`.
- Run `npm install --workspace <workspace>` or `npm install` at the workspace root.
- Commit `package.json` and `package-lock.json` (or relevant lockfile).
  ```bash
  git add <path>/package.json <path>/package-lock.json
  git commit -m "chore(deps): fix CVE-XXXX-XXXX by updating <package> to <version>"
  ```

### 5. Update Go Dependencies (if any alerts involve Go modules)
- Locate the affected `go.mod` (often in `scripts/windows/watchdog-go/` or similar).
- Run `go get <package>@<version>` or `go mod tidy`.
- Commit `go.mod` and `go.sum`.
  ```bash
  git add go.mod go.sum
  git commit -m "chore(deps): fix CVE-XXXX-XXXX by updating <module> to <version>"
  ```

### 6. Update Other Lockfiles (as needed)
- For any other lockfiles (e.g., `poetry.lock`, `yarn.lock`), follow the ecosystem's standard update procedure.
- Commit changes.

### 7. Push Changes
```bash
git push origin main
```

### 8. Verify Alert Reduction
After GitHub processes the push (may take a few minutes), re-check open alerts:
```bash
gh api repos/zapabob/hermes-agent/dependabot/alerts --jq '[.[] | select(.state == "open")] | length'
```
- If count decreased, proceed.
- If not, verify the updated version actually resolves the CVE and possibly open a pull request for review.

### 9. Commit Message Convention
Use `chore(deps): <description>` for dependency security updates.
Include CVE ID or GHSA ID in the commit body if helpful.

## Verification
- Ensure the project still builds and passes basic tests after updates.
- For UI-related changes, run relevant lint/test scripts if time permits.
- Confirm no new alerts were introduced by the update (re-check after push).

## Pitfalls
- Forgetting to update lockfiles after changing version specs -> run appropriate lock command.
- Updating only in one workspace when the dependency is duplicated -> check all workspaces.
- Using version ranges that don't actually include the fix -> use exact version when possible for security patches.
- Not pushing to the correct branch -> ensure you're on `main` unless working on a feature branch that will be merged soon.

## Example
After discovering a high-severity CVE in Pillow:
1. Edited `pyproject.toml` under `tool.uv.override-dependencies`: changed `"pillow>=12.2.0",` to `"pillow==12.3.0",`.
2. Ran `uv lock`.
3. Committed and pushed.
4. Verified the specific alert for GHSA-9hw9-ch79-4vh6 closed.

## Weekly Audit Scan (Read-Only, Cron-Safe)

For scheduled cron jobs or manual audit-only runs — no fixes applied, just scan
all ecosystems and produce a severity-grouped report. This is safe to run
autonomously: read-only, no git changes, no approval needed.

### Multi-Ecosystem Scan Sequence

1. **Dependabot alerts** (GraphQL/REST via `gh api`) — grouped by ecosystem+severity
2. **pip-audit** — local Python package CVEs not tracked by GitHub Dependabot
3. **npm audit** — root + each workspace (apps/*, web, ui-tui, website, plugins)
4. **Go** — `go build` verification on watchdog-go module
5. **Code patterns** — `shell=True`, `eval()`, `exec()`, `subprocess` usage
6. **Secret scanning** — regex for API keys/tokens in source files
7. **Config hardening** — review `.hermes/config.yaml` security-relevant settings

### pip-audit JSON Parsing (Windows/MSYS)

`jq` is often unavailable on Windows MSYS. Use `py -3 -m pip_audit --desc --format=json`
and parse with Python's `json.loads` instead of `--jq`:

```python
import json, subprocess
result = subprocess.run(
    ["py", "-3", "-m", "pip_audit", "--desc", "--format=json"],
    capture_output=True, text=True
)
# pip_audit prints a WARNING line before the JSON — find the first '{'
lines = result.stdout.strip().split('\n')
json_start = next(i for i, l in enumerate(lines) if l.strip().startswith('{'))
data = json.loads('\n'.join(lines[json_start:]))

# Deduplicate by vuln ID (same vuln hits multiple packages)
from collections import defaultdict
by_pkg = defaultdict(list)
for dep in data.get("dependencies", []):
    seen_ids = set()
    for v in dep.get("vulns", []):
        if v["id"] not in seen_ids:
            seen_ids.add(v["id"])
            by_pkg[dep["name"]].append({
                "id": v["id"], "fix": ", ".join(v.get("fix_versions", [])) or "NO FIX",
                "aliases": ", ".join(v.get("aliases", []))
            })
```

Key: use `py -3` (not `python` or `pip-audit` directly) on Windows — the
`python` entry in PATH is the WindowsApps store stub.

### Stale Go Dependabot Alerts

Go Dependabot alerts can persist even when `go.mod` already exceeds the fix
floor (e.g., `golang.org/x/crypto v0.54.0` fixes all `< 0.52.0` alerts but
Dependabot still shows 23 open). For fork-only Go modules (e.g.,
`scripts/windows/watchdog-go/` which is not part of the upstream dependency
surface), these alerts should be dismissed or ignored — they are not actionable.

Verify with:
```sh
cd scripts/windows/watchdog-go && go build . 2>&1  # should exit 0
```

### System venv vs pyproject.toml Pins

`pyproject.toml` pins may be correct (e.g., `Pillow==12.3.0`, `starlette==1.3.1`)
while the system venv still has older versions installed. pip-audit scans the
**installed** environment, not the lockfile. A `uv sync` is needed to propagate
lockfile pins into the active venv. Don't confuse pip-audit findings with
pyproject.toml pin correctness — check both.

### Report Format (for cron delivery)

Structure the report as:
1. **Summary table** — ecosystem × severity matrix
2. **CRITICAL** — package, CVE, fix version, one-line risk description
3. **HIGH** — same, tabular
4. **Actions taken** — what was fixed this run (npm audit fix, uv lock --upgrade, etc.)
5. **Remediation priorities** — immediate / short-term / monitoring

Keep it concise — critical/high only for the body; medium/low counts in the summary.

## References
- Hermes dependency management: see `pyproject.toml` and workspace `package.json` files.
- GitHub Dependabot documentation: https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts
- See `references/fork-workflow.md` in the bundled `dependabot-security-fix` skill for the exact fork PR command sequence and alert-grouping recipes.
- See `references/daily-vuln-scan-recipe.md` in the bundled `dependabot-security-fix` skill for the read-only multi-repo scanning recipe.
- See `references/weekly-audit-cron-recipe.md` in this skill for the step-by-step Windows/MSYS weekly audit cron recipe (pip-audit JSON parsing, npm workspace scan, Go build verification, code pattern checks, config hardening review).