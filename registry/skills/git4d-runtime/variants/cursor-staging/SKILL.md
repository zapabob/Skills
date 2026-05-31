---
name: git4d-runtime
description: "Git4D Runtime Checker - Validate Git for DevOps workflows with CUDA/SSE detection and runtime environment verification."
short_description: Git4D Runtime Checker - Validate Git for DevOps workflows with CUDA/SSE detection and runtime environment verification.
---

# Git4D Runtime Checker Agent Skill

> **Cursor Integration**: This skill is auto-discovered by Cursor. It activates based on the task description matching the skill's capabilities.

## Overview

Git4D Runtime Checker validates Git for DevOps workflows with CUDA/SSE detection and runtime environment verification. Ensures development environments are properly configured for GPU-accelerated development and DevOps operations.

## Capabilities

- **Runtime Detection**: Detect CUDA, SSE, and other runtime capabilities
- **Environment Validation**: Verify development environment setup
- **GPU Verification**: Check GPU availability and configuration
- **Dependency Check**: Validate required dependencies
- **Configuration Audit**: Review Git and system configurations
- **Performance Baseline**: Establish performance benchmarks

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

### Basic Runtime Check

### CUDA Validation

### Full Environment Audit

## Git4D Runtime Architecture

```
┌─────────────────────────────────────────┐
│         Git4D Runtime Checker           │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐     │
│  │ CUDA Detector│───▶│ SSE Detector │     │
│  └─────────────┘    └─────────────┘     │
│         │                  │             │
│         ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐     │
│  │ GPU Checker │    │ CPU Checker │     │
│  └─────────────┘    └─────────────┘     │
│         │                  │             │
│         └─────────┬────────┘             │
│                   ▼                      │
│         ┌─────────────────┐              │
│         │ Runtime Reporter │              │
│         └─────────────────┘              │
└─────────────────────────────────────────┘
```

## Runtime Detection Results

### CUDA Detection

| Capability      | Status | Version | Notes          |
| --------------- | ------ | ------- | -------------- |
| CUDA Available  | ✅/❌  | X.X     | Driver version |
| cuDNN Available | ✅/❌  | X.X     | Deep learning  |
| NVCC Available  | ✅/❌  | X.X     | Compilation    |

### SSE Detection

| Capability | Status | Notes            |
| ---------- | ------ | ---------------- |
| SSE4.2     | ✅/❌  | Modern CPU       |
| AVX        | ✅/❌  | Vector ops       |
| AVX-512    | ✅/❌  | High performance |

### GPU Information

```json
{
  "gpu": {
    "name": "NVIDIA GeForce RTX 4090",
    "memory": "24GB",
    "compute_capability": "8.9",
    "cuda_cores": "16384",
    "driver_version": "535.154"
  }
}
```

## Output Format

The git4d-runtime agent provides:

- Runtime capability report
- GPU information summary
- Configuration recommendations
- Performance baseline metrics
- Validation checklist

- [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
- [cuDNN](https://developer.nvidia.com/cudnn)
- [Git4D Documentation](https://github.com/zapabob/codex-git4d)
- [GPU Computing](https://developer.nvidia.com/gpu-computing)

---

$ the skill-install skill https://github.com/zapabob/codex-git4d-runtime-skill`
**Version**: 1.0.0
