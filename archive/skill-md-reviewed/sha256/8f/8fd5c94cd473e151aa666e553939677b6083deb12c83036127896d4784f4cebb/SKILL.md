---
name: windows-inference-server
description: Deploy and troubleshoot ML inference servers (vLLM, llama.cpp) on Windows with CUDA. Covers community fork wheels, MSYS path translation workarounds, uv cache management across drives, and multi-drive venv setup.
version: "1.0"
author: "Hermes Agent"
license: "MIT"
platforms: ["windows"]
metadata:
  hermes:
    tags: ["windows", "vllm", "inference", "cuda", "ml-serving"]
    category: "mlops"
---

# Windows ML Inference Server Deployment

Guide for running LLM inference servers natively on Windows with CUDA.

## vLLM on Windows

**vLLM does NOT officially support Windows.** Use the community-maintained [SystemPanic/vllm-windows](https://github.com/SystemPanic/vllm-windows) fork for native Windows + CUDA. See [references/windows-deployment.md](references/windows-deployment.md) for step-by-step installation.

## Native llama.cpp First

Before attempting vLLM on Windows, inspect installed native runtimes and reuse a CUDA-enabled `llama-server` when present. On consumer Blackwell GPUs, an installed TurboQuant build may be the most reliable path, while native vLLM often requires a community wheel and tightly matched Python/CUDA/PyTorch versions. Prefer an already installed runtime plus an existing local GGUF over downloading a new model during the same repair session.

For Hermes Agent integrations, keep the model server context at **65536 or higher** when the configured agent context requires it. Validate the actual loaded context from the llama-server log (`n_ctx_slot = 65536` or greater), not just from the launcher argument.

### GPU memory and multimodal projector policy

If a text-only GGUF has an accompanying `mmproj-*.gguf`, do not load the projector unless vision/multimodal input is required. The projector can consume additional VRAM and make an otherwise successful full-GPU load fail. Start with `--n-gpu-layers 99`, then reduce layers only if the model still cannot allocate. Use `--ctx-size 65536`, Flash Attention, and TurboQuant KV types when the installed build supports them.

### Environment contamination

Existing `LLAMA_ARG_*` and TurboQuant environment variables can override or conflict with command-line tuning. For a controlled probe, unset cache/mode variables such as `LLAMA_ARG_CACHE_TYPE_K`, `LLAMA_ARG_CACHE_TYPE_V`, `LLAMA_TURBOQUANT_CACHE_TYPE_K`, `LLAMA_TURBOQUANT_CACHE_TYPE_V`, `LLAMA_TURBOQUANT_MODE`, and related triality/SO8 variables before launching; then pass the intended values explicitly.

### Common Pitfalls

### MSYS Path Translation
When running `uv`/`pip` from git-bash (MSYS), paths like `/h/` get translated to `C:\h\` instead of `H:\`.
- **Fix:** `export MSYS_NO_PATHCONV=1` before running, or use native Windows paths with double backslashes
- **Alternative:** Wrap in `cmd.exe /c "..."`

### uv Cache / Temp Overflow on C:
uv's wheel extraction temp (`C:\Users\<user>\AppData\Local\uv\cache\.tmp*`) fills C: even when the target venv is on another drive.
- **Fix:** Set all three: `TMP`, `TEMP`, `UV_CACHE_DIR` to the same non-C: drive
- Background processes do NOT inherit bash `export` — use cmd.exe for reliable env var propagation

### CUDA_HOME Not Found
Set the environment variable before installing:
```bash
export CUDA_HOME="C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.3"
```

### Python Version Mismatch
SystemPanic vLLM wheels are cp312 (Python 3.12) only. Use `py -3.12 -m venv` to create a 3.12 venv.

## Observed 16GB VRAM ceiling with this build/model

This build/version requires explicit offload and can fail when the requested GPU workload exceeds memory. On this host, `-ngl 99` failed at model load with `cudaMalloc failed: out of memory` while requesting ~14506 MiB, even though `nvidia-smi` showed nominal free VRAM. Do not treat `nvidia-smi` free space as a load guarantee on this runtime; lower `-ngl` until the model loads.

Current local runtime under test:
- `llama-server.exe` build `b10264-81b08be15`
- Model: Qwen3.6-35B-A3B IQ3_M GGUF (~15.4GB)
- Working profile: `-ngl 8`, `-c 65536`, `-ctk q4_0 -ctv q4_0`, `-fa on`, `--no-mmap`, `-t 6 -b 2560 -ub 1024`, `--jinja`, `--spec-type ngram-simple --spec-draft-n-max 4 --spec-draft-n-min 1`
- Endpoint: `http://127.0.0.1:8080`

Known failure modes:
- `-ngl 16` → `CUDA_Host buffer` allocation failure.
- Long generation with the above spec/decode settings can hang under this build; short completion works.
- `--no-mlock` is not supported by this build (`invalid argument`).

KV cache env override pitfall:
Environment variables like `LLAMA_ARG_CACHE_TYPE_K/V` may already be set. The runtime may warn that command-line cache options overwrite env, but the presence of conflicting env can still affect behavior. For deterministic tuning, unset them in the launch environment even when passing CLI cache flags.

## TTS direction: FishStudio/Fish Audio cute female voice

User preference moved to FishStudio/Fish Audio for a cute female Japanese voice. Treat this as the next TTS path to wire into Hermes, ahead of further local voice-engine tuning.

Current `config.yaml` state on this host:
- `tts.provider: fishaudio` is set
- `tts.fishaudio:` block is partially present (keys: `base_url`, `voice`, `model`) — but the plugin reads `tts.fishaudio` OR `tts.fish_audio` (see `core.py` `_fish_config()`). The recognized keys are:
  - `base_url` (default: `https://api.fish.audio`)
  - `voice` / `reference_id` (Fish Audio reference_id of the desired voice)
  - `model` (e.g., `s2.1-pro-free`, `fish-speech`, etc.)
  - `format` / `output_format` (`mp3`, `wav`, `opus`, `pcm`)
  - `speed` (0.5–2.0)
  - `mp3_bitrate` (64, 128, 192)
  - `sample_rate` (optional)
  - `timeout` (default 120s)

**Mandatory wiring order:**
1. Add `FISH_AUDIO_API_KEY` to `.env` only; do not hardcode secrets in `config.yaml`.
2. Ensure `tts.fishaudio` (or `tts.fish_audio`) in `config.yaml` contains at minimum `voice` (reference_id) and `model`.
3. Verify Fish Audio TTS with a direct HTTP call before changing Hermes runtime behavior.
4. If Hermes doesn't read the config keys, call Fish Audio `/v1/tts` directly from a small script and feed the resulting audio path to `text_to_speech` or voice delivery.

See `references/fishaudio-hermes-tts.md` for the exact config shape, voice-selection guidance, and direct-call fallback pattern.

**Session learnings (2026-07-23):**
- Fish Audio plugin (`plugins/fish_audio_tts/`) exists and works: it registers a `TTSProvider` and two tools (`fish_audio_tts_status`, `fish_audio_tts_synthesize`).
- Config keys used by the plugin are `base_url`, `voice`/`reference_id`, `model`, `format`/`output_format`, `speed`, `mp3_bitrate`, `sample_rate`, `timeout`.
- The API key is read from env `FISH_AUDIO_API_KEY` (or `FISH_API_KEY`), **not** from config.yaml.
- Tested: `status_payload()` returns `available: True` and endpoint `https://api.fish.audio/v1/tts`.
- **Blocker:** Fish Audio returns HTTP 402 "Insufficient API credit". The user must add credits at https://fish.audio/app/developers before synthesis works.
- Once credits are added, a direct call like `synthesize_text(text="はくあだよ。", voice="r417e25bd1a4f4084939a135cb1b7c832")` should succeed and return an MP3 path.


### Hermes Desktop model picker / config mismatch on Windows

`C:\Users\<user>\.hermes\config.yaml` is the runtime config. Repo checkouts such as `<repo>\.hermes\config.yaml` are NOT read by the running Desktop app. If provider/model changes appear to have no effect on `/model`, verify the active file and change it there, or use `hermes config set ...` from a terminal. After changing provider/model config, restart Desktop if it was already running; the picker can stay stale until a fresh launch reads the updated config.

For a local OpenAI-compatible `llama-server`, set `model.provider: openai`, `model.base_url: http://127.0.0.1:<port>/v1`, and `model.default` to the backend model id. Also set `model.context_length` to the server-verified context length from `/v1/models`, not the launcher argument.

For an installed CUDA/TurboQuant llama-server and a text GGUF on a 16GB RTX 5060 Ti, start with:

```text
--ctx-size 65536 --n-gpu-layers 99 --flash-attn on
--cache-type-k turbo4 --cache-type-v turbo4
--parallel 1 --batch-size 1024 --ubatch-size 256
--jinja --cont-batching
```

Use `--spec-type ngram-mod` only when the model/runtime supports it; do not assume a model with an MTP head unless its model card confirms MTP. Verify with `/v1/models`, a short `/v1/chat/completions` request, the server log, and `nvidia-smi`. A successful profile should report the requested context in the log and leave enough VRAM headroom for the target workload.

## Current live runtime on this host (verified)

- Binary: `%USERPROFILE%\AppData\Local\Programs\llama-turboquant\bin\llama-server.exe`
- Build: turboquant-enabled CUDA runtime
- Model: `Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M.gguf` (`~15.4GB`)
- Endpoint: `http://127.0.0.1:8080`
- Observed stable flags: `-c 65536 -ngl 28 -fa on --no-mmap -t 8 -np 2 -b 2048 -ub 512 --cache-type-k q4_0 --cache-type-v q4_0 --spec-type ngram-mod --spec-ngram-mod-n-match 24 --spec-ngram-mod-n-min 48 --spec-ngram-mod-n-max 64 --jinja --cont-batching --batch-size 2048 --ubatch-size 512`
- VRAM: RTX 5060 Ti 16GB, ~11.9GB used at rest, ~4.1GB free
- /v1/models reports `n_ctx_train: 262144`, `n_ctx: 32768`; launcher `-c 65536` is the active context target

## 65536-ctx tuning ladder: GPU KV offload + CPU residual

On 16GB VRAM, full f16 KV at 64K is usually too large. Move to KV quantization and explicit cache placement before lowering `-c`:

1) Preferred fast path
```text
-c 65536 -ngl 99 -fa on --no-mmap
--cache-type-k q4_0 --cache-type-v q4_0
--cache-k gpu --cache-v gpu
-t 6 -b 2560 -ub 1024
```
2) If VRAM still too tight, keep model fully offloaded and allow residual CPU work:
```text
-c 65536 -ngl 99 -fa on --no-mmap
--cache-type-k q4_0 --cache-type-v q4_0
--cache-k gpu --cache-v gpu
-t 8 -b 2048 -ub 512
```
3) Fallback: reduce context only after KV/q4 is already enabled:

```text
-c 32768 -ngl 99 -fa on --no-mmap
--cache-type-k q4_0 --cache-type-v q4_0
--cache-k gpu --cache-v gpu
-t 6 -b 2560 -ub 1024
```

**Verification gate:** after every restart, confirm `http://127.0.0.1:8080/v1/models`, one short completion, the server log `n_ctx_slot`, and `nvidia-smi` VRAM/residency. A claimed speed figure is not evidence; measurable throughput and log-reported context are.

## Quick Reference

```bash
# Multi-drive venv + install pattern
export MSYS_NO_PATHCONV=1
export UV_CACHE_DIR="D:\\uv_cache"
export TMP="D:\\tmp"
export TEMP="D:\\tmp"
export CUDA_HOME="C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.3"
py -3.12 -m venv D:\llm-env
uv pip install torch==2.11.0+cu130 --index-url https://download.pytorch.org/whl/cu130 --python "D:\\llm-env\\Scripts\\python.exe"
```
