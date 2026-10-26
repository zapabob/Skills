---
name: llama-cpp-vram-optimization
description: VRAM optimization patterns for llama.cpp/llama-server with long context on consumer GPUs.
version: "1.0"
author: Hermes Agent
license: MIT
platforms: [windows, linux]
tags: [llama.cpp, llama-server, vram, optimization, long-context, gguf]
category: mlops-inference
metadata:
  hermes:
    category: mlops/inference
    tags: [llama.cpp, vram, optimization, long-context]
    related_skills: [local-llm-server, serving-llms-vllm, windows-inference-server]
    config:
      - llama_server_binary_path
      - model_quantization
      - context_length
      - gpu_layers
---

# llama-cpp VRAM Optimization Skill

Optimize llama.cpp/llama-server for maximum throughput on VRAM-constrained GPUs (e.g., RTX 5060 Ti 16GB) with long context (32K–65K tokens).

## When to Use

- Running local LLMs via `llama-server` on Windows/Linux with limited VRAM
- Need 32K–65K context but hitting OOM errors
- Want to balance GPU layers vs. CPU offload for best token/sec

## Prerequisites

- llama.cpp `llama-server` binary (turboquant build or self-compiled with CUDA + Flash Attention)
- GGUF model (IQ3_M, Q4_K_M, Q3_K_M recommended for 16GB VRAM at 65K ctx)
- NVIDIA GPU with 12GB+ VRAM
- `nvidia-smi` for monitoring

## How to Run

### 1. Baseline: Measure Current VRAM

```bash
nvidia-smi
# Note free VRAM before loading model
```

### 2. Start Conservative, Scale Up

**For 65K context on 16GB VRAM with IQ3_M (~15GB model):**

```bash
llama-server.exe \
  -m <model.gguf> \
  -c 65536 \
  -ngl 8 \                    # Start low (8–16 layers on GPU)
  -ctk q4_0 -ctv q4_0 \       # KV cache quantization (critical for 64K)
  -fa on \                    # Flash Attention (saves VRAM, speeds up)
  --no-mmap \                 # Avoid pageouts
  -t 6 -b 2560 -ub 1024 \     # Thread/batch tuning
  --port 8080 --host 127.0.0.1 \
  --jinja \
  --spec-type ngram-simple \  # Speculative decoding (free speedup)
  --spec-ngram-simple-size-n 4 \
  --spec-draft-n-max 4
```

### 3. Find Max `-ngl` Without OOM

Increase `-ngl` by 2–4 until `cudaMalloc failed: out of memory`. Typical sweet spots:

| Model Size | VRAM | Max `-ngl` (65K ctx) | Expected t/s |
|------------|------|---------------------|--------------|
| IQ3_M 35B  | 16GB | 8–12                | 15–21        |
| Q4_K_M 35B | 16GB | 4–8                 | 12–18        |
| Q3_K_M 35B | 16GB | 12–16               | 18–24        |

### 4. Strategy: CPU KV Cache (`--no-kv-offload`)

When the model barely fits in VRAM, place KV cache in **system RAM** instead. This is the highest-throughput config for VRAM-constrained setups because it keeps all model weights on GPU.

```bash
llama-server.exe -m <model.gguf> -c 65536 -ngl 99 --no-kv-offload --flash-attn on
```

- Verified: ~960 tok/s prompt + ~11 t/s generation on RTX 5060 Ti 16GB with 35B IQ3_M
- No VRAM OOM: model (14.2 GB) fully on GPU, KV cache (~1.5–3 GB at 65K) on CPU RAM
- The `common_fit_params` warning (`n_gpu_layers already set by user`) is **non-fatal** when `-ngl` is explicit
- Requires 32 GB+ system RAM
- Effective throughput may be lower than partial offload with quantized KV in VRAM, but enables 65536 ctx where it would otherwise OOM

### 5. Verify Stability

```bash
# Health check
curl http://127.0.0.1:8080/health

# Load test
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"Count to 100."}],"max_tokens":200}'
```

