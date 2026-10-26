---
name: hermes-agent
description: Use when Codex should call the local Hermes Agent tool surface through the Hermes Agent MCP plugin.
---

# Hermes Agent Plugin

Use this plugin when a task benefits from Hermes-specific tools while the main model
turn is running in Codex with CodexAuth.

## Auth Boundary

- CodexAuth belongs to Codex and is read from Codex's own session.
- Hermes provider auth belongs to Hermes and is stored by Hermes, not by this
  plugin.
- Do not read or print `auth.json`, token files, API keys, or local credential
  stores.
- If a Hermes provider specifically needs OpenAI Codex OAuth, use the normal
  Hermes flow: `hermes auth add openai-codex`.

## Available Hermes Bridge

The plugin exposes a local MCP server named `hermes-agent`. It launches:

```bash
python -m agent.transports.hermes_tools_mcp_server
```

Use it for Hermes capabilities that Codex does not provide directly:

- web search and extraction
- browser automation
- vision analysis
- image generation
- skill listing and skill viewing
- text-to-speech
- kanban handoff tools when Hermes provides the required environment

Use Codex built-in shell and patch tools for ordinary file work. Use Hermes
tools only when the Hermes-specific capability is actually needed.

## Safety Notes

- Keep local paths and credentials out of user-facing summaries unless the user
  explicitly asks for them.
- Treat the MCP bridge as local-machine authority. Do not expose it to remote
  hosts.
- If the bridge cannot start, first check that the configured Python executable
  and Hermes worktree still exist.
