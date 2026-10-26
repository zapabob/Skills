---
name: hermes-a2a-multi-agent
description: Set up Hermes A2A inter-agent communication.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [a2a, multi-agent, peer-to-peer, orchestration, profiles]
    category: autonomous-ai-agents
    related_skills: [hermes-agent, agent-heartbeat-and-memory-ops, create-company-ai-employees]
---

# Hermes A2A Multi-Agent Communication

Hermes ships built-in A2A (Agent-to-Agent) tools for peer-to-peer inter-agent messaging and multi-agent orchestration. This is NOT a separate daemon or script — it's a toolset enabled in config.yaml and invoked directly by the agent.

## When to Use

- The user wants multiple Hermes profiles (or remote instances) to talk to each other
- Setting up Bot Mode with inter-agent messaging
- Delegating tasks between agents with different capabilities
- Coordinating multi-step workflows across agents (researcher → writer → reviewer)
- Troubleshooting A2A peer discovery, registration, or messaging failures

## Available Tools

| Tool | Purpose | Key Params |
|------|---------|------------|
| `a2a_list` | List registered peers + metrics | — |
| `a2a_discover` | Find a peer by URL | `url` (required) |
| `a2a_call` | Send message to a peer | peer, message |
| `a2a_orchestrate` | Coordinate multi-agent workflow | plan, agents |
| `a2a_history` | View message history with a peer | peer |

**IMPORTANT**: `a2a_call` and `a2a_orchestrate` are **NOT deferrable tools** — `tool_describe` will fail on them with "not a deferrable tool." This is normal. Call them directly.

## Setup: Enabling A2A (Correct Config Structure)

The A2A platform is enabled under `platforms.a2a` in config.yaml (NOT `gateway.platforms.a2a`).

```yaml
platforms:
  a2a:
    enabled: true
    extra:
      port: 9900
      host: 127.0.0.1
```

Also ensure `a2a` is in `platform_toolsets.cli`:

```yaml
platform_toolsets:
  cli:
    - a2a
```

Restart the gateway: `Ctrl+K → Restart gateway` (or `/restart`).

## Setup: Adding Peers

Peers are registered under `a2a_agents` in config.yaml:

```yaml
a2a_agents:
  job-seeker:
    url: http://127.0.0.1:9901
    timeout: 120
  secretary:
    url: http://127.0.0.1:9902
    timeout: 120
```

**NOTE**: The `hermes config set` command warns "not a recognized config key" for `a2a_agents.*`. This is a false warning — use `--force` to suppress it. The A2A plugin reads these keys at runtime.

## Verifying A2A is Running

After gateway restart, check the Agent Card endpoint:

```bash
curl -sS http://127.0.0.1:9900/.well-known/agent-card.json
```

A valid JSON response with `"name"`, `"url"`, and `"supportedInterfaces"` confirms A2A is active.

## Critical Limitation: Single Gateway Instance

`hermes gateway run` uses a PID file (`~/.hermes/gateway.pid`) to enforce a single running instance per profile. Attempting to start a second profile's gateway fails with:

```
✗ Another gateway instance is already running (PID XXXXX).
```

This means you **cannot** run multiple A2A servers (one per profile) simultaneously on the same machine via the normal gateway.

## Recommended Same-Machine Pattern: Hub + Spoke

For multi-profile inter-agent communication on one machine, use a **hub-spoke** architecture:

```
[default :9900] ← A2A server (always-on hub)
    │
    ├─ terminal → hermes -p job-seeker chat -q '<task>'
    └─ terminal → hermes -p secretary chat -q '<task>'
```

- **default** runs the A2A server and acts as the coordinator
- **Other profiles** are invoked one-shot via `hermes -p <profile> chat -q '<task>'` from the hub's terminal tool
- Results return to the hub, which can relay them via A2A or act on them

### One-Shot Call Pattern

