---
name: colab-gpu-workbench
description: Run Python scripts or Jupyter notebooks on short-lived Google Colab GPU runtimes from Codex on Windows through WSL, recover artifacts, diagnose Colab access, and move inputs or outputs through the installed Google Drive plugin. Use for Colab, free GPU, CUDA offload, remote Python execution, notebook execution, or Drive-backed GPU jobs.
---

# Colab GPU Workbench

Use the plugin's MCP tools for bounded Colab execution. On Windows, the tools bridge to the official `google-colab-cli` installed in the Ubuntu WSL2 distribution.

## Required routing

For Google Drive discovery, download, upload, organization, or verification, load and follow `[@google-drive](plugin://google-drive@openai-curated)`. Do not copy the Drive skill into this plugin and do not use browser automation as a substitute for the connector.

Use Google Drive as the durable transfer surface rather than invoking interactive `colab drivemount` from an agent. Materialize a Drive input with the Drive connector, pass the observed local workspace path to `colab_gpu_run.input_files`, download Colab outputs locally, then upload those observed local paths with the Drive connector. Verify every Drive write by metadata readback before sharing its URL.

## First-use flow

1. Call `colab_gpu_diagnose`. This is read-only and must not allocate a runtime.
2. If the CLI is missing or outdated, run `scripts/bootstrap_colab_wsl.ps1`. It upgrades the official CLI and restores the official Google Colab kernel-client source required by the CLI.
3. If `authRequired` is true, tell the user to run `scripts/authenticate_colab.ps1` from this plugin in an interactive terminal. Never request, echo, store, or relay the OAuth authorization code in chat.
4. After authentication, call `colab_gpu_smoke_test` with `gpu: T4`. Treat a refused allocation as an availability or quota result, not as proof that the installation is broken.
5. Run the requested workload with `colab_gpu_run`. Declare expected remote outputs explicitly so the tool can download them before the VM is released.

## Job rules

- Prefer `T4` unless the user requests another supported accelerator. Supported values are `T4`, `L4`, `G4`, `H100`, and `A100`.
- Never silently substitute CPU or a different GPU after an allocation failure.
- Use absolute local paths for scripts, requirements, inputs, and output directories. Remote input and output paths must stay under `/content`.
- Pass packages only when the workload needs them. Prefer a checked-in requirements file for reproducible environments.
- Keep the runtime only for the duration of the call. The job runner exports a log and always attempts cleanup.
- After any failure, inspect the structured phase and cleanup fields. If cleanup was not confirmed, call `colab_gpu_sessions` and stop the named session with `colab_gpu_stop`.
- Do not run `colab drivemount`, `colab auth`, `colab repl`, or `colab console` through the MCP tools. They require human interaction or a TTY.

## Google Drive handoff

When the user asks to use a Drive input, first ground the exact file with the Google Drive plugin and fetch it as a raw local file. Do not guess file IDs or paths. Supply the materialized path as `localPath` and choose a `/content/...` `remotePath` for the job.

When the user asks to persist or share results, upload only paths returned in `artifacts` by `colab_gpu_run`. Use the Drive connector's returned ID or URL, verify it with metadata readback, and report both the local result and verified Drive location. Preserve the user's existing Drive organization unless they explicitly request a new folder or move.

## Free-tier boundary

Colab's free GPU resources and runtime duration vary with availability and usage. Do not claim guaranteed access, a fixed GPU model, or an uninterrupted runtime. A successful smoke test proves only the allocation observed during that call.
