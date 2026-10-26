---
name: turboquant-llama-tuning
description: Tune llama-server TurboQuant KV cache on limited NVIDIA GPUs.
version: 0.1.0
author: Hermes
metadata:
  hermes.tags: [MLOps, Windows, llama.cpp, TurboQuant]
---

# Local llama.cpp TurboQuant Tuning

Audit an existing llama-server deployment, profile its GPU/VRAM/context usage, and iterate toward an optimal TurboQuant KV cache configuration on constrained NVIDIA GPUs. Covers zapabob/llama.cpp forks and upstream builds that expose `turbo2/turbo3/turbo4` KV types. Does not cover model quantization or non-CUDA backends.

## When to Use

- "最適設定で llama-server を動かして"
- "TurboQuant 版 llama.cpp の設定を深掘りして"
- "RTX 5060 Ti 16GB で 35B-A3B を安定させたい"
- Reviewing/auditing a running `llama-server` on Windows
- Comparing `q4_0` vs `turbo2/3/4` KV cache under VRAM pressure

## Prerequisites

- `llama-server` installed and on PATH, or known absolute path.
- Model GGUF file placed at a stable path.
- NVIDIA driver + CUDA toolkit available; `nvidia-smi` works.
- Optional: PowerShell for Win32_Process inspection on Windows.
- For deep research: `web_search` and `web_extract` access.

## Quick Reference

| Check | Command / Endpoint |
|------|------------------|
| VRAM snapshot | `nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free --format=csv,noheader` |
| Running llama PID | `netstat -ano \| grep ':8080' \| grep 'LISTENING'` |
| Process cmdline | `powershell "Get-CimInstance Win32_Process -Filter 'ProcessId=<pid>' \| Select-Object CommandLine"` |
| Model list | `curl -s http://127.0.0.1:8080/v1/models` |
| Supported KV types | `<llama-server> --help \| grep -i cache-type` |
| TurboQuant help | `llama-server --help \| grep -iE 'cache-type-k|cache-type-v|turbo|tbq|tq'` |

## Procedure

1. Confirm model existence at canonical paths and HF cache mirror.
2. Check whether a server is already listening, and on which port.
3. Identify the llama-server process ID and read its full command line.
4. Pull `/v1/models` to confirm the loaded model name and `n_ctx`/`n_ctx_train`.
5. Inspect current KV cache flags (`-ctk`, `-ctv`).
6. Run `llama-server --help` to verify this binary exposes TurboQuant types.
7. If types are `turbo2/turbo3/turbo4`, plan an A/B switch from `q4_0` to `turbo3` or `turbo4`.
8. Before changing anything, stop the existing server and relaunch with the new flags.
9. Restart and re-run the same VRAM + `/v1/models` checks.
10. If the new config OOMs or degrades throughput, fall back to the last-stable flag set.
11. Document the final command line and VRAM usage as the canonical config.

## Pitfalls

- TurboQuant KV types are runtime-only; existing GGUF weights do not need re-quantization.
- On zapabob/llama.cpp forks, accepted KV types may be `turbo2/3/4` rather than upstream `tbq3_0/tbq4_0`.
- 16 GB VRAM with a 35B MoE model often leaves < 500 MB headroom; tight batch sizes (`-b 512 -ub 256`) matter more than throughput tuning.
- `--spec-type ngram-mod` can coexist with TurboQuant, but profile both together and separately.
- Context length and KV precision trade off directly; larger context + turbo3 can still OOM if buffers are not narrowed.
- On Windows, `llama-server` may be installed under `%LOCALAPPDATA%\Programs\llama-turboquant\bin\` or vendored in a repo's `build/bin`.

## Verification

Run `nvidia-smi` and `curl -s http://127.0.0.1:8080/v1/models`; confirm:
- `memory.free` is non-zero and stable across a 10-token generation
- The loaded model name matches the target GGUF
- Generation speed is ≥ 40 tok/s on RTX 5060 Ti 16GB for Qwen3.6-35B-A3B IQ3_M
