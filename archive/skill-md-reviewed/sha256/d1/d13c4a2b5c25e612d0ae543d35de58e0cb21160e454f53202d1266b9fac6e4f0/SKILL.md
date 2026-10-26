---
name: sillytavern-setup
description: "Setup SillyTavern with Hermes plugin and local llama."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [SillyTavern, LLM, LocalAI, Plugin]
    category: devops
---

# SillyTavern Setup with Hermes

Install SillyTavern as a git submodule, create a Hermes plugin for server
management, auto-configure API keys from `~/.hermes/.env`, and start a local
llama server with optimal VRAM settings. Does NOT cover SillyTavern character
creation or prompt engineering.

## When to Use

- User wants SillyTavern running locally with Hermes API keys
- User wants a Hermes plugin to start/stop/configure SillyTavern
- User needs llama-server + SillyTavern integration
- User wants to use Codex OAuth or xAI Grok inside SillyTavern
- User wants to import SillyTavern characters/chats/lorebooks into Hermes memory

## Prerequisites

- Hermes fork at `C:\Users\<user>\Documents\New project\hermes-agent`
- Node.js installed (`node --version` should return v18+)
- `npm` available in PATH
- llama-server binary (e.g. from `llama-turboquant` at `%LOCALAPPDATA%\Programs\llama-turboquant\bin\llama-server.exe`)
- At least one GGUF model file on disk
- API keys in `~/.hermes/.env` (at least one of `OPENAI_API_KEY`, `GEMINI_API_KEY`)

## How to Run

### 1. Clone SillyTavern as a git submodule

Invoke through the `terminal` tool:

```bash
cd "C:\Users\<user>\Documents\New project\hermes-agent"
git submodule add -b release https://github.com/SillyTavern/SillyTavern.git vendor/SillyTavern
cd vendor/SillyTavern && npm install --no-audit --no-fund && cd ../..
```

### 2. Create the Hermes plugin

Create `plugins/sillytavern/plugin.yaml`:

```yaml
name: sillytavern
version: 0.1.0
description: "Manage a local SillyTavern server and sync Hermes API keys."
author: Hermes
config:
  install_dir:
    type: string
    default: "vendor/SillyTavern (repo submodule; override with SILLYTAVERN_DIR)"
  port:
    type: integer
    default: 8000
  host:
    type: string
    default: "127.0.0.1"
```

The plugin `__init__.py` registers these tools:
- `sillytavern_status` — check installed/running state
- `sillytavern_start` — auto-configure + launch `server.js`
- `sillytavern_stop` — kill the server process (netstat fallback on Windows)
- `sillytavern_version` — read `package.json` version
- `sillytavern_configure` — re-sync secrets/settings without restarting

### 3. Auto-configure from Hermes secrets

The `_configure()` function in the plugin reads `~/.hermes/.env` and writes:

**`data/default-user/secrets.json`:**
```json
{
  "api_key_openai": "<from OPENAI_API_KEY>",
  "api_key_makersuite": "<from GEMINI_API_KEY>",
  "api_key_llamacpp": "local"
}
```

**`data/default-user/settings.json`** key fields:
- `main_api`: `"openai"`
- `api_server`: `"http://127.0.0.1:8080/v1"`
- `max_context`: `65536`
- `oai_settings.reverse_proxy`: `"http://127.0.0.1:8080/v1"`
- `oai_settings.openai_model`: your local model name
- `oai_settings.openai_max_context`: `65536`
- `oai_settings.openai_max_tokens`: `8192`
- `oai_settings.stream_openai`: `true`
- `power_user.max_context_unlocked`: `true`

### 4. Start the local llama server

Invoke through the `terminal` tool with `background=true`:

```bash
"/c/Users/<user>/AppData/Local/Programs/llama-turboquant/bin/llama-server" \
  --model "<path-to-model.gguf>" \
  --port 8080 \
  --ctx-size 65536 \
  --n-gpu-layers 99 \
  --flash-attn on \
  --no-kv-offload \
  --host 127.0.0.1 \
  --parallel 1
```

### 5. Start SillyTavern

From the Hermes agent, call the `sillytavern_start` tool, or invoke through `terminal`:

```bash
cd vendor/SillyTavern && node server.js --browserLaunchEnabled false --port 8000
```

### 6. Codex OAuth / xAI Grok via local reverse-proxy

SillyTavern speaks OpenAI chat-completions. Codex is OAuth-only behind
Cloudflare and needs the `/responses` API; xAI needs an API key. The plugin
ships `codex_proxy.py` — a stdlib proxy on `127.0.0.1:8199` with two routes:

- `/codex/v1` — reads the OAuth `access_token` from `~/.codex/auth.json`, pins
  `originator: codex_cli_rs` + a codex_cli_rs User-Agent + `ChatGPT-Account-ID`
  (from the JWT) to pass Cloudflare, converts chat-completions → `/responses`
  (`input` list, `store:false`, `stream:true`), and streams the SSE back.
- `/xai/v1` — passthrough to `https://api.x.ai/v1` with `XAI_API_KEY`.

Start it via the `sillytavern_proxy_start` tool. In SillyTavern pick
**Chat Completion → Custom (OpenAI-compatible)** and set the proxy URL as the
base. Tools: `sillytavern_proxy_start`, `sillytavern_proxy_stop`,
`sillytavern_proxy_status`.

