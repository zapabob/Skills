---
name: local-llm-server
description: Serve local GGUF models with llama.cpp (including turboquant builds) for use with Hermes.
version: 0.1.0
author: Hermes
platforms: [windows, linux]
metadata:
  hermes:
    tags: [LLM, llama.cpp, GGUF, local server, inference]
---

# Local LLM Server (llama.cpp)

Run a local OpenAI-compatible API server using llama.cpp to serve GGUF models for Hermes Agent.

## When to Use

- You want to use a local GGUF model (e.g., Qwen, Llama, etc.) with Hermes instead of relying on remote APIs.
- You have a GGUF model file and want to start an OpenAI-compatible endpoint.
- You need to configure context length, GPU offloading, and other llama.cpp server options.
- You are using a turboquant build of llama.cpp for improved performance/quantization.

## Prerequisites

- A GGUF model file (e.g., model.gguf).
- llama.cpp binary that supports server mode (e.g., llama-turboquant, llama-server from llama.cpp).
- Sufficient VRAM/RAM for the model and context length.
- Port availability (default 8080).

## How to Run

Invoke via the `terminal` tool with a command similar to the example below, adjusting paths and options for your model and hardware.

## HF Model Substitution Preflight

When replacing an existing local GGUF model with an HF repository reference, treat the migration as incomplete until the intended model is actually serving:

1. Confirm the exact repository, quantization tag, and GGUF filename.
2. Check free disk space before downloading. Budget the GGUF size plus temporary/cache overhead; do not start a large download with only marginal free space.
3. Verify the installed llama.cpp/turboquant build's HF repository resolution independently. A `-hf` command may fail during commit resolution and then attempt to load an empty model path.
4. Treat `--model-url` separately from direct model loading. Verify whether it starts router mode and whether the requested model is actually loaded; an HTTP listener alone is not proof.
5. Before changing Hermes configuration, require all three checks:
   - `GET /health` returns OK;
   - `GET /v1/models` lists the intended model;
   - a short `POST /v1/chat/completions` request succeeds.
6. Only after those checks pass should the old model reference be replaced and the dependent Hermes process restarted.
7. If `/health` succeeds while `/v1/models` is empty, report the server as alive but not model-ready and do not call the migration complete.

Session-specific diagnostics are recorded in `references/hf-model-substitution-preflight.md`.

**Verified behavior on RTX 5060 Ti 16GB with turboquant + Qwen3.6-35B-A3B IQ3_M (~14.2 GB):**

**Primary path (full GPU offload, KV cache on CPU):** `-ngl 99 --no-kv-offload --flash-attn on -c 65536`
  - KV cache lives in CPU RAM, leaving maximum VRAM for model weights.
  - The `common_fit_params` warning ("failed to fit params to free device memory: n_gpu_layers already set by user to XX, abort") is **non-fatal** — the model still loads and runs when `-ngl` is explicitly set.
  - Measured: ~960 tok/s prompt processing, ~11 tok/s generation at 65536 ctx.
  - Requires sufficient system RAM (32 GB+ recommended for 35B + 65K KV cache on CPU).
  - Note: `--flash-attn` now requires an explicit value (`on|off|auto`), not a bare flag.

**CPU fallback:** `-ngl 0 --no-mmap -c 65536` → ~8 t/s (CPU-only, no GPU acceleration).

**Speed/context tradeoff:** If context can drop to `32768`, partial GPU offload (`-ngl 32 -sm layer`) can reach ~21 t/s.

## Quick Reference

| Task | Command |
|------|---------|
| Start server (CPU-only, 65536 ctx) | `llama-server -m model.gguf -c 65536 --host 127.0.0.1 --port 8080 -ngl 0 --no-mmap` |
| Start server (full GPU, KV cache on CPU) | `llama-server -m model.gguf -c 65536 --host 127.0.0.1 --port 8080 -ngl 99 --no-kv-offload --flash-attn on` |
| Check health | `curl http://127.0.0.1:8080/health` |
| Test completion | `curl -s ...` (see procedure section) |
| Stop server | `taskkill /f /im llama-server.exe` (Windows) or `kill <pid>` (Linux) |