```bash
# From hub terminal, call a spoke profile:
hermes -p job-seeker --provider nous -m meituan/longcat-2.0:free chat -q '求人検索して'
hermes -p secretary --provider nous -m meituan/longcat-2.0:free chat -q 'スケジュール確認'
```

**NOTE**: The `-m` flag alone may not route to the correct provider. Always pair with `--provider` flag when calling profiles whose default provider differs from the hub's.

### One-shot fan-out: DROP `-c "Bot Chat"` for conference delivery

`references/bot-mode-cli-delivery.md` recommends `-c "Bot Chat"` for *inbox continuity* — appending to a bot's existing canonical conversation. That is correct for its purpose and **wrong for one-shot conference/meeting fan-out**, for two reasons:

1. **`-c` resumes the target's largest existing session.** Verified 2026-10-02: `secretary`'s Bot Chat held 197 messages, so the message immediately triggered context compression. When `auxiliary.compression.model` is a small local model, compression aborts the whole turn before the bot ever answers:
   ```
   Error: Auxiliary compression model phi4-mini-aux has a context window of 8,192 tokens,
   which is below the minimum 64,000 required by Hermes Agent.
   ```
   Without `-c`, Hermes starts a fresh session, no compression runs, and the bot replies normally.

2. **Without `-c` the reply comes back on stdout.** You do not need `session_search(profile=..., session_id=...)` at all — the answer is in the command's own output, plus a `session_id:` line you can record for later recall. This is strictly less work than the `-c` + `session_search` dance.

Use `-c` only when you specifically need the message appended to an ongoing thread. For a meeting, questionnaire, or broadcast, run it **without** `-c`:

```bash
hermes -p <bot> chat --in ~ -Q -q "Message from <sender>: <msg>"   # fresh session, inline reply
```

See `references/agent-conference-delivery.md` for the full verified fan-out recipe.

## Common Patterns

### Bot Mode + A2A (CRITICAL: use the CLI, not HTTP POST)

The desktop Bot Mode plugin (`hermes-bots`) shows one row per profile in the left pane. Bots run a `hermes serve` JSON-RPC backend on their port (e.g. `:9900`, `:9921`). **That backend registers NO JSON-RPC methods** — so any HTTP POST to `/a2a/chat` returns:

```json
{"jsonrpc":"2.0","error":{"code":-32601,"message":"method not found: "}}
```

**Do NOT attempt to deliver via `/a2a/chat` POST.** The only working injection path into a bot's canonical \"Bot Chat\" session is the Hermes CLI, invoked from another process:

```bash
hermes -p <bot> chat --in ~ -c "Bot Chat" -Q -q "Message from <sender>: <your message>"
```

- `-c "Bot Chat"` → targets the bot's canonical Bot Chat conversation (created on first use, stable session id).
- `-Q` → quiet (suppresses agent chatter to stdout).
- `-q` → injects the message as the user turn; the bot processes it and replies in that session.
- Non-blocking fan-out: launch each call with `Start-Process -WindowStyle Hidden` (PowerShell) or `&`/background so the caller doesn't block on the bot's model response.

**Reading bot replies:** `session_search` FTS5 index only catches the *sending* session, NOT the bot's reply session. To collect replies, query the bot's Bot Chat session **directly by id + profile**:

```python
session_search(profile="job-seeker", session_id="20260815_084502_f3a3d3")
```

You must know (or discover via `hermes -p <bot> sessions list`) the per-profile Bot Chat session id first.

**Custom hub compatibility layer (zapabob go-a2a-hub pattern):** if you run a custom hub that POSTs to bots, wrap the `-32601` failure by exec'ing the hermes CLI from the hub instead of HTTP. Make the handler async (goroutine) so `/send` returns `202 Accepted` immediately while delivery happens in the background; record completion via a `/records` endpoint. Use the **absolute** hermes binary path (e.g. `%USERPROFILE%\Documents\New project\hermes-agent\.venv\Scripts\hermes.exe`) — a detached/exec'd process may not inherit the shell PATH.

