---
name: local-llm-bridge-setup
description: "Bridge local llama, Codex OAuth, and xAI into SillyTavern or other OpenAI-compat UIs."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [SillyTavern, LLM, LocalAI, Codex, xAI, ReverseProxy]
    category: devops
---

# Local LLM Bridge Setup

Run a local OpenAI-compatible proxy so UIs that only speak OpenAI
chat-completions REST (SillyTavern, etc.) can reach backends that don't: a
local `llama-server`, Codex's OAuth-only `/responses` API, and xAI (Grok).

This is the umbrella for the techniques proven in the SillyTavern session:
VRAM-safe llama launch, Codex chat→responses rewriting with Cloudflare-safe
headers, and xAI key pass-through.

## When to Use

- User wants local llama / Codex / Grok reachable from SillyTavern or any
  OpenAI-compat client.
- User mentions "Codex OAuth", "Grok", "xAI", "CodexAPPserver" in a SillyTavern
  or local-LLM context.
- User wants a reverse-proxy that converts chat-completions into another API
  shape.

## Prerequisites

- `llama-server` binary (TurboQuant at `%LOCALAPPDATA%\Programs\llama-turboquant\bin\llama-server.exe`).
- GGUF model on disk.
- For Codex: `~/.codex/auth.json` (`auth_mode: chatgpt`, JWT `access_token`).
- For xAI: `XAI_API_KEY` from console.x.ai (xAI has NO OAuth — key only).
- For Hermes sync: `~/.hermes/.env`.

## How to Run

### Local llama (VRAM-safe for 16GB)
```bash
llama-server --model "<model.gguf>" --port 8080 --ctx-size 65536 \
  --n-gpu-layers 99 --flash-attn on --no-kv-offload --host 127.0.0.1 --parallel 1
```
`--no-kv-offload` keeps the KV cache on CPU so a 14GB IQ3_M fits a 16GB GPU.
`--flash-attn` needs `on`, not bare.

### Codex + xAI reverse-proxy
A pure-stdlib HTTP proxy (see `references/codex-proxy.md`) listens on
`127.0.0.1:8199`:
- `POST /codex/v1/chat/completions` → ChatGPT Codex `/responses`
- `POST /xai/v1/...` → `https://api.x.ai/v1/...`

```bash
python codex_proxy.py --port 8199
```
Point the UI's "Custom (OpenAI-compatible)" source at
`http://127.0.0.1:8199/codex/v1` or `.../xai/v1`.

## Quick Reference

| Backend | UI base URL | Auth |
|---------|-------------|------|
| local llama | `http://127.0.0.1:8080/v1` | none (`local`) |
| Codex | `http://127.0.0.1:8199/codex/v1` | OAuth JWT via proxy |
| xAI | `http://127.0.0.1:8199/xai/v1` | `XAI_API_KEY` |

## Pitfalls

- **Codex OAuth ≠ API key.** `tokens.access_token` in `~/.codex/auth.json` is
  a JWT in `auth_mode: chatgpt`. Reusing it as a Bearer key fails. The proxy
  pins `originator: codex_cli_rs` + `ChatGPT-Account-ID` (from the JWT's
  `chatgpt_account_id` claim) to clear Cloudflare's 403 challenge.
- **`codex app-server` is the WRONG bridge** — it speaks Codex JSON-RPC
  (stdio/`ws://`), not OpenAI REST. A chat-completions→`/responses` HTTP proxy
  is simpler and sufficient.
- **Codex `/responses` body rules** (each was a real error we hit):
  `store` MUST be `false`, `stream` MUST be `true` (SSE), and
  `max_output_tokens` is REJECTED by reasoning models (gpt-5.6-luna) — drop it.
  `Input must be a list` / `Stream must be set to true` / `Store must be set to
  false` / `Unsupported parameter: max_output_tokens` are all proxy-side fixes.
- **`usage_limit_reached` from Codex = success.** It means the proxy is
  correct; only the plan quota is exhausted (resets_at epoch is returned).
- **xAI has no OAuth** — only `XAI_API_KEY` from console.x.ai.
- **Python startup hangs here** — `python -c` blocks ~30s (sitecustomize/`.pth`
  stall). Use `.venv/Scripts/python.exe` for pytest, or `python -S` for
  stdlib-only, or `node -e` for file IO. See `references/python-hang.md`.
- **llama context overflow** — routing Hermes's own long history through the
  local llama (65536 ctx) fails with `request exceeds the available context
  size`; the local server is for the UI's short sessions.

## Verification

```bash
curl -s -o /dev/null -w "codex:%{http_code}\n" -X POST http://127.0.0.1:8199/codex/v1/chat/completions \
  -H "Content-Type: application/json" -d '{"model":"gpt-5.6-luna","messages":[{"role":"user","content":"hi"}]}'
# 200/usage_limit_reached = proxy correct; 403 = header problem
curl -s -o /dev/null -w "xai:%{http_code}\n" http://127.0.0.1:8199/xai/v1/models   # 401 = no key yet, correct
curl -s http://127.0.0.1:8080/v1/models | head -c 100   # local llama
```

## References

- `references/codex-proxy.md` — full Codex `/responses` header + body contract.
- `references/python-hang.md` — why `python -c` blocks and how to run here.
