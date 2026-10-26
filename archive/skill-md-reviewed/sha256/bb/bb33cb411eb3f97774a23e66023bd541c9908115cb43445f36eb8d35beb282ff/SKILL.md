---
name: codex-browser-mcp
description: Route Codex bundled Browser and Chrome plugin usage across Codex, Cursor, and Hermes without creating invalid external MCP entries.
---

# Codex Browser MCP Routing

Use this skill when a request mentions `@browser`, `@ブラウザ`, `@chrome`, `plugin://browser@openai-bundled`, `plugin://chrome@openai-bundled`, browser automation, Chrome automation, or browser-based computer use.

## What Is Enabled

- Codex App and Codex CLI use the bundled plugins `browser@openai-bundled` and `chrome@openai-bundled`.
- The Browser plugin is the in-app browser path. It is best for localhost, `127.0.0.1`, `file://` URLs, local web app checks, screenshots, and direct browser testing.
- The Chrome plugin is the native Chrome path. It is best when the task requires the user's real Chrome profile, existing tabs, cookies, SSO, Chrome extensions, or a logged-in web session.
- These bundled plugins are not ordinary external MCP servers with a stable `command` or `url`. Do not add fake `mcpServers` entries for `plugin://browser@openai-bundled` or `plugin://chrome@openai-bundled`.

## Codex App And Codex CLI

1. Keep these plugin blocks enabled in `%USERPROFILE%\.codex\config.toml`:
   - `[plugins."browser@openai-bundled"]`
   - `[plugins."chrome@openai-bundled"]`
2. Keep the browser/computer-use feature flags enabled under `[features]`:
   - `browser_use = true`
   - `browser_use_external = true`
   - `computer_use = true`
   - `in_app_browser = true`
   - `plugins = true`
   - `apps = true`
3. For Browser work inside Codex, load the bundled Browser skill and use its `iab` backend path through `agent.browsers.get("iab")`.
4. For Chrome work inside Codex, load the bundled Chrome skill. Use its setup scripts for detection and repair guidance; do not manually install or repair the native host outside the plugin workflow.
5. When importing Chrome `scripts/browser-client.mjs`, use the active installed plugin path shown by `codex plugin list`. Do not import the cached plugin copy if it is not the trusted installed path.

## Cursor

- Cursor should not receive invalid `mcp.json` server entries for Codex bundled plugin URIs.
- If Cursor has its own browser MCP or browser automation tool, use Cursor's native tool.
- If the requested operation specifically requires Codex Browser or Codex Chrome, delegate to Codex App or Codex CLI and include the explicit mention `@browser`, `@ブラウザ`, or `@chrome` in the prompt.
- Only add entries to `%USERPROFILE%\.cursor\mcp.json` when there is a real MCP server command or URL.

## Hermes Agent

- Preload this skill together with the Hermes `codex` skill for requests that need Codex-driven browser or Chrome automation.
- When Hermes delegates to Codex CLI, include the explicit plugin mention in the prompt:
  - `@browser` or `@ブラウザ` for in-app browser work.
  - `@chrome` for real Chrome profile work.
- Do not represent the Codex bundled plugins as Hermes external MCP servers unless a real MCP command or URL is provided by the plugin runtime.

## Guardrails

- Do not inspect, export, or modify browser passwords, cookies, local storage, session stores, or profile secrets unless the user gives a narrowly scoped security/debugging request and a safer path has been considered first.
- Ask before downloads, uploads, account changes, purchases, form submissions, extension installs, login changes, permission prompts, or other persistent browser-side actions.
- Keep shell commands, file deletion, and OS-level actions outside this browser routing skill. Use the normal shell/tooling path with its own safety checks.
- Do not bypass authentication, CAPTCHA, paywalls, consent gates, or site access controls.
- Prefer read-only inspection first. Escalate to interaction only when the task requires it.

## Verification Commands

Use these checks after setup or drift repair:

```powershell
codex plugin list
codex features list
Select-String -LiteralPath %USERPROFILE%\.codex\config.toml -Pattern '^\[features\]|^(browser_use|browser_use_external|computer_use|in_app_browser|plugins|apps)\s*='
```

For Chrome-specific readiness, run the bundled plugin scripts from the installed Chrome plugin directory and follow the Chrome skill's repair rules.
