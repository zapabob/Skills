---
name: skill-to-plugin
description: Convert an existing Hermes skill into a working plugin.
version: 0.1.0
author: Hermes
platforms: [windows]
tags: [Plugins, Hermes, Development, Windows]
metadata:
  hermes:
    tags: [Plugins, Hermes, Development, Windows]
---

# Skill to Plugin (CLI Binary Wrapping Pattern)

Converts a procedural Hermes skill (installing and driving a CLI binary) into a
proper Hermes plugin with structured tools, schemas, `check_fn` gating, and a
`plugin.yaml` manifest. Follows the **CLI Binary Wrapping** pattern from
`hermes-plugin-development` — no start/stop lifecycle, stateless per-call tools.

It covers the end-to-end conversion: scaffolding the directory, writing the
plugin manifest and register function, designing tool schemas and handlers,
avoiding common Windows/Python pitfalls, and verifying the plugin loads
correctly. It does NOT cover hooks, MCP servers, or model-provider plugins.

## When to Use

- User says "pluginize this" or "プラグイン化して" after you've authored a skill
- You want to turn a CLI workflow (install → run commands) into registered tools
- You are wrapping a third-party CLI binary (`unity.exe`, `officecli`, etc.)
- You need `check_fn` so tools disappear gracefully when the binary is missing

## Prerequisites

- Hermes repo with `plugins/` directory at the project root
- Existing skill or procedure (the "source" workflow)
- `hermes-plugin-development` skill loaded as reference
- Python 3.12+ with `py_compile` and `importlib` available

## How to Run

Create a `plugins/<plugin_name>/` directory with two files: `plugin.yaml`
(manifest) and `__init__.py` (register function with tool handlers). Then
enable via Hermes plugin system.

## Quick Reference

| File | Purpose |
|------|---------|
| `plugin.yaml` | Name, version, description, tool list, config schema |
| `__init__.py` | `register(ctx)`, tool schemas, handlers, `check_fn` |

| Pivot | Convention |
|-------|------------|
| Directory name | underscore (`unity_cli`) — hyphens break Python import |
| `toolset` value | hyphenated (`unity-cli`) — matches plugin name convention |
| Handler signature | `fn(values: dict, **kwargs) -> str` (JSON string) |
| Handler return | `json.dumps({"ok": bool, ...}, ensure_ascii=False)` |
| `check_fn` | Returns `bool` — `lambda: True` for always-available, named fn for gated |

## Procedure

### 1. Design the plugin structure

```
plugins/<name>/          ← directory: underscores, not hyphens!
  plugin.yaml             ← manifest
  __init__.py             ← register(ctx) + handlers
```

**Critical naming rule:** Python's import system cannot import a directory with
hyphens. If the plugin name has hyphens (e.g. `unity-cli`), create the
directory with underscores (`unity_cli`). The `toolset` string and
`plugin.yaml` `name` field still use hyphens — only the directory name must use
underscores.

### 2. Write `plugin.yaml`

Minimal manifest declaring tools and config:

```yaml
name: <plugin-name>           # hyphenated, e.g. unity-cli
version: 0.1.0
description: What it does.
author: Hermes
kind: standalone
platforms:
  - windows                   # declare only OS-bound platforms
provides_tools:
  - <tool_name_status>        # list every tool name
  - <tool_name_install>
  - <tool_name_run>
config:
  binary_path:
    type: string
    default: ""
    description: "Override path to the binary."
requires_env: []
```

### 3. Write `__init__.py`

Include these sections in order:

**a) Helpers** — binary discovery and subprocess runners

```python
import json, logging, os, subprocess
from pathlib import Path
from typing import Any, Optional

KNOWN_PATHS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Vendor" / "bin" / "tool.exe",
]

def _find_binary(override: str = "") -> Optional[Path]:
    if override:
        p = Path(override)
        return p.resolve() if p.exists() else None
    for p in KNOWN_PATHS:
        if p.exists():
            return p.resolve()
    return None

def _run_tool(args: list[str], binary_path: str = "", timeout: int = 60) -> dict:
    binary = _find_binary(binary_path)
    if not binary:
        return {"ok": False, "code": -1, "stdout": "", "stderr": "Binary not found."}
    try:
        result = subprocess.run([str(binary)] + args, capture_output=True, text=True, timeout=timeout)
        return {"ok": result.returncode == 0, "code": result.returncode,
                "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "stdout": "", "stderr": "Timed out"}
    except Exception as exc:
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(exc)}

def _to_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False)
```

