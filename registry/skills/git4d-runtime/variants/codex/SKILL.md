---
name: git4d-runtime
description: "Git4D Runtime Checker - Validate Git/CUDA/SSE runtime state and export KAMUI4D-compatible Git graph JSON for Codex/Hermes workflows."
---

# Git4D Runtime Checker Agent Skill

## Overview

Git4D Runtime Checker validates Git for DevOps workflows with CUDA/SSE detection and runtime environment verification. Ensures development environments are properly configured for GPU-accelerated development and DevOps operations.

## Capabilities

- **Runtime Detection**: Detect CUDA, SSE, and other runtime capabilities
- **Environment Validation**: Verify development environment setup
- **GPU Verification**: Check GPU availability and configuration
- **Dependency Check**: Validate required dependencies
- **Configuration Audit**: Review Git and system configurations
- **Performance Baseline**: Establish performance benchmarks
- **KAMUI4D Graph Export**: Export Git commits, parent edges, and touched files as portable `git4d.graph.v1` JSON for KAMUI4D/Hermes/Codex consumers

## Implemented Local Tools

Run the dependency-free checker from any repository:

```bash
python scripts/git4d_runtime_check.py --repo . --out git4d-results/runtime-report.json --graph-out git4d-results/kamui4d-graph.json
```

Outputs:

- `git4d-results/runtime-report.json`: Git, Codex, Hermes, uv, Python, Node, CUDA/NVIDIA, CPU feature hints, worktree state, and timing checks
- `git4d-results/kamui4d-graph.json`: Commit/file graph with 4D coordinates (`x`, `y`, `z`, `t`) for graph-based visualization

Use `--no-write --format json` for dry-run automation.

## Tools Required

### MCP Tools

- `git4d_detect_cuda` - Detect CUDA installation and version
- `git4d_detect_sse` - Detect SSE capabilities
- `git4d_check_gpu` - Check GPU availability
- `git4d_validate_env` - Validate development environment
- `git4d_check_dependencies` - Check required dependencies
- `git4d_audit_config` - Audit Git configurations

### File System Access

- **Read**: Full repository access
- **Write**: `./git4d-results/`, `./artifacts/`, `./reports/`

### Network Access

- **None required** - Local environment checks

### Shell Commands

- `git` - Git operations
- `nvcc` - NVIDIA CUDA compiler
- `python` - Python for detection scripts
- `systeminfo` - System information

## Usage Examples

### Basic Runtime Check

```bash
codex $git4d-runtime "Check runtime environment for GPU development"
```

### CUDA Validation

```bash
codex $git4d-runtime "Validate CUDA installation and GPU availability"
```

### Full Environment Audit

```bash
codex $git4d-runtime "Perform full environment audit for DevOps"
```

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

## References

- [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
- [cuDNN](https://developer.nvidia.com/cudnn)
- [Git4D Documentation](https://github.com/zapabob/codex-git4d)
- [GPU Computing](https://developer.nvidia.com/gpu-computing)

---

**Installation**: `$ codex $skill-install https://github.com/zapabob/codex-git4d-runtime-skill`
**Version**: 1.0.0
**Compatibility**: Codex v2.14.0+
