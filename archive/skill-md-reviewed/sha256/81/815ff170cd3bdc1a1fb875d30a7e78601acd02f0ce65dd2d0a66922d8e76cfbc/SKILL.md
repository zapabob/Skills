---
name: milspec-gatekeeper
description: milspec-gatekeeper skill
short_description: milspec-gatekeeper skill
---

# MILSPEC Gatekeeper Skill

**Name**: milspec-gatekeeper
**Description**: 変更前後でMILSPEC品質ゲートを自動実行し、違反時は修正提案まで返す。

## When to Use

Use this skill when you:
- Encounter keywords: `MILSPEC`, `quality gate`, `品質ゲート`, `監査`, `auditability`, `traceability`, `pre-commit`, `CI`, `再現性`, `fail-closed`
- Want to run quality checks before committing or pushing
- Need to verify MILSPEC compliance of new code
- Want to understand what quality gates are failing and why

## What This Skill Does

1. **Runs the full MILSPEC quality gate suite** in the correct order
2. **Reports failures with actionable fixes** — not just raw error output
3. **Checks requirements traceability** via `tests/test_milspec_requirements_trace.py`
4. **Validates MILSPEC 5 principles** in modified files

## Gate Execution Order

Run these commands in sequence (fail-fast on blocking errors):

```powershell
# Stage 1: Lint + Import Order (auto-fix available)
py -3 -m ruff check shinka/ shinka_osint/ shinka_mcp_server.py shinka_mcp_skill_hub.py --fix

# Stage 2: Format Check
py -3 -m black --check shinka/ shinka_osint/ shinka_mcp_server.py shinka_mcp_skill_hub.py

# Stage 3: Requirements Traceability Tests (fast, no external deps)
py -3 -m pytest tests/test_milspec_requirements_trace.py -v --no-cov

# Stage 4: Full Test Suite + Coverage Gate
py -3 -m pytest tests/ -q --cov --cov-fail-under=75

# Stage 5: Secret Scan
py -3 -m detect_secrets scan --baseline .secrets.baseline

# Stage 6: Security Analysis (core paths only)
py -3 -m bandit -c pyproject.toml -r shinka_osint/ shinka_mcp_server.py shinka_mcp_skill_hub.py -q

# Stage 7: Dependency Vulnerability
py -3 -m pip_audit --skip-editable
```

## Common Violations and Fixes

| Violation | Error Code | Fix |
|-----------|------------|-----|
| Bare `except: pass` | E722 | Replace with `except (SpecificError,) as exc: logger.error(...)` |
| Missing `sha256` in EvidenceBlock | REQ-EVID-001 | Add `sha256: str` field to the dataclass |
| `print()` in wrap_eval | REQ-REPRO-003 | Replace with `logger.info()` |
| No `random.seed()` | REQ-REPRO-001 | Add seed handling in `run_experiment` |
| Missing `status` field | REQ-FAIL-003 | Add `status="ok"/"failed"` to return dict |
| Unsorted imports | I001 | Run `ruff check --fix` |
| Unused import | F401 | Remove the import |

## MILSPEC 5 Principles Quick Reference

```
Evidence-first:   sha256 + source_url + access_date on ALL citations
Traceable:        report_id + RunManifest + AuditLogger + ToolCallLogger
Reproducible:     seed → random.seed() + numpy.random.seed() + reproducibility.json
Governable:       CorpusManager allowlist + prohibited topic detection + EvidenceStore SHA-256
Auditable:        hash-chained AuditLogger + _save_artifacts() + _run_subprocess() with error_type
Fail-closed:      fabricated citations → score=0, no bare except, run_experiment never raises
```

## Files Reference

- Quality gate config: `pyproject.toml`, `pyrightconfig.json`, `.pre-commit-config.yaml`
- CI: `.github/workflows/quality-gates.yml`, `.github/workflows/milspec-repo-audit.yml`
- Requirements trace: `tests/test_milspec_requirements_trace.py`, `_docs/requirements_trace.md`
- Cursor rules: `.cursor/rules/milspec-quality-gates.mdc`, `.cursor/rules/python-milspec-secure-coding.mdc`