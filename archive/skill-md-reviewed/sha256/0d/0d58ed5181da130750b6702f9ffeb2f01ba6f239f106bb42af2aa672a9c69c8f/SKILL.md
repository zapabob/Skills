---
name: hypura-local-llm-serving
description: >-
  Serve local GGUF models with Hypura — NVMe-tiered inference, Hermes
  model-provider plugin, Tailscale exposure. Covers context-length tuning,
  TurboQuant fallback, residency profiles, and GPU memory planning.
category: mlops
---

# Hypura Local LLM Serving

Serve GGUF models via `hypura` (Rust-based inference scheduler) with
NVMe-tiered tensor placement. Designed for Hermes Agent integration as an
Ollama-compatible local provider.

## Prerequisites

- `hypura` binary installed (`~/.cargo/bin/hypura`)
- GGUF model downloaded (use `hf download`)
- GPU + NVMe hardware (optional but recommended)

## Downloading models from HuggingFace

Use `hf download` to get GGUF files. The `Q4_K_M` tag in `hf`'s `repo:tag` syntax
maps to a full GGUF filename — you can also download explicitly:

```bash
# Download by quantization variant
hf download HfOrg/Model-Name --include \"*Q4_K_M*\" --local-dir /e/models/model-name-q4km

# Or use an explicit directory
HF_HOME=/e/hf_cache hf download HfOrg/Model-Name --include \"*IQ3_M*\"
```

**Disk space:** C: on Windows may run out of space (model files are 11–24 GB).
Use `--local-dir` on a drive with sufficient free space (D: or E: for large drives),
or set `HF_HOME=/path/with/space` before downloading.

**Quantization selection** (ordered by size, smaller = lower quality):
- IQ2_M (~12 GB) — smallest, lowest quality
- Q2_K (~15 GB)
- IQ3_M (~15.4 GB) — **required for Hermes Agent with 65536 context**
- IQ4_XS (~18.7 GB) — CPU-only on 16 GB GPU
- Q4_K_M (~21 GB) — needs 24 GB+ VRAM for 65536 context
- Q6_K (~30 GB) — needs 24 GB+ VRAM

Check available quants on the HF model page or use:
```bash
huggingface-cli scan-cache  # list cached models and sizes
```

## Operator-first reuse and verification

When the operator says an inference server or model already exists, **inventory and reuse it before downloading, building, or selecting a substitute**. Search the drives they named for real model files, not merely model-named directories. Inspect the installed runtime's `--help` before reusing fork-specific flags.

> **Important for Hermes Agent**: The operator has specified that Hermes Agent requires a context length of **65536 or greater**. Do not consider a model server ready for Hermes Agent unless it supports at least 65536 context tokens. If the operator explicitly lowers the requirement, follow their instruction, but the default assumption for Hermes Agent is 65536+.

If the operator asks for Hypura, keep Hypura as the target runtime. A direct `llama-server` launch is only a clearly labeled diagnostic fallback—not an equivalent completion. Before claiming Hermes integration, verify the runtime API, provider/plugin registration, and that the configured model name matches `/api/tags`.

See [references/windows-existing-assets-and-integration.md](references/windows-existing-assets-and-integration.md) for the Windows asset-inventory sequence, a validated RTX 5060 Ti profile, and the stale-fallback/provider-plugin pitfall.

## Successful Run (Session Summary)

On an RTX 5060 Ti (16GB VRAM) with 34GB system RAM, the following configuration
was validated to run stably with context length 65536 (meeting Hermes Agent requirement):

- Model: `HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive` quantized as **IQ3_M** (~15.4 GB on disk, ~19.7 GPU resident after load)
- Server: `hypura serve` (Rust-based Hypura scheduler)
- Residency profile: `legacy-3tier` (GPU + CPU + NVMe, avoids four-tier OOM on this GPU)
- Context length: `65536`
- TurboQuant mode: `exact` (via `--tq-allow-exact-fallback` flag, as HF GGUF lacks TurboQuant metadata)
- KV cache placement: GPU resident (no NVMe offload needed for this model size)
- Verified via:
  - `curl http://localhost:8080/api/tags` → model listed
  - `curl http://localhost:8080/api/generate` → coherent completion
  - `nvidia-smi` showing ~19.7 GB GPU memory used during inference
  - Hermes provider plugin correctly exposed the model as `hypura:Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive`

Exact command used:
```bash
hypura serve "H:/elt_data/hf-cache/models--HauhauCS--Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive/snapshots/f12a584fecbeb5f20001130d8ecd66c9327ae685/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-IQ3_M.gguf" --host 0.0.0.0 --port 8080 --context 65536 --residency-profile legacy-3tier --tq-allow-exact-fallback
```

## Starting the server

The model path is **positional**, not `--model`:

```bash
# Basic
hypura serve ./model.gguf

# With context and host/port
hypura serve ./model.gguf --host 0.0.0.0 --port 8080 --context 65536

# With 3-tier residency (GPU + CPU + NVMe) – preferred for large contexts on limited VRAM
hypura serve ./model.gguf --host 0.0.0.0 --port 8080 --context 65536 \\
  --residency-profile legacy-3tier

# With TurboQuant exact fallback (for plain HF GGUF files)
hypura serve ./model.gguf --host 0.0.0.0 --port 8080 --context 65536 \\
  --residency-profile legacy-3tier --tq-allow-exact-fallback

# Using the TurboQuant binary directly (zapabob/llama.cpp build)
# This provides optimized TurboQuant support without needing the fallback flag
"%USERPROFILE%/AppData/Local/Programs/llama-turboquant/bin/llama-server" ./model.gguf --host 0.0.0.0 --port 8080 --context 65536
```