Monitor `nvidia-smi` during generation — VRAM should stay stable.

## TurboQuant KV Cache Types (TurboQuant / zapabob builds)

On TurboQuant-enabled `llama-server` builds, prefer `turbo2`, `turbo3`, or `turbo4` over `q4_0` for long-context KV cache compression. These are runtime KV cache types exposed via `-ctk`/`-ctv`; model weights do not need re-quantization.

- `turbo3` ~3.06 bits/element: aggressive memory savings; suitable for 64K–160K context on 16GB.
- `turbo4` ~4.06 bits/element: closer to FP16 quality with smaller memory savings.
- `q4_0` remains a safe fallback if TurboQuant KV types are unavailable or unstable for a model.

Observed practical pairing on zapabob/llama.cpp: `K=bf16, V=turbo3` is a strong baseline when VRAM permits. On tight 16GB targets, `K=turbo3, V=turbo3` gives the largest memory reduction. Verify with `/v1/models`, one short completion, and `nvidia-smi` VRAM/residency after each change.

**Auto-asymmetric K upgrade (GQA models):** For models with GQA (e.g., Qwen 3.6 35B-A3B, n_head=16, n_head_kv=2, ratio 8:1), llama.cpp auto-upgrades K cache from `turbo3` → `q8_0` to prevent quality degradation. Log shows: `auto-asymmetric: GQA ratio 8:1 — upgrading K from turbo3 to q8_0`. Disable with `TURBO_AUTO_ASYMMETRIC=0` but risks quality loss. This reduces VRAM savings slightly vs. pure `turbo3`/`turbo3`.

## MoE-specific flags for Qwen 3.6 35B-A3B

For Qwen3.6 35B-A3B, add `--moe 35` and `--moe-experts 4` so the runtime activates only 4 experts per token in MoE layers. Without these, llama.cpp may emulate dense behavior and degrade throughput/VRAM efficiency. On RTX 5060 Ti 16GB, these flags materially reduce compute and improve decode speed while keeping quality high.

## Quick Reference

| Flag | Purpose | Typical Value |
|------|---------|---------------|
| `-c` | Context size | `65536` |
| `-ngl` | GPU layers | `8–16` (tune) |
| `-ctk/-ctv` | KV cache type | `q4_0` (64K), `turbo3/turbo4` if build supports it |
| `-fa` | Flash Attention | `on` |
| `--no-mmap` | Disable mmap | Always for long ctx |
| `-t` | CPU threads | `6` (match cores) |
| `-b/-ub` | Batch sizes | `2560/1024` or `2048/512` on tight VRAM |
| `--spec-type` | Speculative | `ngram-mod` |
| `--moe` | Expert count | `35` for Qwen3.6 35B-A3B |
| `--moe-experts` | Active experts | `4` for balanced speed/quality |

## Pitfalls

- **`-ngl 99` on 16GB = guaranteed OOM** for 35B models at 65K ctx. The model alone (~15GB) + KV cache (~3GB) exceeds VRAM.
- **KV cache quantization (`q4_0`) is mandatory for 64K+ context** — f16 KV cache alone adds 3–4GB.
- **Multiple server instances on same port** — kills previous process but may leave GPU memory fragmented. Restart GPU driver or reboot if OOM persists after lowering `-ngl`.
- **Flash Attention `auto` may disable itself** — force `-fa on`.
- **Speculative decoding (`ngram-simple`)** adds ~5–15% throughput with zero extra VRAM. Always enable.
- **`--no-mlock` not supported in turboquant build** — omit it.

## Verification

After stable config found:
1. Run 3 consecutive 200-token generations — all should complete < 30s
2. `nvidia-smi` shows VRAM stable (no creep)
3. Token/sec ≥ 15 for 35B IQ3_M on RTX 5060 Ti 16GB

## References

- `references/65k-context-16gb-vram.md` — Detailed test log for IQ3_M 35B on RTX 5060 Ti
- `references/kv-cache-quantization-guide.md` — Why q4_0 KV saves 3GB at 64K