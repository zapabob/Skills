---
name: comfyui-local-video
description: "Local video generation in ComfyUI Desktop on Windows."
version: 0.1.0
author: [hermes-agent]
license: MIT
platforms: [windows]
compatibility: "ComfyUI 0.27+, Comfy Desktop, NVIDIA CUDA."
prerequisites:
  commands: ["git", "python"]
---

# ComfyUI Local Video (Windows Desktop)

Use this skill when the user wants to run **local video generation in ComfyUI on Windows**, especially:
- MiniMax H3 via `ComfyUI_RH_MinMaxH3`
- GGUF/safetensors video checkpoints
- Comfy Desktop instead of manual install
- Custom-node setup + dual model-root layout + restart flow

## Trigger

- User says "ComfyUI で動画を作りたい" on Windows
- User has `.gguf` / `.safetensors` video weights and needs the matching plugin
- Comfy Desktop is installed under `AppData\Local\Comfy-Desktop\`
- Docs mention two roots: `models/MiniMax-H3/` and `models/diffusers/MiniMax-H3/`

## Platform Defaults

- Workspace: `C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\`
- Custom nodes: `<workspace>\custom_nodes\`
- Models: `<workspace>\models\`
- Use workspace venv for installs: `<workspace>\.venv\Scripts\python.exe -m pip install ...`
- `python` on PATH can be the Windows Store stub; prefer the venv python explicitly.

## Core Workflow

### 1. Identify model role and plugin

Confirm whether the file is a video DiT, text encoder, or VAE, then map it to the plugin's expected filenames and loaders.

For MiniMax H3, required pieces are:
- DiT partition: `MiniMax-H3-FL2VA-int8_convrot.safetensors` or `MiniMax-H3-Ref2VA-int8_convrot.safetensors`
- Text encoder: `qwen3-vl-32b-int8_convrot.safetensors`
- Video VAE: `MiniMax-H3-video_vae.safetensors`
- Audio VAE: `MiniMax-H3-audio_vae.safetensors`
- Upstream configs/tokenizer under `models/diffusers/MiniMax-H3/`

### 2. Install the plugin

```powershell
$ws = "C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI"
Set-Location "$ws\custom_nodes"
git clone https://github.com/HM-RunningHub/ComfyUI_RH_MinMaxH3.git
& "$ws\.venv\Scripts\python.exe" -m pip install -r ComfyUI_RH_MinMaxH3/requirements.txt
```

Restart Comfy Desktop afterwards.

### 3. Pin plugin-required dependency versions

Comfy Desktop may upgrade `transformers` above what the plugin allows.
If required, pin with the workspace venv:

```powershell
& "<workspace>\.venv\Scripts\python.exe" -m pip install "transformers>=4.57.0,<=5.8.1"
```

Also verify `accelerate`, `safetensors`, `sentencepiece`, `einops`, `Pillow`.

### 4. Place models in plugin-expected layout

```
<workspace>\models\
├── MiniMax-H3\
│   ├── MiniMax-H3-FL2VA-int8_convrot.safetensors
│   ├── MiniMax-H3-Ref2VA-int8_convrot.safetensors
│   ├── qwen3-vl-32b-int8_convrot.safetensors
│   ├── MiniMax-H3-video_vae.safetensors
│   └── MiniMax-H3-audio_vae.safetensors
└── diffusers\
    └── MiniMax-H3\
        ├── FL2VA\
        │   ├── transformer\
        │   ├── text_encoder\
        │   ├── video_vae\
        │   └── audio_vae\
        └── Ref2VA\
            └── ...
