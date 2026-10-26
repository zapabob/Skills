---
name: local-llm-agent-harness-bringup
description: Wire an agent framework to a local llama-server.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Local-Llm, Llama-Server, Agent-Harness, Tool-Calling, Diagnostics, Vram]
---

# Local LLM Agent Harness Bring-Up

A repeatable order of operations for pointing an agent framework (OpenManus,
AutoGPT-likes, any OpenAI-compatible client) at a local `llama-server` and
proving the loop actually works. It is a diagnostic discipline, not a
model recommendation: it does not pick quantisations or tune sampling, and it
assumes only `terminal`, `read_file`, `write_file`, and `patch`.

The core claim: **a healthy `/health` and a healthy plain chat completion do
not prove an agent harness works.** Agent loops are tool calls, and tool
calling is where local setups silently fall over.

## When to Use

- "Point OpenManus / this agent framework at my local llama-server."
- "The agent framework can reach the model but every run times out."
- "`OpenAI API error: Connection error.` from a child agent process."
- "The endpoint responds but the agent never finishes a single step."
- "`secret environment variable ... is not set` even though I just added it."
- You are switching a delegated-agent plugin from a paid API to local VRAM.

Not for: choosing a GGUF, training, or fixing the framework's own agent logic.

## Prerequisites

- A local `llama-server` binary and a GGUF on disk. Locate both with
  `search_files` (`target='files'`, pattern `llama-server.exe` / `*.gguf`)
  rather than assuming a path — builds land in several places.
- The framework's own Python environment (often a dedicated venv), found by
  reading its plugin/config files with `read_file`.
- GPU headroom. Check with `terminal`:
  `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`
- On Hermes: know the framework plugin's config block and which env var name
  it reads for the API key.

## How to Run

Work the five gates in order through the `terminal` tool. Each gate is cheap
and each one rules out a whole class of failure, so never skip ahead:

```bash
# Gate 1 — server is up
curl -s http://127.0.0.1:8080/health

# Gate 2 — model answers at all (max_tokens >= 256, see Pitfalls)
py -3 probe_completion.py [base_url] [model]

# Gate 3 — THE decisive gate: does it emit OpenAI tool calls, and how fast?
py -3 probe_toolcall.py [base_url] [model]

# Gate 4 — the framework's own config resolves to that endpoint
#   (read the plugin's config loader; do not eyeball the YAML)

# Gate 5 — one bounded live run, in the background
```

Both probes take no arguments in the common case: they read `/health` and
discover the served alias from `/v1/models`, so they work against any
OpenAI-compatible local server. Load them with `skill_view`
(`file_path="scripts/probe_completion.py"` and `scripts/probe_toolcall.py`)
and invoke them through the `terminal` tool. Gate 3 exits non-zero on a slow
*but well-formed* call — that distinction is the diagnosis.

## Quick Reference

| Symptom | Real cause | Fix |
|---|---|---|
| `Connection error` looping in the child | framework's network gate blocks loopback | use its "LLM-only" network scope, not "none" |
| `content: ''` on a short completion | reasoning model, `max_tokens` too small | `max_tokens >= 256`, read `reasoning_content` |
| plain chat fine, agent never finishes | KV-cache spill; slot count too high | `--parallel 1` — do **not** lower `-c` |
| `secret env ... is not set` | new `.env` var invisible to running process | reuse an already-loaded var name |
| tool result says `timed out after 420.0s` | Hermes per-call cap, child still alive | rerun in `terminal(background=true)` |
| CLI flags appear ignored | stale `LLAMA_ARG_*` env overrides | unset them before launch |

Flags that matter for a VRAM-tight single-agent server:

```
-c <65536|131072>   # keep the context you want
--parallel 1        # ONE slot: full ctx per request, one KV cache
-ngl 99 -fa on
--jinja             # required for tool-call templating
--no-mmap
```

## Procedure

1. **Inventory, don't assume.** Use `search_files` to find the real
   `llama-server` binary and GGUF. Read the framework's plugin source with
   `read_file` to learn exactly which config keys and env var it consumes —
   the runner's argument list is the ground truth, not the docs.
2. **Launch with one slot.** Write a launch script with `write_file` that first
   unsets stale `LLAMA_ARG_*` / vendor-prefixed env vars, then starts the
   server with `--parallel 1` and your chosen `-c`. Confirm the log prints
   `n_slots = 1` and the `n_ctx_slot` you asked for.
