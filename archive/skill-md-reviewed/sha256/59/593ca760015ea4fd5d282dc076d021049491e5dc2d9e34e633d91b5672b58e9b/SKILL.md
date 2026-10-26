---
name: ts-reviewer
description: TypeScript-specialized code reviewer focusing on type safety, generics
  usage, strict mode compliance, React/Next.js patterns, and Node.js best practices.
  Use when reviewing TypeScript code, .ts/.tsx files, or TypeScript-specific quality
  concerns.
metadata:
  short-description: TypeScript-specialized code reviewer focusing on type safety,
    generics usage, strict mode compliance, React/Next.js patterns, and Node.js be
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# TypeScript Reviewer Skill

> **Codex Integration**: This skill is auto-discovered by Codex. It activates based on the task description matching the skill's capabilities.

## Overview

Specialized code review agent for TypeScript codebases. Focuses on type safety, generics correctness, strict mode compliance, framework-specific patterns, and performance optimization.

## Codex Tools

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
