---
name: comfy-agent-integration
description: Connect ComfyUI to AI agents via MCP.
version: 1.0.0
author: Hermes Curator
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [comfyui, mcp, comfy, agent-tools, hermes]
    related_skills: [comfyui, native-mcp]
    category: creative
---

# Comfy Agent Integration

Use this class-level workflow when connecting ComfyUI to Hermes or another MCP client. Keep Cloud MCP, official local MCP, and community servers distinct; similarly named packages are not interchangeable.

## Connection types

| Connection | Transport | Target | Distinction |
|---|---|---|---|
| Comfy Cloud MCP | Streamable HTTP | Comfy Cloud | Hosted GPUs; OAuth at `https://cloud.comfy.org/mcp` |
| Official local MCP (`comfy-local-mcp`, documented script `comfy-mcp`) | stdio | Local ComfyUI | First-party wrapper over `comfy-cli` |
| Community MCP servers | stdio or local HTTP | Local ComfyUI | Third-party; verify source and scope |
| PyPI `comfy-mcp-server` | stdio | Configured workflow | Third-party single-workflow server, not official |

## Workflow

1. Identify whether the user wants Cloud, official local, or community local integration; never silently substitute one.
2. Before promising official local setup, verify its current distribution using the docs, GitHub, PyPI, and installed CLI surface. Documentation may precede public packaging.
3. Verify prerequisites: Python 3.10+, `comfy-cli`, an existing ComfyUI workspace, and the local endpoint (normally `http://127.0.0.1:8188`).
4. Check ComfyUI separately with `curl http://127.0.0.1:8188/system_stats`; JSON means reachable, connection refusal means ComfyUI is stopped.
5. Configure Hermes under `mcp_servers` with a distinct name such as `comfy-local`; use `command`, `args`, and an absolute `COMFY_BIN` only when needed.
6. Restart Hermes because MCP discovery occurs at startup. Verify with `hermes mcp list` and actual tool discovery.
7. Do not report success without subprocess connection, discovered tools, and local health evidence.

## Hermes patterns

```yaml
mcp_servers:
  comfy-cloud:
    url: https://cloud.comfy.org/mcp
    auth: oauth
    enabled: true

  comfy-local:
    command: comfy-mcp
    args: []
    env:
      COMFY_BIN: "C:\\Users\\<user>\\.local\\bin\\comfy.exe"
    enabled: true
```

## Pitfalls

- `comfy mcp` is not necessarily a `comfy-cli` subcommand; check the installed version.
- PyPI `comfy-mcp-server` is a naming trap. It expects `COMFY_URL`, `COMFY_WORKFLOW_JSON_FILE`, `PROMPT_NODE_ID`, and `OUTPUT_NODE_ID`, and is not Comfy's first-party local server.
- A stopped `:8188` service is distinct from a broken MCP configuration.
- Cloud and local connections have separate lifecycles and can coexist.
- If official packaging is unavailable, report that accurately and offer `comfy-cli`/ComfyUI workflows or a clearly labeled community alternative.

## References

- `references/comfy-local-mcp-availability.md` — dated evidence and a re-check recipe for official local MCP availability.