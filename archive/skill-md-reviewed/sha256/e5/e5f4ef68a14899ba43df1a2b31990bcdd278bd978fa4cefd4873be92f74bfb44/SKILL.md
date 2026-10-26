---
name: check-dependency
description: Analyze a dependency for vulnerabilities, license issues, and quality metrics using Sonatype Guide. Use when evaluating a specific package before adding it to your project or when investigating a known dependency.
---

# Check dependency

## Trigger

Use when you need to evaluate a specific dependency's security, license, and quality posture.

## Required Inputs

- Package identifier (one of):
  - Package name and version (e.g., `lodash 4.17.21`)
  - PURL format (e.g., `pkg:npm/lodash@4.17.21`)
  - Maven coordinates (e.g., `org.apache.commons:commons-lang3:3.12.0`)

## Workflow

1. Parse the dependency identifier from user input or current file context.
2. Convert to PURL format if needed:
   - npm: `pkg:npm/<name>@<version>`
   - Maven: `pkg:maven/<groupId>/<artifactId>@<version>`
   - PyPI: `pkg:pypi/<name>@<version>`
   - Go: `pkg:golang/<module>@<version>`
3. Call `getComponentVersion` MCP tool with the PURL.
4. Present findings in a structured format:
   - **Security**: Known vulnerabilities (CVEs) with severity
   - **License**: License type and compatibility concerns
   - **Quality**: Maintainability and reliability metrics
   - **Developer Trust Score**: Overall recommendation score
5. If issues found, suggest alternatives using `/find-safer-version`.

## Output

- Component analysis summary
- Risk assessment (Critical/High/Medium/Low/None)
- Actionable recommendations
- Link to detailed Sonatype Guide report

## Example

```
User: Check lodash 4.17.20

Response:
## lodash 4.17.20 Analysis

**Risk Level**: High

### Security
- CVE-2021-23337 (High): Prototype pollution in lodash
- CVE-2020-8203 (High): Prototype pollution via zipObjectDeep

### License
- MIT License - permissive, commercial-friendly

### Quality
- Developer Trust Score: 72/100
- Last updated: 2 years ago

### Recommendation
Upgrade to lodash 4.17.21 which addresses these vulnerabilities.
Run `/find-safer-version lodash` for detailed upgrade options.
```
