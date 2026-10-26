---
name: employee-plugin-builder
description: "Scaffold a standalone Hermes plugin for role-based AI employee organizations. Use when creating a plugin with permissioned profiles, SOUL templates, kanban/cron integration, CLI and slash commands."
metadata:
  hermes:
    tags: [plugin, roles, permissions, kanban, cron, scaffolding]
    related_skills: [ai-employee-org, skill-creator]
---

# Employee Plugin Builder

Build a complete standalone Hermes plugin with role profiles, tool permissions, and ops directories.

## File Tree

```
plugins/<name>/
  plugin.yaml
  __init__.py
  core.py
  hooks.py
  cli.py
  slash.py
  cron_install.py
  stack.py
  config/roles.yaml
  scripts/generate_roles.py
  skill/
    SKILL.md
    templates/SOUL-<role>.md
    references/architecture.md
```

## plugin.yaml

Minimal manifest: name, version, description, author, kind: standalone, platforms list.

## core.py

- Define `ROLES` tuple with name, description, soul filename, toolset list.
- Implement `install_skill()`, `setup_profiles()`, `setup_kanban()`, `ensure_ops_dirs()`, `status()`, `install_all()`.
- Use `get_hermes_home()` and `display_hermes_home()`.
- Use `subprocess.run` with `sys.executable -m hermes_cli.main` for profile/kanban commands.

## config/roles.yaml

```yaml
permissions:
  <role>:
    tool_whitelist: [terminal, file, web, kanban, cronjob, skills, memory]
    blocked_paths: []
    confirm_required: false
```

## hooks.py

- `_load_roles()` reads roles.yaml.
- `enforce_permissions(role)` returns tool whitelist + confirm flag.
- Lifecycle hooks (`kanban_lifecycle`, `agent_lifecycle`) log and return guard.

## cron_install.py

- Define `JOBS` tuple with name, schedule, prompt, toolsets.
- `install_all_crons()` calls `_run_hermes(["cron", "create", ...])`.
- Support `telegram_chat_id` delivery target.

## scripts/generate_roles.py

- Write `config/roles.yaml` from a Python dict using `yaml.safe_dump`.
- Run with project-local `.venv` Python.

## Verification

```bash
"C:/path/to/.venv/Scripts/python.exe" -m py_compile core.py cli.py slash.py hooks.py cron_install.py stack.py scripts/generate_roles.py
```

## Installation and Loading

After scaffolding, the plugin must be installed into the Hermes plugins directory:

```powershell
Copy-Item 'C:\path\to\hermes-agent\plugins\<name>\*' "$HOME\.hermes\plugins\<name>\" -Recurse -Force
```

Then enable it:

```bash
hermes plugins enable <name>
```

Without the `~/.hermes/plugins/<name>` copy, `plugins list` will not see the plugin and `plugins enable` will report "not installed or bundled."

## Service Bridge Plugin Variant

When the plugin wraps an external server (Go binary, Node service, daemon) rather than just defining roles, extend the tree:

```
plugins/<name>/
  plugin.yaml
  __init__.py
  <service>/           # external checkout or vendored server
    main.go
    go.mod
  bridge.py            # subprocess manager, health checks, port discovery
  store.py             # sqlite3 persistence for sessions, tokens, events
  auth.py              # JWT issue/verify
  api.py               # local HTTP server if Hermes tools need an endpoint
  ...
```

Pattern notes:
- Lifecycle hooks (`on_session_start`, `on_session_end`) should start/stop the subprocess, not just log.
- Use `subprocess.Popen` with a session-scoped `contextvars` token so concurrent Hermes sessions don't double-launch.
- Bridge ports should be dynamic (pick free port at startup) or configurable via `config.yaml` under the plugin namespace.
- Secrets (LINE auth tokens, JWT signing keys) belong in `~/.hermes/.env`, never in plugin YAML or git.

## Pitfalls

- Do NOT hardcode ops dirs using user home; use profile-safe paths.
- Plugin toolsets must match allowed tools in roles.yaml to avoid silent drops.
- Windows paths in subprocess calls must be escaped or full-quoted.
- Repo-local `plugins/<name>/` is not auto-discovered; copy to `~/.hermes/plugins/<name>/` first.
- Bash `~` does not expand inside `cp`/`mkdir` on Windows/MSYS; use `$HOME` or absolute `C:\Users\...` paths.
- User-specified Git branch names (e.g. `mas`) may not exist; verify actual default branch (`master`/`main`) before deep-research or cloning.
- `plugins enable <name>` fails with "not installed or bundled" when the plugin only exists in the repo tree; copy to `~/.hermes/plugins/<name>/` first and re-run enable.
