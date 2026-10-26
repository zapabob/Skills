---
name: buzz-integration-hermes
description: Make Hermes Buzz plugin work against local Buzz relay.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [buzz, nostr, plugin, integration, relay]
---

"""Buzz plugin — registers toolset `buzz` with runtime-gated handlers.

Design:
- Pure functions returning JSON strings.
- No hard dependency on a running relay; missing prereqs surface
  JSON error payloads so the agent can report them faithfully.
- Docker compose shortcuts are provided for local dev when
  `vendor/buzz` contains a compose file.
- `BUZZ_BIN` can point at a native `buzz` CLI for channel/message/keypair tools.
"""

## Buzz (Block/Square Nostr agent workspace) Hermes Integration

### Overview
Buzz is an open-source "human + AI agent collaborative workspace" built on Nostr relays (Rust). This skill documents the minimal steps to make the Hermes `plugins/buzz/` toolset actually work against a local Buzz relay.

### Prerequisites
- Buzz repo cloned as submodule at `vendor/buzz/`
- `vendor/buzz/docker-compose.yml` — 開発 infra 用で relay が不足。実運用/ローカル検証は `vendor/buzz/deploy/compose/compose.yml` を使う。
- `vendor/buzz/buzz.exe` — 無い場合は既存の `%USERPROFILE%\.cargo\bin\buzz.EXE` など PATH 内バイナリを利用できる。`plugins/buzz/tools.py` は `vendor/buzz/target/release/buzz.exe` も自動探索する。
- `vendor/buzz/.env` — Hermes ツールは `vendor/buzz/.env` を読まない。Hermes buzz ツールに渡す場合は明示的に `BUZZ_BIN`/`BUZZ_RELAY_URL` を設定するか、ツール側の `.env` 読込を確認する。

## Local Same-Machine Agent Interaction
For Hermes-to-other-AI messaging on the same host, Tailscale/Ngrok are **not required**. Start the relay stack locally and point `BUZZ_RELAY_URL` at `http://localhost:3000` or the observed local relay URL. External exposure only becomes necessary when another machine must reach this relay.

### Configuration
1. **Start local relay stack** (`vendor/buzz/deploy/compose/.env` first, then):
   ```bash
   docker compose -f vendor/buzz/deploy/compose/compose.yml up -d
   # Verify container health:
   docker compose -f vendor/buzz/deploy/compose/compose.yml ps
   ```
2. **Generate Nostr private key** (one-time):
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Add to `vendor/buzz/.env`:
   ```env
   BUZZ_PRIVATE_KEY=<64-char-hex>
   BUZZ_RELAY_URL=ws://localhost:3000
   ```

2. **Hermes plugin config** — already in `plugins/buzz/__init__.py`:
   - Toolset: `buzz`
   - 7 tools: `buzz_relay_status/start/stop`, `buzz_channel_create/list`, `buzz_message_send/read`
   - Default relay fallback in `_run()`: `http://localhost:3000`

3. **Tailscale exposure** (for tailnet access):
   ```bash
   tailscale serve --bg --set-path /buzz --yes http://localhost:3000
   # Available at https://downl.taile4f666.ts.net/buzz
   # Verify: curl -s https://downl.taile4f666.ts.net/buzz/health
   ```

4. **Bitwarden backup** (one-time after key generation):
   ```bash
   # Store BUZZ_PRIVATE_KEY in Bitwarden (item: "Buzz Nostr Private Key")
   # Verify: item exists, field BUZZ_PRIVATE_KEY present, no plaintext in logs/memory
   ```

### CLI Argument Mapping (Critical)
The Hermes plugin must match buzz.exe's actual CLI:
| Operation | buzz.exe subcommand | Key flags |
|---|---|---|
| Channel create | `channels create` | `--name`, `--type stream|forum`, `--visibility open|private` |
| Channel list | `channels list` | `--limit` |
| Message send | `messages send` | `--channel <UUID>`, `--content <text>` |
| Message read | `messages get` | `--channel <UUID>`, `--limit` |

