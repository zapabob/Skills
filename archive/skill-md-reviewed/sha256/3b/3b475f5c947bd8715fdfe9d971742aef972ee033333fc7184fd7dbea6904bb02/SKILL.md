---
name: hermes-plugin-direct-invoke
description: "Load Hermes plugin via importlib when no tool registered."
version: 1.0.0
author: Hermes Agent
tags: [hermes, plugin, importlib, lm-twitterer, x-twitter, standalone-invocation]
---

# Hermes Plugin Direct Invocation

## When to use this

Some Hermes plugins expose their real functionality only through in-process
tools (e.g. `lm_twitterer_reply_mentions`, `lm_twitterer_post`). If **no such
tool is registered in the agent's toolset** (common for direct/agent
invocations — not only no-agent cron), you must load the plugin's `core.py`
yourself and call its functions directly.

This is distinct from the no-agent cron pattern (which the
`lm-twitterer-operations` skill covers). Here the constraint is simply: *there
is no tool to call*, so you shell out to the repo `.venv` Python and import the
module.

## The load sequence (and the gotcha)

Naive `importlib` loading of a module that declares `@dataclass` classes at
module top-level (as `plugins/lm-twitterer/core.py` does at ~line 189) fails
with:

```
AttributeError: 'NoneType' object has no attribute '__dict__'
```

**Root cause:** the `dataclasses` decorator resolves the owning module through
`sys.modules.get(cls.__module__)`. If the load name is *not* registered in
`sys.modules` **before** `exec_module` runs, the lookup returns `None` and
crashes.

**Fix:** register the module object under its load name *before* `exec_module`,
and put the repo root on `sys.path` so the plugin's internal imports
(`hermes_constants`, etc.) resolve:

```python
import importlib.util, os, sys

REPO = "/path/to/hermes-agent"            # the user's Hermes fork checkout
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "plugins"))

spec = importlib.util.spec_from_file_location(
    "lmtt_core", os.path.join(REPO, "plugins", "lm-twitterer", "core.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["lmtt_core"] = mod            # REQUIRED before exec_module
spec.loader.exec_module(mod)
```

## Calling the plugin

```python
result = mod.reply_mentions(
    dry_run=False, count=50, mark_seen_on_dry_run=False,
    provider="moa", model="hakuapulse-orchestrator")
```

- Use the repo `.venv/Scripts/python.exe` (Windows) so
  `twitter_openapi_python` / `tweepy_authlib` / `js2py_` resolve. A global
  interpreter will fail the dependency probe.
- After editing `core.py`, spawn a **fresh** process — the in-process module
  cache means `.pyc` deletion alone is insufficient (same as Pitfall 1 in
  `lm-twitterer-operations`).
- If the plugin has a strict LLM allowlist (`plugins.entries.<plugin>.llm.
  allowed_providers`/`allowed_models`), pass `provider`+`model` that are in
  the allowlist, or the call is rejected even though globals differ.

## Safe output (Ebbinghaus / secrets policy)

Never print cookies, tokens, env vars, or raw candidate records. Emit only
counts/status. A counts-only wrapper pattern lives in
`references/standalone-invocation.md`.

## Caveats

- A `reply_mentions` result of `count_checked: 0` / "no new whitelisted
  mentions" is **not** proof that no mention exists — it reflects the
  HomeLatestTimeline sampling limitation (see Pitfall 0 in
  `lm-twitterer-operations`). Report it as a status, not a failure.
- This is a runtime workaround for a missing tool. If the registered tool
  later becomes available, prefer it over manual import.
