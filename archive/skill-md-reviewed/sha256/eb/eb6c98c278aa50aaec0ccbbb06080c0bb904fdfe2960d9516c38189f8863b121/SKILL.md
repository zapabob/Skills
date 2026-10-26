---
name: buzz-nostr-integration
description: Fix Buzz plugin CLI mismatch and expose relay via Tailscale.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Buzz, Nostr, Plugin, Relay, Integration]
---

# Buzz Nostr Integration

Integrate Block's Buzz Nostr relay platform into Hermes Agent by fixing the bundled `plugins/buzz/` toolset to match the actual `buzz.exe` CLI, configuring authentication, and exposing the relay via Tailscale.

## When to Use

- Need Hermes to create/list channels, send/read messages on a Buzz/Nostr relay
- Want to run a local Buzz relay stack and control it from Hermes
- Require tailnet access to the relay for remote agents

## Prerequisites

- Hermes Agent repo with `vendor/buzz/` submodule (Block/buzz source)
- `buzz.exe` binary at `vendor/buzz/buzz.exe` (pre-built in repo)
- Docker Compose for relay stack (`vendor/buzz/docker-compose.yml`)
- Tailscale installed and logged in (for tailnet exposure)
- Python 3.10+ with `python-dotenv` not required (stdlib parser used)

## How to Run

1. Start relay stack: `buzz_relay_start({})` via Hermes tool
2. Generate Nostr key and write to `vendor/buzz/.env`
3. Expose relay on tailnet: `tailscale serve --bg --set-path /buzz --yes http://localhost:8080`
4. Use `buzz_channel_list`, `buzz_channel_create`, `buzz_message_send`, `buzz_message_read` tools

## Quick Reference

| Tool | Purpose | Key Args |
|------|---------|----------|
| `buzz_relay_status` | Check Docker containers | `compose_path?` |
| `buzz_relay_start` | `docker compose up -d` | `compose_path?` |
| `buzz_relay_stop` | `docker compose down` | `compose_path?` |
| `buzz_channel_list` | List channels | `limit` (default 20) |
| `buzz_channel_create` | Create channel | `name`, `type?`, `private?`, `description?`, `ttl?` |
| `buzz_message_send` | Send message | `channel` (UUID), `text` |
| `buzz_message_read` | Read messages | `channel` (UUID), `limit?` |

## Procedure

### 1. Verify Buzz CLI and relay stack

```bash
cd vendor/buzz
./buzz.exe --help
docker compose ps
curl -s http://localhost:8080/health  # should return {"status":"ok"}
```

### 2. Fix plugin tools to match buzz.exe CLI

Edit `plugins/buzz/tools.py`:

- Change subcommands: `channel` → `channels`, `message read` → `messages get`
- Use flagged args: `--channel`, `--content`, `--name`, `--type`, `--visibility`
- Add `_load_buzz_env()` to read `BUZZ_PRIVATE_KEY` / `BUZZ_RELAY_URL` from `.env`
- Default `BUZZ_RELAY_URL` to `http://localhost:8080` (not 3000)

### 3. Create plugin manifest

Create `plugins/buzz/plugin.yaml`:

```yaml
name: buzz
version: 1.0.0
description: "Buzz/Nostr relay integration — channel, message, and relay management via buzz CLI."
author: "Hermes Agent"
kind: standalone
platforms:
  - linux
  - macos
  - windows
```

### 4. Generate and configure Nostr private key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Write output to vendor/buzz/.env
echo "BUZZ_PRIVATE_KEY=<64-char-hex>" > vendor/buzz/.env
echo "BUZZ_RELAY_URL=ws://localhost:8080" >> vendor/buzz/.env
```

### 5. Expose relay via Tailscale (tailnet access)

```bash
tailscale serve --bg --set-path /buzz --yes http://localhost:8080
# Verify: https://<your-tailnet>.ts.net/buzz/health
```

### 6. Verify plugin loads in Hermes

```python
from hermes_cli.plugins import get_plugin_manager, discover_plugins
discover_plugins(force=True)
mgr = get_plugin_manager()
# Check mgr._plugins['buzz'] shows enabled=True and 7 tools registered
```

## Pitfalls

- **Port mismatch**: Buzz relay runs on 8080 internally; `.env.example` documents 3000. Tools must default to 8080.
- **CLI drift**: `buzz.exe` subcommands change across versions. Always verify with `./buzz.exe <cmd> --help`.
- **Auth required**: All channel/message tools need `BUZZ_PRIVATE_KEY`. Without it, relay returns `auth_error` code 3.
- **UUID channels**: `buzz_message_send/read` require channel UUID from `buzz_channel_list`, not name.
- **WebSocket vs HTTP**: `BUZZ_RELAY_URL` for CLI uses `http://` (REST), but Nostr clients use `ws://` (WebSocket).

## Verification

Run this Hermes tool sequence and confirm no "unrecognized subcommand" or "unexpected argument" errors:

```python
buzz_relay_status({})
buzz_channel_list({"limit": 1})
buzz_channel_create({"name": "test", "type": "stream"})
buzz_message_send({"channel": "<uuid-from-list>", "text": "hello"})
buzz_message_read({"channel": "<uuid-from-list>"})
```

Expected: `ok=False` with `code in (1,2,3,4,5)` and JSON error payloads — **not** CLI usage errors.