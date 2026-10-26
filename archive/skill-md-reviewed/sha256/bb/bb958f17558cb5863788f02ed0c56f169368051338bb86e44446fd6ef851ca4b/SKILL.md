---
name: codex-oauth-responses-proxy
description: "Bridge Codex OAuth to OpenAI chat clients via proxy."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Codex, OAuth, Proxy, xAI, OpenAI]
    category: devops
---

# Codex OAuth / xAI Responses Proxy

Run a local stdlib HTTP proxy that lets any OpenAI chat-completions client
(SillyTavern, custom apps) talk to the Codex ChatGPT backend using OAuth, and
to xAI Grok using an API key. It translates chat-completions requests into the
Codex `/responses` API shape and streams the SSE reply back. Does NOT need
`codex app-server` (that speaks JSON-RPC, not REST).

## When to Use

- An OpenAI-compatible app must consume Codex via ChatGPT OAuth (no API key)
- You need xAI Grok exposed on a local OpenAI-compatible URL
- You hit `403 cf-mitigated: challenge`, `Store must be set to false`,
  `Stream must be set to true`, or `Unsupported parameter: max_output_tokens`
  when POSTing to a Codex endpoint

## Prerequisites

- `~/.codex/auth.json` present with `tokens.access_token` (`auth_mode: chatgpt`).
  It is a JWT — check the `exp` claim for validity; Hermes keeps it refreshed.
- For Grok: `XAI_API_KEY` in `~/.hermes/.env` (console.x.ai issues API keys;
  xAI has NO OAuth for API access).

## Why NOT `codex app-server`

`codex app-server` speaks Codex's own JSON-RPC over stdio / `ws://`, NOT
OpenAI REST. Bridging a chat-completions client to it needs a second
translation layer, so a direct `/responses` reverse-proxy is simpler and the
OAuth token is already kept fresh in `~/.codex/auth.json`.

## Codex request requirements (strict — satisfy ALL)

The ChatGPT Codex backend rejects requests progressively. A working request
must have every one of these:

1. **Cloudflare bypass headers** (mirror the codex-rs CLI so CF whitelists you):
   - `originator: codex_cli_rs`
   - `User-Agent: codex_cli_rs/0.0.0 (...)`
   - `ChatGPT-Account-ID: <acct>` — base64url-decode the JWT payload segment and
     read `claims["https://api.openai.com/auth"]["chatgpt_account_id"]`.
   Without these you get `403` with `cf-mitigated: challenge`, regardless of
   auth correctness.
2. **Endpoint** is `/responses`, not `/chat/completions`. Strip the extra `/v1`.
3. **Body conversion** chat-completions → Responses API:
   - `messages:[{role, content:str}]` → `input:[{role, content:[{type,text}]}]`
   - content `type` = `input_text` for user/system, `output_text` for assistant
4. `"store": false` REQUIRED — else `{"detail":"Store must be set to false"}`
5. `"stream": true` REQUIRED — else `{"detail":"Stream must be set to true"}`;
   the proxy must stream the SSE body back chunk-by-chunk (`resp.read(8192)`).
6. **Omit `max_output_tokens`** for reasoning models (gpt-5.6-luna) — else
   `{"detail":"Unsupported parameter: max_output_tokens"}`.

## Quick Reference

| Route | Backend |
|-------|---------|
| `/codex/v1/...` | `https://chatgpt.com/backend-api/codex` (OAuth Bearer) |
| `/xai/v1/...` | `https://api.x.ai/v1` (XAI_API_KEY passthrough) |

| Error body | Fix |
|-----------|-----|
| HTML login page / 403 | add originator + UA + ChatGPT-Account-ID headers |
| `{"detail":"Input must be a list"}` | convert `messages` → `input` list |
| `{"detail":"Store must be set to false"}` | add `"store": false` |
| `{"detail":"Stream must be set to true"}` | add `"stream": true` + stream SSE |
| `Unsupported parameter: max_output_tokens` | drop `max_output_tokens` |

## Procedure

1. Author the proxy with stdlib only (`http.server.ThreadingHTTPServer` +
   `urllib.request`). Resolve route → (base, auth, remainder, extra_headers).
2. For the codex route, attach the three CF headers and run the body converter.
3. Stream the upstream response body back to the client without buffering.
4. Launch through the `terminal` tool with `background=true`.

## Pitfalls

- **`usage_limit_reached` is SUCCESS**, not failure. A body like
  `{"error":{"type":"usage_limit_reached","plan_type":"prolite","resets_at":...}}`
  means auth, headers, and format all passed — only the plan quota is spent.
- **xai provider `api_mode`** must be `chat_completions`, not `codex_responses`
  — Grok is a standard chat-completions endpoint.
- **Windows stale listeners:** test cycles spawn many short-lived proxies.
  Reap them before starting fresh (see Verification) or duplicates pile up on
  the port. `taskkill //PID` fails under MSYS path mangling — use
  `MSYS_NO_PATHCONV=1 powershell -Command "Stop-Process -Id <pid> -Force"`.

## Verification

```bash
# A converted chat request should reach the real API (200 or usage_limit_reached):
curl -s -N -X POST http://127.0.0.1:8199/codex/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.6-luna","messages":[{"role":"user","content":"hi"}]}'

# xAI route with no key returns 401 (correct); unknown route returns 404:
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8199/xai/v1/models

# Reap stale proxy listeners on Windows:
for pid in $(netstat -ano -p tcp | grep ':8199' | grep LISTENING | awk '{print $NF}'); do
  MSYS_NO_PATHCONV=1 powershell -Command "Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue"
done
```
