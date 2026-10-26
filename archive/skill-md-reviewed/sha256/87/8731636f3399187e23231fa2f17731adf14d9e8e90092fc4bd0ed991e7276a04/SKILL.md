---
name: comfyui-minimax-h3-workflows
description: "ComfyUI MiniMax-H3 workflow patterns and Turbo fixes."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [ComfyUI, MiniMax-H3, Turbo-LoRA, T2VA, workflow]
---

# MiniMax-H3 Local ComfyUI Workflows

Class-level guidance for running MiniMax-H3 T2VA generation in ComfyUI on Windows. Focus: local inference, Turbo LoRA acceleration, and avoiding node-type/validation errors on ComfyUI 0.30.x.

## When to Use

- H3 T2VA generation via `ComfyUI_RH_MinMaxH3` on Windows
- Blackwell/NVFP4/BF16 model layouts and segfault workaround stack
- Turbo LoRA fast-path integration without breaking ComfyUI type validation
- Adapting community workflows for RTX 3060 / RTX 5060 Ti environments
- Converting MiniMax-AI official skills into prompt/style assets for H3 generation

## Environment Assumptions

- ComfyUI Desktop v0.30.x at `C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI`
- `.venv\Scripts\python.exe` is real Python; PATH `python` is a WindowsApps stub
- NVIDIA Blackwell or compatible GPU, CUDA 13.0, PyTorch 2.13.0+cu130
- Port 8188 may be contested by ComfyUI Desktop auto-launch; kill before custom runs

## Reference Material

### references/blackwell-segfault-lessons.md
Blackwell-specific crash notes:
- PyTorch `torch.storage.__getitem__` segfaults on quantized Qwen3-VL weights (INT8/NVFP4/float8)
- Verified workaround stack:
  - `PYTORCH_CUDA_ALLOC_CONF=backend:native`
  - `--disable-cuda-malloc`
  - `disable_mmap=True` in text encoder loader kwargs
  - `sitecustomize.py` monkey-patch for `safetensors.safe_open(..., framework="numpy")`
  - BF16 Qwen3-VL text encoder instead of quantized TE

### references/turbo-lora-workflow-patterns.md
Turbo LoRA integration patterns and community workflow structures, including:
- Node compatibility matrix between `MiniMaxH3TurboLoRA`, `RHMiniMaxH3DualSigmaSampler`, and standard ComfyUI samplers
- Exact failure modes and working workaround patterns from `tlano-z/ComfyUI-MiniMax-H3-Workflows-For3060`

## Model Layouts

### Layout A: Direct NVFP4 + BF16 TE (this environment)
```
<model_root>/
├── fl2va/transformer/
│   └── minimax_h3_fl2va_int8_convrot.safetensors
├── vae/
│   ├── minimax_h3_video_vae_fp16.safetensors
│   └── minimax_h3_audio_vae_fp32.safetensors
├── text_encoder/
│   ├── model-00001-of-00014.safetensors  (BF16 hardlinks)
│   ├── ...model-00014-of-00014.safetensors
│   ├── model.safetensors.index.json
│   ├── config.json  (model_type: "qwen3_vl")
│   └── tokenizer.json, preprocessor_config.json
└── model_index.json
```

Loaders:
- `RHMiniMaxH3DirectModelLoader`: `model_root`, `transformer_path`
- `RHMiniMaxH3DirectVAELoader`: `model_root`, `video_vae_path`, `audio_vae_path`
- `RHMiniMaxH3DirectTextEncoderLoader`: `model_root`, `text_encoder_path="text_encoder"` (relative dir)

