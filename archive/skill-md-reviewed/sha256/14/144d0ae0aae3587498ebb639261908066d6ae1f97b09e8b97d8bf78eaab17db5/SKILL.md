---
name: comfyui-adult-anime-images
description: "Use for local ComfyUI adult-fictional anime glamour images."
version: 1.0.0
license: MIT
metadata:
  hermes:
    category: creative
    tags: [comfyui, sdxl, anime, image-generation, verification]
---

# ComfyUI Adult Fictional Anime Images

Class-level workflow for local ComfyUI/SDXL generation of clearly adult fictional anime characters in non-explicit glamour/editorial styles. Use original characters and original branding. Do not reproduce real services' logos, trademarks, or complete UI layouts.

## Content boundary

Increase provocative styling through mature wardrobe, pose, gaze, lighting, and editorial composition. Keep the character clearly adult and fictional. Exclude minors, youthful presentation, real people, copyrighted characters, sexual acts, exposed genitals, explicit nudity, and pornographic detail. When a user asks for more lewdness, redirect to stronger but still non-explicit glamour.

For platform-like thumbnails, use only an original black-and-orange palette, original title text, and original frame/badge layout. Do not copy a real service's logo, trademark, or full interface.

## Implementation

1. Verify the model card, official source, license, expected file size, and sampler guidance before downloading.
2. For constrained storage, prefer a direct Hugging Face `resolve/main/...` stream to the destination to avoid Hub/Xet temporary reconstruction overhead. On Git Bash/MSYS, use `MSYS_NO_PATHCONV=1` for native Windows paths.
3. Put large checkpoints in an external model root through `extra_model_paths.yaml`, such as `base_path: H:/ComfyUI_models` and `checkpoints: checkpoints`.
4. Use API-format workflow JSON, not editor-format JSON. The minimal graph is `CheckpointLoaderSimple -> CLIPTextEncode positive/negative -> EmptyLatentImage -> KSampler -> VAEDecode -> SaveImage`.
5. For Animagine XL / SDXL, start with Euler Ancestral, 25–28 steps, CFG 4–7, and dimensions divisible by 32. Reduce dimensions when VRAM is tight.
6. State adulthood and fiction in the positive prompt, e.g. `clearly adult fictional woman in her late 20s, original character`. Put minor/youth, real-person, copyrighted-character, explicit-content, logo, trademark, and watermark exclusions in the negative prompt.
7. Keep raw generation and thumbnail composition separate. Add original black/orange framing and labels in post-processing.

## Blackwell SafeTensors compatibility

On RTX 50-series/Blackwell systems, a numpy-based SafeTensors wrapper may be used to avoid native PyTorch storage faults for quantized weights. Any wrapper exposed to ComfyUI must preserve the reader interface, especially `metadata()`; delegate it to the inner reader. After changing the wrapper, restart ComfyUI and test a normal checkpoint load. Do not edit model weights to compensate for a wrapper API mismatch.

The known compatibility failure is an `AttributeError` when ComfyUI calls `f.metadata()` on a wrapper that only implemented tensor access. The minimal fix is:

```python
def metadata(self):
    return self._inner.metadata()
```

## Verification gates

Treat these as separate claims:

- Model integrity: exact size, SafeTensors metadata, and expected key count.
- Workflow integrity: JSON parsing, required node classes, and valid node references.
- Runtime: `/system_stats`, `/queue`, `/history/<prompt_id>`, and `execution_success`.
- Output integrity: reopen with Pillow after `verify()`, confirm PNG format and dimensions.
- Visual review: adult/fictional/non-explicit content, absence of real people/logos/copied UI, readable text, and obvious anatomy defects.

A successful API job does not prove visual or rights compliance. Record failed checks honestly.

## References

Session-specific paths, prompts, exact verification fixture, and the original thumbnail compositor belong in `references/session-animagine-sdxl.md`.
