---
name: audit-dependencies
description: Comprehensive security audit of all project dependencies. Scans package manifests and reports vulnerabilities, license issues, and quality concerns prioritized by severity.
---

# Audit dependencies

## Trigger

Use when you need a full security audit of your project's dependencies.

## Supported File Types

- `package.json` (npm/Node.js)
- `pom.xml` (Maven/Java)
- `build.gradle` / `build.gradle.kts` (Gradle/Java)
- `requirements.txt` / `pyproject.toml` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `Gemfile` (Ruby)

## Workflow

1. Detect dependency file(s) in the current project.
2. Parse all dependencies with their versions.
3. Convert each to PURL format.
4. Batch check via `getComponentVersion` (max 20 per call).
5. Aggregate and prioritize findings:
   - **Critical**: Actively exploited vulnerabilities
   - **High**: Severe vulnerabilities or license violations
   - **Medium**: Moderate security or quality issues
   - **Low**: Minor concerns or outdated packages
6. Generate summary report with actionable recommendations.

## Output

- Executive summary (total dependencies, issues by severity)
- Detailed findings table
- Prioritized remediation plan
- Export option (markdown, JSON, SARIF)

## Example

```
User: Audit my dependencies

Response:
## Dependency Audit Report

**Project**: my-app
**Scanned**: package.json (47 dependencies)
**Scan Date**: 2024-01-15

### Summary
| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 5 |
| Medium | 8 |
| Low | 12 |
| Clean | 20 |

### Critical Issues (Fix Immediately)

1. **log4j-core 2.14.0**
   - CVE-2021-44228 (Log4Shell) - Remote Code Execution
   - Action: Upgrade to 2.21.0

2. **lodash 4.17.19**
   - CVE-2021-23337 - Prototype Pollution
   - Action: Upgrade to 4.17.21

### High Priority Issues
[...]

### Remediation Plan
1. Run: `npm update lodash`
2. Update pom.xml: log4j-core 2.14.0 -> 2.21.0
[...]

Would you like me to apply these fixes?
```

## Guardrails

- Limit batch size to 20 dependencies per API call
- Cache results for repeated audits in same session
- Skip devDependencies by default (configurable)
- Respect .gitignore and lockfile patterns