### Verification Checklist
```python
import os, json
os.environ['BUZZ_BIN'] = 'vendor/buzz/buzz.exe'
from plugins.buzz.tools import buzz_relay_status, buzz_channel_list, buzz_channel_create, buzz_message_send, buzz_message_read

# All should return auth_error (code 3) or user_error (code 1) — NOT CLI syntax errors
for fn in [buzz_relay_status, buzz_channel_list, buzz_channel_create, buzz_message_send, buzz_message_read]:
    out = fn({})
    data = json.loads(out)
    assert data.get('code') in (1, 2, 3, 4, 5), f'CLI syntax error: {data}'
print('All tools reach relay correctly')

# Verify .env auto-loading works
from plugins.buzz.tools import _load_buzz_env
env = _load_buzz_env()
assert 'BUZZ_PRIVATE_KEY' in env, 'Key not loaded from .env'
assert env['BUZZ_PRIVATE_KEY'] == '9a844e43e2df34fac936f8a923980f55a379f6ac1505c4ae43fb2b346cd51f6f'
assert 'BUZZ_RELAY_URL' in env
print('.env auto-load verified')
```

### Common Pitfalls
- **Relay port mismatch**: `vendor/buzz/deploy/compose/compose.yml` exposes **3000** for the relay HTTP/WS port. Do NOT run the relay on 8080 — on this stack `llama-server` already binds 8080, so a buzz relay on 8080 gets shadowed and every request 404s with a `{"Server":"llama.cpp"}` body instead of the relay's.
- **Wrong subcommand**: old plugin used `channel create` / `message read` — must be `channels create` / `messages get`.
- **Host-authority-exact community matching (the #1 local gotcha)**: Buzz relay is multi-tenant; the community is bound to the *authority* of `RELAY_URL` (after `normalize_host`). Incoming requests are rejected `404: no community is configured for this host` unless the request `Host`/authority matches byte-for-byte. If `RELAY_URL=wss://localhost`, connect with `--relay http://localhost:3000` — NOT `http://127.0.0.1:3000` (127.0.0.1 ≠ localhost). Setting `RELAY_URL=wss://host.docker.internal` DOES ensure a community *inside the container*, but requests from the Windows host to `http://host.docker.internal:3000` still 404'd in testing — prefer plain `localhost` for single-host local use. The relay logs `Deployment community ensured host:<authority>` at startup; that authority is what every client request must present.
- **buzz.exe global flags go BEFORE the subcommand**: `buzz channels list --format compact` errors with `unexpected argument '--format' found`. Use `buzz --format compact --private-key <hex> --relay <url> channels list`. `--relay` / `--private-key` / `--auth-tag` / `--format` are all global options (see `buzz --help`), so pass them before the subcommand.
- **Process env doesn't read `.env`**: `os.environ` doesn't auto-load `.env`. Tools must implement `_load_buzz_env()` to read `BUZZ_PRIVATE_KEY` / `BUZZ_RELAY_URL` from `vendor/buzz/.env` at runtime.
- **`RELAY_OWNER_PUBKEY` must be 64-char hex (Nostr format), never secp compressed**: deriving the pubkey with coincurve's `format(compressed=True)` yields a 66-char `02…`/`03…` string. The relay logs `WARN RELAY_OWNER_PUBKEY is not a valid 64-char hex pubkey — ignoring` and ownership bootstraps to the wrong key. Strip the prefix: `coincurve.PrivateKey(bytes.fromhex(priv)).public_key.format(compressed=True).hex()[2:]` (64 chars).
- **Zero-filled `BUZZ_RELAY_PRIVATE_KEY` restart-loops the relay**: a placeholder/zero key makes the container bounce with `invalid BUZZ_RELAY_PRIVATE_KEY: Invalid secret key` (status `restarting`, never healthy). Generate with `openssl rand -hex 32` (or `python -c "import secrets; print(secrets.token_hex(32))"`) and pair it with the matching `RELAY_OWNER_PUBKEY` derived above.
- **User-provided nsec must be bech32-decoded with checksum stripped**: when a user hands you an `nsec1...` key (not raw hex), decode it via bech32 — but **strip the final 6 checksum words BEFORE convertbits(5→8)**. Decoding the whole payload yields 36 bytes (72 hex chars) and coincurve rejects it with `Secret scalar must be greater than 0 and less than ...`. Correct sequence: `bech32_decode` → `data[:-6]` → `convertbits(5→8)` → `bytes().hex()` → expect exactly 64 chars. Use `scripts/nsec_to_hex.py` (also derives the 64-char Nostr pubkey with `--pubkey`, same `[2:]` prefix-strip rule as the owner-pubkey pitfall above). Verified 2026-08-08.
- **Changing `RELAY_URL` re-seeds a NEW community — old channels vanish**: the community is seeded from `RELAY_URL`'s host at startup (`Deployment community ensured host:<authority>`). If you change `RELAY_URL` (e.g. from `ws://localhost:3000` to a public `wss://<ngrok-host>`), the relay creates a fresh community for the new host and channels created under the old host no longer appear. Re-create channels (`channels create --name ... --type stream --visibility open`) against the new URL. Verified 2026-08-08: channels created on `localhost` were invisible through the ngrok host until recreated.

### Public / Hosted Relay (Block `communities.buzz.xyz`)
The CLI alone cannot self-register on Block's hosted relay. Live probe results:
- `wss://communities.buzz.xyz` → 404 (no community for that host).
- `wss://relay.communities.buzz.xyz` → **403 `relay_membership_required`** (this is the real hosted relay endpoint).
- `wss://buzz.xyz` → 404 (not a relay; serves HTML).

To join, membership is invite/account-gated. The `buzz` CLI has **no `invite`/`join`/`register` subcommand** — use a Block community invite link (e.g. `https://<community>.communities.buzz.xyz/invite/...`) or the web/desktop app to add your Nostr pubkey as a relay member. After membership is granted, `buzz --relay wss://relay.communities.buzz.xyz ...` reads/writes normally. See `references/buzz-cli-public-relay.md` for the full probe transcript.

### When to Use
- When adding/fixing Hermes Buzz plugin tools
- When verifying local Buzz relay integration
- When exposing Buzz via Tailscale for remote agents
- When Docker Desktop reports launched but `docker info` never becomes responsive

### Windows Docker Desktop Daemon Recovery (WSL-hang path)
If Docker Desktop launches but the daemon remains unreachable, the root cause is usually a **hung WSL service**, not Docker itself. Verified 2026-08-08 on this host:

1. **Confirm the hang signature**: `docker info` times out; `wsl -l -v` also times out (WSL hung, not Docker); `wsl -d docker-desktop -e true` times out. `wsl -l -v` may list distros as `Stopped` while `vmmemWSL`/`vmwp.exe` still hold memory.
2. **Read the logs** — `%LOCALAPPDATA%\Docker\log\host\`:
   - `Docker Desktop.exe.log` → `[E] backend exited before becoming ready` / `backend process exited`
   - `com.docker.backend.exe.log` / `monitor.log` → `engine linux/wsl failed to start ... DockerDesktop/Wsl/CommandTimedOut: wsl.exe -l -v --all`
   - `electron-errd-<date>.log` → error dialog fired from backend
3. **Check disk free space FIRST**: `cmd.exe /c "dir C:\ /a | findstr 空き"`. WSL2's VHDX on C: cannot expand when C: is nearly full — this host had ~10GB free and WSL distros would not start. Free temp/cache (`del /q /f /s "%LOCALAPPDATA%\Temp\*"`, `npm cache clean --force`, `pip cache purge`) via the `windows-di[REDACTED_TOKEN]` skill, then retry.
4. **Kill the Docker Desktop process tree**, then `wsl --shutdown` (this may itself take 30s+; run it backgrounded with a generous timeout, it is not hung forever):
   ```bash
   cmd.exe /c "taskkill /F /IM docker-desktop.exe /T & taskkill /F /IM com.docker.backend.exe /T & taskkill /F /IM \"Docker Desktop.exe\" /T & taskkill /F /IM wslrelay.exe /T"
   wsl --shutdown   # then re-list: wsl -l -v
   ```
5. **Service restart needs admin**: `net stop wslservice` / `sc config com.docker.service` → `Error 5: Access Denied` from a non-elevated shell. `sc query WslService` may show RUNNING even while WSL is functionally hung. Do not loop on these — they cannot succeed without elevation.
6. **Only after `wsl -l -v` returns promptly** relaunch Docker Desktop and poll `docker info` with a bounded backoff loop, then `docker compose up`.
7. **Bash env-var trap**: the `terminal` tool runs MSYS bash, where `set CARGO_TARGET_DIR=...` is a **no-op** (sets a positional parameter, not an env var). Use `export VAR=value` or inline `VAR=value cmd`. A cargo build that silently ignores `CARGO_TARGET_DIR` because of `set` looks exactly like a toolchain failure — check this before debugging MSVC/probe errors.
8. **Docker-free fallback is a big lift**: `crates/buzz-relay` requires PostgreSQL via sqlx (workspace features are `postgres`-only, no sqlite fallback) plus Redis/MinIO. A native relay without Docker means standing up Postgres+Redis on Windows — prefer fixing Docker.

### External-AI Interaction Completion Rule
Declare success only after the relay is reachable from the external node and a second identity completes a send/get round trip on the same channel. A running local stack alone is not sufficient proof of cross-AI communication.

### Subcommand Drift Guard
`buzz.exe` CLI surface changes across releases. If channel/message tools fail with `unrecognized subcommand`, patch `plugins/buzz/tools.py` to match the installed `buzz.exe --help` exactly.

### Exact Authority, Scheme, and E2E Rules
Buzz tenancy resolves from the request authority, including a non-default port. Keep `BUZZ_DOMAIN`, `RELAY_URL`, `BUZZ_MEDIA_BASE_URL`, `BUZZ_MEDIA_SERVER_DOMAIN`, and `BUZZ_CORS_ORIGINS` on the same hostname:port; never mix `localhost`, `host.docker.internal`, a Tailscale IP, and a MagicDNS hostname. For a non-TLS local/Tailscale relay, use `RELAY_URL=ws://<authority>` on the relay and `BUZZ_RELAY_URL=http://<authority>` for the CLI. Using `wss://` against a plain HTTP Docker port causes NIP-98 URL mismatch or TLS errors.

The relay stack is `vendor/buzz/deploy/compose/compose.yml`. Plugin helpers should resolve paths from the repository root, detect both `compose.yml` and `docker-compose.yml`, and use a stable compose project name so status checks inspect the intended stack. The native CLI does not load dotenv files; load only `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY` from ignored local dotenv files, never print them, and rotate any key exposed in logs or conversation history.

The current CLI surface is plural: `channels list`, `channels create --name <NAME> --type stream --visibility open`, `messages send --channel <UUID> --content <TEXT>`, and `messages get --channel <UUID> --limit <N>`. Global flags such as `--format`, `--private-key`, and `--relay` precede the subcommand. Do not use obsolete singular `message` or nonexistent `keypair` subcommands.

Verify the real integration through the Hermes handlers in this order: `buzz_relay_status` → `buzz_channel_list` → `buzz_channel_create` → `buzz_message_send` → `buzz_message_read`. A successful self-send proves local/Tailscale relay CRUD, but not multi-agent exchange; only claim agent-to-agent communication after a second identity on another node joins the same channel and completes a send/get round trip. Hosted `wss://relay.communities.buzz.xyz` returning `403 relay_membership_required` is an invite/account membership issue, not a CLI syntax failure. See `references/local-relay-exact-authority-and-e2e.md` for the reusable runbook.

### Skill Update Hygiene
This skill governs relay integration; do not create narrow one-off skills like "buzz-relay-on-<date>" for environment fixes. Capture durable class-level lessons here or in `references/`, and only escalate to a new umbrella skill when the topic outgrows this relay/integration scope.

### References
- `references/local-relay-community-binding.md` — localhost vs `host.docker.internal` community-binding wall, verified working `.env`, exact-authority connect rule, and the 8080/llama-server shadowing trap.
- `references/local-relay-same-host.md` — same-host agent interaction without Tailscale/Ngrok, verified local binary resolution and plugin wiring state.
- `references/buzz-cli-public-relay.md` — probe results for Block's hosted relay (`wss://relay.communities.buzz.xyz` = 403 membership_required), the no-join-subcommand limitation, and the global-flag-before-subcommand ordering rule.
- `references/public-relay-ngrok-e2e.md` — full ngrok exposure runbook: RELAY_URL→community reseeding, 64-hex owner pubkey derivation, second-identity send/get round trip (verified 2026-08-08).
- `scripts/nsec_to_hex.py` — decode a user-provided `nsec1...` to 64-char hex (with `--pubkey` for the Nostr pubkey); encodes the mandatory checksum-strip before convertbits.

### Related Skills
- `hermes-plugin-development` — general plugin authoring
- `tailscale-serve-config` — tailnet service exposure