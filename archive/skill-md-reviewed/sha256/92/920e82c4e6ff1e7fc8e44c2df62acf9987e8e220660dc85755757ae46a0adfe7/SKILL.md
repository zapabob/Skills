---
name: minimax-h3-comfyui
description: "MiniMax-H3 video via ComfyUI — RHMiniMaxH3 class names."
version: 1.0.0
author: [hakua]
license: MIT
platforms: [windows]
compatibility: "Requires ComfyUI 0.30.1+, ComfyUI_RH_MinMaxH3, MiniMax-H3 models, RTX 5060 Ti 16GB, CUDA 13+, PyTorch 2.12.1+cu130"
prerequisites:
  commands: ["py", "curl"]
metadata:
  hermes:
    tags: [comfyui, minimax-h3, video-generation, miniMax, runninghub]
    related_skills: [comfyui]
    category: creative
---

# MiniMax-H3 ComfyUI Integration

Generate video with MiniMax-H3 using ComfyUI API. This skill documents the **correct API-format node class names** (with `RHMiniMaxH3...` prefix), model paths, and workflow structures for all three task modes.

## Critical Discovery

**MiniMax-H3 custom nodes register class names with `RHMiniMaxH3...` prefix** — NOT the raw Python class names. This is the #1 source of "class_type not found" errors.

Example:
- Python class: `MiniMaxH3DirectModelLoader`
- Registered class_type: `RHMiniMaxH3DirectModelLoader`

Always check `NODE_CLASS_MAPPINGS` in `minimax_h3_nodes/nodes.py` before building workflows.

## Node Class Registry (from NODE_CLASS_MAPPINGS)

### Loaders
| Python Class | Registered class_type |
|--------------|----------------------|
| MiniMaxH3DirectModelLoader | RHMiniMaxH3DirectModelLoader |
| MiniMaxH3DirectTextEncoderLoader | RHMiniMaxH3DirectTextEncoderLoader |
| MiniMaxH3DirectVAELoader | RHMiniMaxH3DirectVAELoader |
| MiniMaxH3FL2VAModelLoader | RHMiniMaxH3FL2VAModelLoader |
| MiniMaxH3FL2VATextEncoderLoader | RHMiniMaxH3FL2VATextEncoderLoader |
| MiniMaxH3FL2VAVAELoader | RHMiniMaxH3FL2VAVAELoader |
| MiniMaxH3Ref2VAModelLoader | RHMiniMaxH3Ref2VAModelLoader |
| MiniMaxH3Ref2VATextEncoderLoader | RHMiniMaxH3Ref2VATextEncoderLoader |
| MiniMaxH3Ref2VAVAELoader | RHMiniMaxH3Ref2VAVAELoader |

### Targets (Task Definition)
| Python Class | Registered class_type |
|--------------|----------------------|
| MiniMaxH3T2VATarget | RHMiniMaxH3T2VATarget |
| MiniMaxH3FL2VATarget | RHMiniMaxH3FL2VATarget |
| MiniMaxH3Ref2VATarget | RHMiniMaxH3Ref2VATarget |

### Conditioning
| Python Class | Registered class_type |
|--------------|----------------------|
| MiniMaxH3T2VATextEncode | RHMiniMaxH3T2VATextEncode |
| MiniMaxH3FL2VAFirstFrameCondition | RHMiniMaxH3FL2VAFirstFrameCondition |
| MiniMaxH3FL2VALastFrameCondition | RHMiniMaxH3FL2VALastFrameCondition |
| MiniMaxH3FL2VAEncode | RHMiniMaxH3FL2VAEncode |
| MiniMaxH3Ref2VAImageReference | RHMiniMaxH3Ref2VAImageReference |
| MiniMaxH3Ref2VAAudioReference | RHMiniMaxH3Ref2VAAudioReference |
| MiniMaxH3Ref2VAVideoReference | RHMiniMaxH3Ref2VAVideoReference |
| MiniMaxH3Ref2VAEncode | RHMiniMaxH3Ref2VAEncode |

