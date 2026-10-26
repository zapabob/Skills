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

## Common Patterns

### Bot Mode + A2A
The desktop Bot Mode plugin (`hermes-bots`) shows one row per profile in the left pane. Bots can A2A-message each other into their canonical \"Bot Chat\" — useful for multi-agent task delegation with a visual roster.

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

## References

- `references/a2a-tool-usage.md` — detailed parameter shapes, anti-loop behavior, metrics interpretation, and config paths.
- `references/hub-spoke-architecture.md` — verified same-machine multi-profile pattern (hub A2A server + spoke `chat -q` invocations).
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