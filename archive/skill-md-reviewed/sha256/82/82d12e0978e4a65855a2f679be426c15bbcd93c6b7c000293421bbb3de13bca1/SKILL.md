---
name: agent-memory-systems
description: "Design and implement agent memory systems: durable memory, sleep consolidation, Ebbinghaus decay, skill promotion, and wake UX."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, agents, consolidation, forgetting-curve, sleep-cycle, personalization]
    related_skills: [hermes-agent, test-driven-development, systematic-debugging]
---

# Agent Memory Systems

Use this skill when designing, implementing, testing, or troubleshooting AI-agent memory behavior: persistent memories, user profiles, learned workflows, memory pruning, human-like sleep consolidation, Ebbinghaus forgetting curves, or wake/sleep UX.

## Core model

Separate memory into classes instead of storing every trace as a flat log:

1. **Short-term/context memory** — current session context; do not persist blindly.
2. **Episodic memory** — what happened in sessions; usually recoverable via session search, not durable memory.
3. **Semantic memory** — stable facts and user preferences that remain useful across sessions.
4. **Procedural memory** — reusable workflows; promote these to skills, not memory entries.
5. **Ephemeral traces** — OAuth URLs, temporary codes, transient errors, one-off progress; allow fast decay or deletion.

## Cross-model handoff packets

When the agent may need to move context between cloud models, local LLMs, or Grok-style providers, don't copy the raw log. Emit a compact evidence-backed packet instead:

- include stable user preferences and current project facts
- include corrections, contradictions, and freshness hints
- keep it short enough to survive smaller windows
- treat it as additive to the normal system prompt, not a replacement for durable memory storage
- gate the packet with a config flag when the feature needs to be opt-out (`memory.portable_memory_packet_enabled`)
- keep the packet builder separate from the provider-specific memory store so cloud models still get the normal prompt shape
- prefer a structured packet API on the memory store (e.g. `build_memory_packet(target, portable=True)`) and serialize that packet at prompt-build time, instead of hand-concatenating freeform memory text

For a concrete packet shape and trigger list, see `references/portable-memory-packets.md`.

## Implementation shape in Hermes

Hermes now uses a layered approach:

1. `tools/memory_tool.py` owns the durable store and exposes a structured packet builder.
2. `agent/system_prompt.py` decides whether to include a portable packet for the active provider/model family.
3. `hermes_cli/config.py` exposes `memory.portable_memory_packet_enabled`.
4. Tests should check packet emission/suppression directly, not only the full agent prompt.

This keeps the feature composable: cloud providers still get the normal memory snapshot, while Grok/local providers get the same snapshot plus a JSON packet that is easier to transfer between models.

## Human-like sleep consolidation

A sleep cycle is a maintenance pass, not just compression. It should:

1. Review recent traces or stored memories.
2. Rehearse high-salience memories whose retention is falling.
3. Merge duplicates or near-duplicates where safe.
4. Promote repeated successful procedures into skills.
5. Mark low-salience, low-retention traces as forgotten.
6. Optionally prune forgotten traces when the store supports safe deletion.
7. Return a concise report: reviewed, rehearsed, forgotten, pruned.

## Ebbinghaus retention pattern

Use an exponential forgetting curve:

```text
R(t) = exp(-elapsed_days / stability_days)
```

For a concrete cross-model handoff shape, see `references/portable-memory-packets.md`.

- `R(t)` is retention in `[0, 1]`.
- `elapsed_days` is time since the strongest reinforcement anchor: creation, rehearsal, or retrieval.
- `stability_days` grows with salience, retrieval count, rehearsal count, and successful task use.

Recommended policy:

- High salience + low retention → rehearse/consolidate.
- Low salience + low retention → forget or prune.
- Repeatedly retrieved memories → increase stability.
- User-explicit preferences → start with high salience.
- One-time transient details → low salience and decay quickly.

## Private remote memory vaults

When the user wants to store agent memories in a private GitHub repository, prefer an **encrypted memory vault** rather than pushing raw memory files. GitHub Private controls access but is not a substitute for encryption.

Recommended pattern:

```text
memory-vault/
├── README.md
├── .gitignore
├── manifest.json
├── encrypted/
│   ├── hermes-memory-YYYY-MM-DD.json.age
│   ├── ebbinghaus-YYYY-MM-DD.sqlite.age
│   └── skills-YYYY-MM-DD.tar.zst.age
└── scripts/
    ├── backup.sh
    ├── restore.sh
    └── scan-secrets.sh
```

Guidelines:

