---
name: codex-browser-mcp
description: Route Codex bundled Browser and Chrome plugin usage from Cursor without creating invalid external MCP entries.
---

# Codex Browser MCP Routing

Use this skill when a Cursor task mentions `@browser`, `@ブラウザ`, `@chrome`, `plugin://browser@openai-bundled`, `plugin://chrome@openai-bundled`, browser automation, Chrome automation, or browser-based computer use.

## Important Boundary

`browser@openai-bundled` and `chrome@openai-bundled` are Codex bundled plugins. They are not plain external MCP servers with a stable `command` or `url`, so do not add fake `mcpServers` entries for their `plugin://` URIs in `%USERPROFILE%\.cursor\mcp.json`.

## Routing

- Use Cursor's native browser automation or browser MCP if Cursor exposes one in the current session.
- If the task specifically requires Codex Browser or Codex Chrome, delegate to Codex App or Codex CLI and include `@browser`, `@ブラウザ`, or `@chrome` in the prompt.
- Use `@browser` or `@ブラウザ` for localhost, `127.0.0.1`, `file://` URLs, local web app screenshots, and in-app browser checks.
- Use `@chrome` when the task requires the user's real Chrome profile, existing tabs, cookies, SSO, Chrome extensions, or logged-in web sessions.
- Only edit `%USERPROFILE%\.cursor\mcp.json` for MCP servers that provide a real executable command or URL.

## Guardrails

- Do not inspect or export browser passwords, cookies, local storage, session stores, or profile secrets without a narrowly scoped user request.
- Ask before downloads, uploads, account changes, purchases, form submissions, extension installs, login changes, permission prompts, or persistent browser-side actions.
- Keep shell commands, file deletion, and OS-level actions outside this browser routing skill. Use normal shell/tooling with its own safety checks.
- Do not bypass authentication, CAPTCHA, paywalls, consent gates, or site access controls.

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
