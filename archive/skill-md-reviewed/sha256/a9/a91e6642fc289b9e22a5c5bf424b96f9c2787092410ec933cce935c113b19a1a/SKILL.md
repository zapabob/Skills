---
name: python-reviewer
description: Python code review skill focused on quality, correctness, security, and
  framework best practices.
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# Python Reviewer Skill

## Overview

Performs focused Python reviews for code quality, security, maintainability, and common framework usage (for example Django and FastAPI).

## Capabilities

- Static review for bugs and risky patterns
- Security and input-validation checks
- Python style and maintainability guidance
- Framework-aware recommendations

## Usage

```bash
codex $python-reviewer "Review this Python module for bugs and security issues"
```
