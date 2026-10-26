---
name: shinka-osint-troubleshooting
description: Troubleshooting guide for ShinkaEvolve-OSINT plugin in Hermes Agent
category: osint
version: 1.0.0
author: Hermes Agent
---

# ShinkaEvolve-OSINT Troubleshooting

## Description
Guide to resolve common issues with the ShinkaEvolve-OSINT plugin (shinka-osint) in Hermes Agent, including environment setup, dependency problems, and isolation errors.

## When to Use
- Encountering `ModuleNotFoundError: No module named 'shinka'` or `No module named 'shinka_mcp_server'`.
- Seeing `import failed` or `tool_evaluate failed` in Hermes output.
- Getting `Shinka tool shinka_evaluate failed (exit 1): ...` errors.
- Wanting reliable operation of `shinka-osint analyze`, `briefing`, etc.

## Setup Steps

### OSINT Agent Stack Integration
When using ShinkaEvolve-OSINT as part of the `osint-agent` stack:

1. **Enable the stack**
   ```bash
   hermes osint-agent status  # Verify all components
   ```
   Expected stack: `sitdeck-osint`, `worldmonitor-osint`, `scrapling-feeds`, `shinka-osint`, `computer_use`, `web`

2. **Install cron jobs for morning/evening briefs**
   ```bash
   hermes osint-agent cron install
   ```
   Creates two jobs:
   - `osint-agent-morning` at 08:00 JST
   - `osint-agent-evening` at 18:00 JST
   Scripts placed in `~/.hermes/scripts/osint-agent-morning.py` / `osint-agent-evening.py`
   ```
   Adjust the path to your checkout.

3. **Confirm the package is importable**
   ```bash
   python -c "import shinka; print('shinka ok')"
   ```
   Should print without error.

4. **Set the Python interpreter for isolated workers (optional but recommended)**
   If you continue to see import errors in the isolated subprocess, explicitly point to the Hermes venv’s Python:
   ```bash
   hermes config set shinka_osint.python "%USERPROFILE%/Documents/New project/hermes-agent/.venv/Scripts/python.exe"
   ```
   (This sets `SHINKA_OSINT_PYTHON` environment variable for the plugin.)

5. **Disable isolation for problematic tools (workaround)**
   If the above does not resolve `shinka_evaluate` failures, you can temporarily disable process isolation for that tool by editing the plugin:
   - Open `plugins/shinka-osint/bridge.py`
   - Remove `"shinka_evaluate"` from the `_ISOLATED_TOOLS` frozenset near line 50.
   - Restart Hermes.
   This lets the tool run in the main Hermes process where the `shinka` package is already imported.

6. **Test a simple analysis**
   ```bash
   hermes shinka-osint analyze national_security_framework --source-mode mock
   ```
   Should return a JSON result with `"success": true`.

## Common Pitfalls
- **Using system Python instead of Hermes venv**
  The isolated subprocess defaults to `py -3` or `python3` from the PATH, which may lack the `shinka` package. Always verify `SHINKA_OSINT_PYTHON` points to the Hermes venv’s Python.
- **Missing dependencies in the checkout**
  The `shinka-evolve-osint` package declares dependencies in `pyproject.toml`. Installing in editable mode pulls them in; otherwise, you may see `ModuleNotFoundError` for `anthropic`, `google-genai`, etc.
- **Path issues on Windows**
  Use forward slashes or escaped backslashes in paths. Avoid mixing `\` and `/` in environment variables.
- **Stale plugin caches**
  After changing `SHINKA_OSINT_PYTHON` or reinstalling the package, restart the Hermes gateway or reload plugins (`hermes plugins reload`) to ensure the plugin picks up the new environment.

## Verification
After applying the fixes, run:
```bash
hermes shinka-osint status
```
Check that `importable` is `true` and `tool_count` > 0.

Then run a real analysis:
```bash
hermes shinka-osint analyze national_security_framework --source-mode real
```
You should see a successful result with scores and evidence blocks.

## References
- Plugin source: `plugins/shinka-osint/`
- ShinkaEvolve-OSINT repository: <https://github.com/zapabob/ShinkaEvolve-OSINT>
- Hermes plugin documentation: see `agents.md` under "Plugins"
- MILSPEC Morning Briefing workflow: `references/milspec-osint-briefing.md`
- Briefing template: `templates/milspec-morning-briefing.md`
- Pre-cron verification script: `scripts/pre_cron_verify.py`