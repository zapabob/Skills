---
name: ebbinghaus-provider-direct
description: "Run Ebbinghaus memory provider from source for cron jobs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, ebbinghaus, cron, automation, sleep, provider]
    related_skills: [ebbinghaus-memory, agent-memory-consolidation, note-taking/obsidian]
---

# Ebbinghaus Provider Direct Invocation

Use this when you need to drive the Ebbinghaus memory provider from a Python
script — typically a cron job, a batch stats pass, or any context where the
`ebbinghaus_memory` *agent tool* is not exposed in the active tool surface.

> NOTE: The bundled `ebbinghaus-memory` skill's fallback section documents this
> same scenario but with two inaccuracies (it implies an **async** API and
> imports `get_hermes_home` from `core.utils`). This skill is the verified,
> fork-accurate version. Recommend `hermes curator adopt ebbinghaus-memory` to
> fix the bundled fallback.

## When to use

- A scheduled/cron task must run an Ebbinghaus `sleep` / `stats` cycle with no
  user present and no agent tool surface.
- You want to verify memory counts before/after programmatically.
- You are writing a probe/test against `plugins/memory/ebbinghaus/`.

## Prerequisites

- Run with the **project venv Python** (the provider imports `hermes_constants`
  and `plugins.*`, which must resolve from the fork root):
  - Windows: `.venv/Scripts/python.exe script.py`
  - macOS/Linux: `.venv/bin/python script.py`
- The script's `sys.path` must include the fork root (set `HERMES_REPO` or run
  with cwd = fork root).
- Do NOT import `core.utils`; `get_hermes_home` lives in top-level
  `hermes_constants`.
- **hakua-memory v0.3.5+** installed in the environment (`pip install -e /path/to/hakua-memory`)
- Python **>=3.11** required (hakua-memory v0.3.5+ drops Python 3.10 support)

## Verified recipe

```python
import json, os, sys
REPO = os.environ.get("HERMES_REPO", os.getcwd())
sys.path.insert(0, REPO)

from plugins.memory.ebbinghaus import EbbinghausMemoryProvider
from hermes_constants import get_hermes_home

p = EbbinghausMemoryProvider()
# initialize is SYNCHRONOUS and requires session_id as the 1st positional arg.
p.initialize("cron-memory-sleep", hermes_home=str(get_hermes_home()))

pre = json.loads(p.handle_tool_call("ebbinghaus_memory", {"action": "stats"}))

sleep = json.loads(p.handle_tool_call("ebbinghaus_memory", {
    "action": "sleep",
    "prune": True,                  # -> prune_mode "delete" (physical delete)
    "rehearse_threshold": 0.45,
    "forget_threshold": 0.08,
    "salience_keep_threshold": 0.7,
    "limit": 200,
}))

post = json.loads(p.handle_tool_call("ebbinghaus_memory", {"action": "stats"}))
p.shutdown()
print(json.dumps({"pre": pre, "sleep": sleep, "post": post}, ensure_ascii=False, default=str))
```

A known-good, ready-to-run copy lives at `templates/ebbinghaus_sleep_cron.py`.

## Critical API facts (verified on this fork)

- **Everything is synchronous.** `initialize(session_id, hermes_home=...)`,
  `handle_tool_call("ebbinghaus_memory", args) -> str` (JSON string, NOT a dict,
  NOT awaitable), and `shutdown()` are all plain methods. Do NOT `await` them.
- `handle_tool_call` returns a **JSON string**; `json.loads(...)` it.
- `initialize` signature is `initialize(self, session_id, **kwargs)`. Pass a
  dummy session id (e.g. `"cron-memory-sleep"`); `hermes_home` goes in kwargs.
- Correct imports:
  - `from plugins.memory.ebbinghaus import EbbinghausMemoryProvider`
  - `from hermes_constants import get_hermes_home`  (NOT `core.utils`)

## Sleep parameter semantics

- `prune=true` resolves to `prune_mode="delete"` (physical row DELETE).
- `prune_mode` accepts `none | archive | delete`. Leave `prune` unset to use the
  plugin default (usually `archive`).
- `forget_threshold`, `rehearse_threshold`, `salience_keep_threshold` are floats
  in `[0, 1]`, clamped internally.

## Stats & verification

- `stats()` returns a dict. Useful keys:
  - `count` = **total** memories across all states (use this to verify deletes).
  - `active_count`, `archived_count`, `retained_count`, `avg_salience`,
    `rehearsal_count`, `retrieval_count`.
- `sleep_cycle()` returns a dict with: `reviewed` (int), `rehearsed` (list of
  ids), `forgotten` (list of ids), `pruned` (list of ids), `archived` (list),
  `active_count`, `archived_count`.
- **Verification rule:** the `sleep` tool output can under-report changes. Always
  confirm by comparing `stats()['count']` BEFORE vs AFTER. A `delete` prune drops
  `count` by exactly `len(pruned)`. (Verified: 2293 -> 2218 = 75 pruned.)

## Platform / repo quirks (this fork, Windows host)

- venv layout is `.venv/Scripts/python.exe` (Windows), not `.venv/bin/activate`.
- `search_files` (ripgrep-backed) returns IO errors on repo paths containing
  spaces (e.g. `%USERPROFILE%\Documents\New project\hermes-agent`). Use
  `terminal` `grep`/`ls` for discovery on this checkout.

## Pitfalls

- Do not `await` any provider call — they are sync and the await will raise
  `TypeError: 'str'/'NoneType' is not awaitable`.
- Do not import `get_hermes_home` from `core.utils` — `ModuleNotFoundError`.
- `prune=true` physically deletes rows; counts are irreversible. Use `archive`
  mode if you only want to hide, not delete.
- Re-running a `sleep` mutates state — do not re-run just to "verify"; use a
  `py_compile` syntax check or a no-sleep `stats`-only dry run for re-verification.
- Do not estimate counts from the `sleep` output. Use `len(sleep["rehearsed"])`
  for rehearsed count, `len(sleep["pruned"])` for pruned count, or diff
  `stats()["sleep_rehearsal_count"]` / `stats()["count"]` before vs after.
- On some Windows installs, `python` is a non-functional WindowsApps stub. Use
  `py -3` instead, or the project venv at `.venv/Scripts/python.exe`.
