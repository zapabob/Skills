---
name: reference-guided-image-transformation
description: "Use for faithful reference-image transformations."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [image-to-image, reference-image, ComfyUI, style-preservation, lighting, VRChat-avatar]
---

# Reference-Guided Image Transformation

## When to Use

Use this skill when a user provides a reference image and requests a faithful variation that preserves the subject, composition, and rendering style while changing a constrained attribute such as brightness, warmth, color mood, or background cleanliness.

Use img2img rather than text-to-image when visual identity or pose continuity matters.

## Core workflow

1. Inspect the reference before generating. Record subject identity, hair, face, clothing, accessories, pose, camera distance and aspect ratio, rendering style, palette, background, and any text/UI that must be retained or removed.
2. Define the transformation boundary explicitly: preserve identity, outfit, pose, camera angle, composition, proportions, and rendering style; change only the requested attribute.
3. Prefer img2img over text-to-image. Use the reference as the latent input, resize with aspect-ratio preservation, encode with the checkpoint VAE, and sample with conservative denoising. Start around `denoise=0.30–0.40` for faithful edits; increase only if the requested change is not visible.
4. Put invariant features first in the positive prompt, then the requested edit. For brightening, use high-key daylight or soft warm-white illumination, gentle highlights, a cleaner brighter background, pastel color language, and natural contrast. Avoid vague prompts such as “make it better,” which encourage redesign.
5. Use a negative prompt for identity drift, altered outfit/hairstyle/pose, dark or gloomy exposure, photorealism when the source is 3D/anime, anatomy defects, duplicate subjects, text, UI, logos, watermarks, and unwanted explicitness.
6. Generate at a practical resolution and visually compare the output with the reference. Do not claim exact identity preservation without comparison.
7. Verify file existence, image decodability, dimensions, and the requested visual criteria separately. Report actual output paths and dimensions.

## ComfyUI implementation pattern

Use `LoadImage → ImageScale (Lanczos, crop disabled) → VAEEncode → KSampler → VAEDecode → SaveImage`. `CheckpointLoaderSimple` supplies the model and VAE; CLIP positive and negative encoders feed the sampler. The sampler latent must come from `VAEEncode`, not `EmptyLatentImage`.

A practical Animagine XL starting point is portrait output around 768×1360, 28 steps, CFG 5.5, Euler ancestral with the normal scheduler, and denoise 0.34. Adjust for source aspect ratio and available VRAM.

## Runtime pitfall

On affected Windows/NVIDIA installations, ComfyUI may fail during CUDA initialization because automatic `cudaMallocAsync` selection conflicts with the PyTorch allocator configuration. Use a per-process launch with `--disable-cuda-malloc` and without forcing conflicting allocator environment variables. This is a launch workaround, not a permanent global configuration edit.

If the ComfyUI environment lacks `requests`, use Python standard-library `urllib.request` for multipart upload, prompt submission, history polling, and output retrieval.

## Safety and provenance

Treat an avatar/reference image as fictional unless the user establishes otherwise. Keep transformations within the requested non-explicit boundary. Do not add third-party logos, trademarks, watermarks, or copied platform UI. Preserve or remove source text/UI only according to the user's request.

## References

- `references/bright-img2img-comfyui.md` — validated prompt structure, API graph, startup workaround, and evidence checklist.