## Procedure

### 1. Prepare the Model

Ensure you have a GGUF model file. Place it in a convenient location, e.g., `H:\elt_data\hf-cache\models--model-name\model.gguf`.

### 2. Choose Server Binary

Use a llama.cpp build that includes server support. Examples:
- Official llama.cpp `llama-server.exe`
- Turboquant builds (e.g., `llama-turboquant\bin\llama-server.exe`)
- Any binary providing `llama-server` command.

### 3. Determine GPU Layers (`-ngl`)

- Start with a low value (e.g., 10) and increase until VRAM usage is high but not exceeding limits.
- For RTX 5060 Ti 16GB, `-ngl 20` may work for 35B models with context 65536.
- Use `--no-mmap` if you encounter mmap-related allocation issues.
- Monitor VRAM usage via task manager or `nvidia-smi`.

### 4. Set Context Size (`-c`)

Match the context length you intend to use with Hermes. Common values: 65536, 32768, etc.
Set via `-c 65536`.

### 5. Start the Server

Example command for a turboquant build on Windows:

```bash
"%USERPROFILE%/AppData/Local/Programs/llama-turboquant/bin/llama-server" ^
  -m "H:\elt_data\hf-cache\models--HauhauCS--Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M\Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M.gguf" ^
  -c 65536 ^
  --host 127.0.0.1 ^
  --port 8080 ^
  -ngl 20 ^
  --no-mmap
```

Adjust paths and flags as needed.

### 6. Verify Server is Running

Wait a moment for model load, then check:

```bash
curl -s http://127.0.0.1:8080/health
# Expected: {"status":"ok"}
```

### 7. Configure Hermes to Use the Server

**「登録」とデフォルト切替は別作業。** Registering a live `/v1/models` id without flipping Nous/Codex as primary is documented in `hermes-local-model-register` — load it with `skill_view(name='hermes-local-model-register')`. That path writes `custom_providers.0.*` and the matching `fallback_providers.N.model` via `hermes config set` nested keys. Do **not** `patch` `~/.hermes/config.yaml`.

Only if the user explicitly asked to **switch the primary** to the local server:

```bash
hermes config set model.provider custom
hermes config set model.default <backend-model-id>
hermes config set model.base_url http://127.0.0.1:8080/v1
```

Then `/reset` or restart Hermes. Editing a copy of `config.yaml` outside the active Hermes home will not change runtime behavior, and direct edits to the live config file can be blocked by the agent; `hermes config set` is the supported writer.

**Custom provider vs openai provider:** both work for local OpenAI-compatible servers, but `provider: custom` is the verified path when `base_url` points to a non-OpenAI backend. If the Desktop provider/model picker is unavailable, the most common cause is a `moa`/orchestrated provider setup whose runtime readiness probe does not expose a simple curated model list. Switching to `provider: custom` with `base_url: http://127.0.0.1:8080/v1` usually restores picker usability.

### 8. Test with Hermes

Send a simple prompt via Hermes to confirm the model responds.

## Verified: Qwen3.8-27B MTP on RTX 5060 Ti 16GB

Local GGUF `qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf` (arch `qwen35`, `nextn_predict_layers=1`) on `llama-turboquant` `b10264-81b08be15`:

```text
unset LLAMA_ARG_CACHE_TYPE_K LLAMA_ARG_CACHE_TYPE_V
unset LLAMA_TURBOQUANT_CACHE_TYPE_K LLAMA_TURBOQUANT_CACHE_TYPE_V
unset LLAMA_TURBOQUANT_MODE LLAMA_TURBOQUANT_SO8 LLAMA_TURBOQUANT_TRIALITY LLAMA_TURBOQUANT

llama-server -m <this.gguf> --host 127.0.0.1 --port 8080
  -c 65536 -ngl 99 -fa on -ctk q8_0 -ctv turbo3
  --spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-n-min 1
  --jinja --alias qwen3.8-27b-abliterated-mtp --no-mmap -np 1 -t 8 -b 2048 -ub 512
```

