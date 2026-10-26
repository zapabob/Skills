---
name: llama-server-ctx-manage
description: Manage Llama-server context size for Windows.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes.tags: [llama, server, ctx, mtp, turbo3, vrAM]
---

# Llama-server Context Size Management (Windows)

## When to Use
- Llama-server context size adjustment for RTX 5060 Ti 16GB + 12GB GGUF model setups
- MTP (Speculative Decoding) enablement/disablement
- K/V cache type tuning (q8_0, q4_0, turbo3, f16)
- VRAM optimization and tool-call stability

## Prerequisites
- RTX 5060 Ti 16GB or higher GPU
- llama-turboquant installed at `%USERPROFILE%/AppData/Local/Programs/llama-turboquant/`
- Qwen3.8-27B-abliterated-MTP GGUF model at `%USERPROFILE%/Desktop/SO8T/gguf_models/soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf`
- Windows OS with PowerShell/CLI access

## How to Run

### Start Llama-server with ctx 65536 (stable, verified)
```powershell
/Users/downl/AppData/Local/Programs/llama-turboquant/bin/llama-server.exe `
  --port 8080 `
  --model "%USERPROFILE%/Desktop/SO8T/gguf_models/soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf" `
  -c 65536 `
  -ngl 99 `
  -fa on `
  -ctk q8_0 `
  -ctv turbo3 `
  --spec-type draft-mtp `
  --spec-draft-n-max 3 `
  --spec-draft-n-min 1 `
  --parallel 1 `
  --jinja `
  --no-mmap `
  --alias qwen3.8-27b-abliterated-mtp
```

### Start Llama-server with ctx 131072 (may fail on current filesystem)
```powershell
/Users/downl/AppData/Local/Programs/llama-turboquant/bin/llama-server.exe `
  --port 8080 `
  --model "%USERPROFILE%/Desktop/SO8T/gguf_models/soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf" `
  -c 131072 `
  -ngl 99 `
  -fa on `
  -ctk q8_0 `
  -ctv turbo3 `
  --spec-type draft-mtp `
  --spec-draft-n-max 3 `
  --spec-draft-n-min 1 `
  --parallel 1 `
  --jinja `
  --no-mmap `
  --alias qwen3.8-27b-abliterated-mtp
```

### Check current ctx status
```powershell
curl -s http://127.0.0.1:8080/health
```

### Test inference
```powershell
curl -s -X POST http://127.0.0.1:8080/chat/completions -H "Content-Type: application/json" -d '{"model":"qwen3.8-27b-abliterated-mtp","messages":[{"role":"user","content":"2+2?"}],"max_tokens":16,"temperature":0.1}'
```

## Pitfalls
- ctx 131072: File system constraint on Windows — GGUF files recognized as directories, causing path nesting errors. Not achievable on current RTX 5060 Ti 16GB + 12GB model setup without filesystem changes.
- `--spec-type draft-mtp`: Windows file sharing may cause Permission denied errors. `--no-mmap` + `--parallel 1` mitigates but may not fully resolve.
- ctx > 65534: Extreme VRAM contention — prompt processing drops to ~1 tok/s (seen at ctx 78334).
- `LLAMA_ARG_*` / `LLAMA_TURBOQUANT_*` env vars: Always unset before launch; they override CLI flags.

## Verification
```powershell
# Confirm server running and responsive
curl -s http://127.0.0.1:8080/health

# Confirm ctx 65536 and MTP active
curl -s -X POST http://127.0.0.1:8080/chat/completions -H "Content-Type: application/json" -d '{"model":"qwen3.8-27b-abliterated-mtp","messages":[{"role":"user","content":"2+2?"}],"max_tokens":16,"temperature":0.1}'
```