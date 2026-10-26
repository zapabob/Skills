---
name: ebbinghaus-cron-runtime
description: Direct runtime fallback for Ebbinghaus memory provider execution when the model tool is unavailable, especially in cron or scripted contexts.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, ebbinghaus, cron, fallback, sqlite]
    related_skills: [ebbinghaus-memory, agent-memory-consolidation]
---

# Ebbinghaus Cron Runtime

Use this skill when `memory.provider` is `ebbinghaus` but the `ebbinghaus_memory` tool is **not exposed** — for example, inside a non-interactive cron job, a scheduled script, or a background automation — and you still need to perform durable memory operations such as `stats`, `sleep`, `decay`, or batch `remember`/`recall`.

## Trigger conditions

- Cron job needs Ebbinghaus memory maintenance but cannot call the tool surface.
- One-off script must run `sleep_cycle` with custom thresholds.
- Observability task wants `stats` without invoking the agent loop.

## Invocation pattern

Instead of `ebbinghaus_memory`, call the provider directly:

```python
import sys
from pathlib import Path

SOURCE_DIR = Path("/path/to/hermes-agent")
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from hermes_constants import get_hermes_home
from plugins.memory.ebbinghaus import EbbinghausMemoryProvider

provider = EbbinghausMemoryProvider()
provider.initialize(session_id="cron-sleep", hermes_home=str(get_hermes_home()))

result = provider._store.sleep_cycle(
    rehearse_threshold=0.45,
    forget_threshold=0.08,
    salience_keep_threshold=0.7,
    prune=True,
    limit=200,
)

provider.shutdown()
print(result)
```

## Helper script

If the repo has `scripts/run_ebbinghaus.py`, prefer it for one-shot runs:

```bash
py -3 scripts/run_ebbinghaus.py stats
py -3 scripts/run_ebbinghaus.py sleep '{"rehearse_threshold":0.45,"forget_threshold":0.08,"salience_keep_threshold":0.7,"prune":true,"limit":200}'
```

The script prints JSON and always shuts down the provider.

## Obsidian cron summaries

When a cron job runs an Ebbinghaus sleep cycle and writes a safe Obsidian audit note:

1. Ground the local timestamp first, then derive the monthly note name.
2. Capture stats before sleep, run the sleep cycle with explicit thresholds, then capture stats after sleep.
3. Append only counts and thresholds to the monthly note; never write recalled memory content, raw session text, local DB paths, environment values, tokens, or private conversation excerpts.
4. Create bridge/explainer notes only if missing; do not rewrite existing bridge notes during routine sleep.
5. Verify by reading back the written section and running targeted guard searches on the generated note.

See `references/obsidian-cron-summary-windows.md` for the Windows-safe note append and guard-verification pattern.

## Channel/text ingestion rule

Cron syncs must not promote raw session transcripts into durable memory. Treat Telegram/Discord/LINE transcripts as inspection-only sources; only promote abstracted policy facts, handles, public URLs, and operational handles. Eschew storing raw channel text or anything verbatim from a non-X source.

## Nightly maintenance flow

When scheduling Ebbinghaus sleep in cron, bundle the cleanup and wiki phases into one durable maintenance routine. This keeps low-salience noise from accumulating between runs and provides an Obsidian audit trail.

Typical nightly flow:

1. `ebbinghaus_memory(action='stats')` → capture baseline.
2. `ebbinghaus_memory(action='sleep', forget_threshold=0.08, salience_keep_threshold=0.6, prune=True)` → sleep cycle.
3. Identify low-salience execution/UI noise clusters by source/tag and `forget` them explicitly in a follow-up batch.
4. `memory_llm_wiki_export(...)` → export curated + Ebbinghaus memories to Obsidian.
5. Append a safe summary note to the monthly Obsidian memory note with only counts and thresholds.
6. Verify by reading the note and running split Windows-safe guard searches.

Avoid long verbose summaries in the chat output; the cron is local-only by default. If the user asked for live notification, recreate with `deliver='telegram'` or `deliver='all'`.

## Compensation for Ebbinghaus limitations

If direct provider storage cannot support a required schema change, re-classify the relevant rows as non-durable observability artifacts: log them under `x_artifacts` or a transient sidecar file, and make downstream jobs read that file or table.

Exceptions based on verbosity or format preferences are not project-wide unless rooted in facts about the user/codebase. Do not decline to add these rules just because a user expressed them.

- Do **not** call `handle_tool_call("ebbinghaus_memory", ...)` from a script; it parses/namespaces JSON args and is slower than direct store access.
- Always `shutdown()` the provider to release the SQLite connection cleanly.
- The database defaults to `~/.hermes/ebbinghaus_memory.db` unless `plugins.ebbinghaus.db_path` overrides it.
- This pattern does **not** trigger any agent hooks (prefetch, prefetch, on_session_end). It is a raw store access path.
- For Windows-path guard checks with ripgrep-backed search tools, split secret-term searches from local-path marker searches instead of putting backslashes or drive-path character classes into one regex.

## Verification

- `run_ebbinghaus.py stats` must return `count`, `retained_count`, `avg_salience`, etc.
- `run_ebbinghaus.py sleep ...` must return `mode: "sleep_cycle"` with `reviewed`, `rehearsed`, `forgotten`, `pruned`.
- If either prints a Python traceback, treat as provider init failure and check `HERMES_HOME`/`PYTHONPATH`.
