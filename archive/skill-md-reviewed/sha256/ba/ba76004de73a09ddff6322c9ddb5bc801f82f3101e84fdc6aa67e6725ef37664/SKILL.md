---
name: colab-bonsai-lora
description: Train Bonsai 2 with QLoRA on Google Colab A100, diagnose Drive save failures, resume verified checkpoints, merge Safetensors, build PrismML llama.cpp and evaluate a quantized GGUF. Use for Colab CLI, Colab MCP or notebook workflows involving Bonsai and Google Drive.
---

# Colab Bonsai LoRA

Read `references/workflow.md` for execution and capacity requirements. The bundled scripts implement an experimental text-only Bonsai 2 pipeline. Do not claim successful training or export until the corresponding Drive artifacts and actual reports exist.

## Establish the runtime

Confirm the exact HF model/revision and user's intended outputs from their request and available files. Reconstruction accepts only `prism-ml/Ternary-Bonsai-2-27B-mlx-2bit` schema 2, affine 2-bit groups of 128 and explicit Hadamard signs. It unfolds rotations into ordinary FP16 weights; it does not edit ternary bits in place. Other model formats require a separate validated loader. Treat numerical equivalence and quality as unverified until measured.

Prefer the user's available official Colab CLI or connected notebook. Official `colab-mcp` requires a local MCP client and `notifications/tools/list_changed`; do not invent a remote HTTP endpoint or host its local browser proxy on Sites. CLI authentication and a signed-in browser are distinct sessions; never transfer browser cookies or credentials into the CLI.

For local CLI: provision `colab new -s bonsai2-a100 --gpu A100 --high-mem`, then `colab drivemount -s bonsai2-a100`. Use bundled `colab_cli_run.py --stage bootstrap`, which sends all sibling dependencies. CLI timeout is in seconds. `colab auth` authenticates the VM for GCP services, not the CLI itself. Windows CLI is unsupported by the documented release; use notebooks or an appropriate supported environment.

For notebooks: use `assets/Bonsai2_Nimble_Pipeline.ipynb`, which embeds executable sources. Select A100/high-memory and run the Drive mount cell. Follow active browser permission and authentication rules if interaction is required.

Run `scripts/bootstrap.py` only inside Colab after mounting Drive. Verify `A100_DRIVE_READ_WRITE_OK`, then confirm `connection_check.json` through Drive API/Web. A directory named MyDrive alone is insufficient. Do not start cloud training in the local Codex CPU workspace.

## Execute and verify

Set `BONSAI_ROOT` to a new directory when changing data/model/settings. Default is `/content/drive/MyDrive/bonsai2-nimble`; preserve initial Bonsai runs in `nimble-train`. Plan about 150–180 GiB Drive and 85 GiB local space; DriveFS free-space reporting is advisory and quota failures stop the run.

1. `scripts/stage1_fetch_to_drive.py`: pin source revision, verify downloads, preserve Nimble `.git`, reconstruct language tensors with resume progress. Check `base/COMPLETE.json` and HF key/shape coverage. Shape coverage alone is not full numerical parity.
2. `scripts/stage2_qlora_train.py`: require A100, NF4/BF16 compute, prepare k-bit model, candidate-only classification. Score labels use type-aware target conversion. Keep eval sealed until training ends; dev comes from train. Save optimizer/scheduler/RNG and adapter every 25 steps, including the short final accumulation window. Check `adapters/LATEST.json`, complete manifest and measured `nimble_contract.json`.
3. `scripts/stage3_merge_eval.py`: label NF4+adapter evaluation explicitly; stream FP16 plus LoRA delta without loading 27B CPU weights together. Check `merged/COMPLETE.json`; adapter/data/base signatures must match.
4. `scripts/stage4_build_quantize.py`: pin `PrismML-Eng/llama.cpp` prism branch commit, build CUDA SM80, export GGUF and verify Drive hash. Default `QUANT_TYPE=Q4_K_M`; PQ2_0/PTQ1_0 are experimental after unfolding/LoRA and do not preserve the original lattice by assumption. Check runtime/export manifests.
5. `scripts/stage5_eval_export.py`: run actual GGUF through local llama-server, verify token IDs, use raw log probabilities and candidate-only softmax. Missing candidates are failures. Check `exports/<quant>/evaluation.json` with n, errors, GGUF hash and source commit before reporting quality.

Never equate NF4+adapter evaluation with the merged or quantized output. Labels may be provisional; report agreement, not guaranteed correctness. Never invent accuracy, GPU usage or runtime duration.

## Recovery and limits

Resume a stage when model/data/settings/dependency fingerprints match. Save to unique version directories, verify copies, then update COMPLETE/LATEST. Never treat a partial download, merge, subprocess failure or absent evaluation as DONE. Preserve the last good checkpoint; do not delete user artifacts without authorization. DriveFS readback is not proof of service synchronization: verify final artifacts via Drive API/Web before disconnecting.

If a mount or authorization blocks execution, finish independently authorized repair/package work and explain the exact blocked step. Return concrete artifacts without claiming the A100 run completed. Do not publish data/weights to Sites or elsewhere unless requested.

Prism Linux SM80 binaries are for A100 Linux; rebuild for other operating systems/GPUs. Local tests validate guards, reconstruction algebra, score contracts and merge; they cannot validate GPU memory, full numerical parity or quality. See `references/model_contract_check.json` for the 851-key shape comparison and its limits.
