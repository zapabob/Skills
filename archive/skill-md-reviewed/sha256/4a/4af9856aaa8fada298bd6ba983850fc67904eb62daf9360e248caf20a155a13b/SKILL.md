---
name: minimax-h3
description: "MiniMax-H3 FL2VA/Ref2VA video diffusion and model setup."
version: 1.0.0
author: Hermes Agent
category: creative
---

# MiniMax-H3

MiniMax-H3 is a video diffusion model by MiniMax/RunningHub with two inference
paths: **FL2VA** (first-frame conditional) and **Ref2VA** (ordered references).
The INT8 single-file variant (~132 GB total) is optimized for single-GPU
ComfyUI inference.

## When to Use

- User asks to generate video from an image with MiniMax-H3
- User needs FL2VA (first-frame) or Ref2VA (reference chain) video generation
- User asks about MiniMax-H3 model setup, VRAM, or drive placement
- User needs FL2VA vs Ref2VA workflow configuration

## Architecture: Dual-Directory Model Layout

MiniMax-H3 requires **two** ComfyUI model directories:

```
models/diffusers/MiniMax-H3/          ← sharded release (architecture, config, tokenizer)
models/MiniMax-H3/                    ← flat single-file INT8 weights (inference)
```

The sharded release provides `config.json`, `tokenizer/`, `preprocessor_config.json`.
The flat INT8 weights provide the actual inference tensors.

### File Naming Convention

| File | Partition | Purpose |
|------|-----------|---------|
| `MiniMax-H3-FL2VA-int8_convrot.safetensors` | FL2VA DiT INT8 | Video generation transformer |
| `MiniMax-H3-Ref2VA-int8_convrot.safetensors` | Ref2VA DiT INT8 | Video generation transformer |
| `qwen3-vl-32b-int8_convrot.safetensors` | Qwen3-VL INT8 | Multimodal text encoder |
| `MiniMax-H3-video_vae.safetensors` | Video VAE | Video encode/decode |
| `MiniMax-H3-audio_vae.safetensors` | Audio VAE | Audio encode/decode |

**File naming is the partition proof**: a `.safetensors` file without the
convention name is ignored. FL2VA nodes reject Ref2VA weights and vice versa.

### Component Catalog

**FL2VA nodes** (all under `RunningHub/MiniMax H3/` category in ComfyUI):

| Node ID | Display Name | Purpose |
|---------|-------------|---------|
| `RHMiniMaxH3DirectModelLoader` | RunningHub MiniMax H3 Model Loader (Direct) | Load DiT + VAE + TextEncoder |
| `RHMiniMaxH3DirectTextEncoderLoader` | RunningHub MiniMax H3 Qwen3-VL Loader (Direct) | Load text encoder only |
| `RHMiniMaxH3DirectVAELoader` | RunningHub MiniMax H3 Dual VAE Loader (Direct) | Load Video VAE + Audio VAE |
| `RHMiniMaxH3FL2VAFirstFrameCondition` | RunningHub MiniMax H3 FL2VA First/First+Last | Reference frame conditioning |
| `RHMiniMaxH3FL2VALastFrameCondition` | RunningHub MiniMax H3 FL2VA Last Only | Last-frame-only mode |
| `RHMiniMaxH3FL2VATarget` | RunningHub MiniMax H3 FL2VA Target | Prompt conditioning |
| `RHMiniMaxH3FL2VAEncode` | RunningHub MiniMax H3 FL2VA Encode | Encode conditions into latent |
| `RHMiniMaxH3EmptyAVLatent` | RunningHub MiniMax H3 Empty AV Latent | Create empty video+audio latent |
| `RHMiniMaxH3DualSigmaSampler` | RunningHub MiniMax H3 Dual Sigma Sampler | Diffusion sampling |
| `RHMiniMaxH3DecodeAV` | RunningHub MiniMax H3 Decode Video + Audio | Decode latent to video+audio |

