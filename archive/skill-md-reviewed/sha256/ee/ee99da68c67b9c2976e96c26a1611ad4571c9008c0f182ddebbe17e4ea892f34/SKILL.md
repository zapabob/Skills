---
name: pre-commit-audit
description: Run Ruff linting/formatting + Bandit security audit before committing and pushing to main. Encodes the explicit user-requested workflow for code quality gates.
---

# Pre-Commit Audit Workflow

When the user requests code quality checks, security audit, or "Ruff + security before commit/push", execute this sequence.

## Trigger Conditions
- User explicitly asks for Ruff, Bandit, security audit, or pre-commit checks
- User says "エラーを原因を特定してtest Ruffで整えてメインにコミットプッシュ" or equivalent
- User requests "全てセキュリティ監査も実施"

## Required Tools
- `ruff` (lint + auto-fix)
- `bandit` (security scanning)

## Workflow Steps

1. **Install audit tools** (if not present):
   ```bash
   pip install ruff bandit --quiet
   ```

2. **Run Ruff with auto-fix** on changed paths:
   ```bash
   ruff check <path> --fix
   ```
   - Common targets: `gateway/`, `tools/`, `agent/`, or specific files
   - Verify "All checks passed!" before proceeding

3. **Run Bandit security scan**:
   ```bash
   bandit <path> -f json
   ```
   - Review: `SEVERITY.HIGH` and `SEVERITY.MEDIUM` counts
   - Low-severity issues (bare `except: pass`, etc.) are acceptable if confidence is documented

4. **Git hygiene**:
   - Remove any stray files (e.g., `NUL` on Windows)
   - `git status --short` to confirm clean state
   - `git add -A` only after Ruff passes

5. **Commit & push** (user executes):
   ```bash
   git commit -m "<conventional commit message>"
   git push origin main
   ```

## Pitfalls
- Do NOT commit if Ruff reports errors — fix first
- Bandit High/Medium findings require review; do not auto-suppress
- On Windows, `NUL` device file can appear in `git status` — remove it before `git add`

## References
- `references/send_message_tool_audit.md` — example audit output from `tools/send_message_tool.py`
