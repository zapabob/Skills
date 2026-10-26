---
name: comfyui-blackwell-gpu
description: "Fix PyTorch allocator/segfault on Blackwell GPUs in ComfyUI."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [ComfyUI, Blackwell, RTX-5060, Segfault, CUDA]
---

# ComfyUI on Blackwell GPUs (RTX 5060 Ti / 5090)

Work around PyTorch 2.13.0+cu130 issues on NVIDIA Blackwell architecture (sm_120):
1. `cudaMallocAsync != native` allocator mismatch assertion failure
2. `torch.storage.__getitem__` segfault when loading quantized/BF16 weights via `safetensors`

## When to Use

- ComfyUI Desktop on RTX 5060 Ti / 5090 with CUDA 13 / PyTorch 2.13.0+cu130
- Server crashes with `RuntimeError: Allocator backend parsed at runtime != allocator backend parsed at load time`
- Segfault (`Windows fatal exception: page error`) in `transformers/modeling_utils.py` when loading safetensors
- MiniMax-H3, Flux, or other models using Qwen3-VL text encoder or quantized weights

## Prerequisites

- ComfyUI Desktop with `.venv` at `C:\\Users\\<user>\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyGUI\\ComfyUI\\.venv\\`
- `ml_dtypes` pip package for BF16 numpy support
- `safetensors` package (patched via `sitecustomize.py`)

## Root Causes

### 1. CUDA Allocator Mismatch

PyTorch 2.13.0+cu130 defaults to `cudaMallocAsync` on Blackwell, but some libraries (e.g., `comfy-aimdo`) load with `native` backend, causing assertion failure at `CUDAAllocatorConfig.cpp:50`.

**Fix**: Force `backend:native` before importing torch.

### 2. safetensors `storage.__getitem__` Segfault

`safe_open(framework="pt")` → `PySafeSlice.__getitem__` → `torch.storage.__getitem__` access violation on Blackwell when reading `float8_e4m3fn` (NVFP4/INT8) or even `bfloat16` tensors.

**Fix**: Monkey-patch `safetensors.safe_open` and `safetensors.torch.load_file` to use `framework="numpy"` + copy to torch tensor via `torch.from_numpy()`.

## How to Run

### 1. Apply sitecustomize.py Patch

Place in `.venv/Lib/site-packages/sitecustomize.py`:

```python
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "backend:native"

def _patch_safetensors():
    import safetensors
    _orig_safe_open = safetensors.safe_open
    import numpy as np, torch, ml_dtypes

    class _NumpySafeReader:
        def __init__(self, filename, framework, device):
            self._inner = _orig_safe_open(filename, framework="numpy", device="cpu")
        def keys(self): return self._inner.keys()
        def get_slice(self, key): ...
        def get_tensor(self, key):
            arr = self._inner.get_tensor(key)
            if arr.dtype == ml_dtypes.bfloat16:
                return torch.from_numpy(arr.astype(np.float32).copy()).to(torch.bfloat16)
            return torch.from_numpy(arr.copy())
        def get_tensors(self):
            return {k: self.get_tensor(k) for k in self.keys()}
        def __enter__(self): return self
        def __exit__(self, *a): return self._inner.__exit__(*a) if hasattr(self._inner, '__exit__') else False

    def _patched(filename, framework="pt", device="cpu", backend="mmap"):
        if framework == "pt":
            return _NumpySafeReader(filename, framework, device)
        return _orig_safe_open(filename, framework=framework, device=device, backend=backend)

    safetensors.safe_open = _patched

    # Also patch safetensors.torch.load_file
    import safetensors.torch as torch_module
    def _patched_load_file(filename, device="cpu", *, backend="mmap"):
        with _patched(filename, "numpy", device, backend) as f:
            return f.get_tensors()
    torch_module.load_file = _patched_load_file

_patch_safetensors()
```

### 2. Start ComfyUI with Correct Allocator

```bash
cd "C:/Users/<user>/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyGUI/ComfyUI"
PYTORCH_CUDA_ALLOC_CONF=backend:native .venv/Scripts/python -m main --listen 127.0.0.1 --port 8188 --disable-auto-launch --cuda-device 0
```

Or use `sitecustomize.py` which sets the env var early.

### 3. Verify

```bash
PYTORCH_CUDA_ALLOC_CONF=backend:native .venv/Scripts/python -c "
import torch
print('CUDA:', torch.cuda.is_available(), torch.cuda.get_device_name(0))
print('PyTorch:', torch.__version__)
"
# Expected: NVIDIA GeForce RTX 5060 Ti : native
```

## Pitfalls

- **Allocator must be set BEFORE `import torch`** — `sitecustomize.py` or shell env var works; `os.environ` after import does not.
- **ComfyUI Desktop auto-launches competing process** on port 8188 — kill with `netstat -ano | grep 8188` → `taskkill -PID <pid> -F` before starting.
- **`ml_dtypes` required** for `numpy.bfloat16` support: `pip install ml_dtypes`.
- **BF16 → FP32 → torch.bfloat16 copy** avoids `torch.from_numpy` BF16 segfault (unsupported ScalarType).
- **Quantized weights (NVFP4/INT8) still segfault** — use BF16 non-quantized models (e.g., `Qwen/Qwen3-VL-32B-Instruct`) loaded via Transformers `from_pretrained()`.
- **`sitecustomize.py` patch can cause `MemoryError` / `PyObject pointer is null` on large checkpoints** — the numpy-route copies every tensor into RAM, which can exhaust memory on 6–7GB checkpoints. If ComfyUI crashes during checkpoint load with `pyo3_runtime.PanicException` or `MemoryError`, temporarily rename `.venv/Lib/site-packages/sitecustomize.py` before starting ComfyUI. This removes the safetensors workaround, so only use it when the model/weights are known-good for direct torch loading, and restore the patch afterward if needed for other models.
- **Large checkpoint + 32GB RAM is unstable on this machine** — prefer smaller checkpoints or lower resolutions (`384x512`) when using a single 6.9GB model; clear the queue between runs and watch VRAM/RAM headroom.
- **llama-server competes for RAM and can starve ComfyUI** — on this Windows machine, running `llama-server.exe` simultaneously with ComfyUI can cause prompt timeouts or segfaults even when VRAM appears free. Before heavy generation, stop llama-server first (`tasklist | findstr llama-server.exe` → `taskkill /F /IM llama-server.exe`), then restart ComfyUI. This is especially important for single-6.9GB-checkpoint setups on 32GB RAM.
- **Single-prompt submission + queue inspection is more reliable than batch scripts on unstable Windows setups** — when a batch script times out, inspect `/api/queue` and `/api/history/<prompt_id>` directly rather than assuming the server is ready for the next prompt. Clear pending items with `POST /api/queue {"clear": true}` before retrying.

## Related Skills

- `comfyui-minimax-h3-blackwell` — MiniMax-H3 specific workflow using this workaround

## Verification

```bash
curl -s "http://127.0.0.1:8188/system_stats"
# Should return JSON with pytorch_version: "2.13.0+cu130" and device: "cuda:0 NVIDIA GeForce RTX 5060 Ti : native"
```