---
name: ts-reviewer
description: TypeScript review skill focused on type safety, API contracts, and runtime
  reliability.
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# TS Reviewer Skill

## Overview

Reviews TypeScript code for type correctness, runtime safety, and maintainable structure.

## Capabilities

- Type safety and strictness checks
- Async/error-flow review
- API contract consistency
- Refactoring and maintainability suggestions

## Usage

```bash
codex $ts-reviewer "Review this TypeScript service for type and runtime issues"
```
