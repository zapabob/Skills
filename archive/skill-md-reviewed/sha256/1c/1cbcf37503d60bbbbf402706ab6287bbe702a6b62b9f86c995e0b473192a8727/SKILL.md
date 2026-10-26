---
name: comfyui-local-api
description: Use for verified local ComfyUI REST and Tkinter GUI work.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    category: creative
    tags: [comfyui, api, tkinter, img2img, lora]
---

# Local ComfyUI API Integration

Use this class skill when building or repairing scripts or desktop GUIs that control a local ComfyUI server.

## Safety and scope

- Use `127.0.0.1` by default; do not add remote endpoints or save credentials.
- A GUI may stop only the ComfyUI process it started; never kill unrelated processes.
- Keep network work in daemon threads and update Tk widgets through `root.after(0, ...)`.

## REST contract

- Health: `GET /system_stats`.
- Checkpoint discovery: `GET /object_info/CheckpointLoaderSimple`; verify the exact filename in `input.required.ckpt_name[0]`.
- Submit API-format workflow: `POST /prompt` with `{"prompt": workflow}`; read `prompt_id`.
- Poll: `GET /history/{prompt_id}`. Treat `status_str == "error"` as a workflow failure; catch only transport/JSON errors while polling.
- Cancel: `POST /interrupt`.
- Image upload: multipart `POST /upload/image` with `image` and `type=input`; reference the returned server filename in `LoadImage`.

## Workflow invariants

A basic SDXL graph is `CheckpointLoaderSimple -> CLIPTextEncode -> KSampler -> VAEDecode -> SaveImage`. For img2img, add `LoadImage -> VAEEncode`; both VAE nodes must use checkpoint VAE output `[checkpoint_node, 2]`. When adding `LoraLoader`, rewire only model and CLIP through LoRA; keep VAE connected to the checkpoint node.

Use a relative `SaveImage.filename_prefix` such as `comfy_gui`; configure the output directory at server launch rather than embedding an absolute Windows path in the workflow.

## Windows low-VRAM launch

Use the ComfyUI venv Python and `main.py` with `--listen 127.0.0.1 --port 8188 --output-directory <dir> --lowvram --cache-none --disable-cuda-malloc`, and set `TQDM_DISABLE=1`. Initialization may take 60–90 seconds; wait for `/system_stats`.

## GUI pattern

Expose connection status, ComfyUI start/stop, generation stop, image selection, prompt/negative prompt, resolution, steps, CFG, seed, sampler, scheduler, denoise, and LoRA controls. Prefer a Desktop `.py` plus `.bat` launcher using the ComfyUI venv Python with `py -3` fallback.

## Verification gate

Completion requires:

1. `py_compile` and module import.
2. txt2img and img2img+LoRA workflow construction tests, including node counts and VAE wiring.
3. Live `/system_stats` and exact checkpoint discovery.
4. A minimal 384x512, one-image, low-step generation with a verified PNG in the configured output directory.

Report static checks, live API checks, generation output, and residual risks separately.

## Reference

See `references/windows-comfyui-desktop.md` for workstation-specific paths, launch command, verified workflow JSON, stability limits, and GUI layout.
