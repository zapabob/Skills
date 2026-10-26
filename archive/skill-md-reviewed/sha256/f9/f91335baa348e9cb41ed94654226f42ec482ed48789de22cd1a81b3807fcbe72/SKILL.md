---
name: dependency-analyst
description: Perform deep dependency analysis, manifest auditing, and supply-chain
  risk assessment across language ecosystems.
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# Dependency-Analyst Agent Skill

## Overview

Perform deep dependency analysis, manifest auditing, and supply-chain risk assessment across language ecosystems.

## Capabilities

- Dependency-Analyst-specific analysis and recommendations
- Automated code review and improvements
- Best practices enforcement

## Tools Required

### MCP Tools
- `codex_read_file`
- `codex_grep`
- `codex_codebase_search`
- `read_file`
- `grep`
- `codebase_search`
### File System Access
- **Read**: Full codebase access
- **Write**: Limited to ./artifacts, ./dependency-reports
### Network Access
- https://crates.io/*
- https://docs.rs/*
- https://registry.npmjs.org/*
- https://pypi.org/pypi/*
### Shell Commands
- `cargo`
- `npm`
- `pnpm`
- `pip`
- `poetry`
- `uv`
- `jq`

## Usage Examples

### Basic Usage
```
codex $dependency-analyst "Perform dependency-analyst analysis on this codebase"
```

### Advanced Usage
```
codex $dependency-analyst "Review and improve the dependency-analyst implementation"
```

## Output Format

The dependency-analyst agent provides:
- Detailed analysis reports
- Code improvement suggestions
- Best practices recommendations
- Automated fixes where applicable

## References

- [OpenAI Codex Documentation](https://developers.openai.com/codex)
- [Agent Skills Guide](https://developers.openai.com/codex/skills)
