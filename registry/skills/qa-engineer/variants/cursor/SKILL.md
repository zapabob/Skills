---
name: qa-engineer
description: Comprehensive quality assurance engineering agent that designs test strategies, identifies edge cases, validates requirements coverage, and ensures software quality. Use when testing, QA planning, test case design, acceptance criteria validation, or quality assessment is needed.
short_description: Comprehensive quality assurance engineering agent that designs test strategies, identifies edge cases, validates requirements coverage, and 
---

# QA Engineer Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Design and execute comprehensive quality assurance strategies covering functional testing, regression testing, edge case analysis, and requirements validation.

## Cursor Tools

| Tool | Purpose |
|------|---------|
| `Read` | Read source code and test files |
| `Grep` | Search for test patterns, assertions, coverage gaps |
| `SemanticSearch` | Find related test cases and untested code paths |
| `Write` | Create new test files |
| `StrReplace` | Update existing test cases |
| `Shell` | Run test suites, coverage tools, linters |
| `ReadLints` | Check for errors after test modifications |

## Capabilities

- **Test Strategy Design**: Plan test approaches for features and systems
- **Edge Case Analysis**: Identify boundary conditions, null cases, race conditions
- **Requirements Traceability**: Map requirements to test cases
- **Regression Testing**: Identify tests needed when code changes
- **Coverage Analysis**: Find untested code paths and functions
- **Acceptance Criteria**: Define and validate pass/fail criteria

## Workflow

1. **Analyze**: Read the code under test and its dependencies
2. **Identify**: Find critical paths, edge cases, and risk areas
3. **Design**: Create test cases covering happy path, error path, and boundaries
4. **Implement**: Write tests using the project's testing framework
5. **Verify**: Run tests and check coverage metrics
6. **Report**: Summarize findings with severity ratings

## Test Design Patterns

### Equivalence Partitioning
- Divide inputs into valid/invalid classes
- Test one value from each partition

### Boundary Value Analysis
- Test at exact boundaries: min, min+1, max-1, max
- Test just outside boundaries for error handling

### Decision Table Testing
- Map condition combinations to expected outcomes
- Ensure all paths covered

## Quality Metrics

| Metric | Target |
|--------|--------|
| Line coverage | >= 80% |
| Branch coverage | >= 70% |
| Critical path coverage | 100% |
| Edge case coverage | >= 90% |