### Latent & Sampling
| Python Class | Registered class_type |
|--------------|----------------------|
| MiniMaxH3EmptyAVLatent | RHMiniMaxH3EmptyAVLatent |
| MiniMaxH3DualSigmaSampler | RHMiniMaxH3DualSigmaSampler |
| MiniMaxH3SeparateAVLatent | RHMiniMaxH3SeparateAVLatent |
| MiniMaxH3CombineAVLatent | RHMiniMaxH3CombineAVLatent |
| MiniMaxH3EncodeVideoAVLatent | RHMiniMaxH3EncodeVideoAVLatent |
| MiniMaxH3FrameRate | RHMiniMaxH3FrameRate |

### Decode
| Python Class | Registered class_type |
|--------------|----------------------|
| MiniMaxH3DecodeAV | RHMiniMaxH3DecodeAV |

## Model Files (E:/ComfyUI_models/MiniMax-H3/)

| File | Size | Purpose |
|------|------|---------|
| MiniMax-H3-FL2VA-int8_convrot.safetensors | ~47 GB | DiT model (FL2VA partition) |
| MiniMax-H3-video_vae.safetensors | ~10 GB | Video VAE |
| MiniMax-H3-audio_vae.safetensors | ~0.6 GB | Audio VAE |
| qwen3-vl-32b-int8_convrot.safetensors | ~27 GB | Qwen3-VL text encoder |

## T2VA Workflow (Text-Only Video Generation — RECOMMENDED)

No image inputs required. Best for pure text-to-video.

```json
{
  "1": {
    "class_type": "RHMiniMaxH3DirectModelLoader",
    "inputs": {
      "model_root": "E:/ComfyUI_models/MiniMax-H3",
      "dtype": "auto",
      "transformer_path": "E:/ComfyUI_models/MiniMax-H3/MiniMax-H3-FL2VA-int8_convrot.safetensors"
    }
  },
  "2": {
    "class_type": "RHMiniMaxH3DirectVAELoader",
    "inputs": {
      "video_vae_path": "E:/ComfyUI_models/MiniMax-H3/MiniMax-H3-video_vae.safetensors",
      "audio_vae_path": "E:/ComfyUI_models/MiniMax-H3/MiniMax-H3-audio_vae.safetensors"
    }
  },
  "3": {
    "class_type": "RHMiniMaxH3DirectTextEncoderLoader",
    "inputs": {
      "text_encoder_path": "E:/ComfyUI_models/MiniMax-H3/qwen3-vl-32b-int8_convrot.safetensors"
    }
  },
  "4": {
    "class_type": "RHMiniMaxH3T2VATarget",
    "inputs": {
      "aspect_ratio": "16:9",
      "duration_seconds": 10.0,
      "width": 1280,
      "height": 720
    }
  },
  "5": {
    "class_type": "RHMiniMaxH3T2VATextEncode",
    "inputs": {
      "h3_text_encoder": ["3", 0],
      "h3_vae_bundle": ["2", 0],
      "target": ["4", 0],
      "prompt": "anime girl, cute, pink hair, school uniform, blushing, beautiful, detailed, 1girl, high quality"
    }
  },
  "6": {
    "class_type": "RHMiniMaxH3EmptyAVLatent",
    "inputs": {
      "target": ["4", 0]
    }
  },
  "7": {
    "class_type": "RHMiniMaxH3DualSigmaSampler",
    "inputs": {
      "h3_model": ["1", 0],
      "conditioning": ["5", 0],
      "av_latent": ["6", 0],
      "seed": 42,
      "sigma_points": 30,
      "video_shift": 12.3,
      "audio_shift": 5.0,
      "accel": "off",
      "denoise_video": true
    }
  },
  "8": {
    "class_type": "RHMiniMaxH3DecodeAV",
    "inputs": {
      "h3_vae_bundle": ["2", 0],
      "sampled_av_latent": ["7", 0]
    }
  }
}
```

