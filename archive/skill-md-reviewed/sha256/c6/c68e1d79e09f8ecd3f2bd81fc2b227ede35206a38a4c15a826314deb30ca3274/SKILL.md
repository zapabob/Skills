---
name: llama-turboquant-kv-optimize
description: Optimize llama-server KV cache with TurboQuant turbo3 on Windows RTX 5060 Ti.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [LLM, TurboQuant, KV-Cache, llama.cpp, VRAM-Optimization]
    category: mlops/inference
---

# llama-turboquant-kv-optimize

Optimize llama-server KV cache quantization using TurboQuant `turbo3` on Windows with NVIDIA RTX 5060 Ti 16GB. Reduces VRAM pressure while maintaining 65K context for MoE models like Qwen3.6-35B-A3B. Does NOT cover draft-model speculative decoding or Linux/macOS paths.

## When to Use

- Running 35B-A3B MoE models on 16GB VRAM with 65K context
- Need ~4GB VRAM headroom for safety margin
- Using zapabob's llama-turboquant build on Windows
- Accept ~10 tok/s generation speed (vs ~40 tok/s with q4_0)

## Prerequisites

- Windows 10/11 with NVIDIA driver 560+
- `llama-turboquant` installed at `%LOCALAPPDATA%\Programs\llama-turboquant\`
- Model file: `Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M.gguf` (or similar IQ3_M)
- Port 8080 free for `llama-server`
- `nvidia-smi` in PATH for VRAM verification

## How to Run

Invoke through the `terminal` tool with the exact commands below. All paths use MSYS-style `/c/...` format.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `taskkill /PID <pid> /F` | Stop existing llama-server |
| `llama-server.exe -m <model> -c 65536 -ngl 28 -fa on -ctk turbo3 -ctv turbo3 --port 8080 --spec-type ngram-simple` | Start with turbo3 KV cache |
| `curl http://127.0.0.1:8080/health` | Health check |
| `nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader,nounits` | Verify VRAM |
| `curl -X POST http://127.0.0.1:8080/completion -d '{"prompt":"...","n_predict":128}'` | Test inference |

## Procedure

1. **Locate installation and model**
   ```bash
   ls -la "/c/Users/$USER/AppData/Local/Programs/llama-turboquant/bin/"
   ls -la "/c/Users/$USER/Desktop/SO8T/gguf_models/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M.gguf"
   ```

2. **Kill any existing llama-server**
   ```bash
   tasklist | findstr llama
   taskkill /PID <pid> /F
   ```

3. **Start llama-server with turbo3 KV cache**
   ```bash
   cd "/c/Users/$USER/AppData/Local/Programs/llama-turboquant/bin"
   ./llama-server.exe \
     -m "/c/Users/$USER/Desktop/SO8T/gguf_models/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M.gguf" \
     -c 65536 \
     -ngl 28 \
     -fa on \
     -ctk turbo3 \
     -ctv turbo3 \
     --port 8080 \
     --spec-type ngram-simple \
     --spec-ngram-simple-size-n 12 \
     --spec-ngram-simple-size-m 48 \
     --spec-ngram-simple-min-hits 1
   ```
   Run in background via `terminal(background=true)`.

4. **Wait for model load** (poll process output until `listening on http://127.0.0.1:8080` appears).

5. **Verify health**
   ```bash
   curl -s http://127.0.0.1:8080/health
   # Expect: {"status":"ok"}
   ```

6. **Check VRAM usage**
   ```bash
   nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader,nounits
   # Target: ~12GB used, ~4GB free
   ```

7. **Test inference speed**
   ```bash
   curl -s http://127.0.0.1:8080/completion \
     -H "Content-Type: application/json" \
     -d '{"prompt":"### Human: Hello\n### Assistant:","n_predict":128,"temperature":0.7,"top_p":0.9,"repeat_penalty":1.1}'
   ```
   Extract `predicted_per_second` from response. Expect 9–13 tok/s.

## Pitfalls

- **Auto-asymmetric K upgrade**: GQA 8:1 forces K cache from `turbo3` → `q8_0` (log warning). Disable with `TURBO_AUTO_ASYMMETRIC=0` but risks quality loss.
- **Model path**: Must use absolute Windows path (`C:\...`) or MSYS `/c/...` — relative paths fail.
- **Benchmark tool**: `llama-bench.exe` cannot load this model (OOM). Use server `/completion` endpoint for throughput.
- **ngl limit**: `-ngl 28` is near max for 16GB. Higher causes OOM during graph allocation.
- **Flash Attention**: Required (`-fa on`) for 65K context on this hardware.

## Verification

Successful run shows:
- `curl /health` → `{"status":"ok"}`
- `nvidia-smi` → VRAM used ≤ 13GB, free ≥ 3GB
- `/completion` → `predicted_per_second` ≥ 8 tok/s
- Process stays alive > 5 minutes without OOM/crash