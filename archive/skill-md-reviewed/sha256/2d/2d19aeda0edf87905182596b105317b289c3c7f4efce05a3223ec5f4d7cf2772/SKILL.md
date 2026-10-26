---
name: openmanus-local-qwen38-harness
description: "Run OpenManus on the local Qwen3.8 llama-server harness."
version: 1.0.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Openmanus, Qwen, Llama-Server, Local-Llm, Harness, Delegation]
    related_skills: [local-llm-agent-harness-bringup, openmanus-delegation, hermes-agent]
---

# OpenManus × Local Qwen3.8 Harness

Wires the Hermes `openmanus` plugin to the local `qwen3.8-27b-abliterated-mtp`
llama-server instead of a paid remote endpoint. Covers bring-up, config wiring,
verification, and the timeout traps specific to this pairing.

This is the host-specific instance of a general procedure. For a different
framework, model, or machine, load `local-llm-agent-harness-bringup` — it holds
the portable five-gate method and stdlib probe scripts.

## When to Use

- You want OpenManus delegated runs to consume local VRAM instead of API credits.
- A remote OpenManus LLM (NVIDIA/OpenRouter) is rate-limited or out of budget.
- You are debugging `OpenAI API error: Connection error.` from an OpenManus child.

Do not use this for tasks needing a large context window: this GGUF serves
`n_ctx=65536` across 4 slots, and OpenManus fills a slot per concurrent step.

## Prerequisites

| Item | Value on this host |
|------|--------------------|
| llama-server | `%LOCALAPPDATA%\Programs\llama-turboquant\bin\llama-server.exe` (b10264) |
| GGUF | `%USERPROFILE%\Desktop\SO8T\gguf_models\soyaakinohara\qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf\qwen3.8-27b-abliterated-3.69bpw-12GB-MTP.gguf` |
| GPU | RTX 5060 Ti 16GB — `--parallel 1` lands ~14.5/16.3 GB (~1.7 GB spare) |
| OpenManus venv | `_runtime/openmanus-venv/Scripts/python.exe` |
| Workspace root | `_runtime/research-workspace` |

## CRITICAL: `--parallel 1` is what makes this usable

`llama-server` defaults to `n_slots = 4`. It then allocates **four** KV caches
and splits `-c` across them. On a 16 GB card with a 12 GB model that spills, and
prompt processing collapses:

| Config | prompt processing | tool-call round trip |
|--------|-------------------|----------------------|
| default `n_slots = 4` | **6.7 tok/s** | > 400 s (never finished) |
| `--parallel 1` | ~37 tok/s | **3.3 s** |

`--parallel 1` keeps `n_ctx_slot = 65536` (the full context per request) — it
does **not** reduce the context window. Never "fix" the slowness by lowering
`-c`; lower the slot count instead. Also unset stale `LLAMA_ARG_*` /
`LLAMA_TURBOQUANT_*` env vars, which silently override CLI flags.

## How to Run

One command brings the whole harness up and verifies it:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts\windows\openmanus-qwen38-harness.ps1
```

Add `-Probe` to also run a real bounded agent task. Individual pieces:

```bash
# just the server — keep CtxSize at 65536 or 131072, keep Parallel at 1
powershell -NoProfile -ExecutionPolicy Bypass \
  -File scripts/windows/start-llama-qwen38-openmanus.ps1 -CtxSize 65536 -Parallel 1

# config + endpoint verification only (no agent)
py -3 scripts/standalone/openmanus_qwen38_check.py

# does the served model emit OpenAI tool calls at all? (fast triage, ~3s healthy)
py -3 scripts/standalone/qwen38_toolcall_probe.py

# live bounded agent run, bypassing the 420s tool cap
py -3 scripts/standalone/openmanus_qwen38_probe.py 6 1200
```

## Quick Reference

Required `plugins.entries.openmanus` shape in `~/.hermes/config.yaml`:

```yaml
llm:
  provider: custom
  model: qwen3.8-27b-abliterated-mtp
  base_url: http://127.0.0.1:8080/v1
  api_type: openai
  api_key_env: OPENMANUS_API_KEY