## FL2VA Workflow (First/Last Frame to Video)

Requires `LoadImage` nodes for keyframes. Connect to `RHMiniMaxH3FL2VAFirstFrameCondition`.

```json
{
  "1": { "class_type": "RHMiniMaxH3DirectModelLoader", "inputs": {...} },
  "2": { "class_type": "RHMiniMaxH3DirectVAELoader", "inputs": {...} },
  "3": { "class_type": "RHMiniMaxH3DirectTextEncoderLoader", "inputs": {...} },
  "4": { "class_type": "LoadImage", "inputs": { "image": "first_frame.png" } },
  "5": { "class_type": "LoadImage", "inputs": { "image": "last_frame.png" } },
  "6": { "class_type": "RHMiniMaxH3FL2VAFirstFrameCondition", "inputs": { "first_frame": ["4", 0], "last_frame": ["5", 0] } },
  "7": { "class_type": "RHMiniMaxH3FL2VATarget", "inputs": { "keyframes": ["6", 0], "aspect_ratio": "16:9", "duration_seconds": 10.0 } },
  "8": { "class_type": "RHMiniMaxH3FL2VAEncode", "inputs": { "h3_text_encoder": ["3", 0], "h3_vae_bundle": ["2", 0], "target": ["7", 0], "keyframes": ["6", 0], "prompt": "..." } },
  "9": { "class_type": "RHMiniMaxH3EmptyAVLatent", "inputs": { "target": ["7", 0] } },
  "10": { "class_type": "RHMiniMaxH3DualSigmaSampler", "inputs": { "h3_model": ["1", 0], "conditioning": ["8", 0], "av_latent": ["9", 0], ... } },
  "11": { "class_type": "RHMiniMaxH3DecodeAV", "inputs": { "h3_vae_bundle": ["2", 0], "sampled_av_latent": ["10", 0] } }
}
```

## Ref2VA Workflow (Reference-Based)

Requires reference images/audio/video. Use `RHMiniMaxH3Ref2VAImageReference` / `AudioReference` / `VideoReference` chained together, then `RHMiniMaxH3Ref2VATarget` + `RHMiniMaxH3Ref2VAEncode`.

## Launch ComfyUI (Windows, CUDA 13+)

```bash
cd "%USERPROFILE%/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyGUI/ComfyUI"
".venv/Scripts/python" -m main --listen 127.0.0.1 --port 8188 --disable-auto-launch --cuda-device 0 --disable-nvml-pressure
```

## Submit Workflow via API

```bash
curl -X POST "http://127.0.0.1:8188/prompt" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Node 'MiniMaxH3DirectModelLoader' not found` | Using Python class name | Use `RHMiniMaxH3DirectModelLoader` |
| `Node 'FL2VAPrompt' not found` | Wrong node name | Use `RHMiniMaxH3FL2VATarget` + `RHMiniMaxH3FL2VAEncode` |
| `JSONDecodeError: Extra data` | Malformed JSON in curl | Validate JSON with `python -m json.tool` |
| `Connection refused` | Server not running | Launch ComfyUI first, verify `curl http://127.0.0.1:8188/system_stats` |
| OOM / CUDA OOM | 16GB VRAM exceeded | Reduce resolution, duration, or sigma_points; use `accel: "minimax-h3-velocity-cache-v1"` |

## GPU Requirements

- RTX 5060 Ti 16GB: 1280x720 10s 24fps ~8-10 GB with Dynamic VRAM
- CUDA 13.0+ (PyTorch 2.12.1+cu130)
- Dynamic VRAM enabled (auto-detected in ComfyUI 0.30.1)

## ⚠️ Blackwell GPU (RTX 50-series) Limitation — CRITICAL

**RTX 5060 Ti / 5090 (sm_120, Blackwell) + CUDA 13+ + PyTorch 2.12.1-2.13.0 CANNOT load INT8 convrot or NVFP4 quantized MiniMax-H3 models.**

