---
name: ts-reviewer
description: TypeScript-specialized code reviewer focusing on type safety, generics usage, strict mode compliance, React/Next.js patterns, and Node.js best practices. Use when reviewing TypeScript code, .ts/.tsx files, or TypeScript-specific quality concerns.
short_description: TypeScript-specialized code reviewer focusing on type safety, generics usage, strict mode compliance, React/Next.js patterns, and Node.js be
---

# TypeScript Reviewer Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Specialized code review agent for TypeScript codebases. Focuses on type safety, generics correctness, strict mode compliance, framework-specific patterns, and performance optimization.

## Cursor Tools

| Tool | Purpose |
|------|---------|
| `Read` | Read TypeScript source files |
| `Grep` | Search for type patterns, `any` usage, unsafe casts |
| `SemanticSearch` | Find related types, interfaces, and implementations |
| `Shell` | Run `tsc --noEmit`, eslint, tests |
| `ReadLints` | Check TypeScript compiler and linter errors |

## Review Checklist

### Type Safety
- [ ] No unnecessary `any` or `unknown` types
- [ ] Proper use of generics (not over-constrained or too loose)
- [ ] Discriminated unions over type assertions
- [ ] Correct use of `readonly` for immutable data
- [ ] Null checks via strict null checking

### React/Next.js Patterns
- [ ] Props interfaces properly defined
- [ ] Event handler types explicit (not `any`)
- [ ] Hooks dependencies arrays correct
- [ ] Server/Client component boundaries clear
- [ ] Proper use of `Suspense` and error boundaries

### Node.js Patterns
- [ ] Error handling with typed errors
- [ ] Async/await over raw promises
- [ ] Environment variable validation at startup
- [ ] Proper stream handling and cleanup

### Performance
- [ ] No unnecessary re-renders (React.memo, useMemo, useCallback)
- [ ] Efficient type narrowing (avoid runtime overhead)
- [ ] Tree-shaking friendly exports
- [ ] Lazy loading for heavy modules

## Severity Levels

- **Critical**: Type unsafety that could cause runtime errors
- **Warning**: Suboptimal patterns that reduce maintainability
- **Info**: Style suggestions and minor improvements

## Output Format

```markdown
## TypeScript Review: {file}

### Critical
- L{line}: `any` type on public API - use explicit type

### Warning
- L{line}: Missing `readonly` on config object

### Info
- L{line}: Consider using `satisfies` operator for type validation
```
