---
name: social-memory-sync
description: "Synchronize social platform session logs (Telegram, Discord, LINE, X/Twitter) into durable agent memory using Ebbinghaus consolidation and optional LINE personal-account bot plugins."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, ebbinghaus, social, line, telegram, discord, twitter, x, cleanup]
    related_skills: [autonomous-ai-agents/ebbinghaus-memory]
---

# Social Memory Sync

Use this skill to consolidate social platform interaction logs into durable agent memory and to build/operate personal-account bot interfaces on Telegram, Discord, LINE, and X/Twitter.

## When to Use

- Use when the user asks for social memory integration, session log cleanup, platform trace consolidation, or bot plugin development.
- Use after playing back social sessions when durable facts, preferences, or guardrails should survive sleep/decay cycles.
- Use when wiring a personal account into Hermes as a bot through `linepy`, Telegram/Discord adapters, or LM-twitterer pipelines.
- Use when auditing or repairing broken sync scripts and Windows-path execution wrappers.

## Scope

This skill is a class-level umbrella covering:
1. Social log replay and durable memory enrichment.
2. Platform-specific bot plugin wiring (LINE personal account, X posting policy, Telegram/Discord low-frequency reply behavior).
3. Known-good patterns for Windows execution and subprocess isolation.

## Core Procedure

### Consolidate Social Traces Into Memory

1. Ensure the active memory provider is `ebbinghaus` or compatible.
2. Run the social sync script from the repo's `.venv`, quoting full Windows paths.
3. Capture resulting counts (`sessions seen`, `X events seen`, `memories written`, `sleep cycle results`).
4. If the user defines an operational policy during cleanup, immediately save it as a high-salience durable memory via `ebbinghaus_memory` with `action="remember"`.
5. Rehearse or sleep-maintain only after the durable policy writes are confirmed.

### Write Durable Policy Memories

Use the pattern introduced in the 2026-06-20 session:

```json
{"action":"remember","content":"Public X posts require dry-run first. No attachment_url/reply unless explicit. Restrict auto-replies to follower-only/rate-limit scope. Disclose AI involvement.","tags":"social-memory,x,twitter,lm-twitterer,policy,safety","salience":0.95}
```

Key requirements:
- Use tags that the user or future agents can search for.
- Use salience `0.9` or higher for operational policy constraints.
- Verify with `recall` using the same tags before relying on the memory.

### Build a Personal-Account Bot Plugin

**Primary reference**: `fadhiilrachman/line-py` (`master` branch). The `mas` branch referenced by the user does not exist as of the 2026-06-20 session; default to `master` unless otherwise confirmed.

Core API shape:
```python
from linepy import LINE
line = LINE('EMAIL', 'PASSWORD')
line = LINE('AUTHTOKEN')
line.log("Auth Token : " + str(line.authToken))
```

Message dispatch:
- `line.sendMessage(to, text)` for 1:1 or group chat.
- `line.sendMessageWithMention(to, text, dataMid=[...])` for mention formatting.
- Rich media: `sendImage`, `sendVideo`, `sendAudio`, `sendFile`, `sendSticker`, `sendGift`.

Auth flows:
- Credential login using email + password.
- QR login using `loginWithQrCode`; LINE posts a verifier URL `line://au/q/<verifier>`.
- Auth-token recovery and local certificate persistence in `<id>.crt`.

OEPoll long-poll event loop:
```python
oepoll = OEPoll(line)
oepoll.addOpInterruptWithDict({
    OpType.RECEIVE_MESSAGE: RECEIVE_MESSAGE,
})
while True:
    oepoll.trace()
```

Plugin integration pattern for Hermes:
1. Create `plugins/<name>/plugin.yaml` with platform list.
2. Implement `register(ctx)` to expose CLI slash commands and lifecycle hooks.
3. Implement async event loops separate from the agent process; use Hermes queue tools for cross-process observations.
4. For Windows, avoid `simple_term_menu`; prefer `curses_ui.py` patterns if interactive menus are needed.

## Windows Execution Pattern

From the 2026-06-20 session:
- Use the project-local `.venv` Python: `"C:/Users/<user>/.../.venv/Scripts/python.exe" <script>`
- Quote full paths with spaces.
- Use `python -m py_compile <script>` to validate before execution.
- Use `python -c "..."` for small file/content checks when targeting Windows paths.

## Session Memory Operations

1. `sleep` with `prune=true` and configured thresholds reduces overall saturation.
2. `recall` before answering from memory strengthens retrieval stats.
3. `rehearse` on high-salience policy entries before heavy sleep passes.
4. `decay` with `prune=true` is threshold-based cleanup; avoid pruning memories with high salience or user-preference tags.

## Verification

- `ebbinghaus_memory` appears in the active tool list.
- `remember` followed by `recall` returns the stored content.
- A sleep pass returns `mode: "sleep_cycle"` with `rehearsed`, `forgotten`, and `pruned` arrays.
- The personal-account bot can authenticate and at least log its auth token before live chat dispatch.
- Plugin files exist under `plugins/<name>/` with `plugin.yaml`, `__init__.py`, and `register(ctx)`.

## Pitfalls

- Do not treat `sleep` as a background thread. The built-in idle path is lazy and runs before the next turn after the idle threshold.
- Do not prune high-salience memories just because retention is low.
- Do not hardcode `~/.hermes` in instructions or code; use profile-aware paths.
- Do not use full private chat dumps as durable memory; redact secrets and tokens before storage.
- Do not assume the `mas` branch exists for `line-py`; verify branches first and default to `master` unless the user provides a commit SHA.
- Do not retry identical failing Hermes commands unchanged; inspect root cause and switch strategy when the same invocation fails twice with identical output.

## References

- `references/session-social-consolidation-2026-06-20.md`
- `references/2026-06-21-counts-only-cron-sync.md` — validated Bitwarden-safe scheduled sync pattern: canonical `state.db`, direct lm-twitterer JSONL parsing, URL-only public X artifacts, scoped post-write guard/remediation, and counts-only final output.
