---
name: irodori-tts-windows-startup
description: Start Irodori-TTS server on Windows with CPU fallback.
version: 0.1.0
author: Hermes Agent
platforms: [windows]
metadata:
  hermes:
    tags: [irodori, tts, startup, windows, cpu]
    category: mlops
---

# Irodori-TTS Windows Startup

Start the Irodori-TTS server (`irodori_openai_tts`) on a Windows host where the venv's torch has no CUDA support. Covers the GPU crash workaround (SIGSEGV), preload avoidance, and health verification.

## When to Use

- "irodoriTTSが起動しない"
- "Irodori-TTS server crashes with SIGSEGV"
- "irodoriTTSを起動して"
- Before any workflow that depends on irodoriTTS (VRChat daily post, Hakua voice synthesis, etc.)

## Prerequisites

- Irodori-TTS server checkout at `%USERPROFILE%\Documents\New project\irodori-tts-server`
- Python venv at `.venv\Scripts\python.exe` inside the server directory
- Port 8088 free (or custom via `--port`)

## Quick Reference

```bash
cd %USERPROFILE%\Documents\New project\irodori-tts-server
set IRODORI_MODEL_DEVICE=cpu
set IRODORI_CODEC_DEVICE=cpu
set IRODORI_PRELOAD=false
set HF_HUB_ENABLE_HF_TRANSFER=0
.venv\Scripts\python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
```

## Procedure: GPU (CUDA) Startup — Primary

Use this when the venv has CUDA torch installed (torch +cu128). This is the preferred path for RTX 5060 Ti (Blackwell) and other GPUs.

1. **Ensure CUDA torch is present.** The project's `pyproject.toml` defines a `cu128` extra. Sync it:
   ```bash
   cd /c/Users/downl/Documents/New\ project/irodori-tts-server
   export HF_HUB_ENABLE_HF_TRANSFER=0
   uv sync --extra cu128
   ```
   **Disk space note:** torch cu128 is ~2.7 GB download + extraction. uv cache lives on C:\. If C: is full (this machine: 99% used / 14 GB free), extraction fails with "ディスクに十分な空き領域がありません (os error 112)". Workaround: free space on C:, or set `UV_CACHE_DIR=D:\uv-cache` (or E:) before `uv sync`.

2. **Verify torch sees CUDA:**
   ```bash
   .venv/Scripts/python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
   ```
   Expected: `2.10.0+cu128 True NVIDIA GeForce RTX 5060 Ti`

3. **Configure devices for GPU.** The `.env` has `IRODORI_MODEL_DEVICE=auto` which is correct for GPU — it will pick CUDA. Explicitly set:
   ```bash
   export IRODORI_MODEL_DEVICE=cuda
   export IRODORI_CODEC_DEVICE=cuda
   export IRODORI_PRELOAD=false
   export HF_HUB_ENABLE_HF_TRANSFER=0
   ```
   Use `IRODORI_PRELOAD=false` to load lazily on first request (avoids startup OOM).

4. **Start the server:**
   ```bash
   cd /c/Users/downl/Documents/New\ project/irodori-tts-server
   export IRODORI_MODEL_DEVICE=cuda IRODORI_CODEC_DEVICE=cuda IRODORI_PRELOAD=false HF_HUB_ENABLE_HF_TRANSFER=0
   .venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
   ```

5. **Verify health:**
   ```bash
   curl http://127.0.0.1:8088/health
   ```
   Expected: `"model_device": "cuda", "codec_device": "cuda"`

---

## Procedure: CPU Fallback (current venv, no CUDA torch)

Use when CUDA torch cannot be installed (disk full, SIGSEGV on GPU, etc.).

1. **Verify the venv.** Check that `.venv/Scripts/python.exe` exists and has the `irodori_openai_tts` module.

2. **Override device and preload.** The venv's torch is CPU-only. The server's `.env` file sets `IRODORI_MODEL_DEVICE=auto` which resolves to CUDA and crashes with exit code 139 (SIGSEGV). Set these env vars:
   - `IRODORI_MODEL_DEVICE=cpu` — force model to CPU
   - `IRODORI_CODEC_DEVICE=cpu` — force codec to CPU
   - `IRODORI_PRELOAD=false` — skip model loading at startup (load happens on first synthesis)
   - `HF_HUB_ENABLE_HF_TRANSFER=0` — avoid hf_transfer download errors

3. **Start the server.** Run from the server directory using the venv Python:
   ```bash
   cd /c/Users/downl/Documents/New\ project/irodori-tts-server
   export IRODORI_MODEL_DEVICE=cpu IRODORI_CODEC_DEVICE=cpu IRODORI_PRELOAD=false
   export HF_HUB_ENABLE_HF_TRANSFER=0
   .venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
   ```
   Or in Windows PowerShell:
   ```powershell
   cd %USERPROFILE%\Documents\New project\irodori-tts-server
   $env:IRODORI_MODEL_DEVICE="cpu"
   $env:IRODORI_CODEC_DEVICE="cpu"
   $env:IRODORI_PRELOAD="false"
   $env:HF_HUB_ENABLE_HF_TRANSFER="0"
   .\.venv\Scripts\python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088
   ```

