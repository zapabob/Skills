---
name: hermes-memory-plugin-integration
description: Design and implement Hermes plugin integrations that read from and write to agent memory systems such as Ebbinghaus memory, while preserving persona continuity and safe external-output boundaries.
tags:
  - hermes
  - plugins
  - memory
  - ebbinghaus
  - social-output
  - testing
---

# Hermes Memory Plugin Integration

Use this skill when modifying a Hermes plugin so its outputs are aligned with the agent's durable memory, sleep/consolidation cycle, or Ebbinghaus-style recall/decay. Typical examples: social posting plugins, briefing generators, cron outputs, personal-agent embodiments, or any plugin that should both consume trusted memories and write generated artifacts back into memory.

## Core pattern

1. **Identify the memory substrate first.**
   - Prefer the official tool/provider API when it is available inside the runtime.
   - If the memory tool is external to the repo but has a stable local store, bridge through that store defensively.
   - For the Ebbinghaus memory store used in this environment, the durable SQLite DB has a `memories` table with fields such as `content`, `encoded`, `cues`, `tags`, `salience`, `strength`, `source`, `session_id`, `created_at`, and `updated_at`.

2. **Fail closed, not loud.**
   - If the DB path is absent, schema is missing, credentials are unavailable, or memory recall errors, the plugin should continue with normal behavior and no memory context.
   - Do not make posting, cron delivery, or UX-critical actions depend on memory being available unless the user explicitly asked for that hard dependency.

3. **Separate trusted memory from untrusted public content.**
   - Memory snippets are trusted context for style/factual continuity.
   - Tweets, mentions, RSS items, web pages, and user-provided public text are untrusted content.
   - Keep explicit prompt boundaries: e.g. “Use these trusted memory notes only as style and factual continuity; do not expose them as private memory dumps.”

4. **Use bounded recall.**
   - Add env/config switches:
     - enable/disable bridge
     - memory DB/path/provider
     - recall limit
   - Keep snippets short and limit count to prevent memory dumps, prompt bloat, or accidental disclosure.
   - Rank with lightweight overlap + salience/strength/freshness when full semantic retrieval is unavailable.
   - For cron/social reconciliation, prefer counts-only summaries in stdout and keep raw candidate rows out of the final report.

5. **Write generated artifacts back as low/medium salience memories.**
   - For drafts/posts/briefings, store a concise durable record, not a whole session narrative.
   - Include provenance fields such as `source='lm-twitterer'` or the plugin name.
   - Include tags/cues for later retrieval: plugin name, output class, persona, topic.
   - Do not store secrets, cookies, raw auth state, or private thread dumps.

6. **Preserve external-output safety gates.**
   - Dry-run/draft paths may write to memory as drafts.
   - Live external actions still need the plugin’s usual publishing gate; memory alignment is not permission to publish.

## Testing checklist

- Unit-test that relevant memory is injected into the generation prompt.
- Unit-test that no memory context is injected when disabled or DB missing.
- Unit-test that dry-run/live output writes the expected memory row with source/tags.
- Keep tests independent of the user’s real memory DB by creating a temporary SQLite fixture with the expected schema.
- If repository pytest addopts depend on optional plugins, run targeted tests with addopts cleared rather than treating the missing plugin as a product failure.

## Implementation notes

- Avoid adding heavy dependencies just to tokenize memory. A simple regex token overlap and small CJK n-grams are often enough for a first bridge.
- Use `INSERT ... ON CONFLICT(content) DO UPDATE` when the memory table has unique `content` rows.
- Always truncate recalled snippets before inserting into prompts.
- For SQLite-backed social sync, treat `state.db` as session/message provenance and `ebbinghaus_memory.db` as the durable store; do not write durable memory into `state.db`.
- Expose bridge state in the plugin status command so operators can see whether memory alignment is active.

## References

- `references/lm-twitterer-ebbinghaus-bridge.md` — concrete implementation notes from bridging `plugins/lm-twitterer` to the Ebbinghaus memory DB.
- `references/social-platform-ebbinghaus-sync.md` — pattern for syncing LINE/Discord/Telegram session traces plus LM-twitterer X activity into Ebbinghaus memory with redaction, tags, upserts, and sleep verification.
