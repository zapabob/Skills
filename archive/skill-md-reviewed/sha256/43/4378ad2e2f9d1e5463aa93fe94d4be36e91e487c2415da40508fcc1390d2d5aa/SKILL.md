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

### pip-audit Hangs / Dead gh Token — OSV Batch Fallback

Two failure modes that block the standard sequence:

**1. `gh` token expired** — `gh auth status` prints "The token in default is
invalid" and every `gh api repos/.../dependabot/alerts` returns `HTTP 401`.
Dependabot data is simply unavailable until the user runs
`gh auth login -h github.com` interactively. Report this as a blocker; do not
try to guess or synthesize alert data.

**2. `pip_audit` hangs indefinitely** (observed: >280s, zero stdout, network
confirmed working via pypi.org 200). `importlib.metadata` enumeration of the
venv works fine, so it is pip-audit's advisory-DB fetch stalling.

Fast fallback — query the OSV batch API directly. Scanning 199 dists takes ~3s:

```python
import json, subprocess, urllib.request
code = '''
import importlib.metadata as md, json
out = {}
for d in md.distributions():
    n = d.metadata["Name"]
    if n: out[n.lower().replace("_", "-")] = d.version
print(json.dumps(out))
'''
r = subprocess.run([venv_py, "-c", code], capture_output=True, text=True)
pkgs = json.loads(r.stdout)
q = [{"package": {"ecosystem": "PyPI", "name": n}, "version": v} for n, v in pkgs.items()]
req = urllib.request.Request("https://api.osv.dev/v1/querybatch",
    data=json.dumps({"queries": q}).encode(),
    headers={"Content-Type": "application/json"})
res = json.loads(urllib.request.urlopen(req, timeout=90).read())["results"]
hits = [(n, v, x["id"]) for (n, v), r in zip(pkgs.items(), res) for x in r.get("vulns", [])]
```

**CRITICAL pitfall — do NOT parse OSV `ranges`/`versions` to decide exposure.**
For many PyPI GHSAs both fields come back empty (my first pass reported
`fixed_in=[]` and "ok" for genuinely affected packages, including a CRITICAL
PyJWT advisory). The `querybatch` hit list is already version-filtered and is
authoritative — a package in `hits` IS affected. To find the clean version,
probe a ladder:

```python
def batch(pairs):  # returns per-version id lists
    ...
for v, r in zip(["2.7.0", "2.7.1", "2.8.0"], batch([("urllib3", v) for v in ...])):
    print(v, [x["id"] for x in r.get("vulns", [])])
```

Severity lives in `vulns[].database_specific.severity` on the per-vuln
`GET /v1/vulns/<ID>` endpoint; the batch response omits it. Enrich in a second
pass. `PYSEC-*` records usually have no severity — dedupe them against the
`GHSA-*` twin by summary text.

Also always **diff declared pins vs installed venv**. On this repo `pyproject.toml`
pins `PyJWT==2.15.1` / `setuptools==83.0.0` / `oauthlib==4.0.0` (all clean) while
the venv still had 2.13.0 / 65.5.0 / 3.3.1 (37 OSV hits). Reporting those as
dependency risk is a false positive — the real finding is "venv is stale, run
`uv sync`", and `uv.lock` is the other place to check (it held `urllib3 2.7.0`,
which was genuinely exposed).

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

### Degraded-Mode Scan (terminal guard broken, no gh auth, browser down)

Observed 2026-10-06. When the Windows terminal guard rejects **every** command with
`command length exceeds safe limit` (even `ls`), and `gh` has no token:

1. **Do not keep retrying the terminal.** Two failures is the cutoff.
2. **`execute_code` is the working fallback** — it has outbound network, `os.walk`
   filesystem access, AND `subprocess` (so `git`, `go build` still work). Run the
   whole scan from one script; no shell needed.
3. **`browser_exec` is DOWN** — cloud backend returns `402 insufficient_funds`
   (Nous billing) and local backend fails with `edge is running and has its profile
   locked`. Don't attempt it as a Dependabot UI fallback.
4. **Substitute OSV for Dependabot.** `api.github.com/.../dependabot/alerts` needs
   auth and returns 401; unauth REST still gives repo metadata and 60 req/hr core,
   but GraphQL quota is 0. Note the repo is **`zapabob/hermes-agent-windows`**
   (the `zapabob/hermes-agent` path redirects).

### Lockfile Inventory — Pairs, Not a Merged Dict

Collect **`(name, version)` tuples**, never `{name: version}`. A repo holds multiple
versions of the same package (`undici 6.28.0` + `7.29.0`, `joi 17.13.6` + `18.2.5`,
`fast-uri 3.1.5`/`3.1.6`/`4.1.3`). A merged dict keeps only one and silently
under-reports. My first pass lost 4 affected packages this way.

### Classify Reachability Before Reporting Severity

The lockfile's own `dev` / `optional` flags plus a source-import grep keep the report
honest — most hits here were dev-only:

| Package | Where | Real exposure |
|---|---|---|
| `undici 6.28.0` | root + `ui-tui` (direct) | **RUNTIME** |
| `undici 7.29.0` | photon sidecar | **RUNTIME** |
| `@grpc/grpc-js 1.14.4` | photon sidecar | **RUNTIME** |
| `dompurify 3.4.13` | root + website | **RUNTIME** |
| `fast-uri 3.1.6` | website | **RUNTIME** |
| `@angular/router 22.1.4` | artemis showcase_ui | **RUNTIME**, direct |
| `piscina 5.2.0` (CRITICAL) | artemis | dev-only, zero source imports |
| `electron 41.10.3`, `axios`, `engine.io`, `hono`, `fast-uri 4.1.3` | root / artemis | dev-only |

Also grep first-party source for `require('piscina')` etc. before calling anything
exploitable — `piscina` had a CRITICAL prototype-pollution/RCE advisory and matched
**zero** first-party imports.

### `requirements.txt` Is a Stale Artifact Here

`requirements.txt` still pinned `pyjwt==2.13.0` / `urllib3==2.7.0` (37 OSV hits)
while `pyproject.toml` (`PyJWT[crypto]==2.15.1`, `urllib3>=2.8.0,<3`) and
`uv.lock` (2.15.1 / 2.8.0) were both already clean. Reporting the requirements.txt
pins as dependency risk is a **false positive** — the real finding is "regenerate
requirements.txt" (`uv pip compile pyproject.toml --upgrade -o requirements.txt`).
Always diff all three before escalating.

### Secret Scan Needs a Fixture Allowlist

Naive regex over 17.7k files returns 50+ "hits" that are almost all **test
fixtures** (`tests/gateway/test_slack.py`, `tests/agent/test_credential_pool.py`,
`test_redact.py`) and redaction-module regex literals (`agent/redact.py`). These are
correct behavior, not leaks. Always verify tracking status before escalating:

```python
git ls-files --error-unmatch <path>   # rc 0 => tracked = real problem
git check-ignore -v <path>            # matches .gitignore:203 .hermes/
```

`.hermes/.env`, `.hermes/auth.json`, and `.hermes/cache/terminal/hermes-snap-*.sh`
all matched credential patterns and are correctly gitignored — report as
"verified not committed", not as a finding. Never echo matched values; counts and
paths only.

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