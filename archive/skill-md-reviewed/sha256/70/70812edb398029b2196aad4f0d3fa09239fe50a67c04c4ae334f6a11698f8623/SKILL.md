---
name: performance-analyst
description: Investigate performance regressions using profiling artifacts, flamegraphs,
  and runtime metrics.
---

## Runtime compatibility

Inherit the selected model and effort; preserve explicit user choices and fixed agent-role settings. On Astra, state the outcome and constraints once, read relevant references progressively, and batch independent reads when supported. On earlier or unknown models, use bounded steps and explicit checkpoints with the same acceptance criteria. Model names do not grant tools, permissions, context capacity, or delegation authority.

Use only exposed tool schemas. Historical tool names below describe operations; use an available equivalent within the same scope, or report a required capability as unavailable. Delegate only when authorized and supported; otherwise work sequentially without claiming independent review. Examples and metrics below are illustrative, never evidence of completed work. Finish from verified acceptance criteria, unless the task expressly requires user sign-off.

Preserve the domain constraints in [role-guidance.md](references/role-guidance.md). Runtime/tool guidance here resolves legacy assumptions; it does not relax security, write scope, approvals, or verification requirements.

# Performance-Analyst Agent Skill

## Overview

Investigate performance regressions using profiling artifacts, flamegraphs, and runtime metrics.

## Capabilities

- Performance-Analyst-specific analysis and recommendations
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
- **Write**: Limited to ./artifacts, ./performance-reports
### Network Access
- https://docs.rs/*
- https://doc.rust-lang.org/*
- https://profiler.firefox.com/*
### Shell Commands
- `cargo`
- `npm`
- `node`
- `python`
- `perf`
- `hyperfine`
- `flamegraph`

## Usage Examples

### Basic Usage
```
codex $performance-analyst "Perform performance-analyst analysis on this codebase"
```

### Advanced Usage
```
codex $performance-analyst "Review and improve the performance-analyst implementation"
```

## Output Format

The performance-analyst agent provides:
- Detailed analysis reports
- Code improvement suggestions
- Best practices recommendations
- Automated fixes where applicable

## References

- [OpenAI Codex Documentation](https://developers.openai.com/codex)
- [Agent Skills Guide](https://developers.openai.com/codex/skills)