**Ref2VA nodes**: Same loader nodes + `Ref2VAImageReference`, `Ref2VAAudioReference`,
`Ref2VAVideoReference`, `Ref2VATarget`, `Ref2VAEncode`.

## FL2VA Workflow

1. **Load models**: Use `RHMiniMaxH3DirectModelLoader` with `model_root`,
   `dit_path`, `text_encoder_path`, `video_vae_path`, `audio_vae_path`
2. **Load reference image**: Use `RHMiniMaxH3FL2VAFirstFrameCondition` with
   `image_path` pointing to the first frame image
3. **Set prompt**: Use `RHMiniMaxH3FL2VATarget` with `prompt` (positive) and
   `negative_prompt` (negative)
4. **Create latent**: Use `RHMiniMaxH3EmptyAVLatent` (set `width`, `height`, `duration`)
5. **Encode**: Use `RHMiniMaxH3FL2VAEncode` — connect FL2VA Target + latent + loaded models
6. **Sample**: Use `RHMiniMaxH3DualSigmaSampler` — connect encoded latent
7. **Decode**: Use `RHMiniMaxH3DecodeAV` — connect sampled latent
8. **Create video**: Use `RHMiniMaxH3CreateVideo` (set `fps`, `format`)
9. **Save**: Use `RHMiniMaxH3SaveVideo` (set `output_path`)

## Ref2VA Workflow

1. **Load models**: Same as FL2VA, but use Ref2VA-specific loader nodes
2. **Build reference chain**: Use `Ref2VAImageReference` / `Ref2VAAudioReference` /
   `Ref2VAVideoReference` nodes sequentially, chaining via the `references` input
3. **Set prompt**: Use `Ref2VA Target` with `prompt` + `negative_prompt`
4. **Encode**: Use `Ref2VA Encode` — connect reference chain + loaded models
5. **Sample + Decode + CreateVideo + SaveVideo**: Same as FL2VA

**Ref2VA `ref_image_size` option**:
- `match` (default): scales references to canvas pixel area, preserving aspect ratio
- `max`: keeps 2048px short edge for identity fidelity (slower)

## Model Sizes and VRAM Requirements

### INT8 Single-File Weights

| Component | Size |
|-----------|------|
| FL2VA DiT INT8 | 47 GB |
| Ref2VA DiT INT8 | 47 GB |
| Qwen3-VL 32B INT8 | 27 GB |
| Video VAE | 10.4 GB |
| Audio VAE | 0.6 GB |
| **Total** | **~132 GB** |

### Download Strategy (Windows)

During download, temp files can reach **2× model size** (~264 GB temporarily).
Plan storage accordingly:

- **D: drive (950 GB)**: Fits but tight; CRC errors possible under sustained I/O
- **E: drive (1 TB)**: Recommended primary; more headroom for temp files
- **C: drive (99% full)**: Too small — avoid for model downloads

Download files **sequentially** rather than all-at-once to reduce simultaneous
I/O pressure. If the source drive develops CRC errors mid-transfer, re-download
directly to the fallback drive rather than copying from the corrupted location.

### VRAM Requirements

| Configuration | VRAM Needed | Notes |
|--------------|-------------|-------|
| INT8 + layerwise offload | ~8-10 GB | RTX 3060 12 GB minimum comfortable |
| BF16 full load | ~16+ GB | Needs RTX 3080+/RTX 4090 |
| Layerwise offload disabled | ~12-14 GB | More stable, uses more VRAM |

**Host RAM**: ≥16 GB recommended for layerwise offload (more for larger batches).
The layerwise offload mechanism streams DiT layers one at a time to GPU memory.

## Windows Junction Setup

When models live on a secondary drive, link them into ComfyUI's models directory:

```cmd
:: Remove existing junction (if any)
cmd.exe /c "rd /s /q "%USERPROFILE%\AppData\Local\Comfy-Desktop\ComfyGUI\ComfyUI\models\MiniMax-H3""

:: Create junction to model storage
cmd.exe /c "mklink /J "%USERPROFILE%\AppData\Local\Comfy-Desktop\ComfyGUI\ComfyUI\models\MiniMax-H3" "E:\ComfyUI_models\MiniMax-H3""
```

