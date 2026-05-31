---
name: yolo-auto
description: "YOLO (You Only Live Once) full-stack automation skill with OpenClaw MCP bridge and GPU model selection."
short_description: YOLO (You Only Live Once) full-stack automation skill with OpenClaw MCP bridge and GPU model selection.
---

# YOLO Auto Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

YOLO (You Only Live Once) full-stack automation skill with OpenClaw MCP bridge and GPU model selection. Enables autonomous multi-agent orchestration with intelligent task distribution across different GPU models.

## Capabilities

- **GPU Model Selection**: Select optimal GPU model (claude-3-opus, gpt-4, gpu-5.3-codex)
- **Multi-Agent Orchestration**: Coordinate multiple agents for complex tasks
- **OpenClaw Integration**: Use OpenClaw MCP bridge for tool access
- **Task Distribution**: Distribute work across agents intelligently
- **Result Aggregation**: Collect and synthesize results from multiple sources
- **Autonomous Execution**: Execute complex workflows with minimal input

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

### Basic Workflow

### GPU Selection

### Multi-Agent Task

## YOLO Architecture

```
┌─────────────────────────────────────────┐
│           YOLO Orchestrator              │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    │
│  │ GPU Router  │───▶│ Task Queue   │    │
│  └─────────────┘    └─────────────┘    │
│         │                  │            │
│         ▼                  ▼            │
│  ┌─────────────┐    ┌─────────────┐    │
│  │ Agent Pool  │◀───│ Work Stealer │    │
│  │ - claude-3  │    └─────────────┘    │
│  │ - gpt-4     │                        │
│  │ - gpu-5.3   │                        │
│  └─────────────┘                        │
│         │                                │
│         ▼                                │
│  ┌─────────────┐                        │
│  │ Result       │                        │
│  │ Aggregator  │                        │
│  └─────────────┘                        │
└─────────────────────────────────────────┘
```

## GPU Models

| Model         | Strengths                  | Use Cases                |
| ------------- | -------------------------- | ------------------------ |
| claude-3-opus | Complex reasoning, coding  | Architecture, planning   |
| gpt-4         | Fast iteration, creativity | Prototyping, exploration |
| gpu-5.3-codex | Local processing           | Security, privacy tasks  |

## OpenClaw Integration

OpenClaw provides MCP bridge for external tools:

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": ["serve"]
    }
  }
}
```

## Workflow Definition

```yaml
name: full-stack-web
stages:
  - name: frontend
    agents: 2
    gpu: claude-3-opus
    tasks:
      - Create React components
      - Implement state management
  - name: backend
    agents: 2
    gpu: gpt-4
    tasks:
      - Design API schema
      - Implement endpoints
  - name: integration
    agents: 1
    gpu: claude-3-opus
    tasks:
      - Connect frontend to backend
      - Test end-to-end
```

## Output Format

The yolo-auto agent provides:

- Workflow execution reports
- Agent task distributions
- GPU utilization metrics
- Result aggregations
- Performance statistics

- [OpenClaw GitHub](https://github.com/anomalyco/openclaw)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Claude Code](https://claude.com/code)
- [Multi-Agent Systems](https://arxiv.org/abs/2308.02790)

---

$ the skill-install skill https://github.com/zapabob/codex-yolo-auto-skill`
**Version**: 1.0.0
