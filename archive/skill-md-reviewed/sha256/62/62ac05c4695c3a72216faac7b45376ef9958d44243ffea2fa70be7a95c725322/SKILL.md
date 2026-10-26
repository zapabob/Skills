---
name: hermes-plugin-standalone-run
description: "Run a Hermes plugin headless when its tools are absent."
version: 1.0.0
author: Hermes Agent
tags: [hermes, plugin, cron, standalone, headless, venv, lm-twitterer]
---

# Hermes Plugin Standalone Execution

## When to use

A plugin's tools (e.g. `lm_twitterer_*`) may be **absent from the agent's callable tool schema** — common when a cron job runs as a bare agent or a `no_agent: true` job spawns a standalone process. Calling `tool_call(name="<plugin>_foo")` then returns *"not a deferrable tool"* (or the tool simply isn't listed).

This does NOT mean the plugin is broken. The plugin's Python functions are still importable and callable directly. Execute them headless in the Hermes venv. This is the same pattern the `lm-twitterer-operations` skill calls the "Safe Script Pattern" (no-agent cron uses direct plugin import, not CLI).

## Locating the plugin

- Plugins often live under `~/.hermes/plugins/<name>/` (a junction/symlink on Windows), **not** necessarily in the repo's `plugins/` dir.
- The Hermes venv is `<repo>/.venv/Scripts/python.exe` (Windows) / `<repo>/.venv/bin/python` (Linux/macOS).
- Plugin code imports shared Hermes modules (`hermes_constants`, `hermes_cli.config`) from the **repo root**, so add the repo root to `sys.path` before importing the plugin.

## Verified run recipe (Windows / MSYS git-bash)

```python
import sys, os
REPO = r"C:/path/to/hermes-agent"          # repo root (has hermes_constants.py, hermes_cli/)
PLUGIN = r"C:/Users/<user>/.hermes/plugins/<name>"
sys.path.insert(0, REPO); sys.path.insert(0, PLUGIN)
import importlib.util
spec = importlib.util.spec_from_file_location("plugin_mod", os.path.join(PLUGIN, "core.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["plugin_mod"] = mod            # REQUIRED before exec (see gotcha)
spec.loader.exec_module(mod)
res = mod.some_function(...)                # call the plugin entry point
```

A worked, copy-ready example for lm-twitterer is in `templates/standalone_plugin_run.py`.

## Windows / MSYS gotchas (verified in-session)

1. **Register module in `sys.modules` before `exec_module`.** Loading via `spec_from_file_location` without first assigning `sys.modules["name"] = mod` raises `AttributeError: 'NoneType' object has no attribute '__dict__'` at the first `@dataclass` (dataclasses resolves `sys.modules[cls.__module__]`). Always register first.
2. **MSYS path mangling.** Passing `/c/Users/...` to the native `python.exe` makes Windows treat it as relative → `C:\c\Users\...` (file not found). Always pass Windows-native drive-letter paths (`C:/Users/...` or `C:\Users\...`).
3. **ripgrep under `.hermes`.** `search_files` / `rg` can fail with an IO error resolving paths under `~/.hermes` (junction). Use terminal `ls`/`grep` on the resolved absolute path instead.
4. **Set `HERMES_HOME`.** Export `HERMES_HOME` (e.g. `C:/Users/<user>/.hermes`) so `get_hermes_home()` and the plugin env loader (`get_env_value`) resolve state dir, whitelist, and credentials correctly.
5. **LLM facade not bound.** Plugins that *generate* text (replies, posts) call a bound LLM factory (`_llm_factory`) that only exists inside the live Hermes process. A standalone script raises e.g. *"LM-twitterer plugin LLM facade is not bound"* if it reaches generation. This is harmless when the operation finds **zero candidates to act on** (the loop never reaches generation) — the normal case for read-only / no-match runs. For operations that must actually generate, run inside the live agent (tool call), not standalone.

## Safe output

Plugins may return structures containing secrets-adjacent data (cookies, tokens, threads, raw candidate records, tweet IDs). When reporting from a headless run, extract ONLY safe summary fields (counts, ok/error booleans, status messages) and never print the raw result object or `actions[]` arrays. Keep stdout clean so cron delivery doesn't leak private data.

## Pitfalls

- Don't assume a missing tool = broken plugin. Check whether the tool is simply not in the current session's schema (cron/no-agent), then run headless.
- Don't `pip install` plugin deps into the global interpreter — the plugin runs in the repo `.venv`. Verify deps there first (`python -c "import <dep>"`).
- After a successful headless run that changes deployed behavior, sync the script into the repo copy if it's meant to be the canonical cron launcher.
