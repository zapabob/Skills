---
name: hermes-config-troubleshooting
description: Diagnose and fix Hermes Agent configuration file corruption, especially auth.json.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata.hermes.tags: hermes, config, troubleshooting, auth.json
metadata.hermes.category: devops
metadata.hermes.related_skills: hermes-agent, computer-use
---

# Hermes Config Troubleshooting Skill

## When to Use
Use this skill when you suspect Hermes configuration files (e.g., auth.json, config.yaml) are corrupted, causing authentication errors, tool failures, or unexpected behavior. Typical signs include JSON parsing errors, missing credentials, or Hermes failing to start.

## Prerequisites
- Hermes Agent installed and accessible via CLI.
- Basic familiarity with JSON and YAML formats.
- Access to the Hermes home directory (`~/.hermes` or `%USERPROFILE%\.hermes`).

## How to Run
1. Invoke the skill via `hermes skills run hermes-config-troubleshooting` (or use the agent directly).
2. Follow the interactive prompts or execute the steps outlined in the Procedure section.
3. Optionally, reference the detailed notes in `references/auth-json-corruption.md`.

## Quick Reference
- **Check JSON validity**: `python -m json.tool <file>`
- **View file**: `hermes read_file --path <file>`
- **Backup before editing**: copy the file to `.bak`
- **Restore from backup**: copy `.bak` back to original location
- **Re-authenticate**: run `hermes auth` to refresh tokens

## Procedure
1. **Locate the suspect file**
   The auth.json lives in your active Hermes home directory.
   Run `echo $HERMES_HOME` (or check `hermes config show paths`)
   - default is `~/.hermes/`, profiles use `~/.hermes/profiles/<name>/`.
   Typical path: `$HERMES_HOME/auth.json`.

2. **Validate JSON syntax**
   Run:
   ```bash
   python -m json.tool /path/to/auth.json
   ```
   If it returns an error, note the line and column indicated.

3. **Inspect the file content**
   Use `hermes read_file` or a text editor to view the problematic area. Common issues:
   - Truncated strings (missing closing quotes)
   - Trailing commas
   - Invalid control characters
   - Duplicate keys

4. **Create a backup**
   Copy the file to `auth.json.bak` before making changes.

5. **Fix the JSON**
   - Remove trailing commas.
   - Ensure all strings are properly quoted and escaped.
   - Validate that the structure matches the expected schema (top‑level object with `active_provider`, `credential_pool`, `providers`, `updated_at`, `version`).
   - If unsure, compare with a known good backup or the default template.

6. **Validate again**
   Re-run the JSON validation step. Repeat until no errors are reported.

7. **Restart Hermes**
   Restart the Hermes agent or reload the configuration (`hermes auth` may trigger a reload).

8. **Verify functionality**
   Try the operation that previously failed (e.g., `hermes tools`, `hermes auth check`). Success indicates the fix worked.

## Pitfalls
- **Do not edit protected files** like `AGENT.md`, `MEMORY.md`, or `SOUL.md`; they are managed by the ASI core.
- Avoid using non‑JSON tools (e.g., `cat` with special characters) that can corrupt the file further.
- If the file appears zero‑length, it may have been truncated; restore from the latest backup or re‑run `hermes auth` to regenerate.
- Some fields (like tokens) are intentionally redacted in logs; do not mistake missing tokens for corruption if they are intentionally omitted.

## Verification
After completing the procedure, run:
```bash
hermes auth
```
You should see a successful status (e.g., `last_status: "ok"` for the active provider) and no JSON parsing errors. Additionally, run a command that uses the configuration (like `hermes tools list`) to confirm normal operation.

## References
- See `references/auth-json-corruption.md` for a detailed transcript of a real‑world corruption case and the steps taken to resolve it.