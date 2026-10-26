---
name: cross-platform-memory-sleep
description: "Cross-platform memory consolidation workflow for Discord, X, Telegram, and LINE with Ebbinghaus sleep and safe channel separation."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [memory, ebbinghaus, sleep, discord, telegram, line, x, social-memory, automation]
---

# Cross-Platform Memory Sleep

Use this skill when the user wants social/agent memory across Discord, X, Telegram, and LINE to be consolidated, slept, or automated as one continuity layer while keeping channel-specific details separated.

## Goals
- Preserve stable shared facts across platforms.
- Keep platform-specific tone, relationship context, and reply behavior separate.
- Run Ebbinghaus recall / rehearsal / sleep cycles for durable memory maintenance.
- Avoid leaking secrets, raw auth data, or private URLs.

## Recommended workflow

1. **Recall first**
   - Search for durable context about cross-platform identity, preferences, and ongoing projects.
   - Only trust high-confidence shared facts.

2. **Separate what should stay separate**
   - Discord: reply style, channel norms, bot cadence.
   - X: public post style, public artifacts, post URLs.
   - Telegram: DM continuity and direct user preferences.
   - LINE: direct contact and urgent/home-channel context.

3. **Consolidate only stable shared facts**
   - Name / persona / long-term preferences.
   - Cross-platform project continuity.
   - Stable safety and privacy boundaries.

4. **Run sleep maintenance**
   - Rehearse important low-retention memories.
   - Forget low-salience, obsolete traces.
   - Prune only after threshold-based decay.

5. **Use a cron fallback when the memory tool is unavailable**
   - For scheduled maintenance jobs, prefer `no_agent: true` plus a deterministic script if the cron environment cannot expose `ebbinghaus_memory`.
   - Write a short marker note into the job output directory and defer the actual memory consolidation to a later interactive Hermes session.
   - See `references/cron-fallback-pattern.md` for the standard fallback shape.

6. **Notify carefully**
   - If sending results to messaging platforms, keep the summary short and sanitized.
   - Do not include secrets, tokens, raw OAuth responses, or private callback URLs.

## Full memory integration / unification pass (multi-platform + secrets vault + X posting)

When the user explicitly requests "記憶の統合と管理" (memory integration and management) or equivalent for a setup involving Hermes gateway (Telegram/LINE/Discord) + lm-twitterer (X) + Bitwarden vault:

1. **Gather state**
   - `ebbinghaus_memory` with `action=stats`, `list`, `recall` (high limit, low min_score).
   - `memory` tool for user profile entries.
   - `lm_twitterer_status` + parse recent `~/.hermes/lm-twitterer/activity.jsonl` for public post counts.
   - `cronjob list` (focus on Bitwarden-safe memory/social sync, cross-platform-memory-sleep, lm-twitterer jobs).

2. **Ingest / reinforce durable facts via Ebbinghaus**
   - Use `ebbinghaus_memory remember` (salience 0.85–1.0) for:
     - Primary address forms and in-joke/persona cues (e.g. ボブにゃん + にゃ〜ん(雄犬)).
     - Secrets policy (Bitwarden-only for passwords, env vars, AES keys; never in memory or chat).
     - Cross-platform continuity rules (one layer for facts, strict separation for tone/cadence/style; public X only when `posted:true`).
     - Orchestration preference (はくあ/Codex leads; Hermes/Grok as subagents).
     - Workflow automation rule (recurring tasks → skills + cron).
     - X safety (explicit human intent required; English posts must stay English-only).
     - TTS preference (Hakua/irodori voice, specific reminder cadences).
     - Backup policy (private GitHub AES-256-GCM, Bitwarden key escrow).
   - Immediately `rehearse` the highest-salience entries (especially persona cues and policy facts).

3. **Trigger live sync automation**
   - `cronjob run` on the "Bitwarden-safe memory/social sync" job (id usually contains "1180..." or similar).
   - Optionally run the daily "cross-platform-memory-sleep" fallback script job.
   - Re-check `cronjob list` and `ebbinghaus_memory list` after.

4. **Verify**
   - Confirm new high-salience memories appear with recent `memory_id`.
   - Confirm lm-twitterer shows correct identity (#hermesagent, whitelist, posted counts).
   - Report only counts, reinforced items, and residual risk — never raw content or secrets.

See `references/2026-06-11-memory-unification-pass.md` for a concrete execution trace (salience values, memory_ids created, cron runs, DB inspection commands, and verification steps used in a real session).

## Safe consolidation rules
- Keep platform-specific identity boundaries intact.
- Do not merge public X artifacts into private chat history unless the result is a deliberate summary.
- Do not merge secret-bearing notes into general memory.
- Prefer conservative consolidation over aggressive merging.

## Ebbinghaus commands

Typical maintenance pass:

```json
{"action":"recall","query":"Discord X Telegram LINE cross-platform memory","limit":5}
```

Sleep cycle:

```json
{"action":"sleep","prune":true,"rehearse_threshold":0.7,"forget_threshold":0.35,"salience_keep_threshold":0.6,"threshold":0.4}
```

Remember a durable cross-platform preference:

```json
{"action":"remember","content":"User wants Discord, X, Telegram, and LINE memories treated as one continuity layer, while channel-specific details stay separated.","tags":"user-preference,cross-platform-memory,social-memory","salience":0.85}
```

## Output style
- Report only what changed.
- If nothing changed, stay quiet or say that no consolidation was needed.
- When useful, return a brief bullet summary:
  - shared facts kept
  - channel-specific facts preserved
  - items rehearsed or forgotten

## Pitfalls
- Do not treat public X posts as private memory by default.
- Do not collapse different platforms into one undifferentiated profile.
- Do not retain raw auth or callback strings.
- Do not assume a recalled memory is still current without live verification.