- Use `--spec-type draft-mtp` (in-GGUF nextn head). Do not substitute ngram-simple for this file.
- Unset leftover `LLAMA_ARG_*` / `LLAMA_TURBOQUANT_*` so CLI `-ctk q8_0 -ctv turbo3` actually wins.
- Measured 2026-08-18: `/health` ok, `n_ctx=65536`, ~38 tok/s, MTP accept ~70%, VRAM ~15136/16311 MiB (~0.9 GB free).
- `common_fit_params` warning with explicit `-ngl 99` is non-fatal.
- Japanese JSON in git-bash curl can fail UTF-8; write the body to a file and use `--data-binary @file`.

## Turboquant / zapabob build tuning
## Verification

After server is running, run a quick completion test:

```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "local", "messages": [{"role": "user", "content": "Say hello in Japanese."}], "max_tokens": 30}' \
  | jq -r '.choices[0].message.content'
```

Should return a sensible response. If a small `max_tokens` test succeeds but larger generations hang, reduce `-ngl` or lower context; that pattern means the config starts but is unstable under load.

## Pitfalls

- **`--flash-attn` syntax change**: Recent turboquant builds require an explicit value (`--flash-attn on`, `--flash-attn off`, or `--flash-attn auto`). A bare `--flash-attn` without a value is rejected with `error: unknown value for --flash-attn`.
- **MSYS path translation**: When running `llama-server.exe` (native Windows binary) from git-bash, MSYS paths like `/c/Users/...` are NOT recognized. Use full Windows paths (`C:\Users\...`). The binary is a native Windows executable, so it expects native Windows path syntax.
- **Verify proc IDs before trusting performance claims.** Past notes citing a specific PID/speed may be stale or from a different substrate. Use `psutil`, `Get-WmiObject`, `wmic`, `tasklist`, and server-side `/health` before changing config.
- **VRAM OOM / thrash**: `cudaMalloc failed: out of memory` usually means the model + KV cache exceed VRAM. First try `--no-kv-offload` (puts KV cache on CPU RAM) before reducing `-ngl`. If that still fails, reduce `-ngl` or switch to CPU-only (`-ngl 0 --no-mmap`). On 16 GB VRAM with a 14.2 GB IQ3_M model, `-ngl 99 --no-kv-offload --flash-attn on` is verified stable.
- **CPU-Host buffer OOM**: `failed to allocate CUDA_Host buffer` usually means hybrid offloading is asking for more pinned host memory than available; lower `-ngl` or move to CPU-only.
- **KV V protection**: when using quantized KV, prefer keeping KV values in a higher precision type (`-ctv f16`) to preserve attention quality; do not quantize V unless VRAM demands it.
- **Slow Response / timeout under load**: Too few or too many GPU layers may bottleneck. Increase `-ngl` gradually only after a stable completion test passes, not just `/health`.
- **Context Truncation**: Ensure `-c` matches your desired context; otherwise long prompts may be cut.
- **Turboquant tensor split limitation**: On some turboquant builds, `-sm tensor` is not supported and aborts with `llama_params_fit is not implemented for SPLIT_MODE_TENSOR`. If partial offload is desired, use layer-wise offload counts instead, or test tensor split before relying on it.
- **Turboquant KV offload caveat**: `--kv-offload` may exist, but on 16GB VRAM with a 15.4GB IQ3_M model, it can still yield unusable throughput (~1-3 t/s) because the GPU is memory-bound rather than compute-bound.
- **Config path**: On Hermes, only `C:\Users\<user>\.hermes\config.yaml` is authoritative. A repo-local copy will not be read by the running Hermes instance.
- **Config validation gate**: Desktop/model-picker usability depends on backend runtime readiness, not just top-level YAML syntax. If the provider picker is unavailable, check backend mode/runtime rather than retrying unrelated config rewrites.
- **HF repo resolution failure with turboquant**: `llama-server --hf-repo <repo>:<quant>` can fail with `failed to resolve commit for <repo>` and then load an empty model path. That indicates the local runtime cannot resolve/download the GGUF as expected. Verified workaround: download the exact file with `huggingface_hub.hf_hub_download` or an authenticated `curl` to `https://huggingface.co/<repo>/resolve/main/<file>`, then serve the downloaded GGUF directly with `--model <local-path>`. See `references/turboquant-hf-repo-resolution.md`.
- **Windows GGUF file system anomaly / file lock**: On Windows hosts with AV (MsMpEng, Avast), a GGUF file can appear as a **directory** (`Attributes: Directory` in PowerShell) with a nested same-named file inside, or become completely locked (`Permission denied` / error 5 / error 32 from `CreateFileW`). `llama-server --spec-type draft-mtp` loads the model twice and triggers shared-lock collisions that fail the second `gguf_init_from_file`. If the file shows size 0 / directory attribute, check for a nested path (`dir "file.gguf\"`) and use that nested path as `--model`. Fallbacks in priority order: (1) nested-path invocation, (2) `--spec-type none` (no spec), (3) AV exclusion for the model directory, (4) `Remove-Item -Path file.gguf -Recurse -Force` + re-download if the directory entry is truly corrupted. See `references/windows-gguf-filesystem-anomaly.md` for investigation commands and workarounds.
- **Model Loading Time**: Large models can take minutes to load; be patient during startup.
- **Port Conflict / stale assumptions**: If `/health` returns `ERR_CONNECTION_REFUSED`, the server is not running on that port. Re-check with `netstat` before assuming an old instance is alive.
- **Turboquant Specifics**: Some turboquant builds may require additional flags; consult the build's documentation.
- **Stopping Server**: Always terminate the server process when done to free resources; orphan processes can linger.
- **Speculative decoding requires model MTP support**: `--spec-type draft-mtp` requires the GGUF to contain MTP layers (`nextn_predict_layers > 0`). Models without MTP (e.g., Nemotron, non-MTP Qwen3 variants, Llama) fail with `context type MTP requested but model doesn't contain MTP layers` → `failed to create MTP context`. **Fix**: omit `--spec-type` entirely. Do not retry with `--spec-type draft-ngram` unless you have verified the model supports it — ngram draft has its own constraints.
- **Windows env var cleanup requires PowerShell**: `LLAMA_ARG_*` and `LLAMA_TURBOQUANT_*` are process-level Windows env vars. From git-bash, `Remove-Item Env:\LLAMA_ARG_*` is NOT available (it's a PowerShell cmdlet). Either run `powershell -Command "Remove-Item Env:\LLAMA_ARG_* -ErrorAction SilentlyContinue; Remove-Item Env:\LLAMA_TURBOQUANT_* -ErrorAction SilentlyContinue"` before starting the server, or start the server from a fresh PowerShell session where you've cleared them there. Stale env vars silently override CLI `-ctk`/`-ctv` flags.

## Verification

After server is running, run a quick completion test:

```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "local", "messages": [{"role": "user", "content": "Say hello in Japanese."}], "max_tokens": 30}' \
  | jq -r '.choices[0].message.content'
```

Should return a sensible response.

## References

- `references/turboquant-hf-kv-substitution.md` — HTTPS-capability preflight, router-mode false positives, exact local-path verification, and the K=bf16/V=turbo3 profile.
- `references/windows-gguf-filesystem-anomaly.md` — Windows file system anomaly, GGUF recognized as directory, AV file lock collisions, investigation commands, and workarounds.
- `references/nemotron-3.5-lightning-30b-a3b.md` — Nemotron-3.5-Lightning-30B-A3B-Q4_K_M launch recipe: K=turbo4 V=turbo3 cpu-moe, MTP unsupported (omit --spec-type), Windows env cleanup via PowerShell.
- llama.cpp documentation: https://github.com/ggerganov/llama.cpp
- Turboquant builds: https://github.com/zapabob/llama-turboquant (example)