### Root Cause
PyTorch's `torch.storage.__getitem__` has an access violation on Blackwell when loading quantized tensors (INT8 convrot / NVFP4) via `safetensors`. The crash occurs in:
```
_stream_load_quantized_backbone → reader.get_tensor() → torch.storage.__getitem__ (segfault)
```

### What Does NOT Work
| Attempt | Result |
|---------|--------|
| NVFP4 models (lilcheaty/MiniMax-H3-NVFP4) | Same segfault — still quantized |
| NVFP4 + `framework="numpy"` in safetensors | Same — tensor conversion triggers storage |
| `torch.from_numpy()` / `torch.tensor(tolist())` | Storage shared / OOM on large tensors |
| `ctypes.memmove` into `torch.empty()` | Fresh storage but first access triggers bug |
| Disabling comfy-aimdo (rename aimdo.dll) | No effect — bug is in PyTorch storage layer |
| PyTorch 2.13.0 upgrade | Same — bug persists in 2.13.0+cu130 |

### WORKING Workaround: BF16 Text Encoder
**Use the official non-quantized Qwen3-VL-32B text encoder (BF16, ~62 GB) instead of INT8/NVFP4.**

```bash
# Download official BF16 Qwen3-VL-32B text encoder
HF_HUB_ENABLE_HF_TRANSFER=1 python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Qwen/Qwen3-VL-32B',
    local_dir='E:/ComfyUI_models/MiniMax-H3/text_encoder',
    allow_patterns=['*.json','*.safetensors','tokenizer*','processor*'],
    resume_download=True,
)
"
```

The BF16 text encoder loads via standard `from_pretrained` path (no quantized storage) and works on Blackwell.

### Configuration
Update `model_index.json` at `E:/ComfyUI_models/MiniMax-H3/model_index.json`:
```json
{
  "_minimax_h3": {"partition": "fl2va", "schema_version": 1, "sigma_shift_scales": {"audio": 3.0, "video": 12.0}, "tasks": ["t2va", "fl2va"]},
  "text_encoder": ["MiniMaxH3Qwen3VL", null],
  "transformer": ["MiniMaxH3Transformer", null],
  "vae": ["MiniMaxH3VAE", null],
  "video_vae": ["MiniMaxH3VideoVAE", null],
  "audio_vae": ["MiniMaxH3AudioVAE", null]
}
```

Ensure `text_encoder/` directory contains the BF16 model files (config.json, model-*.safetensors, tokenizer/processor files).

### Alternative: Stay on Ampere (RTX 30-series) or Hopper (H100)
If you must use INT8 convrot, run on non-Blackwell GPUs where `torch.storage.__getitem__` works correctly.

### Model Size Impact
| Component | INT8 convrot | NVFP4 | BF16 (working) |
|-----------|-------------|-------|----------------|
| Text Encoder | 27 GB | 14.6 GB | **62 GB** |
| DiT (FL2VA) | 47 GB | 11.7 GB | 47 GB (unchanged) |
| Video VAE | 10 GB | 4.9 GB | 10 GB (unchanged) |
| Audio VAE | 0.6 GB | 0.6 GB | 0.6 GB (unchanged) |

**Total VRAM/RAM impact**: BF16 text encoder requires ~62 GB disk + significant RAM during load. Ensure ≥64 GB system RAM.

## Output

`RHMiniMaxH3DecodeAV` returns `(IMAGE, AUDIO)` — frames tensor + audio tensor.
Use standard ComfyUI `SaveVideo` / `SaveAudio` nodes to write files.

## References

- Custom nodes: `%USERPROFILE%/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyGUI/ComfyUI/custom_nodes/ComfyUI_RH_MinMaxH3/`
- NODE_CLASS_MAPPINGS: `minimax_h3_nodes/nodes.py`
- Model contracts: `minimax_h3_nodes/contracts/` (H3_TASK_T2VA, H3_TASK_FL2VA, H3_TASK_REF2VA)