### 7. Import SillyTavern data into Hermes memory

The plugin parses character cards (PNG tEXt V2/V3), chat `.jsonl`, and
lorebook `.json` via `st_import.py` (stdlib — no PIL, which hangs on Windows).

- `sillytavern_scan` — list importable characters/chats/lorebooks.
- `sillytavern_import_memory` — emit `{content, tags, salience}` records; the
  agent persists chosen ones with the `ebbinghaus_memory` / `memory` tools.

## Quick Reference

| Service | URL | Port |
|---------|-----|------|
| SillyTavern | http://127.0.0.1:8000 | 8000 |
| llama-server | http://127.0.0.1:8080/v1 | 8080 |
| Codex route | http://127.0.0.1:8199/codex/v1 | 8199 |
| xAI route | http://127.0.0.1:8199/xai/v1 | 8199 |
| llama route | http://127.0.0.1:8199/llama/v1 | 8199 |

| Secret Key | Source |
|-----------|--------|
| `api_key_openai` | `OPENAI_API_KEY` from `~/.hermes/.env` |
| `api_key_makersuite` | `GEMINI_API_KEY` from `~/.hermes/.env` |
| `api_key_xai` | `XAI_API_KEY` from `~/.hermes/.env` |
| `api_key_llamacpp` | hardcoded `"local"` |

## Pitfalls

- **VRAM overflow (16GB GPU):** A 14GB IQ3_M model + 65536 KV cache on GPU
  requires `--no-kv-offload` to keep KV on CPU. Without it, `cudaMalloc
  out of memory` occurs. The `--n-gpu-layers 99` warning about "already set"
  is harmless — the model loads fine.
- **`--flash-attn` requires `on/off/auto`:** SillyTavern's TurboQuant build
  needs `--flash-attn on` not bare `--flash-attn`.
- **CSRF errors on startup:** Normal when the browser sends stale tokens.
  Refreshing the page resolves it. Non-fatal.
- **Context overflow:** If Hermes routes its own long conversation through the
  local llama server and exceeds `--ctx-size`, requests fail with
  `"request exceeds the available context size"`. This is expected — the
  llama server is for SillyTavern's shorter roleplay sessions, not Hermes's
  full context.
- **`secrets.json` path:** Always under `data/default-user/secrets.json`
  relative to the SillyTavern install dir. The plugin auto-creates the
  `data/default-user/` directory if missing.
- **Codex `/responses` rejection chain:** the backend returns errors one at a
  time — fix them in order: 403 (add codex_cli_rs originator/UA/account-ID
  headers) → `Input must be a list` (convert messages→input list) →
  `Store must be set to false` (`store:false`) → `Stream must be set to true`
  (`stream:true`) → `Unsupported parameter: max_output_tokens` (drop it for
  reasoning models like gpt-5.6-luna).
- **`usage_limit_reached` is success, not failure:** a JSON error with
  `plan_type`/`resets_at` means auth, headers, conversion, and streaming all
  worked — the Codex plan quota is just spent (it resets at `resets_at`).
- **xAI has no OAuth:** Grok uses an API key from console.x.ai only. A 401 on
  `/xai/v1` with no key set is correct behavior.
- **llama route passthrough:** `/llama/v1` forwards to the local llama-server
  (already OpenAI-compatible) with a nominal `Bearer local` key. No body
  conversion needed — if the local model returns `reasoning_content`, SillyTavern
  shows it as the assistant message (expected for Qwen3.6 reasoning models).
- **Duplicate `/v1` prefix:** xAI and llama base URLs already end in `/v1`, so
  the proxy strips the duplicate `/v1` from the request remainder. A 404 with
  `File Not Found` from llama means the prefix wasn't stripped.
- **Windows python `-S` / site hang:** if `python -c` hangs ~30s, the global
  interpreter's `site`/`.pth` init is stuck. Use the venv python
  (`.venv/Scripts/python.exe`) or `python -S` for quick checks — but `-S`
  hides site-packages, so run pytest with the venv python, not `-S`.
- **Duplicate proxy processes:** each `codex_proxy.py` launch binds 8199; kill
  stragglers with `Stop-Process` before restarting (invoke `taskkill`/
  PowerShell through the `terminal` tool with `MSYS_NO_PATHCONV=1`).

## Verification

```bash
# Check llama server is responding:
curl -s http://127.0.0.1:8080/v1/models | python -c "import json,sys; print(json.load(sys.stdin))"

# Check SillyTavern is responding:
curl -s http://127.0.0.1:8000/ | head -5

# Check plugin is registered (in Hermes agent):
# Call sillytavern_status — should return {"installed": true, "running": true}

# Check the Codex/xAI proxy (after sillytavern_proxy_start):
curl -s -X POST http://127.0.0.1:8199/codex/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.6-luna","messages":[{"role":"user","content":"hi"}]}'
# Expect a real Codex response OR {"error":{"type":"usage_limit_reached",...}}
# — both prove the bridge works. A 403 means the CF headers regressed.
```

A reference copy of the proxy lives at `scripts/codex_proxy.py` in this skill.
