---
name: code-reviewer
description: Advanced code analysis agent that performs comprehensive code reviews focusing on security, performance, maintainability, and best practices. Generates actionable feedback with severity levels and automated fix suggestions.
short_description: Advanced code analysis agent that performs comprehensive code reviews focusing on security, performance, maintainability, and best practices
---

# Code Reviewer Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Advanced code analysis agent that performs comprehensive code reviews focusing on security, performance, maintainability, and best practices. Generates actionable feedback with severity levels and automated fix suggestions.

## Capabilities

- **Security Analysis**: Vulnerability detection, unsafe patterns, authentication issues
- **Performance Review**: Bottleneck identification, optimization opportunities, resource usage analysis
- **Code Quality**: Maintainability assessment, complexity analysis, duplication detection
- **Best Practices**: Language-specific conventions, framework compliance, testing coverage
- **Type Safety**: Type checking, null safety, generic usage validation

## Cursor Tools

This skill uses the following Cursor-native tools:

| Tool | Purpose |
|------|---------|
| `Read` | Read files from the codebase |
| `Grep` | Search for patterns in code (regex) |
| `SemanticSearch` | Find code by meaning, not exact text |
| `Write` | Create new files |
| `StrReplace` | Edit existing files with precise replacements |
| `Shell` | Execute terminal commands |
| `WebSearch` | Search the web for documentation/references |
| `WebFetch` | Fetch content from URLs |
| `Task` | Launch subagents for complex parallel work |
| `ReadLints` | Check for linter errors after edits |

## Usage Examples

### Basic Code Review

### Comprehensive Analysis

### Language-Specific Review
```bash
the code-reviewer skill "Review Rust code for unsafe patterns, lifetime issues, and performance bottlenecks"
the code-reviewer skill "Review Python code for type hints, error handling, and best practices"
```

### CI/CD Integration

## Output Format

### Review Report Structure
```
## Code Review Summary

### Severity Breakdown
- 🔴 Critical: X issues
- 🟠 High: X issues
- 🟡 Medium: X issues
- 🟢 Low: X issues

### Categories
#### Security Vulnerabilities
- [ISSUE-001] SQL Injection vulnerability in user input handling
  - Location: `src/auth/login.rs:45`
  - Severity: Critical
  - Recommendation: Use parameterized queries

#### Performance Issues
- [ISSUE-002] Inefficient database query in hot path
  - Location: `src/api/user_handler.rs:123`
  - Severity: High
  - Impact: N+1 query problem
  - Fix: Implement batch loading

#### Code Quality
- [ISSUE-003] Missing error handling for file operations
  - Location: `src/utils/file_ops.rs:67`
  - Severity: Medium
  - Recommendation: Add proper error propagation

### Automated Fixes Available
- [FIX-001] Add input sanitization
- [FIX-002] Implement query optimization
- [FIX-003] Add error handling wrapper
```

### JSON Output (for CI/CD)
```json
{
  "summary": {
    "total_issues": 15,
    "critical": 2,
    "high": 4,
    "medium": 6,
    "low": 3,
    "auto_fixable": 8
  },
  "issues": [
    {
      "id": "ISSUE-001",
      "category": "security",
      "severity": "critical",
      "file": "src/auth/login.rs",
      "line": 45,
      "description": "SQL Injection vulnerability",
      "recommendation": "Use parameterized queries",
      "auto_fix_available": true
    }
  ],
  "metrics": {
    "complexity_score": 4.2,
    "test_coverage_estimate": 85,
    "maintainability_index": 72
  }
}
```

## Progressive Disclosure

### Level 1: Quick Scan
Basic syntax, security vulnerabilities, critical issues only.

### Level 2: Standard Review
Full analysis including performance, maintainability, best practices.

### Level 3: Deep Analysis
Advanced patterns, architectural issues, long-term maintainability.

## Configuration

### Review Rules Customization
```json
{
  "rules": {
    "security": {
      "enabled": true,
      "severity_threshold": "medium"
    },
    "performance": {
      "enabled": true,
      "complexity_threshold": 10
    },
    "maintainability": {
      "enabled": true,
      "min_test_coverage": 80
    }
  },
  "languages": ["rust", "python", "typescript"],
  "output_format": "markdown"
}
```

## Integration Points

### GitHub Actions
```yaml
- name: Code Review
  uses: openai/codex-code-review@v1
  with:
    paths: 'src/'
    fail_on: 'critical'
    output_format: 'sarif'
```

### VS Code Extension
```json
{
  "contributes": {
    "commands": [
      {
        "command": "codex.codeReview",
        "title": "Run Code Review"
      }
    ]
  }
}
```

- [OWASP Code Review Guide](https://owasp.org/www-pdf-archive/OWASP_Code_Review_Guide_v2.pdf)
- [Microsoft SDL](https://www.microsoft.com/en-us/security/blog/2019/05/14/sdl-migration/)
- [Rust Security Guidelines](https://rustsec.org/)

---

$ the skill-install skill https://github.com/zapabob/codex-code-reviewer-skill`
**Version**: 2.1.0
