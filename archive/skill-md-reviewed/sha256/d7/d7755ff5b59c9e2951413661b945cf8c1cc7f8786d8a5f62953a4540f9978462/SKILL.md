---
name: agent-memory-consolidation
description: "Design and operate agent memory maintenance: sleep-like consolidation, forgetting, skill promotion, and session replay."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, agents, consolidation, sleep, skills, session-search, cron]
    created_by: agent
---

# Agent Memory Consolidation

Use this skill when designing, configuring, or reviewing an agent's long-term memory behavior: nightly/idle memory cleanup, human sleep-inspired replay, deciding what belongs in memory vs skills vs session search, or preventing memory bloat.

## Core model

Treat agent memory maintenance as a **sleep-like consolidation cycle**, not as raw log compression.

Separate memory into classes:

- **Working/short-term context**: active task details; do not persist unless they become durable preferences or procedures.
- **Episodic record**: what happened in sessions; keep in session history/search, not durable memory.
- **Semantic memory**: stable facts about the user, environment, or project conventions that reduce future steering.
- **Procedural memory**: reusable workflows and troubleshooting recipes; encode as skills, not user memory.
- **Forgetting candidates**: temporary URLs, OAuth codes, issue/PR IDs, transient error states, and one-off progress notes.

## Sleep cycle workflow

For a nightly or idle-time pass:

1. **Replay** recent sessions within a bounded lookback window.
   - Identify user corrections, repeated preferences, durable environment facts, and successful non-trivial procedures.
2. **Classify** each candidate.
   - User identity/preference/environment fact -> persistent memory.
   - Reusable procedure/workflow/pitfall -> skill update.
   - One-off progress/task artifact -> leave in session history only.
   - Secret, OAuth code, temporary link, stale ID -> discard.
3. **Consolidate** only compact, durable facts.
   - Write declarative memory entries, not imperatives.
   - Avoid saving anything likely stale within a week.
4. **Promote procedures to skills**.
   - Prefer patching an existing class-level umbrella skill.
   - Add `references/` files for session-specific details or condensed research.
5. **Forget aggressively**.
   - Do not preserve OAuth auth URLs, `code=` parameters, stack traces after a fix, or transient setup failures as durable constraints.
6. **Handle cross-platform social traces as bounded memory artifacts** when the user asks to unify LINE/Discord/Telegram/X memory.
   - Read Hermes gateway platforms from `state.db` `sessions.source` (for example `line`, `discord`, `telegram`) and X/LM-twitterer artifacts from the plugin activity log rather than guessing from titles.
   - Treat desktop-facing Hermes sessions as first-class sources too: `webui` and `tui` are the practical desktop/PC traces, while `telegram`/`line`/`discord` are messaging traces.
   - Store compact redacted traces with explicit provenance/tags, not raw private chat dumps.
   - For implementation details, see `references/social-platform-ebbinghaus-sync.md` and `references/cross-platform-memory-sync-2026-06-07.md`.
7. **Report briefly** if user-facing reporting is enabled.
   - Summarize fixed memories, skill updates, and discarded categories without exposing secrets.
- **Use explicit source mapping for cross-platform social sync.**
   - Trust `sessions.source` for Hermes gateway sessions (`line`, `telegram`, `discord`, `webui`, `tui`, `cli`) rather than inferring source from titles or message text.
   - Read X/lm-twitterer artifacts from `~/.hermes/lm-twitterer/activity.jsonl`.
   - When reading Hermes SQLite, use `sessions.started_at` for ordering; `created_at` is not part of the sessions schema in this environment.
   - Write only compact policy facts, public URLs, and generalized design principles into durable memory.
   - See `references/social-platform-ebbinghaus-sync.md` for the safe extraction recipe.

**Explicit full unification pass (when user says "記憶の統合と管理")**:
When a user with active gateway + lm-twitterer + Bitwarden vault requests memory integration:
- Start by loading the core skills (ebbinghaus-memory, cross-platform-memory-sleep, agent-memory-consolidation, bitwarden-memory-vault).
- Perform bulk `ebbinghaus_memory remember` (salience 0.85–1.0) for persona cues, secrets policy, cross-platform separation rules, orchestration preferences, X safety, TTS/voice rules, and backup policy.
- Immediately `rehearse` the highest-salience items (especially in-jokes and policy facts).
- Manually `cronjob run` the "Bitwarden-safe memory/social sync" job.
- Verify with ebbinghaus list, lm_twitterer_status (confirm posted counts and identity), and cron status.
- Report only counts, reinforced memory_ids, and "integration completed". See `references/2026-06-11-memory-unification-pass.md` (under cross-platform-memory-sleep) for the exact trace.

## Design pattern for Hermes

A practical Hermes implementation can be a scheduled cron job that runs during low-activity hours:

```yaml
memory_sleep:
  enabled: true
  schedule: "30 3 * * *"
  idle_only: true
  lookback_hours: 24
  consolidate_user_profile: true
  consolidate_skills: true
  prune_ephemeral: true
  report: summary
```

The prompt for such a job should be self-contained and must prohibit recursive scheduling. It should explicitly distinguish:

- `memory` for stable facts and preferences
- `skill_manage` for procedures and pitfalls
- `session_search` for historical recall
- no persistence for transient task state

## Ebbinghaus forgetting-curve layer

When the memory backend tracks retention/stability, add an explicit Ebbinghaus layer rather than treating sleep as simple cleanup:

```text
R(t) = exp(-days_since_reinforcement / stability_days)
```

Implementation policy:

1. **Decay continuously** by computing retention from the last reinforcement anchor.
2. **Rehearse important low-retention traces**: if retention falls below a rehearsal threshold but salience remains high, increment rehearsal/strength and reset the reinforcement anchor.
3. **Forget low-value low-retention traces**: if retention falls below the forget threshold and salience is low, classify as forgotten; optionally prune.
4. **Report IDs and thresholds** so automated nightly jobs can audit what was rehearsed, forgotten, and pruned.

For the concrete Hermes Ebbinghaus provider pattern, see `references/ebbinghaus-sleep-cycle-implementation.md`.

### Cron-to-Obsidian sleep summaries

When a scheduled job is only meant to run an Ebbinghaus sleep cycle and externalize a safe audit summary to Obsidian, keep the path narrow:

1. Get the current local/JST timestamp with `terminal` first so the monthly note name and heading are grounded.
2. Capture `stats` before sleep, run `sleep` with explicit thresholds, then capture `stats` again.
3. If the `ebbinghaus_memory` model tool is not exposed in the active tool surface, use the provider directly from the Hermes source tree as a fallback: instantiate `plugins.memory.ebbinghaus.EbbinghausMemoryProvider`, call `initialize(..., hermes_home=str(get_hermes_home()))`, and invoke `handle_tool_call("ebbinghaus_memory", args)` for `stats`/`sleep`; always `shutdown()` afterward.

   Note: If the `ebbinghaus_memory` tool is exposed in the toolset, you can also invoke it non-interactively in a cron job using `hermes -z` with a JSON action string, e.g.:
   `hermes -z "Use the ebbinghaus_memory tool to get stats."`
   `hermes -z "Use the ebbinghaus_memory tool to run a sleep cycle with prune=true, rehearse_threshold=0.45, forget_threshold=0.08, salience_keep_threshold=0.7, limit=200."`

   **Important**: The `sleep` tool's output may not reliably reflect actual changes (e.g., reporting 0 memories processed while counts actually changed). Always verify the sleep cycle's effect by comparing the `count` field in `stats` before and after the sleep operation, as documented in the ebbinghaus-memory skill's pitfalls.
4. Write only count/threshold summaries to Obsidian. Do not copy recalled memory content, private session text, local environment variable values, tokens, or raw JSON payloads.
5. Create a bridge/explainer note only if it is missing; never overwrite an existing bridge note during routine sleep.
6. Final cron reports should be short and include only the saved path, before/after counts, and prune count unless a step failed. Report in Japanese and keep it concise, as per user preference.

See `references/cron-obsidian-ebbinghaus-summary.md` for a concrete session trace and safe markdown shape.

## Pitfalls

- **Do not equate more memory with better memory.** Sleep is selective consolidation plus forgetting.
- **Do not save task progress as memory.** Progress belongs in session history or task trackers.
- **Do not save tool failures as negative durable rules.** Capture the fix or retry pattern under the relevant setup/troubleshooting skill.
- **Do not create one-session-one-skill clutter.** Patch class-level umbrella skills and put session detail in `references/`.
- **Do not store secrets or OAuth artifacts.** Auth URLs, redirect `code=` values, and tokens are never memory.
- **For social-sync runs, trust the source field rather than titles.** Hermes gateway sessions should be classified by `sessions.source` (e.g. `line`, `telegram`, `discord`). If the activity log is missing, report that as an absence and do not infer posts from unrelated files.
- **Treat X activity as public only when `dry_run=false` and `posted:true`.** Generated-only drafts and reply simulations belong in session history, not durable memory.
- **When logs are large or truncated, page intentionally.** Use offset-based reads on `activity.jsonl` / journals rather than assuming the first chunk contains the newest or only relevant artifacts.
- **Do not rely solely on the output of the `ebbinghaus_memory sleep` tool to assess changes.** Always compare the `count` field in `stats` before and after the sleep cycle to verify actual changes.
- **Use the Ebbinghaus memory DB, not `state.db`, for durable memory writes.** In this profile the memory table lives in `~/.hermes/ebbinghaus_memory.db` (`memories` table); `~/.hermes/state.db` is for sessions/messages and should only be read for source classification.
- **Keep cron sync output abstract.** Final reports should contain only counts, exclusions, and residual risk; never raw candidate records, secret-like fragments, or local path details.
- **If a public post workflow only produced dry runs, keep it local.** Generated-only X drafts are not public artifacts and should not be promoted into memory as if they were posted.

### Cross-platform social sync

See `references/social-platform-ebbinghaus-sync.md` for the safe extraction recipe that maps Hermes gateway sessions (`sessions.source`) and `lm-twitterer/activity.jsonl` into abstract policy memory.
## References

- `references/sleep-cycle-design.md` — concise design notes from the session that introduced the user's desired sleep-like memory mechanism.
- `references/ebbinghaus-sleep-cycle-implementation.md` — concrete Hermes Ebbinghaus provider pattern: store API, `sleep` tool action, tests, and pitfalls.
- `references/obsidian-ebbinghaus-sleep-bridge.md` — pattern for resolving an Obsidian vault, running Ebbinghaus sleep, and writing safe monthly sleep summaries without raw logs or secrets.
- `references/obsidian-session-inventory-sleep-2026-06-22.md` — concrete pattern for “記憶の統合と睡眠 + Obsidian session-log inventory”: aggregate `state.db`, run Ebbinghaus stats/sleep/rehearsal, write sanitized monthly Markdown, and verify with split secret-pattern searches on Windows paths.