### Layout B: Pruned INT8 + Pruned Turbo LoRA (community standard)
- Base: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- TE: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` or `qwen3vl_32b_minimax_h3_int8_convrot.safetensors`
- VAE: `minimax_h3_video_vae_int8_convrot.safetensors` (requires ComfyUI PR #15334)
- Turbo LoRA: `minimax_h3_turbo_4step_ema_ckpt850_pruned_comfyui.safetensors`
- Preferred nodes: standard `UNETLoader`/`CLIPLoader`/`VAELoader` + `MiniMaxH3ImageToVideo` + `MiniMaxH3SigmaShift`

## Workflow Patterns

### Pattern 1: Standard RH Direct Loader (50-step baseline)
1. `RHMiniMaxH3DirectModelLoader`
2. `RHMiniMaxH3DirectVAELoader`
3. `RHMiniMaxH3DirectTextEncoderLoader`
4. `RHMiniMaxH3T2VATarget` — width/height divisible by 32, duration 4–15s
5. `RHMiniMaxH3T2VATextEncode`
6. `RHMiniMaxH3EmptyAVLatent`
7. `RHMiniMaxH3DualSigmaSampler` — 50 steps, video_shift=12, audio_shift=3
8. `RHMiniMaxH3DecodeAV`
9. `CreateVideo` + `SaveVideo`

### Pattern 2: Turbo LoRA via Standard ComfyUI Sampler (recommended)
Use when `MiniMaxH3TurboLoRA` → `RHMiniMaxH3DualSigmaSampler` fails with type mismatch.

1. Install `ComfyUI-MiniMax-H3-Turbo`
2. Download `minimax_h3_turbo_4step_ema_ckpt850.safetensors` into `models/loras/`
3. `MiniMaxH3TurboLoRA` → standard sampler path:
   - `MiniMaxH3TurboLoRA` outputs `MODEL`
   - `BasicGuider(model=TurboLoRA, conditioning=...)`
   - `SamplerCustomAdvanced(sampler=MiniMaxH3TurboSampler, sigmas=BasicSchedule..., ...)`
   - Do NOT connect `MiniMaxH3TurboLoRA` directly to `RHMiniMaxH3DualSigmaSampler`

### Pattern 2b: Patch `MiniMaxH3TurboLoRA` type signature (validated workaround)
If the standard sampler path is not available (e.g. `MiniMaxH3ImageToVideo` / `MiniMaxH3SigmaShift` are missing from `custom_nodes/`), edit `custom_nodes/ComfyUI-MiniMax-H3-Turbo/__init__.py` to change the `MiniMaxH3TurboLoRA` type signature:

```python
# Change BOTH INPUT_TYPES["model"] and RETURN_TYPES:
"model": ("MINIMAX_H3_DIRECT_MODEL",),  # was "MODEL"
RETURN_TYPES = ("MINIMAX_H3_DIRECT_MODEL",)  # was ("MODEL",)
```

This lets `MiniMaxH3TurboLoRA` connect directly to `RHMiniMaxH3DualSigmaSampler` without `prompt_outputs_failed_validation`. Verified on `ComfyUI-MiniMax-H3-Turbo` 0.1.x with `ComfyUI_RH_MinMaxH3` on Blackwell. Survives server restart (requires `pycache` clear + server restart to pick up).

### Pattern 2c: Kijai-format Turbo LoRA with standard nodes
Use `Kijai/MiniMax-H3_comfy` repo's `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` (4-step distillation, standard `LoraLoaderModelOnly` compatible):

```
hf_hub_download(repo_id='Kijai/MiniMax-H3_comfy',
                filename='loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors',
                local_dir='E:/ComfyUI_models/MiniMax-H3-Turbo-Lora')
# Copy to models/loras/
```

Then `LoraLoaderModelOnly(lora=...file)` → standard sampler. Requires `MiniMaxH3ImageToVideo` + `MiniMaxH3SigmaShift` (NOT in `ComfyUI_RH_MinMaxH3`).

### Pattern 3: Direct Low-Step RH Sampler (no Turbo LoRA)
If Turbo LoRA is unavailable, reduce steps on the native sampler:
- `RHMiniMaxH3DualSigmaSampler` with `sigma_points=4..8`
- Keep `video_shift=12`, `audio_shift=3`
- Audio quality degrades below ~8 steps; use only for quick tests

### Pattern 4: Pruned-base Turbo (community 3060 pattern)
- `UNETLoader` + `CLIPLoader` + `VAELoader`
- `LoraLoaderModelOnly` with pruned Turbo LoRA
- `MiniMaxH3ImageToVideo` for conditioning
- `MiniMaxH3SigmaShift(video=12, audio=5)`
- `BasicScheduler(simple, 8 steps)` + `KSamplerSelect(res_multistep)` + `SamplerCustomAdvanced`

This pattern requires `MiniMaxH3ImageToVideo` and `MiniMaxH3SigmaShift` nodes, which are not in `ComfyUI_RH_MinMaxH3`.

## Prompt / Skill Integration

Official MiniMax-H3 skills live at `https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills`. Relevant skills:
- `h3-prompt-writing` — prompt construction skill
- Style skills: `3d-animation-short-generator`, `brand-promo-video-generator`, `co-op-game-intro-generator`, `handdrawn-live-video-generator`, `minimalist-product-ad-generator`, `paper-collage-explainer-generator`, `papercraft-stop-motion-explainer`

To install a skill into Hermes:
1. Read the skill's `SKILL.md` from GitHub
2. Save to `~/.hermes/skills/<skill-name>/SKILL.md`
3. Load with `skill_view(name='...')` before generation tasks

## API Notes

- Submit: `POST http://127.0.0.1:8188/prompt` with `{"prompt": workflow_dict}`
- Monitor: `GET http://127.0.0.1:8188/history/<prompt_id>`
- Stats: `GET http://127.0.0.1:8188/system_stats`
- Node registry: `GET http://127.0.0.1:8188/object_info` — grep for `minimax` / `sigma`

