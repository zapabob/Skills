---
name: comfyui-model-management
description: Download large ComfyUI models to Windows junctions via HF.
category: mlops
tags: [comfyui, huggingface, windows, junctions, model-storage, large-models, disk-management]
---

# ComfyUI Model Management on Windows

Class-level skill for managing large ComfyUI model downloads and storage across multiple drives using Windows junctions. Handles HuggingFace CLI downloads, disk space constraints, file system errors, and multi-drive strategies.

## When to Use

- Downloading large models (>50GB) for ComfyUI on Windows
- C: drive (NVMe) critically low on space — need to offload models to secondary drives
- Multi-drive strategy: fast NVMe for cache/active, HDD/SSD for bulk storage
- HuggingFace `hf download` with `--local-dir` pointing to non-C: drives
- Windows junction (`mklink /J`) to link ComfyUI `models/` to external storage
- CRC errors / file system corruption on source drive during copy/move
- Insufficient disk space during atomic move (need 2x file size temporarily)

## Prerequisites

- HuggingFace CLI (`hf.exe`) authenticated with token
- ComfyUI installed (locate `models/` directory)
- Admin rights for `mklink /J` (junction creation)
- Multiple drives with sufficient free space

## Workflow

### 1. Locate ComfyUI Models Directory

```bash
# Typical ComfyUI Desktop install
C:\Users\<user>\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\models\
```

### 2. Plan Multi-Drive Strategy

| Drive | Role | Example |
|-------|------|---------|
| C: (NVMe) | Runtime cache, active tensors, HF cache | Keep ~10GB free |
| D: (HDD) | Primary model storage | 100GB+ free |
| E: (SSD/HDD) | Overflow / secondary | 500GB+ free |

### 3. Create Target Directory & Junction

```powershell
# Create model directory on target drive
mkdir D:\ComfyUI_models\MiniMax-H3

# Remove existing ComfyUI model dir (if empty or backed up)
Remove-Item 'C:\...\models\MiniMax-H3' -Recurse -Force

# Create junction
New-Item -ItemType Junction -Path 'C:\...\models\MiniMax-H3' -Target 'D:\ComfyUI_models\MiniMax-H3'
```

### 4. Download with HuggingFace CLI

```bash
export HF_TOKEN="hf_xxx"
hf download <repo_id> --local-dir D:\ComfyUI_models\MiniMax-H3
```

### 5. Handle Disk Space Errors

**Error**: `IO Error: ディスクに十分な空き領域がありません。 (os error 112)`

**Cause**: Atomic move during download needs 2× file size free on target drive.

**Fixes**:
- Free space on target drive (move other files, cleanup)
- Download to drive with more space (E:)
- Use `--include` to download one file at a time

### 6. Handle CRC Errors (File System Corruption)

**Error**: `CRC エラー` / `Data error (cyclic redundancy check)` during copy/move

**Cause**: Source drive file system corruption.

**Fixes**:
- `robocopy` with `/R:0 /W:0` (no retry) — may still fail
- **Best**: Re-download directly to healthy drive (E:)
- Run `chkdsk D: /f /r` after recovery

### 7. Consolidate Across Drives

If models split across D: and E:, point junction to the drive with complete set:

```powershell
# Remove old junction
Remove-Item 'C:\...\models\MiniMax-H3' -Force

# Create new junction to complete set
New-Item -ItemType Junction -Path 'C:\...\models\MiniMax-H3' -Target 'E:\ComfyUI_models\MiniMax-H3'
```

## MiniMax H3 INT8 CONVROT Specifics

| File | Size | Required for |
|------|------|--------------|
| `MiniMax-H3-FL2VA-int8_convrot.safetensors` | 47 GB | T2V (Text-to-Video) |
| `MiniMax-H3-Ref2VA-int8_convrot.safetensors` | 47 GB | I2V (Image-to-Video) — deferrable |
| `qwen3-vl-32b-int8_convrot.safetensors` | 27 GB | Text encoder |
| `MiniMax-H3-video_vae.safetensors` | 10 GB | Video VAE |
| `MiniMax-H3-audio_vae.safetensors` | 0.6 GB | Audio VAE |
| `models/diffusers/MiniMax-H3/` | ~1 GB | Config + tokenizer |

**Minimum for T2V**: ~85 GB (FL2VA + Qwen3-VL + Video VAE + Audio VAE + config)

## VRAM Optimization (RTX 5060 Ti 16GB)

Edit `custom_nodes/ComfyUI_RH_MinMaxH3/minimax_h3_nodes/runtime/h3_settings.py`:

```python
ENABLE_DIT_LAYERWISE_OFFLOAD = True
OPT_ADALN_RELEASE_WEIGHTS = True
OPT_FUSED_QK_ROPE = True
DYNAMIC_ACTIVATION_RESERVE = True
LRU_RESIDENCY_POLICY = True
MAX_RESOLUTION = (832, 480)
MAX_FRAMES = 125  # 5 seconds
SAMPLER = "res_multistep"
STEPS = 21
```

## Verification Checklist

