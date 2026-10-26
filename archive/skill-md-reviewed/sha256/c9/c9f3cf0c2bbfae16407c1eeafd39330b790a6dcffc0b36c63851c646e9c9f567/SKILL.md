---
name: comfyui-quantized-model-debugging
description: "Use when quantized ComfyUI models crash or hang."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [ComfyUI, safetensors, quantization, Blackwell, debugging]
    category: mlops
---

# ComfyUI Quantized Model Debugging

Use this class-level skill when quantized or mixed-precision ComfyUI models crash, hang, or leave `/history/<prompt_id>` empty on Windows, especially on NVIDIA Blackwell GPUs.

## Core rules

- `/prompt` acceptance, `node_errors: {}`, and a `running` queue entry are not execution proof.
- Do not repeatedly resubmit while the loader is unverified.
- Keep NVFP4, INT8-CONVROT, and BF16 artifacts in separate component directories.
- Never invent quantization metadata; use the artifact's official loader contract.
- Test boundaries in order: header → representative tensors → component loader → minimal graph → full workflow.

## Diagnostic sequence

1. Record GPU, CUDA, PyTorch, safetensors, NumPy, RAM, allocator, and ComfyUI versions.
2. Read safetensors headers on CPU. Record key count, representative shapes/dtypes, quantization suffixes, and curve-table keys.
3. Compare config and checkpoint. A checkpoint containing `adaln_t_table` is a curve-table variant; its config must match the table grid and rank.
4. Test U8/INT8 payload and F8/FP8 scale tensors separately in a fresh process with `faulthandler` enabled.
5. For INT8 ComfyUI loaders, test with ComfyUI's `comfy.ops` available. A standalone `ModuleNotFoundError` only proves the test environment is incomplete.
6. Load one component at a time. Add text encoder, VAE, LoRA, and sampler incrementally.
7. Run a minimal low-resolution, short-duration graph and verify history completion, execution messages, logs, and output files before scaling up.

## Blackwell safetensors guidance

Validate a global safetensors monkey-patch for every dtype it reads. A patch that handles BF16 or U8 may still crash on F8_E4M3 scale tensors. If `faulthandler` reports a page fault in `sitecustomize.py` during `get_tensor()` for F8_E4M3 `weight_scale`, isolate or remove that read path before retrying workflows.

## Memory planning

Calculate model footprint before selecting fallbacks. A BF16 Qwen3-VL-32B text encoder around 62 GB is not practical on a host with about 34 GB physical RAM. Verify the actual size and hash of any INT8 alternative before treating it as installed.

## MiniMax-H3 guidance

The documented RH_MinMaxH3 converted format is the flat INT8-CONVROT set from `Gluttony10/MiniMax-H3-INT8-CONVROT`; configs and tokenizer/processor files belong in the documented diffusers component layout. The official FL2VA filename carries partition evidence. An NVFP4 filename from another repository is not automatically accepted by the INT8/convrot loader.

`resolve_component(model_root, keys, *, explicit=None, required_files=())` takes `keys` positionally and `explicit` as a keyword-only argument. `transformer_path` identifies a component directory; `transformer_weights` identifies a converted flat file.

## Evidence standard

Report a model as working only after completed execution and a verified artifact. Keep prompt IDs, history status, logs, and output paths as evidence. A listening server is not proof that the model loaded.

## Windows runtime stability

On Windows, headless ComfyUI runs can fail in non-interactive shells with `tqdm`/`asyncio` stderr flush errors. Prefer `TQDM_DISABLE=1` and a minimal graph. Also treat orphan recovery notices as state-inspection signals: before retrying, verify whether the previous side effect actually completed.

## Memory and queue management

Do not pile multiple 512x512 prompts against a single 6.9GB checkpoint on a 32GB host. Clear the queue, serialize runs, and use smaller resolutions or smaller batches when `/history/<id>` shows repeated `execution_error` or the output directory does not advance.

## References

- `references/quantized-blackwell-session-lessons.md` — loader contracts, curve-table checks, F8 crash signature, memory guidance, and evidence rules.