allow_llm_network: true
```

Tool invocation that actually reaches localhost:

```python
openmanus_run(
    task="...",
    dry_run=False,
    allow_side_effects=True,
    acknowledge_side_effects=True,
    network_scope="llm_only",   # NOT "none" — "none" cannot reach 127.0.0.1:8080
    max_steps=4,
)
```

## Procedure

1. Start the server with the verified flag set (`-ctk q8_0 -ctv turbo3
   --spec-type draft-mtp --spec-draft-n-max 3 --jinja --no-mmap`). Unset stray
   `LLAMA_ARG_*` / `LLAMA_TURBOQUANT_*` first — they silently override CLI flags.
2. Confirm a real completion returns non-empty `content`. This model emits
   `reasoning_content` first; a bare `max_tokens: 16` returns `content: ''` and
   looks like a broken model when it is only mid-reasoning. Use ≥256.
3. Point `plugins.entries.openmanus.llm` at the local endpoint with
   `scripts/standalone/openmanus_point_to_qwen38.py` (backs up config, preserves
   the prior remote entry under `llm_previous`).
4. Use `api_key_env: OPENMANUS_API_KEY`. That name is already present in
   `~/.hermes/.env` and therefore already loaded in the running Hermes process.
5. Run with `network_scope="llm_only"` and `allow_llm_network: true`.
6. For live runs longer than ~7 minutes, drive `runner.py` through
   `openmanus_qwen38_probe.py` in a background terminal instead of the tool.

## Pitfalls

- **`network_scope: "none"` kills the LLM call.** The runner passes
  `--no-network`, and the child cannot reach `127.0.0.1:8080`. Symptom:
  `OpenAI API error: Connection error.` repeated with backoff, then
  `RetryError[...APIConnectionError]`. Fix: `llm_only`.
- **`no_secret_env: true` does not help a no-auth local server.** It empties
  the api_key, and the OpenAI client fails before connecting. Pass a dummy
  secret through the normal env route instead.
- **A brand-new env var in `.env` is not visible to the running process.**
  `core.py` reads `os.environ` directly, so a freshly appended
  `OPENMANUS_LOCAL_API_KEY` yields `secret environment variable ... is not set`
  until the process restarts. Reuse an already-loaded name, or call
  `hermes_cli.config.reload_env()`.
- **The Hermes tool call caps at ~420s.** `openmanus_run` raises
  `timed out after 420.0s` while the child keeps running, and because the
  parent died the receipt is never written. Judge the outcome from the
  llama-server log and the workspace, not from the tool result.
- **Only ~0.9 GB VRAM is spare at `n_slots = 4`.** That is the spill that causes
  the 6.7 tok/s collapse. Run `--parallel 1` and stop other GPU consumers
  (ComfyUI, a second llama-server, heavy Electron/Edge windows) before bring-up.
- **A healthy `/health` plus a healthy plain completion does not prove the
  harness works.** Plain chat was fine at 6.7 tok/s while tool-calling took
  > 400 s. Always run `qwen38_toolcall_probe.py` — the whole agent loop is
  tool calls, so that is the throughput that matters.
- **`/tmp` is invisible to native binaries.** Write scratch files under
  `%USERPROFILE%/AppData/Local/Temp/`.

## Verification

Harness is genuinely ready when all five hold:

1. `curl http://127.0.0.1:8080/health` → `{"status":"ok"}`.
2. Server log shows `n_slots = 1, n_ctx_slot = 65536` (or 131072) — **not**
   `n_slots = 4`.
3. `py -3 scripts/standalone/qwen38_toolcall_probe.py` returns
   `finish_reason = tool_calls` with a well-formed `create_file` call in
   **≈3 s** (not minutes).
4. `py -3 scripts/standalone/openmanus_qwen38_check.py` prints
   `OK: openmanus is wired to the local Qwen3.8 llama-server`.
5. A live run completes with `exit_code 0` and the artifact exists.
   Verified 2026-08-19: direct probe `exit_code 0` in 66.2 s, Hermes
   `openmanus_run` tool `status: completed` in ~14 s, zero
   `Connection error` lines, `harness_ok.txt` / `harness_tool_ok.txt`
   written into the workspace.
