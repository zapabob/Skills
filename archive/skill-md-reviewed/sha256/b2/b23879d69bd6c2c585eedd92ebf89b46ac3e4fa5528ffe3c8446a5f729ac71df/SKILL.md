---
name: find-safer-version
description: Find recommended replacement versions for a dependency ranked by Developer Trust Score. Use when upgrading dependencies or looking for more secure alternatives.
---

# Find safer version

## Trigger

Use when you need to find better, more secure versions of a dependency.

## Required Inputs

- Package identifier (one of):
  - Package name with optional current version
  - PURL format
  - Maven coordinates

## Workflow

1. Parse the dependency identifier from user input or current file context.
2. Convert to PURL format (version is optional for recommendations).
3. Call `getRecommendedComponentVersions` MCP tool.
4. Present top recommendations ranked by Developer Trust Score:
   - Version number
   - Trust Score
   - Security status (vulnerabilities fixed/introduced)
   - Compatibility notes (major/minor/patch change)
5. If user selects a version, offer to update the dependency file.

## Output

- Ranked list of recommended versions
- Comparison with current version (if provided)
- One-click update option

## Example

```
User: Find safer version of spring-core 5.3.20

Response:
## Recommended Versions for spring-core

Current: 5.3.20 (Trust Score: 68)

| Rank | Version | Trust Score | Security | Notes |
|------|---------|-------------|----------|-------|
| 1 | 6.1.4 | 94 | No known CVEs | Major upgrade, Spring 6.x |
| 2 | 5.3.31 | 89 | No known CVEs | Patch upgrade, same major |
| 3 | 6.0.15 | 87 | No known CVEs | Major upgrade |

### Recommendation
For minimal risk: Upgrade to **5.3.31** (same major version)
For best security: Upgrade to **6.1.4** (requires Java 17+)

Would you like me to update your pom.xml?
```