- [ ] Junction exists: `dir C:\...\models\MiniMax-H3` shows `<JUNCTION>`
- [ ] All required `.safetensors` files present in target
- [ ] File sizes match expected (no truncated downloads)
- [ ] ComfyUI loads model without "file not found" errors
- [ ] Test generation at 832×480, 125 frames, 21 steps works

## Storage-health and transfer gate

Before copying or loading a large model, map logical drives to physical disks with `Get-CimInstance Win32_DiskDrive | Select-Object Index,Model,Status`. A `Pred Fail` source or `STATUS_IN_PAGE_ERROR` takes precedence over loader debugging: stop retrying reads and reacquire the artifact on healthy media. A different drive letter is not an independent backup when both letters share the same physical disk.

For rescue copies, never use `/MIR`, never delete the source, and never treat robocopy exit code 0–7 as proof of success. Verify the destination exists, compare exact byte sizes, and retain/read the robocopy log; a failing source can report exit 0 with `Copied: 0, Failed: 1`.

For Hugging Face/Xet downloads, inspect the repository manifest and `X-Linked-Size`/`content-length` before starting. Budget temporary reconstruction/cache space in addition to final artifact size; insufficient headroom can raise OS error 112 even when the final file would fit. If the final file fits but Xet reconstruction does not, a direct resolve-URL stream may reduce temporary overhead; download to a temporary filename, verify completion and byte size, then rename. Do not claim recovery until those checks pass.

From Git Bash on Windows, prefix commands that pass Windows paths to `cmd.exe`, `robocopy`, or PowerShell with `MSYS_NO_PATHCONV=1`; otherwise drive paths can be mangled. Avoid complex inline PowerShell because nested quoting can drop `$variables`; use a temporary `.ps1` or `.py` script instead. For direct streams, use the final artifact's expected `X-Linked-Size` and do not mistake an early `curl` response/header size for completion.

For MiniMax-H3, keep raw NVFP4, INT8/convrot, and experimental configs in separate component trees. Do not infer provenance from filenames: the official `Gluttony10/MiniMax-H3-INT8-CONVROT` FL2VA file is roughly 47 GB, while similarly named local files may be about 12.5 GB and be a different artifact. Check the repository manifest rather than assuming `model_index.json` exists.

## Pitfalls & Gotchas

| Issue | Symptom | Fix |
|-------|---------|-----|
| Junction not followed | ComfyUI can't find models | Use `dir` to verify `<JUNCTION>` marker |
| HF cache on C: fills up | C: drive full during download | Set `HF_HOME=D:\\hf_cache` or symlink `.cache` |
| Atomic move needs 2× space | "Insufficient space" on 50GB free | Download to larger drive, or download one file at a time |
| CRC error on copy | Robocopy/powershell fails | Re-download to healthy drive; run `chkdsk` |
| Python `python` is Windows Store stub | `python` prints "Python" and exits | Use `py -3` or full venv path |
| Symlinks need admin (WinError 1314) | `os.symlink()` fails | Use `os.link()` (hardlink) for files on same volume — no admin needed |
| T2VATarget rejects 1280×720 | "width/height 必须按 32 对齐" | Use dimensions divisible by 32: 1280×704, 832×480, 640×640 |
| `/prompt` returns `no_prompt` | API rejects bare workflow JSON | Wrap in `{"prompt": {...}}` — see `references/minimax-h3-video-workflow.md` |
| INT8 convrot crashes on Blackwell | `Windows fatal exception: access violation` in `torch.storage.__getitem__` | INT8 **AND NVFP4** both segfault on RTX 5060 Ti + CUDA 13 + PyTorch 2.12/2.13. **Use BF16 non-quantized text encoder** — download `Qwen/Qwen3-VL-32B-Instruct` (62GB, 14 shards) and use `_load_qwen_bf16_checkpoint` path. See `references/minimax-h3-video-workflow.md` |
| ComfyUI Desktop auto-launches on 8188 | Workflow submission gets stale process / wrong pycache | `netstat -ano \| grep 8188` → `taskkill -PID … -F` → clear pycache → start venv instance. See `references/minimax-h3-video-workflow.md` |
| `text_encoder_path` absolute path rejected | `无法解析文本编码器模型名：<absolute_path>` | `text_encoder_path` must be **relative to `model_root`** (e.g. `"text_encoder"`, not `E:/...`)|
| `model_index.json` not found | `H3ComponentError: Could not find MiniMax H3 partition 'fl2va'` | Create Diffusers-style `model_index.json` with `_minimax_h3.partition` field |
| Incomplete model copies | Loader crashes / corrupt weights | Use hardlinks (`os.link`) not broken symlinks; verify file sizes match original |

## References

- `references/minimax-h3-download-log.md` — Session log of 132GB download with CRC recovery
- `references/windows-junction-cheatsheet.md` — Junction commands and verification
- `references/di[REDACTED_TOKEN].md` — Common disk space errors and fixes
- `references/minimax-h3-video-workflow.md` — Full API workflow spec, NVFP4 setup, config.json requirements, Blackwell crash workaround
- `scripts/submit_minimax_h3_workflow.py` — Reusable CLI script for submitting MiniMax-H3 T2VA workflow to ComfyUI API