3. **Gate 2 — plain completion.** Send one request with `max_tokens >= 256`.
   Assert `content` is non-empty. A reasoning model spends its first tokens in
   `reasoning_content`, so a small budget returns an empty string and looks
   like a dead model.
4. **Gate 3 — tool call.** Run `scripts/probe_toolcall.py`. Require
   `finish_reason == "tool_calls"`, a well-formed arguments object, and a
   **single-digit-seconds** round trip. A multi-minute tool call means spill:
   go back to step 2 and reduce slots or free VRAM. This gate is the whole
   point of the skill — it is what a plain completion cannot tell you.
5. **Gate 4 — config wiring.** Point the framework's LLM block at the local
   `base_url`/model with a script that backs up the config first and preserves
   the previous entry (e.g. under an `llm_previous` key). For the API key, use
   an env var name that already exists in the environment; a freshly appended
   one is not visible to an already-running process. Verify by importing the
   plugin's own loader and printing what it resolved, then probing that
   resolved URL — not by re-reading the YAML you just wrote.
6. **Open the loopback gate.** Set the framework's network scope to its
   LLM-only mode and enable the matching allow-flag. A blanket "no network"
   mode also blocks `127.0.0.1`, which is the single most common cause of the
   `Connection error` loop.
7. **Gate 5 — bounded live run.** Ask for the smallest verifiable artifact
   ("create a file containing exactly X, then terminate") with a low step cap.
   Run it via `terminal(background=true, notify_on_complete=true)` so the
   ~420 s per-call cap cannot kill the parent. Write a receipt JSON with exit
   code, elapsed time, and stderr tail so the outcome survives a dead parent.
8. **Verify against artifacts.** Confirm the file exists and its content is
   exact, and confirm the child's stderr contains zero `Connection error`
   lines. Only then retry through the framework's normal tool call.
9. **Record the numbers.** Persist the working flag set, the measured
   tool-call latency, and each trap you hit — into this skill with
   `skill_manage` patch, or into `memory` / `ebbinghaus_memory`.

## Pitfalls

- **Slot count, not context length, is the VRAM lever.** `llama-server`
  defaults to several slots and allocates a KV cache per slot while splitting
  `-c` across them. On a tight card that spills to host memory and prompt
  processing collapses — measured once at 6.7 tok/s versus ~37 tok/s with one
  slot. Lowering `-c` is the wrong reflex; it sacrifices the context window and
  leaves the extra caches in place.
- **Never conclude "the model can't tool-call" from a slow run.** The same
  model that took over 400 s per tool call returned in 3.3 s after the slot fix.
  Latency is a resource symptom; malformed JSON is a model symptom.
- **A framework's "no network" mode is not agent-friendly for local models.**
  It cannot distinguish loopback from the internet. Read the runner's arg
  handling to find the narrower LLM-only scope.
- **Emptying the API key to "skip auth" breaks it.** A no-auth local server
  still needs the client to construct successfully; an empty key fails before
  the socket opens. Pass any dummy value through the normal path.
- **A tool-call timeout is not a failed run.** The child process keeps going
  after the parent is cut off, and the receipt is never written. Read the
  server log and the workspace directory before assuming failure.
- **Other GPU consumers count.** Electron apps, browsers, game launchers, and a
  second inference server all take VRAM. Check
  `nvidia-smi --query-compute-apps=pid,process_name --format=csv` before
  blaming the config.
- **On Windows, `/tmp` is invisible to native binaries.** Point scratch files
  at `$LOCALAPPDATA/Temp`. Also prefer `py -3`; a bare `python` may be a store
  stub.
- **Stale env vars beat CLI flags.** Vendor builds read `LLAMA_ARG_*`-style
  variables that silently override what you passed on the command line.

## Verification

The harness is proven only when all of these hold — in this order:

1. `/health` returns `{"status":"ok"}`.
2. The server log shows `n_slots = 1` and the intended `n_ctx_slot`.
3. `scripts/probe_toolcall.py` exits `0`, printing
   `finish_reason = tool_calls` with valid JSON arguments **in single-digit
   seconds**. Verified against a local 27B GGUF: 2.0 s.
4. The framework's own config loader resolves to the local `base_url`, and a
   probe against that resolved URL returns non-empty content.
5. A bounded live run exits `0`, the requested artifact exists with exact
   content, and the child's stderr contains zero `Connection error` lines.
