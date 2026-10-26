---
name: hermes-plugin-runtime-sync
description: Use when syncing Hermes plugins across runtime revisions.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, plugins, synchronization, runtime, verification, cron, mcp]
    related_skills: [hermes-plugin-development, windows-hermes-code-verification]
---

# Hermes Plugin Runtime Synchronization

## When to Use

Use this skill when a Hermes plugin must be ported between source and active runtime checkouts, when plugin discovery reports API drift, or when a plugin needs live `.hermes` verification after synchronization.

Use this class-level workflow when a plugin works in a development checkout but fails in the active Hermes runtime, or when current Hermes APIs have drifted from older plugin code. The goal is a minimal, evidence-backed port verified in the actual runtime tree.

## Principles

1. Identify the exact runtime checkout and interpreter before editing. On Windows, distinguish the development repository from `C:\Users\\<user>\\.hermes\\hermes-agent`.
2. Compare source and runtime files, manifests, tests, and Git history before changing anything. Do not infer missing files from an error string alone.
3. Respect discovery boundaries: general plugins, model providers, platforms, memory providers, and cron scheduler providers may use separate loaders.
4. Synchronize only verified plugin files and narrowly required host support modules. Preserve unrelated changes, secrets, and user configuration.
5. Verify syntax, focused tests, runtime discovery, and bounded capability probes separately. A loaded provider may still be unavailable because external configuration is absent.

## Compatibility checks

### Tool registration

Current `PluginContext.register_tool()` requires a `toolset` argument. When porting an older plugin, enumerate every `register_tool()` call and add a stable plugin-specific toolset, not only the first failing call:

```python
ctx.register_tool(
    name="example_status",
    toolset="example",
    description="...",
    schema={"type": "object", "properties": {}},
    handler=example_status,
    check_fn=check_requirements,
)
```

Keep handlers JSON-returning and compatible with `task_id` or `**kwargs` injection.

### Dedicated cron providers

Cron providers under `plugins/cron_providers/<name>/` are loaded through `plugins.cron_providers`, not ordinary `PluginContext`. Keep their registration compatible with the dedicated collector and exclude `cron_providers` from the general plugin scanner to avoid double discovery or shadowing. Verify discovery and loading independently:

```python
from plugins.cron_providers import discover_cron_schedulers, load_cron_scheduler
print(discover_cron_schedulers())
provider = load_cron_scheduler("chronos")
print(provider is not None, provider.name, provider.is_available())
```

`is_available() == False` is not automatically a load failure; report the provider instance/load error separately from missing URLs or credentials.

### CLI-side support modules

CLI-registering plugins may depend on host-owned modules such as `hermes_cli.cli_builtins`. If the module exists in the verified source checkout but is absent in the active runtime, synchronize it with the plugin and compile it before discovery. Avoid copying broad unrelated core changes merely to silence an import error.

## Synchronization workflow

1. Record current status and remotes for both source and runtime checkouts.
2. Locate manifests, entrypoints, tests, dedicated loaders, and all failing symbol definitions/usages.
3. Inspect relevant Git commits/diffs; compare focused hashes or diffs for plugin files, manifests, and support modules.
4. Apply the smallest source-backed change. For bulk edits on Windows, use a controlled script with explicit replacement-count assertions and compile immediately.
5. Copy only verified files into the active runtime checkout; do not overwrite unrelated dirty files.
6. Normalize line endings before comparing or syncing. Python text rewrites on Windows can introduce CRLF and create misleading whole-file diffs.
7. Run focused tests with the project venv and `-p no:randomly` when pytest-randomly creates unrelated seed noise.
8. Run a fresh runtime smoke process importing `model_tools`, forcing discovery, and printing bounded status: enabled flag, error, registered-tool count, and CLI names. Never print credentials or raw config.
9. Invoke dedicated provider loaders separately and distinguish `loaded` from `available`.
10. Report exact test counts, source/runtime status, and unrelated dirty artifacts without silently deleting them.

## Verification checklist

- [ ] Source and runtime paths are explicit.
- [ ] Git history/diff justifies the port.
- [ ] All registration calls match the current host signature.
- [ ] Dedicated provider categories are excluded from general discovery where required.
- [ ] Required host support modules exist in the runtime.
- [ ] Synchronized file hashes match after line-ending normalization.
- [ ] Changed files compile.
- [ ] Focused regression tests pass.
- [ ] Ordinary plugins report `enabled=True` and `error=None`.
- [ ] Dedicated provider loader returns an instance; availability is reported separately.
- [ ] Unrelated dirty files are preserved and disclosed.

## References

- `references/windows-runtime-sync-transcript.md` — validated Windows registration, dedicated-loader, support-module sync, line-ending, and smoke-test details.
