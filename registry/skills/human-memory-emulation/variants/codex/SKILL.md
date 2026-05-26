---
name: human-memory-emulation
description: Build, install, enable, operate, or debug a Hermes/Codex memory system that mimics human memory with cue encoding, local storage, retrieval, rehearsal, and an Ebbinghaus forgetting curve. Use when the user asks for human-like memory, memory encoding/storage/search, forgetting-curve behavior, Ebbinghaus memory, or the Hermes ebbinghaus memory provider/plugin.
---

# Human Memory Emulation

## Core Workflow

Use this skill to maintain a local Hermes memory provider that behaves like a lightweight human-memory model:

1. Inspect the active Hermes repo and config before changing anything.
2. Prefer the bundled provider path `plugins/memory/ebbinghaus/` in `hermes-agent`.
3. Keep the provider local-first: SQLite storage, no cloud service, no secret exposure.
4. Activate it with `memory.provider: ebbinghaus` in `$HERMES_HOME/config.yaml`.
5. Validate discovery, tool calls, and forgetting-curve behavior with focused tests.
6. Restart Hermes gateway/WebUI only when config changes must reach running processes.

## Implementation Contract

Implement the provider as a `MemoryProvider` named `ebbinghaus`.

Expose one tool named `ebbinghaus_memory` with these actions:

- `remember`: encode content into cues and store it.
- `recall`: search by cue overlap and retention score.
- `rehearse`: strengthen a memory and reset its retention anchor.
- `forget`: delete one memory.
- `decay`: list or prune memories below a retention threshold.
- `list`: show recent memories.
- `stats`: show count, retention, and database path.

Use the retention curve:

```text
retention = exp(-elapsed_days / stability_days)
```

Increase stability with salience, rehearsal count, retrieval count, and memory strength. Keep scores explainable in tool output so another agent can see why a memory surfaced.

For more detailed schema and scoring notes, read [references/hermes-ebbinghaus-provider.md](references/hermes-ebbinghaus-provider.md).

## Validation

Run the bundled check script first when diagnosing a live install:

```powershell
python "$env:USERPROFILE\.codex\skills\human-memory-emulation\scripts\check_hermes_ebbinghaus.py" --repo "<path-to-hermes-agent>"
```

Use the Hermes venv for repo tests on Windows:

```powershell
venv\Scripts\python.exe -m pytest tests\plugins\test_ebbinghaus_plugin.py tests\agent\test_memory_provider.py::TestPluginMemoryDiscovery -q --timeout-method=thread
```

If validating the full memory manager, also run:

```powershell
venv\Scripts\python.exe -m pytest tests\agent\test_memory_provider.py -q --timeout-method=thread
```

## Operating Rules

- Do not store tokens, passwords, API keys, raw `.env` content, or private chat IDs as memories.
- Do not enable a second external memory provider at the same time; Hermes allows one external provider alongside built-in memory.
- When using live storage, default database path is `$HERMES_HOME/ebbinghaus_memory.db`.
- Prefer probe tests against a temporary database unless the user explicitly wants to write a live memory.
- On Windows, override pytest timeout to `--timeout-method=thread`; `SIGALRM` is not available.