- Start with a sanitized summary export before adding database or skill archives.
- Encrypt artifacts with `age` or equivalent before commit/push.
- Generate a manifest with timestamps, checksums, source profile, and excluded classes.
- Secret-scan before every push.
- Exclude `.env`, cookies, OAuth codes/URLs, `auth.json`, browser profiles, Telegram/Discord/LINE/X tokens, raw full session logs, and unnecessary personal information.
- Store procedural knowledge as skills; store stable facts as sanitized semantic memories; do not preserve every episode.
- Add restore tests periodically so the vault is not just write-only backup.

## Implementation checklist

When adding sleep/forgetting behavior to an agent:

1. **Keep storage local/profile-safe** — use the framework’s profile-aware home/path helpers.
2. **Expose explicit maintenance APIs** — e.g. `sleep`, `decay`, `rehearse`, `forget`, and `stats` actions.
3. **Make pruning opt-in** — default to reporting forgotten traces before destructive deletion.
4. **Use configurable thresholds** — e.g. `rehearse_threshold`, `forget_threshold`, `salience_keep_threshold`, and `limit`.
5. **Track evidence fields** — salience, retention, stability, age, days since reinforcement, rehearsal count, retrieval count.
6. **Prefer deterministic tests** — inject a fake clock instead of waiting for real time.
7. **Test both store and provider/tool layers** — direct store behavior plus tool action routing/schema exposure.
8. **Avoid LLM-only sleep for deterministic maintenance** — use a script/tool path for decay/rehearsal; use LLM reasoning only for summarization or skill-promotion proposals.

## Idle sleep and wake UX

For user-facing agents, sleep can be triggered when there is no input for a configured time after startup or between turns.

Suggested state machine:

```text
awake -> idle timer expires -> sleeping -> next input arrives -> wake greeting -> normal response
```

Guidelines:

- Prefer a **lazy idle sleep** integration before adding background timer threads: when a new turn arrives, compare `now - last_activity_at`; if it exceeds the threshold, run memory maintenance before the turn and arm a one-shot wake greeting. This works across CLI and gateway paths when both share the main conversation loop.
- Run memory maintenance during `sleeping` or lazy pre-turn wake-up.
- Do not spam periodic sleep reports unless the user asked for them.
- On wake, prepend a short greeting if the user requested it, then continue the task.
- Make greeting/user-name preferences configurable or memory-backed, not hardcoded.

For this user, when implementing wake UX, the preferred wake greeting is:

```text
おはよう！ボブにゃん。
```

## Encrypted memory vault backups

When the user asks to back up or synchronize agent memory to GitHub/private storage:

1. Treat private repository visibility as access control, not encryption.
2. Store repository name/owner/remote/local path in environment variables, not hardcoded scripts.
3. Keep encryption keys outside git. If the user does not want GPG, use an AES-256-GCM envelope with a 32-byte random `MEMORY_VAULT_AES_KEY_B64` key in `~/.hermes/.env`.
4. Escrow the AES key in the user's password manager when requested/preferred. For this user, Bitwarden is preferred: create or update a secure item named `Hermes Memory Vault AES Key`, store `MEMORY_VAULT_AES_KEY_B64` as the password or hidden field, and store repo/local-path/encryption metadata as custom fields.
5. Verify password-manager escrow without printing the key: read the item back, compare it to the env value in-process, and report only `password_matches_env=True` plus a short non-secret hash prefix if useful.
6. Back up semantic memory, Ebbinghaus DBs, and skills; exclude `.env`, auth files, cookies, tokens, browser profiles, raw session logs, volatile caches, and lock files.
7. Verify by decrypting and extracting one backup before declaring success.

## References

- `references/ebbinghaus-sleep-cycle-hermes.md` — concrete Hermes plugin pattern from a session: store-level `sleep_cycle`, tool action schema, fake-clock tests, and wake preference notes.
- `references/memory-vault-aes-gcm-github.md` — AES-256-GCM private GitHub memory vault pattern, env variables, payload policy, and verification checklist.
- `references/encrypted-github-memory-vault.md` — private GitHub memory vault pattern: env-driven repo settings, encrypted-only payloads, secret exclusions, and verification checklist.

## Pitfalls

- Do not persist every session event as long-term memory; that creates noise and stale constraints.
- Do not store temporary OAuth URLs, codes, PR numbers, commit SHAs, or one-off progress in durable memory.
- Do not turn environment-specific failures into durable negative rules about a tool.
- Do not make forgetting destructive by default; report first, prune only when configured.
- Do not put procedural workflows in memory; write or patch a skill instead.

## Verification

Minimum test coverage for an implementation:

- Forgetting curve math returns expected exponential values.
- Rehearsal restores retention and increases stability/rehearsal count.
- Decay identifies low-retention traces.
- Sleep cycle rehearses high-salience decayed memories.
- Sleep cycle marks/prunes low-salience decayed memories.
- Provider/tool action exposes the sleep cycle and returns a structured report.