See `references/bot-mode-cli-delivery.md` for a ready-to-run multi-bot fan-out script and the PowerShell quoting pitfalls.

### Task Delegation
Use `a2a_call` to assign a task to a peer with the right capabilities (e.g., a profile with `code_execution` enabled sends compute work to a profile with more RAM).

### Orchestration
Use `a2a_orchestrate` for multi-step workflows that span agents — e.g., researcher gathers sources, writer drafts, reviewer critiques.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `a2a_list` → "No peers configured" | No `a2a_agents` in config | Add peer entries to config.yaml |
| `a2a_discover` → "'url' is required" | Missing URL param | Pass the peer's A2A endpoint URL |
| `tool_describe` fails on `a2a_call` | Not a deferrable tool | Call directly; don't use tool_describe |
| Tools not appearing in session | `a2a` not in platform_toolsets | Add to `platform_toolsets.cli`, restart gateway |
| POST to `:99xx/a2a/chat` → `-32601 method not found` | bot-mode JSON-RPC backend registers **no** methods | Deliver via `hermes -p <bot> chat --in ~ -c "Bot Chat" -Q -q "..."` CLI instead (see Bot Mode + A2A) |
| `session_search` can't find a bot's reply to a meeting message | FTS5 only indexes the *sending* session, not the bot's reply session | Query the bot's Bot Chat session directly: `session_search(profile="<bot>", session_id="<id>")` |

## References

- `references/a2a-tool-usage.md` — detailed parameter shapes, anti-loop behavior, metrics interpretation, and config paths.
- `references/hub-spoke-architecture.md` — verified same-machine multi-profile pattern (hub A2A server + spoke `chat -q` invocations).
- `references/bot-mode-cli-delivery.md` — ready-to-run multi-bot fan-out script + PowerShell quoting pitfalls for delivering into bot-mode "Bot Chat" sessions. Use `-c "Bot Chat"` here.
- `references/agent-conference-delivery.md` — **one-shot conference/broadcast delivery**: why to DROP `-c`, the `-z` pre-flight probe, `SSL_CERT_FILE` unblock, parallel fan-out with per-profile output files, and failure-cause classification.
- `templates/a2a-config-template.yaml` — copy-paste config blocks for quick setup.

## Implementation Notes (Session 2026-08-18)

This skill was activated to implement the following user requirements:
- Stop PONG token transmission (no PONG/ping definitions found in plugin.js; instead configured `cronjob.enabled` and `plugins.hermes-bot-mode.enabled` flags)
- Enable A2A inter-agent communication via Bot Mode plugin
- Route results back to main agent via A2A protocol
- Avoid 429/503 round-robin errors through proper peer configuration

**Completed setup steps:**
1. `hermes config set platforms.a2a.enabled true` — A2A server on port 9900
2. `hermes config set platform_toolsets.cli '["a2a", ...]'` — A2A toolset activated
3. `hermes config set a2a_agents.main-agent.url http://127.0.0.1:9900` — Peer registration (note: `hermes config set` shows false "not recognized" warning — use `--force` to suppress)
4. Verified via `curl -sS http://127.0.0.1:9900/.well-known/agent-card.json` — Agent Card JSON response confirms A2A active
5. Tested `a2a_call` with `peer: "main-agent"` — successful round-trip message exchange

**Round-robin & error avoidance:** The A2A system inherently distributes calls across configured peers. `anti_loop` metric prevents infinite message loops. For 429/503 mitigation, rely on the agent's built-in retry/backoff patterns and the `rate_limited` metric to throttle call frequency.

**Hub-spoke pattern (same-machine):** One profile (`default`) runs the A2A server at `:9900`. Other profiles are invoked one-shot via `hermes -p <profile> chat -q '<task>'` from the hub terminal, avoiding the single-gateway-instance limitation.