---
name: comfyui-minimax-h3-blackwell
description: "Fix MiniMax-H3 segfault on Blackwell GPUs in ComfyUI."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [ComfyUI, MiniMax-H3, Blackwell, NVFP4, Segfault, PyTorch]
---

# MiniMax-H3 on ComfyUI with Blackwell GPUs

Run MiniMax-H3 T2VA video generation through ComfyUI's `RH_MinMaxH3` custom node on NVIDIA Blackwell GPUs (RTX 5060 Ti / 5090, sm_120) where PyTorch's `storage.__getitem__` segfaults on quantized (INT8/NVFP4/float8_e4m3fn) text encoder weights. The workaround uses a BF16 (non-quantized) Qwen3-VL text encoder that bypasses the quantized loader entirely.

## When to Use

- MiniMax-H3 T2VA video generation via ComfyUI API on Blackwell GPUs
- `torch.storage.__getitem__` access violation / segfault when loading NVFP4 or INT8 Qwen3-VL weights
- Need to configure `ComfyUI_RH_MinMaxH3` custom node model layout on Windows
- DiT (FL2VA) loads fine but text encoder crashes the server

## Prerequisites

- ComfyUI Desktop v0.3+ at `C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\`
- Custom node `ComfyUI_RH_MinMaxH3` under `custom_nodes/`
- `.venv` Python at `.venv\Scripts\python.exe`
- NVIDIA Blackwell GPU (sm_120), CUDA 13.0, PyTorch 2.13.0+cu130
- `ml_dtypes` pip package, E: drive ~120GB free

### Model Files

| Component | Source | Size | Local Path |
|-----------|--------|------|------------|
| DiT (FL2VA NVFP4) | `lilcheaty/MiniMax-H3-NVFP4` | 11.7GB | `<model_root>/fl2va/transformer/` |
| Video VAE | `lilcheaty/MiniMax-H3-NVFP4` `vae/` | 4.9GB | `<model_root>/vae/` |
| Audio VAE | `lilcheaty/MiniMax-H3-NVFP4` `vae/` | 0.6GB | `<model_root>/vae/` |
| Text Encoder (BF16) | `Qwen/Qwen3-VL-32B-Instruct` | 62GB | `<model_root>/text_encoder/` |

## How to Run

1. `execute_code`: Download DiT + VAE, hardlink BF16 shards, copy config + tokenizer.
2. `terminal`: Kill port 8188 processes, clear `__pycache__`, start server.
3. `terminal` (background): POST workflow to `/prompt` with `text_encoder_path: "text_encoder"`.

## Quick Reference

- API: `POST http://127.0.0.1:8188/prompt` → `{"prompt": {<workflow>}}`
- Stats: `GET http://127.0.0.1:8188/system_stats`
- History: `GET http://127.0.0.1:8188/history/<prompt_id>`
- Start: `.venv/Scripts/python -m main --listen 127.0.0.1 --port 8188 --disable-auto-launch --cuda-device 0 --disable-nvml-pressure --disable-metadata`
- Key file: `custom_nodes/ComfyUI_RH_MinMaxH3/minimax_h3_nodes/runtime/qwen_encoder/loading.py`

## Procedure

### 1. Download Model Files

Invoke through the `terminal` tool. See `scripts/download_models.py` for the full download script.

### 2. Set Up Directory Layout

Use `execute_code` to hardlink BF16 shards via `os.link()` (same-volume Windows hardlinks, no admin needed):

```
<model_root>/
├── fl2va/transformer/
│   ├── minimax_h3_fl2va_pruned_nvfp4.safetensors
│   └── config.json
├── vae/
│   ├── minimax_h3_video_vae_fp16.safetensors
│   └── minimax_h3_audio_vae_fp32.safetensors
├── text_encoder/
│   ├── model-00001-of-00014.safetensors  (hardlinks from BF16)
│   ├── ...model-00014-of-00014.safetensors
│   ├── model.safetensors.index.json
│   ├── config.json                        (model_type: "qwen3_vl")
│   ├── tokenizer.json, preprocessor_config.json, etc.
└── model_index.json
```

- `config.json` must contain `"model_type": "qwen3_vl"` and `"text_config"` with `"num_hidden_layers": 64`.
- Loader trims to 32 layers at runtime (`SELECTED_LAYERS`).

### 3. Kill Competing ComfyUI Desktop Process

```bash
netstat -ano | grep 8188
taskkill -PID <pid> -F
find "C:/Users/<user>/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyGUI/ComfyUI/custom_nodes/ComfyUI_RH_MinMaxH3" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

### 4. Start ComfyUI Server

```bash
cd "C:/Users/<user>/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyGUI/ComfyUI"
".venv/Scripts/python" -m main --listen 127.0.0.1 --port 8188 --disable-auto-launch --cuda-device 0 --disable-nvml-pressure --disable-metadata
```

### 5. Submit T2VA Workflow

POST to `http://127.0.0.1:8188/prompt` with `{"prompt": <workflow_dict>}`. See `scripts/submit_workflow.py`.
- Node 3 (TextEncoderLoader): `"text_encoder_path": "text_encoder"` (relative dir, NOT absolute)

## Pitfalls

- **FATAL BUG (Blackwell)**: `torch.storage.__getitem__` segfault on RTX 5060 Ti with PyTorch 2.12.1 AND 2.13.0+cu130. Triggered by torch tensor creation from `float8_e4m3fn` data (NVFP4/INT8 Qwen3-VL weights). NOT fixed by: PyTorch upgrade, numpy framework + from_numpy/frombuffer/tolist/ctypes.memmove, disabling comfy-aimdo.dll.
- **DiT (FL2VA) does NOT segfault** — only Qwen3-VL text encoder quantized weights trigger it.
- **ComfyUI Desktop auto-launch**: spawns competing process on port 8188 — always kill first.
- **`text_encoder_path` must be relative** to `model_root` — absolute paths fail.
- **Width/height must be divisible by 32** — 832x480 OK, 1280x720 rejected (use 1280x704).
- **`/prompt` requires `{"prompt": <dict>}`** wrapper — bare JSON returns `no_prompt`.
- **aimdo.dll**: `comfy_aimdo` baked into ComfyUI Desktop. Rename `aimdo.dll` to `aimdo.dll.disabled` to disable.
- **BF16 text encoder is ~62GB in RAM** — 32GB system RAM is borderline; close other processes.
- **`Qwen/Qwen3-VL-32B`** (no `-Instruct`) does NOT exist — use `Qwen/Qwen3-VL-32B-Instruct`.
- **Windows `python` stub**: PATH `python` is WindowsApps store stub — use `.venv/Scripts/python.exe`.

## Verification

```bash
curl -s "http://127.0.0.1:8188/system_stats"
".venv/Scripts/python.exe" -c "import torch; print(torch.__version__, torch.cuda.get_device_name(0))"
```

Expected: `2.13.0+cu130` and `NVIDIA GeForce RTX 5060 Ti`.
