---
name: hermes-provider-oauth-operations
description: Configure Hermes model providers, fallback chains, and OAuth re-authentication from remote or messaging sessions, especially when the `hermes` executable is not on PATH and the repo checkout must be invoked with `python -m hermes_cli.main`.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [hermes, model, provider, oauth, xai-oauth, grok, openai-codex, telegram, remote-auth]
---

# Hermes Provider OAuth Operations

Use this skill when the user asks to change Hermes' primary model/provider, set a fallback/sub model, or re-authenticate an OAuth-backed provider such as `xai-oauth`/Grok from Telegram or another remote messaging channel.

This skill supplements the protected `hermes-agent` skill with operational patterns learned from real remote-auth sessions.

## Core workflow

1. Load `hermes-agent` first for canonical Hermes commands and config semantics.
2. Prefer Hermes CLI config commands over direct file edits for `~/.hermes/config.yaml`. For this user's current default, set Codex GPT-5.5 with low reasoning effort:
   ```bash
   hermes config set model.provider openai-codex
   hermes config set model.default gpt-5.5
   hermes config set agent.reasoning_effort low
   hermes config set fallback_providers '[{"provider":"xai-oauth","model":"grok-build-0.1"}]'
   ```
3. If `hermes` is not on PATH but the repo checkout is available, run the same CLI through the module entrypoint from the repo root:
   ```bash
   python -m hermes_cli.main config set model.provider openai-codex
   python -m hermes_cli.main config set model.default gpt-5.5
   python -m hermes_cli.main config set agent.reasoning_effort low
   python -m hermes_cli.main config set fallback_providers '[{"provider":"xai-oauth","model":"grok-build-0.1"}]'
   ```
4. Always verify the effective config after writes before declaring success:
   ```bash
   hermes config | sed -n '/◆ Model/,+6p'
   python - <<'PY'
   from pathlib import Path
   import yaml
   cfg = yaml.safe_load(Path.home().joinpath('.hermes','config.yaml').read_text(encoding='utf-8-sig'))
   print(cfg.get('model', {}))
   print('reasoning_effort:', cfg.get('agent', {}).get('reasoning_effort'))
   PY
   ```
   If a Windows atomic replace/permission error appears after one of several `config set` calls, inspect the file before retrying: a prior command may already have left the requested provider/model/reasoning values in place.
5. Start OAuth re-auth in an interactive PTY when the flow requires pasting a callback URL/code:
   ```bash
   python -m hermes_cli.main auth add xai-oauth --no-browser --manual-paste --timeout 900
   ```
   Use `background=true` with `pty=true` so the process remains at `Callback URL:` instead of receiving EOF.
6. Send the authorization URL to the user. Ask them to paste either:
   - the full failed loopback callback URL, e.g. `http://127.0.0.1:<port>/callback?code=...&state=...`, or
   - the bare authorization code if the provider displays it in-page.
7. Submit the pasted callback/code to the waiting PTY process, then verify with:
   ```bash
   python -m hermes_cli.main auth list xai-oauth
   python -m hermes_cli.main config | sed -n '1,20p'
   ```
8. If this is a gateway/Telegram session, tell the user whether a gateway restart or `/reset` is needed for the new model/provider state to apply to future sessions.

## Pitfalls

- Do not patch `~/.hermes/config.yaml` directly when Hermes refuses sensitive config writes. Use `hermes config set` or `python -m hermes_cli.main config set`.
- Non-PTY background OAuth commands can exit immediately at the paste prompt with `missing authorization code` because stdin is closed. Restart the command with `pty=true` and keep the process running.
- Treat `command not found: hermes` as a PATH/setup condition, not as a Hermes failure. Use the repo module entrypoint if available.
- Do not ask the user to send tokens, refresh tokens, or secrets. The callback URL/code is an OAuth authorization artifact for the waiting local flow; handle it only by submitting it to the active auth process.
- Avoid saying re-auth is complete until `auth list` or an equivalent command shows a new usable credential.

## References

- `references/grok-oauth-telegram-manual-paste.md` — concise transcript-derived notes for xAI/Grok OAuth via Telegram manual paste.
