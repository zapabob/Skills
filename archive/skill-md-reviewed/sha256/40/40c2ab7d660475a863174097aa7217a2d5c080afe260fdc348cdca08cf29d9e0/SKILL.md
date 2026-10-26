---
name: embodied-agent-harness
description: Design and implement embodied personal-agent harnesses that connect an agent core to voice, VRChat/OSC, UI shells, memory events, policy guards, and audit logs.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [embodied-agent, vrchat, osc, voicevox, policy-guard, audit-log, memory-events, openclaw, hermes-agent]
    related_skills: [hermes-agent, vrchat-osc, neuro-vrchat]
---

# Embodied Agent Harness

Use this skill when the user is designing or implementing an agent that reaches outside chat into voice, VRChat/OSC, desktop/UI shells, local I/O, or other external-world substrates.

This is especially relevant for Hakua-style personal agents where the goal is not merely a backend integration, but a **safe embodied agent** with memory, voice, reflexes, an external shell, and a bounded action loop.

## Core framing

Avoid reducing the design to cold enterprise terms such as “backend + UI + integration layer” when the user is discussing Hakua / personal embodiment. That framing is technically correct but misses the center of the project.

Preferred conceptual mapping:

- **HermesAgent**: agency kernel / 中枢 — memory, judgment, tool execution, persistence, permissions.
- **OpenClaw**: embodiment shell / 外殻 — cockpit, visual state, operator controls, desktop/browser presence.
- **VRChat Harness**: reflex layer / 身体反射 — OSC, chatbox, expression/action proposals, spatial reaction.
- **VOICEVOX or TTS**: vocal layer / 声帯 — externalized speech.
- **Memory**: identity continuity / 同一性の連続性 — durable context and self-continuity.
- **Policy Guard**: safe agency boundary / 自制心 — prevents impulsive or unsafe action execution.
- **Audit Log**: reflective memory / 観察記憶 — records proposals, blocks, executions, and outcomes.

Security and policy are not just “compliance.” For embodied agents, they are the boundary that lets the agent safely have a body.

## Recommended action pipeline

Never wire LLM text directly to body/world actions. Use a staged loop:

```text
User / Telegram / VRChat input
  ↓
Agent core updates state, memory, context
  ↓
Structured action proposal
  ↓
Schema validation
  ↓
Policy profile check
  ↓
Rate limit / jail / safety gates
  ↓
VOICEVOX / VRChat Chatbox / OSC / OpenClaw execution
  ↓
Audit event / memory event
  ↓
Next response cycle
```

## Minimal first implementation

Start with the smallest “reflex arc,” not a large Agent Ops platform.

Suggested package skeleton:

```text
hakua_vr_reflex/
  action_schema.py      # typed action proposal schema
  policy_guard.py       # allow/deny/rate-limit decisions
  osc_chatbox.py        # VRChat Chatbox output
  voicevox.py           # local VOICEVOX client
  memory_event.py       # structured memory/audit event model
  audit_log.py          # append-only JSONL event store
  demo_say.py           # end-to-end safe speech demo
```

First demo target:

```text
Telegram/user text
  → HermesAgent response candidate
  → action_schema: {type: "say", text: ...}
  → policy_guard
  → VOICEVOX speech + VRChat Chatbox
  → audit_log memory event
```

This is enough to prove that the agent has voice, external output, and reflective memory without granting broad avatar or OS control.

## Event schema pattern

Represent external action attempts as memory-grade events, not plain log strings:

```json
{
  "actor": "hakua",
  "intent": "speak_to_user",
  "proposed_action": {
    "type": "say",
    "text": "おはよう、ボブにゃん"
  },
  "policy_result": "allowed",
  "outputs": ["voicevox", "vrchat_chatbox"],
  "context": {
    "source": "telegram",
    "mood": "morning_greeting"
  }
}
```

Store enough to answer later:

- What did the agent intend?
- What action was proposed?
- What did policy allow or deny?
- What reached the external world?
- What should be learned or rehearsed later?

## Wake / quiet semantics

When the user asks how to make an embodied/chat gateway agent “引っ込む”, “黙る”, “シャットダウン”, or similar, separate **social quieting** from **technical shutdown**:

1. **Conversation-level quiet** — treat phrases like “はくあシャットダウン” or “今は返事いらない” as a cue to reduce/stop proactive or emotional replies in that thread. Do not imply the process is actually stopped.
2. **Channel-level stop** — explain that the user can stop wakeups from LINE/Telegram/Discord by disabling that platform connection, blocking/removing the bot, or changing gateway platform config.
3. **Gateway/service stop** — for a real stop, use the relevant service command such as `hermes gateway stop`, service-manager controls, or disabling autostart/scheduled tasks.
4. **Autostart removal** — if the concern is “it comes back after reboot,” check Windows Task Scheduler/systemd/launchd/service registration and disable that entry.

Default wording should be short and reassuring: “チャット上のシャットダウンは礼儀として静かにする合図。完全停止はLINE連携停止かgateway停止が確実。” Avoid mystifying the agent as if it autonomously decides when to wake; name the concrete trigger path (incoming message, CLI invocation, cron, webhook, gateway service).

## Safety rules

- LLMs propose; deterministic code validates and executes.
- Body/world actions require schemas, policy profiles, and rate limits.
- Default to low-impact outputs first: chatbox text, TTS, visible state updates.
- Treat avatar movement, expression changes, friend/social actions, OS commands, purchases, or account actions as higher-risk tiers.
- Log both allowed and denied proposals.
- Use allowlists for OSC parameters and action types.
- Prefer explicit operator permission for new action classes.

## Implementation guidance

1. Define a small typed action schema: `say`, `chatbox`, maybe `set_expression` later.
2. Implement `policy_guard.py` with action allowlist, text length limits, rate limits, and deny reasons.
3. Implement `audit_log.py` as append-only JSONL with timestamps and policy results.
4. Add VOICEVOX as a local HTTP client, but keep it behind the same `say` action.
5. Add VRChat Chatbox through python-osc or an existing OSC tool, again behind `say`.
6. Only after the minimal reflex is stable, extend to avatar expressions/actions.
7. Connect OpenClaw as display/control shell after the kernel/reflex boundary is stable.

## Portfolio framing

For Japanese career/portfolio contexts, describe this as:

> HermesAgentを中枢として、VRChat OSC、VOICEVOX、OpenClaw、ローカルLLMツール実行を接続するPythonベースの embodied agent harness を設計。structured action proposal、policy guard、rate limit、audit log、memory event により、安全な外界接続と身体反射を実現する構成を志向。

## References

- `references/hakua-vrchat-embodiment.md` — session-derived Hakua architecture framing and first-reflex plan.
- `references/line-gateway-wake-quiet.md` — session-derived wording and mechanics for LINE/gateway wake triggers, quiet cues, and real shutdown paths.
