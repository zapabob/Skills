---
name: dependency-security-fix
description: "Resolve Dependabot / dependency security vulnerabilities across npm, Python (uv), and Go ecosystems in polyglot repos. Covers alert triage, upstream check, per-ecosystem fix, and PR creation."
version: 1.0.0
author: Hermes Agent
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [security, dependencies, dependabot, npm, uv, go, audit]
    category: devops
    related_skills: [github-pr-workflow, ci-cd-and-automation]
---

# Dependency Security Fix Workflow

Resolve Dependabot alerts across multiple ecosystems in a polyglot repository.
Always assess the severity and check upstream first before applying fixes.

## 0. Triage — Check Alerts

```bash
# Count and severity summary
gh api repos/owner/repo/dependabot/alerts --paginate --jq '
  group_by(.dependency.package.ecosystem)[] |
  "\(.[0].dependency.package.ecosystem): \(length) total"
'

# Severity breakdown per ecosystem
gh api repos/owner/repo/dependabot/alerts \
  --paginate --jq 'group_by(.security_severity)[] | "\(.[0].security_severity): \(length)"'
```

### Check Upstream

Before fixing, check if the upstream repository (if this is a fork) has already resolved the issues:

```bash
# Check upstream for recent dependabot merges
git log upstream/main --oneline -30 --author=dependabot -- '*.txt' '*.toml' '*.lock'

# Compare version pins
git show upstream/main:pyproject.toml | grep "python-multipart\|tornado\|starlette\|aiohttp"
```

If upstream already fixed it, sync from upstream instead of re-doing the work.

## 1. npm — JavaScript/TypeScript

### Root project + sub-projects

Find all `package-lock.json` files (excluding `node_modules`, `.omo`, `.specstory`):

```bash
find . -name "package-lock.json" -not -path "*/node_modules/*" \
  -not -path "*/.omo/*" -not -path "*/.specstory/*"
```

### Fix each

```bash
# Root
npm audit fix

# If --force needed (breaking changes in dev deps only), use:
npm audit fix --force

# Each sub-project
cd plugins/platforms/photon/sidecar && npm audit fix && cd -
cd scripts/whatsapp-bridge && npm audit fix && cd -
cd website && npm audit fix && cd -
```

### Transitive deps that block

If `npm audit fix --force` doesn't resolve an issue (e.g. `@photon-ai/whatsapp-business` → `protobufjs`), check whether the intermediate package needs an upstream update. Note as a remaining item — these are usually safe moderate-severity alerts with no exploit path.

### Desktop apps with pnpm

Desktop sub-projects may use pnpm. Check with `ls pnpm-lock.yaml` before assuming npm.

## 2. Python — uv/pip

### uv.lock upgrade

```bash
# Upgrade all dependencies to latest within version constraints
uv lock --upgrade

# Regenerate requirements.txt from pyproject.toml
uv pip compile pyproject.toml --upgrade -o requirements.txt
```

### Key packages to verify after upgrade

| Package | Known CVEs (2025-2026) | Target |
|---------|----------------------|--------|
| python-multipart | CVE-2026-53537/38/39/40 | >=0.0.32 |
| starlette | CVE-2026-48710/54283/48818/48817 | >=1.3.1 |
| aiohttp | CVE-2026-34993(RCE)/34513/34518/34519/34520/34525/47265 | >=3.14.1 |
| tornado | CVE-2026-49855/49853/49854 | >=6.5.7 |
| nltk | CVE-2026-37353 | >3.9.2 |
| cbor2 | CVE-2026-40531 | >=5.6.5 |

## 3. Go — Watchdog / CLI tools

### Update specific vulnerable packages

```bash
cd path/to/go/module
go get -u golang.org/x/crypto@latest
go get -u golang.org/x/net@latest
go get -u golang.org/x/text@latest
go get -u filippo.io/edwards25519@latest
go mod tidy
```

### Build verification

```bash
# Full module build
go build ./...

# If Go runs out of page file on Windows, build individual files:
go build -o /dev/null file1.go file2.go ...
```

### Add build artifacts to .gitignore

If the Go module produces `.exe` files, ensure `.gitignore` has `*.exe`:

```bash
# Check
grep -q '*.exe' .gitignore || echo '*.exe' >> .gitignore
```

## 4. Commit & PR

### Multi-ecosystem changes

Commit all dependency changes together in one `chore(deps):` commit:

```bash
git add package-lock.json apps/desktop/package.json \
       plugins/platforms/photon/sidecar/package*.json \
       scripts/whatsapp-bridge/package-lock.json \
       scripts/windows/watchdog-go/go.mod \
       scripts/windows/watchdog-go/go.sum \
       uv.lock requirements.txt website/package-lock.json \
       .gitignore

git commit -m "chore(deps): fix Dependabot security vulnerabilities across npm/pip/go

Summary bullet points per ecosystem with key version bumps and CVEs fixed.

npm:
- npm audit fix: package-a X.Y -> A.B (CVE-2026-xxxxx)

Python:
- uv lock --upgrade: dep X.Y -> A.B (CVE-2026-xxxxx)

Go (watchdog):
- golang.org/x/crypto X.Y -> A.B (CVE-2026-xxxxx)"
```

### PR creation

```bash
# Create a feature branch from main first if on main
git checkout -b chore/deps-security-YYYYMMDD

# Push
git push -u origin HEAD

# gh PR — use --repo if working from a fork
gh pr create --repo owner/repo \
  --base main \
  --head "$(git branch --show-current)" \
  --title "chore(deps): fix Dependabot security vulnerabilities" \
  --body "..."
```

## 5. Verification

- After push, GitHub shows a Dependabot summary of remaining alerts (refresh takes minutes to hours).
- Remaining alerts are typically transitive deps that need an intermediate package update.
- Run a quick build/test before committing to avoid breaking CI.

## Pitfalls

- **gh pr create "No commits" error**: The remote tracking ref may be stale. Use `--repo owner/repo` explicitly, or `git fetch origin main && git log origin/main..HEAD --oneline` to verify.
- **Windows page file exhaustion**: Go builds with many transitive deps (tsnet, mcu) can hit Windows virtual memory limits. Build individual files instead of the full module.
- **npm --force downgrades**: `npm audit fix --force` can downgrade packages if the fixed version is SemVer-major but older than installed. Review the diff before committing.
- **uv.lock CRLF warnings**: Git bash/LF interop causes harmless warnings on Windows. They don't affect functionality.
- **Sub-projects**: Don't forget sub-project lockfiles (website, plugins, scripts). Dependabot alerts them independently.
- **Transitive protobufjs in photon sidecar**: If `@photon-ai/whatsapp-business` pins an old `protobufjs`, the fix must come from the upstream package maintainer.