## Pitfalls

- **Do not connect `MiniMaxH3TurboLoRA` output to `RHMiniMaxH3DualSigmaSampler`**: type `MODEL` vs `MINIMAX_H3_DIRECT_MODEL` mismatch → `return_type_mismatch`. Use Pattern 2b (patch type signature) or Pattern 2c (Kijai LoRA + standard nodes) instead.
- **Do not use `K_SIGMAS` on ComfyUI 0.30.1**: missing node; use `BasicScheduler` + `KSamplerSelect` instead
- **Pruned Turbo LoRA filename**: community uses `*_pruned_comfyui.safetensors`; non-pruned base needs the non-pruned Turbo LoRA
- **Audio over-step**: at 4 steps, audio stream can break if scheduler does not respect separate video/audio sigma clocks
- **ComfyUI Desktop port conflict**: always `taskkill` competing PID on 8188 before starting custom server
- **`aimdo.dll` missing**: rename to `aimdo.dll.disabled` to silence load error; it is not required for Blackwell inference
- **Server hangs after `/prompt` POST timeout**: if the request body is accepted but no `prompt_id` response arrives within ~5 min, the server may enter a half-dead state (LISTENING, multiple `CLOSE_WAIT` connections, no response to `/system_stats`). Recovery: `taskkill /F /PID <pid>` and restart. Check `netstat -ano | grep 8188` to confirm port is free before relaunch. Root cause is unknown but correlates with model load + workflow complexity on Blackwell.
- **Initial DiT load takes minutes**: `disable_mmap=True` forces full RAM read via numpy framework; do not assume a hung server if VRAM is still 15.9GB free at startup — check RAM decrease instead.

## Verified Patterns (This Session)

### Pattern 2b: Patch `MiniMaxH3TurboLoRA` type signature ✅ VERIFIED
Edit `custom_nodes/ComfyUI-MiniMax-H3-Turbo/__init__.py`:
```python
# BOTH input and output types:
"model": ("MINIMAX_H3_DIRECT_MODEL",),  # was "MODEL"
RETURN_TYPES = ("MINIMAX_H3_DIRECT_MODEL",)  # was ("MODEL",)
```
This allows direct connection to `RHMiniMaxH3DualSigmaSampler` without `prompt_outputs_failed_validation`. Requires:
1. `pycache` clear: `find "custom_nodes/ComfyUI-MiniMax-H3-Turbo" -name "__pycache__" -type d -exec rm -rf {} +`
2. Server restart with `--disable-cuda-malloc`

### Pattern 2c: Kijai-format Turbo LoRA details
- Repo: `Kijai/MiniMax-H3_comfy`
- File: `loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`
- Download: `hf_hub_download(repo_id='Kijai/MiniMax-H3_comfy', filename='loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors', local_dir='E:/ComfyUI_models/MiniMax-H3-Turbo-Lora')`
- Copy to `models/loras/`
- Requires: `MiniMaxH3ImageToVideo` + `MiniMaxH3SigmaShift` (NOT in `ComfyUI_RH_MinMaxH3` — must install `ComfyUI-MiniMax-H3` Kijai fork or RunningHub variant)

### Observed Server Behavior (Blackwell RTX 5060 Ti)
- `/prompt` POST accepted, `prompt_id` returned, but **VRAM stays at 15.9GB free** for 4+ minutes
- RAM decreases from 19GB → 14GB over time (model loading into RAM via `disable_mmap=True`)
- `got prompt` logged but no further ComfyUI executor logs
- 15-min timeout in monitor script triggered; server still LISTENING but CLOSE_WAIT pile-up
- **Possible cause**: `disable_mmap=True` + numpy framework loads 11.7GB NVFP4 DiT + 62GB BF16 TE sequentially into RAM — single-threaded, can take 10-30+ min before GPU kernel launch

### Workaround: Use Low-Step RH Sampler Without Turbo (Pattern 3)
If Turbo LoRA integration fails, use native `RHMiniMaxH3DualSigmaSampler` with `sigma_points=4` (4 steps) directly:
```json
{
  "class_type": "RHMiniMaxH3DualSigmaSampler",
  "inputs": {
    "h3_model": ["DIRECT_LOADER", 0],
    "conditioning": ["TEXT_ENCODE", 0],
    "av_latent": ["EMPTY_LATENT", 0],
    "seed": 42,
    "sigma_points": 4,
    "video_shift": 12.0,
    "audio_shift": 3.0,
    "accel": "off",
    "denoise_video": true,
    "video_denoise": 0.12,
    "audio_denoise": 2,
    "denoise": 4,
    "control_start": 0.0,
    "control_end": 1.0
  }
}
```
Audio quality degrades below ~8 steps but usable for quick tests. Avoids Turbo LoRA node entirely.