**Important**: Use `mklink /J` via **cmd.exe**, NOT PowerShell's
`New-Item -ItemType Junction`. PowerShell may fail with "directory not empty"
errors when a previous junction exists but is stale.

## Parameters and Constraints

**Video duration**: 5-15 seconds target. The model internally rounds up to
`17n+5` frames at 24 fps (e.g., 5 seconds → 124 frames).

**Aspect ratios**: FL2VA follows reference image aspect ratio. Ref2VA supports
`21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`.

**Resolution**: 16:9 recommended (e.g., 1280×720). The downscale chain for
16:9 is `1344×768 → 1024×576 → 832×480 → 640×352`.

**Sampling**: Separate video and audio noise streams. Visual condition rows
pinned at sigma 0.999; audio-reference rows at sigma 1.0. 50 sigma points =
49 DiT forward passes.

## Pitfalls

1. **FL2VA ≠ Ref2VA**: FL2VA takes a single reference frame (first frame).
   Ref2VA takes an ordered chain of references. They do not share DiT weights
   — using a Ref2VA DiT in an FL2VA node (or vice versa) fails closed.

2. **INT8 filename is proof**: The flat single-file `.safetensors` filename
   encodes the partition. A Ref2VA DiT fed into an FL2VA node produces a
   closed error rather than silently using wrong weights.

3. **Two-directory requirement**: Both the sharded release (`models/diffusers/MiniMax-H3/`)
   AND the flat INT8 weights (`models/MiniMax-H3/`) are required. The sharded
   release provides `config.json`, `tokenizer/`, and `preprocessor_config.json`.
   The flat weights provide actual inference tensors.

4. **Model root selects the sharded release**: FL2VA nodes resolve only the
   `FL2VA` partition; Ref2VA nodes resolve only `Ref2VA`. Each task has three
   explicit component loaders that only list their own component type.

5. **D: drive CRC errors**: Under sustained I/O, the D: drive may develop
   CRC errors (especially on large files like video VAE at 10.4 GB). If a file
   fails to copy/move with a CRC error, re-download directly to the fallback
   drive rather than retrying the copy.

6. **Video VAE and Qwen3-VL are large**: At 10.4 GB and 27 GB respectively,
   they are the slowest to download. Plan bandwidth accordingly.

7. **INT8 reduces checkpoint size but NOT inference memory**: INT8 brings
   storage from ~66 GB (BF16 DiT) to ~47 GB, but the model still needs full
   host RAM for layerwise offload during inference.

8. **ComfyUI must be restarted** after adding new model files — node definitions
   are read once at startup.

## AdaLN Curve Table (Optional)

The adaLN projection is ~26 GB of the BF16 DiT checkpoint. If using the
adaln_curve format (pruning the projection to rank-k approximation):
- BF16: 66.3 GB → ~40 GB
- INT8: 47 GB → ~21 GB

This reduces checkpoint size by ~50% at the cost of a rank-k approximation
instead of exact adaLN. The loader detects this format automatically from
the `adaln_t_table` tensor.

## Acceleration Options

The plugin supports velocity-cache and Cache-DiT acceleration for single-GPU:

- `auto`: Good first try
- `minimax-h3-velocity-cache-v1`: Preferred (whole-step velocity reuse + Taylor)
- `minimax-h3-cache-v1`: Alternative with Cache-DiT

Set acceleration on the sampler node in `h3_settings.py`. Velocity-cache can
achieve ~3.2× speedup on validated configurations.

## References

- Plugin: https://github.com/HM-RunningHub/ComfyUI-RH-MiniMax-H3
- Official release: https://huggingface.co/RunningHub/MiniMax-H3-INT8-CONVROT
- Model weights: `Gluttony10/MiniMax-H3-INT8-CONVROT` on HuggingFace