```

Filenames decide component type and partition; loaders filter by task.

### 5. HuggingFace auth and download on Windows

The old `huggingface-cli` entrypoint is deprecated in modern `huggingface_hub`. Use the workspace venv explicitly and prefer the `hf` CLI:

```powershell
& "<workspace>\.venv\Scripts\python.exe" -m pip install -U huggingface_hub
$env:HF_TOKEN = "hf_..."
& "<workspace>\.venv\Scripts\python.exe" -m huggingface_hub.cli.huggingface_cli login --token $env:HF_TOKEN
```

To download:

```powershell
$env:HF_TOKEN = "hf_..."
& "<workspace>\.venv\Scripts\python.exe" -m huggingface_hub.cli.huggingface_cli download Gluttony10/MiniMax-H3-INT8-CONVROT --local-dir "<workspace>\models\MiniMax-H3"
```

**Windows disk-space fallback**: If the system drive is low on free space, check all drives before downloading. MiniMax-H3 INT8-CONVROT is ~132 GB total (FL2VA 47GB + Ref2VA 47GB + Qwen3-VL 27GB + Video VAE 10GB + Audio VAE 0.6GB). On Comfy Desktop the default `--local-dir` path sits on the system drive; if free space is insufficient:

1. **Preferred**: Download to a secondary drive with sufficient space (e.g., `D:\ComfyUI_models\MiniMax-H3`) and create a **directory junction** pointing from the ComfyUI models path:
   ```powershell
   # Remove existing directory first (if any)
   Remove-Item -LiteralPath "<workspace>\models\MiniMax-H3" -Recurse -Force
   # Create junction
   New-Item -ItemType Junction -Path "<workspace>\models\MiniMax-H3" -Target "D:\ComfyUI_models\MiniMax-H3"
   ```

2. **Alternative**: Download to alternate drive, wait for completion, then copy/move into place.

**Critical**: Run `wmic logicaldisk get caption,size,freespace` or `Get-PSDrive` to check ALL drives before starting. On this host, C: had ~2.4GB free but D: had ~117GB free — the junction approach worked.

If auth/download still fails, download manually via browser and copy files into place.

### 6. Verify and run

1. Restart Comfy Desktop
2. Confirm `RunningHub/MiniMax H3/*` nodes appear
3. Load an example workflow from `examples/workflows/` in the plugin repo
4. Run `t2va.json` for text-to-video+audio or `fl2va_first_frame.json` for image-to-video

## MiniMax H3 Notes

- Tasks: T2VA, FL2VA, Ref2VA
- Recommended VRAM: 24 GB single GPU with INT8 + layerwise offload; 12 GB reports exist
- Sampler modes: `euler` (50 sigma points) or `res_multistep` (~21 sigma points)
- Audio is generated jointly, not post-dubbed

## Pitfalls

1. **GGUF alone is not enough.** A single `.gguf` is usually one component; video generation needs DiT + text encoder + video VAE + audio VAE.
2. **Two model roots are required.** Missing `models/diffusers/MiniMax-H3/` causes load failures.
3. **Comfy Desktop uses its own venv.** System `pip` installs won't affect the server.
4. **HuggingFace auth state is per-env.** One venv's login does not carry into another.
5. **Node registration happens at startup.** Restart Comfy Desktop after clone/update.
6. **License check.** MiniMax H3 weights may have territory clauses; verify before commercial use.
7. **Disk-space check is mandatory before full-model download.** MiniMax-H3 INT8-CONVROT totals ~132 GB. On Windows, default model paths live on the system drive; if free space is below ~150 GB, download to another drive first and copy into place, or use a directory junction.
8. **The user's existing GGUF may be one component, not the whole model.** Map the filename to the plugin's expected component before promising generation.

## Verification Checklist

- [ ] Plugin repo exists at `<workspace>\custom_nodes\ComfyUI_RH_MinMaxH3\`
- [ ] Plugin requirements installed with workspace venv python
- [ ] `transformers` matches plugin constraint when needed
- [ ] `models/MiniMax-H3/` contains DiT + text encoder + video_vae + audio_vae
- [ ] `models/diffusers/MiniMax-H3/` contains config/tokenizer/preprocessor
- [ ] Comfy Desktop restarted after install
- [ ] Nodes appear under `RunningHub/MiniMax H3/*`
- [ ] Example workflow loads without missing-node errors
