---
name: comfyui-windows-multidrive-model-setup
description: Set up ComfyUI multi-drive model storage with junctions.
category: mlops
tags: [comfyui, windows, multi-drive, huggingface, model-download, vram-optimization, junction]
---

# ComfyUI Windows Multi-Drive Model Setup

## Overview
Configure ComfyUI Desktop on Windows to handle large models (100GB+) across multiple drives when C: (NVMe) is critically low on space. Uses junctions to redirect `models/` to larger drives, downloads with `hf.exe --local-dir`, and applies VRAM optimizations for 16GB GPUs.

## Drive Strategy (Example Layout)
| Drive | Type | Free Space | Role |
|-------|------|------------|------|
| C: | NVMe | ~2 GB | **Active inference cache only** — never store models here |
| D: | HDD | ~117 GB | **Primary model storage** — ComfyUI `models/` junction target |
| E: | HDD/SSD | ~379 GB | **Large overflow** — models >40 GB that exceed D: move headroom |
| H: | HDD | ~24 GB | **Secondary overflow** — smaller models, temp files |

**Key lesson from MiniMax H3 setup**: When D: has <60 GB free, 47 GB files (FL2VA, Ref2VA) cannot atomically move from HF cache to target (requires 2× free). Use E: as dedicated overflow for largest files, then junction to E: instead of D:.

