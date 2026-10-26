---
name: llama-server-turboquant-workflow
description: Start TurboQuant llama-server with GGUF model on Windows.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [LLM, llama.cpp, TurboQuant, GGUF, Windows]
---


# llama-server TurboQuant workflow skill

## When to Use
- You want to start a local llama-server with a TurboQuant-built binary and a GGUF model.
- You need to verify the model loads correctly and basic inference works.
- You are troubleshooting encoding issues with Japanese text in curl commands.

## Prerequisites
- TurboQuant llama.cpp binary installed (e.g., `C:\Users\<user>\AppData\Local\Programs\llama-turboquant\bin\llama-server.exe`).
- A GGUF model file path (e.g., `%USERPROFILE%\Desktop\SO8T\gguf_models\soyaakinohara\qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf\qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf`).
- PowerShell access for environment variable cleanup.

## How to Run
### 1. Kill any existing llama-server process
```powershell
taskkill //F //IM llama-server.exe
```
or via Windows Management:
```powershell
wmic process where "name='llama-server.exe'" call terminate()
```

### 2. Clear stale LLAMA_* environment variables (PowerShell)
```powershell
$env:LLAMA_ARG_CACHE_TYPE_K=''
$env:LLAMA_ARG_CACHE_TYPE_V=''
$env:LLAMA_TURBOQUANT_CACHE_TYPE_K=''
$env:LLAMA_TURBOQUANT_CACHE_TYPE_V=''
$env:LLAMA_TURBOQUANT_MODE=''
$env:LLAMA_TURBOQUANT_SO8=''
$env:LLAMA_TURBOQUANT_TRIALITY=''
$env:LLAMA_TURBOQUANT=''
```

### 3. Start the TurboQuant llama-server with your model
```powershell
& "%USERPROFILE%\AppData\Local\Programs\llama-turboquant\bin\llama-server.exe" `
  -m "%USERPROFILE%\Desktop\SO8T\gguf_models\soyaakinohara\qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf\qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf" `
  --host 127.0.0.1 `
  --port 8080 `
  -c 131072 `
  -ngl 99 `
  --flash-attn on `
  -ctk q8_0 `
  -ctv turbo3 `
  --spec-type draft-mtp `
  --spec-draft-n-max 3 `
  --spec-draft-n-min 1 `
  --jinja `
  --alias qwen3.8-27b-abliterated-mtp `
  --no-mmap `
  -np 1 `
  -t 8 `
  -b 2048 `
  -ub 512
```
> The model load takes time; watch for `load_model` log lines. The `common_fit_params` warning about `n_gpu_layers already set` is non-fatal when `-ngl 99` is explicit.

### 4. Verify server is healthy
```bash
curl -sS --max-time 10 http://127.0.0.1:8080/health
```
Expected: `{"status":"ok"}`

### 5. Test a minimal inference request (ASCII only via curl)
```bash
curl -sS --max-time 30 -X POST http://127.0.0.1:8080/v1/chat/completions -d '{"model":"local","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}'
```
Expected: JSON with `choices[0].message.content` and token counts. If Japanese text fails, use a file to avoid encoding issues:
```bash
curl -sS --max-time 30 -X POST http://127.0.0.1:8080/v1/chat/completions -H "Content-Type: application/json" --data-binary @C:/tmp/payload.json
```

## Pitfalls
- **Environment variable conflict**: Stale `LLAMA_ARG_*` / `LLAMA_TURBOQUANT_*` vars override CLI flags. Always clear them first (PowerShell `Remove-Item Env:\*` or the `$env:x=''` pattern).
- **`--flash-attn` syntax**: Recent turboquant builds require an explicit value (`--flash-attn on|off|auto`). A bare flag is rejected.
- **MSYS path translation**: When running the native Windows binary from git-bash, use full Windows paths (`C:\...`) not MSYS paths (`/c/Users/...`).
- **Japanese JSON encoding**: git-bash `curl` may fail with Japanese text in JSON. Write the payload to a file (`echo ... > C:/tmp/payload.json`) and use `--data-binary @C:/tmp/payload.json` to avoid corruption.
- **Model loading time**: Large GGUF models need dozens of seconds to load; do not mistake the initial timeout for a crash.
- **VRAM OOM**: If `cudaMalloc failed: out of memory` appears, try `--no-kv-offload` (puts KV cache on CPU) or reduce `-ngl`.

## Verification
Run the health check and a minimal curl request as in steps 4–5 above. Success is confirmed when:
- `/health` returns `{"status":"ok"}`
- `/v1/chat/completions` returns a 200 response with `model`, `choices`, and token usage fields.