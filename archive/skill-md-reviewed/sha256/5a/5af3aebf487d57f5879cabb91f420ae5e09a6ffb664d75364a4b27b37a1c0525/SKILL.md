# Llama-server GGUF Setup Skill

## When to Use

Use when starting a Llama-turboquant or llama.cpp server with a GGUF model file. This skill covers:

- Correct model path specification (avoiding directory/vs-file recognition issues on Windows)
- K/V cache type selection (`-ctk` for K, `-ctv` for V)
- Speculative decoding (MTP/draft) configuration
- Context length (`-c`) and parallelism (`--parallel`)
- VRAM optimization flags (`-fa`, `--no-mmap`)
- Alias assignment for model routing

## Triggers

- "Start Llama-server with GGUF model"
- "Set up llama-server"
- "Start inference server"
- "Run model with MTP"
- "Configure cache types q8_0 turbo3"

## Pitfalls & Workarounds

### 1. File System Recognition Issue (Windows)

**Problem**: GGUF files may be recognized as directories on Windows, causing path errors like `failed to open GGUF file '...' (No such file or directory)` or `Permission denied`.

**Root cause**: Windows file system cache or antivirus (Avast) may intercept GGUF file handling, causing the OS to treat the `.gguf` extension as a directory.

**Fix**:

- Verify the file exists and is not a directory: `dir /a "-d" "path\to\file.gguf"`
- If the parent folder is a directory containing the file, use the nested path: `.../folder_name/file.gguf`
- Place the `.gguf` file directly in a non-directory folder, or use `--no-mmap` flag
- Run `chkdsk` on the drive if file system corruption is suspected

**Example**:

```bash
# Correct: file directly in folder
"%USERPROFILE%/Desktop/SO8T/gguf_models/soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf"

# Avoid: folder recognized as directory causing nesting
"%USERPROFILE%/Desktop/SO8T/gguf_models/soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf"
```

### 2. ctx 131072 vs 65536

**Constraint**: ctx 131072 may fail due to file system/ RAM constraints. ctx 65536 is the stable default on RTX 5060 Ti 16GB + 12GB model setups.

**Fix**: Use `-c 65536` for stable operation. If 131072 is required, ensure adequate VRAM and no file system anomalies.

### 3. MTP (Speculative Decoding) File Locking

**Problem**: `--spec-type draft-mtp` may fail with `[spec] failed to measure MTP context memory` on Windows due to file sharing conflicts.

**Fix**:

- Always pair with `--no-mmap`
- Use `--parallel 1`
- If MTP continues to fail, disable with `--spec-type` omitted

### 4. Cache Type Mismatch

**Problem**: `-ctk q4_0 -ctv f16` may not provide optimal VRAM/quality balance.

**Recommended**: `-ctk q8_0 -ctv turbo3` for quality/VRAM balance on RTX 5060 Ti 16GB.

### 5. --parallel 1 for tool-call Stability

**Problem**: With `-c 65536` and default `n_slots 4`, tool-call throughput collapses to 6.7 tok/s due to KV cache spill.

**Fix**: `--parallel 1` maintains `n_ctx_slot=65536` and recovers ~37 tok/s with tool-call 3.3 s / 往復.

## Startup Command Template

```bash
/Users/downl/AppData/Local/Programs/llama-turboquant/bin/llama-server.exe \
  --port 8080 \
  --model "%USERPROFILE%/Desktop/SO8T/gguf_models/soyaakinohara/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf/qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf" \
  -c 65536 \
  -ngl 99 \
  -fa on \
  -ctk q8_0 \
  -ctv turbo3 \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  --spec-draft-n-min 1 \
  --parallel 1 \
  --jinja \
  --no-mmap \
  --alias qwen3.8-27b-abliterated-mtp
```

## Verification

After startup, confirm:

1. `curl http://127.0.0.1:8080/health` returns `{}` or `{"status":"ok"}`
2. `curl -s -X POST http://127.0.0.1:8080/chat/completions -H "Content-Type: application/json" -d '{"model":"qwen3.8-27b-abliterated-mtp","messages":[{"role":"user","content":"2+2?"}],"max_tokens":16,"temperature":0.1}'` returns `4`
3. VRAM usage ~15xxx/16311 MiB (memory-context reference)

## Support Files

Recommended support files for this skill:

- `references/gguf-path-troubleshooting.md` — Detailed path resolution steps
- `templates/llama-server-start.bat` — Windows batch file template
- `scripts/verify_llama_server.py` — Health check and inference verification script

## Related Skills

- `omh-model-setup` — Hermes model provider configuration (different domain)
- `hyperframes-install` — HyperFrames video generation setup
- `lm-twitterer-post` — X posting with configured model

---
*Skill auto-generated from session 2026-08-19 Llama-server GGUF setup troubleshooting*