## Prerequisites
- ComfyUI Desktop installed (e.g., `C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\`)
- Python venv with `huggingface_hub[hf_transfer]` installed
- HuggingFace token with access to target repos
- Admin rights for junction creation (`mklink /J` or `New-Item -ItemType Junction`)

## Steps

### 1. Create Model Directory on Primary Drive (D:)
```powershell
mkdir D:\ComfyUI_models\MiniMax-H3
```

### 2. Remove Existing Models Dir & Create Junction
```powershell
# Remove ComfyUI's default models/MiniMax-H3 if exists
Remove-Item -LiteralPath 'C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\models\MiniMax-H3' -Recurse -Force -ErrorAction SilentlyContinue

# Create junction pointing to D:
New-Item -ItemType Junction -Path 'C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\models\MiniMax-H3' -Target 'D:\ComfyUI_models\MiniMax-H3'
```

### 3. Download Models with HF CLI to Target Drive
```bash
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxx"
hf.exe download Gluttony10/MiniMax-H3-INT8-CONVROT --local-dir D:\ComfyUI_models\MiniMax-H3
```

### 4. Handle Disk Space During Large File Moves
**Critical**: HF downloads to `.cache/huggingface/download/` then atomically moves to target. This requires **2× file size** free on the *target drive* during the move.

If D: has insufficient headroom for a 47 GB file (needs >94 GB free during move):
1. **Download largest files directly to overflow drive (E:)** with `--include`:
   ```bash
   # Download FL2VA (47 GB) to E:
   hf.exe download Gluttony10/MiniMax-H3-INT8-CONVROT --include "MiniMax-H3-FL2VA-int8_convrot.safetensors" --local-dir E:\ComfyUI_models\MiniMax-H3
   ```
2. **Move from HF cache to final model dir on E:**:
   ```powershell
   Move-Item "E:\ComfyUI_modelsMiniMax-H3\MiniMax-H3-FL2VA-int8_convrot.safetensors" "E:\ComfyUI_models\MiniMax-H3\"
   ```
3. **Point junction to E: instead of D:** for the model directory:
   ```powershell
   New-Item -ItemType Junction -Path 'C:\...\models\MiniMax-H3' -Target 'E:\ComfyUI_models\MiniMax-H3'
   ```
4. **For corrupted source drive files (CRC errors)**: Do NOT attempt to copy/move. Re-download directly to healthy drive (E:) with `--include`.
5. **Use background downloads** (`background=true, notify_on_complete=true`) for 100GB+ downloads to avoid 600s foreground timeout.

### 5. Verify Files in ComfyUI Models Dir
```bash
ls -la "C:/Users/<user>/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyGUI/ComfyUI/models/MiniMax-H3/"
```
Should show all `.safetensors` files via the junction.

### 6. Apply 16GB VRAM Optimizations (MiniMax H3)
Edit `custom_nodes/ComfyUI_RH_MinMaxH3/minimax_h3_nodes/runtime/h3_settings.py`:
```python
ENABLE_DIT_LAYERWISE_OFFLOAD = True      # Offload DiT layers to CPU
OPT_ADALN_RELEASE_WEIGHTS = True         # Release adaLN weights after use
OPT_FUSED_QK_ROPE = True                 # Fused QK-RoPE kernel
DYNAMIC_ACTIVATION_RESERVE = 2           # GB reserved for activations
LRU_RESIDENCY_POLICY = True              # LRU cache for layer weights
MAX_RESOLUTION = (832, 480)              # Max resolution for 16GB
MAX_FRAMES = 125                         # 5 seconds at 25fps
DEFAULT_SAMPLER = "res_multistep"        # 21 steps recommended
```

## MiniMax H3 NVFP4 Model Files (Alternative to INT8)
| File | Size | Source Repo |
|------|------|-------------|
| `minimax_h3_fl2va_pruned_nvfp4.safetensors` | 11.7 GB | `lilcheaty/MiniMax-H3-NVFP4` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 14.6 GB | `lilcheaty/MiniMax-H3-NVFP4` |
| `qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors` | 14.6 GB | `sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4` |
| `minimax_h3_video_vae_fp16.safetensors` | 4.9 GB | `lilcheaty/MiniMax-H3-NVFP4` |
| `minimax_h3_audio_vae_fp32.safetensors` | 0.6 GB | `lilcheaty/MiniMax-H3-NVFP4` |

**NVFP4 total**: ~32 GB (vs ~85 GB INT8). However, NVFP4 triggers the
Blackwell segfault (see pitfalls). BF16 alternative: ~62 GB from
`Qwen/Qwen3-VL-32B-Instruct` (non-quantized, avoids segfault).

## MiniMax H3 INT8 CONVROT Model Files
| File | Size | Required For |
|------|------|--------------|
| `MiniMax-H3-FL2VA-int8_convrot.safetensors` | 47 GB | T2V (Text-to-Video) |
| `MiniMax-H3-Ref2VA-int8_convrot.safetensors` | 47 GB | I2V (Image-to-Video) — *deferrable* |
| `qwen3-vl-32b-int8_convrot.safetensors` | 27 GB | Text encoder (required) |
| `MiniMax-H3-video_vae.safetensors` | 10.4 GB | Video VAE (required) |
| `MiniMax-H3-audio_vae.safetensors` | 0.6 GB | Audio VAE (required) |
| `models/diffusers/MiniMax-H3/` | ~1 GB | Config + tokenizer |

**Minimum for T2V only**: ~85 GB (FL2VA + Qwen3-VL + Video VAE + Audio VAE + config)

## Pitfalls & Workarounds
- **Blackwell (sm_120) segfault loading NVFP4/INT8 quantized Qwen3-VL weights**: `torch.storage.__getitem__` access violation in `loading.py` when `safe_open(framework="pt")` reads float8_e4m3fn tensors. NOT fixed by PyTorch 2.13.0, NOT caused by comfy_aimdo, NOT caused by quantization format. **Working alternative**: use BF16 non-quantized text encoder (`Qwen/Qwen3-VL-32B-Instruct`, ~62GB) which routes through Transformers `from_pretrained()` and avoids the streaming safetensors path. BF16 text encoder confirmed: 62.14GB, 14 shards, `Qwen/Qwen3-VL-32B-Instruct` (requires HF auth). Point `text_encoder_path` to the BF16 dir in the workflow; BF16 loads via Transformers `from_pretrained()` which avoids the segfault path entirely.
- **numpy framework workaround insufficiency**: `safe_open(framework="numpy")` bypasses `torch.storage.__getitem__` but numpy lacks native `float8_e4m3fn` support. Even with `ml_dtypes`, subsequent `tensor.to(device=...)` in `_flush_linear_bag` re-enters the storage path and segfaults. Only the BF16 non-quantized path fully avoids this.
- **ComfyUI Desktop auto-launch**: ComfyUI Desktop can silently launch its own ComfyUI process on port 8188. Always `netstat -ano | grep 8188` → `taskkill -PID <pid> -F` → clear pycache → start your venv instance.
- **Junction creation fails**: Ensure target dir exists and source dir is fully removed. Run PowerShell as Admin.
- **Existing symlink instead of junction**: `ls -la` shows `lrwxrwxrwx` / `dir /al` shows `<SYMLINKD>`. Remove with `rm` (not `rd`/`Remove-Item`), then create junction with `New-Item -ItemType Junction`.
- **HF download fails with "Disk full" (os error 112)**: Target drive needs 2× largest file free during atomic move. Download largest files to overflow drive (E:) with `--include` and `--local-dir`.
- **Source drive filesystem corruption (CRC errors)**: `robocopy`/`Copy-Item`/`Move-Item` fail with error 23 (0x17). Files appear in `dir` but cannot be read. **Do not attempt to recover** — re-download affected files directly to healthy drive (E:).
- **HF download stalls on lock files**: Kill any `python`/`hf` processes holding locks: `taskkill /f /im python.exe /im hf.exe`
- **C: drive critically low**: Move `%TEMP%`, browser caches, pip/uv caches to D:/E:. Use `windows-di[REDACTED_TOKEN]` skill.
- **ComfyUI can't find models**: Verify junction with `dir /al` shows `<JUNCTION>` and target path is correct.
- **VRAM OOM on 16GB**: Enable all optimizations above, reduce resolution to 832×480, use `res_multistep` 21 steps, limit to 5s/125 frames.

## Verification Checklist
- [ ] Junction shows `<JUNCTION>` in `dir /al` output
- [ ] All required `.safetensors` files present in ComfyUI `models/` via junction
- [ ] `h3_settings.py` has VRAM optimizations enabled
- [ ] ComfyUI launches and loads MiniMax H3 nodes without OOM
- [ ] Test generation at 832×480, 125 frames completes successfully

## Related Skills
- `windows-di[REDACTED_TOKEN]` — Free up C: space for cache
- `windows-inference-server` — Multi-drive venv patterns
- `hypura-local-llm-serving` — NVMe-tiered inference concepts
- `local-llm-server` — General local model serving patterns

## References
- `references/minimax-h3-model-files.md` — Model file details and sizes
- `references/vram-optimization-16gb.md` — Detailed VRAM optimization rationale
- `references/junction-troubleshooting.md` — Common junction issues and fixes
- `references/blackwell-nvfp4-segfault-workaround.md` — Blackwell sm_120 segfault on NVFP4/INT8 quantized Qwen3-VL weights, full diagnosis and BF16 workaround
- `scripts/submit_workflow.py` — Submit MiniMax H3 T2VA workflow to ComfyUI /prompt endpoint (argparse CLI, polls for completion)