**b) Schemas** — JSON Schema for each tool. Declare as module-level constants:

```python
STATUS_SCHEMA = {
    "type": "object",
    "properties": {},
    "description": "Check if tool is installed.",
}
```

**c) Handlers** — each returns JSON string via `_to_json()`:

```python
def _handle_status(values: dict, **kwargs: Any) -> str:
    binary = _find_binary()
    if not binary:
        return _to_json({"ok": True, "installed": False})
    return _to_json({"ok": True, "installed": True, "path": str(binary)})
```

**d) `check_fn`** — gates tools that need the binary:

```python
def _is_installed(**kwargs: Any) -> bool:
    return _find_binary() is not None
```

**e) `register(ctx)`** — wire everything:

```python
def register(ctx) -> None:
    ctx.register_tool(
        name="tool_status",
        toolset="<plugin-name>",       # hyphenated
        schema=STATUS_SCHEMA,
        handler=_handle_status,
        check_fn=lambda: True,         # always visible
        description="Check if installed.",
    )
    ctx.register_tool(
        name="tool_run",
        toolset="<plugin-name>",
        schema=RUN_SCHEMA,
        handler=_handle_run,
        check_fn=_is_installed,        # gated
        description="Run a command.",
    )
```

### 4. Verify the plugin

Use a verification script that mimics the Hermes plugin loader:

```python
import importlib, json, sys
sys.path.insert(0, ".")
plugin = importlib.import_module("plugins.<name_underscored>")

# Check helpers exist
assert hasattr(plugin, "_find_binary")
assert hasattr(plugin, "_run_tool")

# Stub ctx to test registration
class StubCtx:
    def __init__(self):
        self.tools = []
    def register_tool(self, name, toolset, schema, handler, check_fn, **kw):
        self.tools.append({"name": name, "has_handler": callable(handler),
                           "has_check_fn": callable(check_fn)})

ctx = StubCtx()
plugin.register(ctx)
assert len(ctx.tools) == N  # N = expected tool count

# Run a handler
result = json.loads(plugin._handle_status({}))
assert result["ok"] is True
```

Run via `terminal`:

```bash
cd /project/root && python -c "..."  # or run the script
```

## Pitfalls

- **Hyphens in import path.** Python cannot `import` a directory named
  `unity-cli`. Always use underscores (`unity_cli`) for the filesystem
  directory. The `toolset` and `plugin.yaml name` still use hyphens.
- **Forgetting `toolset` in `register_tool`.** This is a required positional
  argument. Omitting it raises
  `PluginContext.register_tool() missing 1 required positional argument: 'toolset'`
  and the plugin loads as `enabled=False`.
- **Handler must return `str` (JSON).** Returning a dict breaks the tool
  dispatcher. Always wrap the return dict with `json.dumps()`.
- **Schema `description` field.** Both the tool-level `description` (passed to
  `register_tool()`) and the schema dict-level `description` are separate. The
  schema description appears in the tool's parameter help; the register
  description appears in the tool index.
- **`check_fn` for install tools.** Install/status tools should use
  `check_fn=lambda: True` so they remain available even when the binary is
  missing — useful for first-time setup. Only gate run/command tools with a
  real `_is_installed` check.
- **Timeouts.** CLI binaries can hang. Set reasonable timeouts (60s default,
  300s max) on `subprocess.run` and handle `TimeoutExpired` gracefully.
- **Windows path from MSYS.** When running PowerShell from MSYS bash, `$env`
  must be escaped (`\$env`) or bash expands it to empty. In the plugin (pure
  Python), this isn't an issue — use `subprocess.run(["powershell.exe",
  "-NoProfile", "-Command", script])`.

## Verification

```bash
cd /project/root && python -c "
import importlib, sys
sys.path.insert(0, '.')
p = importlib.import_module('plugins.<name_underscored>')
print('Import OK')
# Stub register
class C:
    def __init__(s): s.tools = []
    def register_tool(s, n, ts, schema, handler, check_fn, **kw):
        s.tools.append(n)
ctx = C()
p.register(ctx)
print(f'Registered: {ctx.tools}')
"
```
