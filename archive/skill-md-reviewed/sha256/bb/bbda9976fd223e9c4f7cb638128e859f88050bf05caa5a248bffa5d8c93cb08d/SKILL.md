---
name: codex-browser-mcp
description: Route Codex bundled Browser and Chrome plugin usage from Hermes Agent without creating invalid external MCP entries.
version: 1.0.0
author: local
platforms: [windows]
metadata:
  hermes:
    tags: [mcp, browser, chrome, codex, computer-use]
    related_skills: [codex, hermes-agent]
---

# Codex Browser MCP Routing

Use this skill when Hermes is asked to use `@browser`, `@ブラウザ`, `@chrome`, `plugin://browser@openai-bundled`, `plugin://chrome@openai-bundled`, browser automation, Chrome automation, or browser-based computer use through Codex.

## Important Boundary

`browser@openai-bundled` and `chrome@openai-bundled` are Codex bundled plugins. They are not plain external MCP servers with a stable `command` or `url`, so do not add fake Hermes MCP server entries for their `plugin://` URIs.

## Routing

- Preload this skill together with `codex` for Codex-driven browser work.
- Delegate to Codex App or Codex CLI when the requested operation requires Codex Browser or Codex Chrome.
- Include an explicit plugin mention in the Codex prompt:
  - `@browser` or `@ブラウザ` for in-app browser work.
  - `@chrome` for real Chrome profile work.
- Use Hermes native tools only when they provide the browser capability needed for the current task.
- Only use `hermes mcp add` when a real MCP server command or URL exists.

## Codex State To Expect On This PC

Codex should keep these configured:

- `[plugins."browser@openai-bundled"] enabled = true`
- `[plugins."chrome@openai-bundled"] enabled = true`
- `[features] browser_use = true`
- `[features] browser_use_external = true`
- `[features] computer_use = true`
- `[features] in_app_browser = true`
- `[features] plugins = true`
- `[features] apps = true`

## Guardrails

- Do not inspect or export browser passwords, cookies, local storage, session stores, or profile secrets without a narrowly scoped user request.
- Ask before downloads, uploads, account changes, purchases, form submissions, extension installs, login changes, permission prompts, or persistent browser-side actions.
- Keep shell commands, file deletion, and OS-level actions outside this browser routing skill. Use normal shell/tooling with its own safety checks.
- Do not bypass authentication, CAPTCHA, paywalls, consent gates, or site access controls.