4. **Verify health.** After startup, check the health endpoint:
   ```bash
   curl http://127.0.0.1:8088/health
   ```
   Expected: `{"status":"ok","runtime":{"preload":false,"loaded":false,...}}`

5. **First synthesis.** The first TTS request triggers model loading. This takes 5-20 seconds on CPU. Subsequent requests are fast (model stays in memory).

## Pitfalls

- **SIGSEGV on startup:** If the server exits with code 139, it tried to use CUDA on a CPU-only torch. Always set `IRODORI_MODEL_DEVICE=cpu IRODORI_CODEC_DEVICE=cpu` for CPU fallback, or ensure CUDA torch is installed for GPU mode.
- **Preload crash:** With `IRODORI_PRELOAD=true` (the default in `.env`), the model loads at startup and crashes. Set to `false` and let it load lazily.
- **hf_transfer error:** If you see "Error while downloading using hf_transfer", set `HF_HUB_ENABLE_HF_TRANSFER=0`.
- **Duplicate .env override:** The `.env` file has `IRODORI_MODEL_DEVICE=auto` and `IRODORI_PRELOAD=true`. Env vars you export override `.env` values at process level but the `.env` is read by pydantic-settings. Exporting before launch works; changing the `.env` file would also work but is not recommended since Docker may need auto mode.
- **Non-interactive shell rejects `export`:** When Hermes launches background processes in non-interactive bash (Windows/MSYS), `export VAR=val` can fail with `bash: no job control in this shell`. Use inline `env VAR=val command` instead, or set the env in PowerShell with `$env:VAR="val"`.
- **Port in use:** Default is 8088. Check with `curl http://127.0.0.1:8088/health` first. Use `--port <other>` to change.
- **Model download on first run:** On first startup, the server downloads `Aratako/Irodori-TTS-500M-v3` (~500MB) and `Aratako/Semantic-DACVAE-Japanese-32dim` from HuggingFace Hub. Takes ~3 minutes on a typical connection. Cached for subsequent runs.
- **Inlining non-ASCII JSON in `curl -d` fails under MSYS/git-bash/PowerShell:** A request like `curl -X POST ... -d '{"input":"こんにちは",...}'` returns `{"detail":"There was an error parsing the body"}` because the multibyte UTF-8 text is corrupted in transit. Always write the payload to a utf-8 temp file (e.g. `cat > _req.json <<'JSON' ... JSON`) and POST with `--data-binary @_req.json`. This is the single most common papercut when scripting irodoriTTS synthesis from the Hermes terminal on Windows. A ready-made reusable tool that does this correctly (plus `ffplay` playback) lives at `references/hakua-voice-chat-tool.md`.
- **Native curl.exe cannot read MSYS `/tmp` paths:** curl on Windows is a native exe, so `--data-binary @/tmp/payload.json` fails with `error encountered when reading a file` (exit 26) even though bash sees the file — MSYS virtual paths are invisible to the native binary. Write the payload to a real Windows path (repo cwd or `$TEMP`), or convert with `WP=$(cygpath -w /tmp/payload.json)` and use `--data-binary @"$WP"`. Same for `-o /tmp/out.wav`: it silently writes nothing; use `$(cygpath -w ...)` or a relative path.
- **Disk full on C: prevents uv sync --extra cu128:** torch cu128 is ~2.7 GB download. uv cache defaults to `C:\Users\<user>\AppData\Local\uv\cache`. If C: is near capacity (this machine: 14 GB free / 930 GB used), extraction fails with "ディスクに十分な空き領域がありません (os error 112)" or CRC errors (os error 23). Workaround: `mkdir D:\uv-cache && set UV_CACHE_DIR=D:\uv-cache` before `uv sync --extra cu128`, or free space on C:.
- **CRC error during torch download:** Network glitches can corrupt the wheel. If you see "CRC エラー (巡回冗長検査 (CRC) エラー) (os error 23)", delete the uv cache (`rm -rf D:\uv-cache\*` or the cache dir) and re-run `uv sync --extra cu128`.

## Verification

```bash
# Health check
curl http://127.0.0.1:8088/health
# → {"status":"ok","model":{"model_device":"cpu","codec_device":"cpu"},...}

# Quick synthesis test (requires model loaded)
# NOTICE: never inline non-ASCII JSON in `curl -d` under MSYS/git-bash/PowerShell.
# The Japanese bytes get mangled and the server returns
# `{"detail":"There was an error parsing the body"}`. Pass the payload via a
# utf-8 file with --data-binary @file instead.
cat > _req.json <<'JSON'
{"input":"こんにちは","model":"irodori-tts","voice":"hakua","response_format":"wav"}
JSON
curl -X POST http://127.0.0.1:8088/v1/audio/speech \
  -H "Content-Type: application/json" \
  --data-binary @_req.json \
  -o test_output.wav
rm -f _req.json
```