**Note:** If you encounter address already in use errors, first check for and terminate any existing llama-server or hypura processes on the target port. On Windows, use `tasklist | findstr llama` and `taskkill /f /im llama-server.exe` or similar for hypura.

> **For Hermes Agent**: Always ensure the context length is set to **65536 or higher** when starting the server, unless the operator explicitly specifies a different value. The server logs should confirm the loaded context size (look for `n_ctx_slot = 65536` or similar).

## Residency profiles

| Profile | Tiers | Use case |
|---------|-------|----------|
| `four-tier` (default) | GPU + host pageable + host pinned + NVMe | Full streaming (may OOM on 16GB GPU with large context) |
| `legacy-3tier` | GPU + CPU + NVMe | Fewer allocation failures with large contexts; recommended for 16GB GPUs |

## TurboQuant fallback

HF-downloaded GGUF files lack TurboQuant metadata. Hypura fail-closes:
pass `--tq-allow-exact-fallback` or `--turboquant-mode exact`.

## GPU memory planning (RTX 5060 Ti 16GB, context=65536)

| Quant | Size | Fits? | Notes |
|-------|------|-------|-------|
| IQ2_M | 11.7 GB | ✅ | Lowest quality |
| IQ3_M | 15.4 GB | ✅ | **Required** – leaves headroom for KV cache and overhead (mandatory for Hermes Agent 65536 context) |
| IQ4_XS | 18.7 GB | ❌ | CPU-only on 16 GB GPU |
| Q4_K_M | 21.2 GB | ❌ | Too large + KV cache (exceeds 16GB VRAM) |
| Q6_K | 30 GB | ❌ | Needs 24 GB+ VRAM |

## Hermes provider integration

Create `plugins/model-providers/hypura/plugin.yaml` and `__init__.py`
(see [references/hermes-provider-plugin.md](references/hermes-provider-plugin.md) for code).

The `__init__.py` MUST override `fetch_models()` to call `/api/tags` — Hypura/Ollama
does not expose `/v1/models`. Using `super().fetch_models()` returns `None`.

MUST set `fallback_models` tuple on the profile — without it the desktop picker
shows `models: []` because the generic live-fetch code requires an API key.

MUST make two core Hermes changes for the desktop picker to show no-auth local
providers (see [references/hermes-core-changes.md](references/hermes-core-changes.md)):

1. **`hermes_cli/model_switch.py`**: Section 2b of `list_authenticated_providers`
   needs a no-auth bypass so providers with `env_vars=()` pass the credential gate.
2. **`hermes_cli/auth.py`**: `is_provider_explicitly_configured` needs a
   `fallback_providers` check so local providers in the fallback chain appear
   in the explicit-only desktop picker.

Add hypura to fallback_providers in `~/.hermes/config.yaml`:
```bash
python -c "
import yaml
from pathlib import Path
cfg = yaml.safe_load((Path.home() / '.hermes' / 'config.yaml').read_text())
cfg['fallback_providers'].insert(0, {'provider': 'hypura', 'model': '<model-name>'})
Path.home().joinpath('.hermes','config.yaml').write_text(yaml.dump(cfg, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding='utf-8')
```

Verify:
```bash
python -c \"from providers import get_provider_profile; p = get_provider_profile('hypura'); print(p.fetch_models(base_url='http://localhost:8080', timeout=5.0))\"
# → ['Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive']
```

## Tailscale exposure

```bash
tailscale serve --bg 8080
# → https://<hostname>.taile4f666.ts.net/api/tags
```

## Monitoring & verification

```bash
# Check GPU memory usage during load
watch -n 2 nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv

# Check server progress (load takes ~110s for 15GB model)
curl -s http://localhost:8080/api/tags

# Check port is open
netstat -ano | findstr :8080

# Test basic generation
curl -s -H \"Content-Type: application/json\" \\
  http://localhost:8080/api/generate \\
  -d '{\"model\": \"<model-name-from-tags>\", \"prompt\": \"Hello\", \"stream\": false}' \\
  | python -c \"import sys,json; print(json.load(sys.stdin).get('response','')[:200])\"
```

## Pitfalls

- **`--model` does not exist.** Model path is positional.
  Wrong: `hypura serve --model ./model.gguf`
  Right: `hypura serve ./model.gguf`
- **TurboQuant fail-closed.** Always add `--tq-allow-exact-fallback` for
  HF-downloaded models.
- **KV cache full.** At context=65536, 35B+ MoE models may exhaust GPU
  memory. Drop quantization (IQ3_M < Q4_K_M) or reduce context.
- **Server startup time.** First load takes ~110s for a 15GB model.
  The process shows only `\"bash: no job control in this shell\"` during loading —
  check progress via `process(action='poll')` or `process(action='log')`.
- **HF download disk space.** C: drive may be too full for model downloads.
  Use `--local-dir /e/models/...` or set `HF_HOME=/e/hf_cache` before download.
  Unauthenticated downloads are rate-limited; set `HF_TOKEN` for speed.
- **Tailscale serve persists across reboots.** Disable with
  `tailscale serve --https=443 off`. Check existing routes with `tailscale serve status`.
- **Hermes provider plugin fetch_models().** Must override to call `/api/tags`
  (not `/v1/models`). Default `super().fetch_models()` returns `None`.