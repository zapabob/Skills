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
2. Prefer Hermes CLI config commands over direct file edits for `~/.hermes/config.yaml`. Do **not** assume a cached or remembered model name is still valid; verify the provider owns the model before setting it. For a cheap/free default in this user's current setup, prefer OpenCode Zen auto-rotation:
   ```bash
   hermes config set model.provider opencode-zen
   hermes config set model.default auto-free
   hermes config set fallback_providers '[{"provider":"opencode-zen","model":"auto-free"},{"provider":"nvidia","model":"nvidia/llama-3.1-nemotron-70b-instruct"}]'
   ```
   For Codex accounts, avoid invented variants such as `gpt-5.5-low`; if using Codex, confirm the exact supported model first.
3. If `hermes` is not on PATH but the repo checkout is available, run the same CLI through the module entrypoint from the repo root:
   ```bash
   python -m hermes_cli.main config set model.provider opencode-zen
   python -m hermes_cli.main config set model.default auto-free
   python -m hermes_cli.main config set fallback_providers '[{"provider":"opencode-zen","model":"auto-free"},{"provider":"nvidia","model":"nvidia/llama-3.1-nemotron-70b-instruct"}]'
   ```
4. Always verify the effective config after writes before declaring success:
   ```bash
   hermes config | sed -n '/◆ Model/,+6p'
   python - <<'PY'
   from pathlib import Path
   import yaml
   cfg = yaml.safe_load(Path.home().joinpath('.hermes','config.yaml').read_text(encoding='utf-8-sig'))
   print(cfg.get('model', {}))
   print('fallback_providers:', cfg.get('fallback_providers'))
   print('reasoning_effort:', cfg.get('agent', {}).get('reasoning_effort'))
   PY
   ```
   If a Windows atomic replace/permission error appears after one of several `config set` calls, inspect the file before retrying: a prior command may already have left the requested provider/model/reasoning values in place.

   For this user's preferred high-end routing, do **not** put GPT5.5 under OpenCode Zen. GPT5.5 is a Codex-auth model:
   ```yaml
   model:
     provider: openai-codex
     default: gpt-5.5
   fallback_providers:
     - provider: openai-codex
       model: gpt-5.5
     - provider: nvidia
       model: nvidia/llama-3.1-nemotron-70b-instruct
     - provider: nous
       model: nous-freetier-latest
     - provider: opencode-zen
       model: opencode-freetier-latest
     - provider: custom
       model: local-llama
       base_url: http://127.0.0.1:8081/v1
       key_env: LOCAL_API_KEY
       start_command: powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\\Users\\downl\\Desktop\\hermes-agent-upstream-sync\\scripts\\windows\\start-hermes-llama-fallback-rtx3060.ps1" -Port 8081 -ContextSize 65536
       start_timeout_seconds: 180
   ```
   Leave `model.context_length` unset unless the user explicitly asks for a cap; Hermes should resolve each model's maximum context window when primary/fallback models switch.
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
- When using the `lm-twitterer` plugin, ensure `model.provider` and `model.default` are set to values allowed by the plugin (check `plugins.entries.lm-twitterer.llm.allowed_models` and `allowed_providers` in your config).
- If cron starts but job content fails with `404 Model ... not found` or `400 model is not supported`, treat it as a provider/model ownership mismatch until proven otherwise: inspect `agent.conversation_loop` logs, check `fallback_providers`, `delegation`, and named profile configs, then remove stale cache entries that bind model aliases to the wrong base URL.
- Never put `nvidia/...` model ids or `auto-free` under `provider: nous`. `auto-free` belongs to `opencode-zen`; NVIDIA NIM models belong to `provider: nvidia`; Nous fallbacks should use Nous-owned model names unless the current Nous provider catalog explicitly says otherwise.
- Never put `gpt-5.5` under `provider: opencode-zen` for this user's preferred route. GPT5.5 should use `provider: openai-codex` / Codex auth.
- Use live free-tier sentinels (`nous-freetier-latest`, `opencode-freetier-latest`) only when the Hermes checkout expands them at runtime; otherwise update `hermes_cli/fallback_chain.py` first or use a script that refreshes the catalog before writing config.
- On 429 routing requests, check whether the code retries the same credential once before falling back. If the user asks for immediate rotation, update the recovery path so rate-limit failures rotate/fallback without a same-model retry.
- Local llama fallback should be cold-started via a fallback `start_command`, not launched at Hermes startup, when the user says startup is already heavy.
- For NVIDIA NIM fallback in this Hermes tree, prefer the provider plugin canonical names `nvidia/llama-3.1-nemotron-70b-instruct` and `nvidia/llama-3.3-70b-instruct` over stale `nvidia/nemotron-3-*` aliases found in old catalogs/caches.
- After provider config edits, restart the gateway before judging cron behavior; the scheduler may have cached the old config in the running gateway process.

## References

- `references/grok-oauth-telegram-manual-paste.md` — concise transcript-derived notes for xAI/Grok OAuth via Telegram manual paste.
- `references/cron-provider-model-mismatch.md` — cron/fallback debugging notes for provider/model mismatch, stale Nous/NVIDIA aliases, and cache cleanup.
- `references/live-freetier-fallback-routing.md` — Codex GPT5.5 primary, live Nous/OpenCode free-tier fallback expansion, immediate 429 rotation, model-max context, and cold llama-server local fallback.
