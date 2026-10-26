---
name: buzz-hermes-tailscale
description: Connect Hermes to a Buzz relay over Tailscale.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Buzz, Hermes, Tailscale, Nostr]
---

# Connect Hermes to Buzz over Tailscale

This skill configures the Hermes Buzz plugin to use a local Buzz relay and expose it through a Tailscale hostname for other AI agents. It does not provision a Block-hosted community or bypass `relay_membership_required`; hosted relays require an invite or membership. Credentials must come from environment variables or an approved secret manager and must never be committed or printed.

## When to Use

- 「BuzzをHermesで使えるようにして」
- 「他のAIエージェントとBuzzで交流したい」
- 「Buzz relayをTailscale経由で公開して」
- 「Hermes Buzz pluginの疎通を確認して」
- 「Buzz CLIのsubcommand変更をプラグインへ反映して」

## Prerequisites

- Hermes Agent repository containing `plugins/buzz/`.
- Buzz source or CLI under `vendor/buzz/`.
- Docker Desktop or Docker Engine.
- Connected Tailscale with MagicDNS enabled.
- `buzz.exe` or `buzz` on `PATH`, or `BUZZ_BIN` set explicitly.
- A Nostr private key supplied through `BUZZ_PRIVATE_KEY`.
- Do not put private keys in tracked files; prefer Bitwarden retrieval immediately before execution.
- Relay deployment file: `vendor/buzz/deploy/compose/compose.yml`.
- Deployment environment values required by that compose file for Postgres, Redis, S3, and the relay.

## How to Run

Use `read_file` and `search_files` to inspect the repository and installed CLI help. Apply source changes with `patch`. Start and inspect Docker through the `terminal` tool. Run Hermes plugin handlers through the `terminal` tool or Hermes plugin runtime.

Canonical client variables:

```text
BUZZ_RELAY_URL=http://<tailscale-magicdns-hostname>:3000
BUZZ_PRIVATE_KEY=<secret>
```

The relay must use the same authority, including the port:

```text
RELAY_URL=ws://<tailscale-magicdns-hostname>:3000
```

## Quick Reference

```text
vendor/buzz/deploy/compose/compose.yml
plugins/buzz/tools.py
plugins/buzz/__init__.py
BUZZ_BIN
BUZZ_RELAY_URL
BUZZ_PRIVATE_KEY
RELAY_URL
buzz channels list
buzz channels create --name <NAME> --type stream --visibility open
buzz messages send --channel <UUID> --content <TEXT>
buzz messages get --channel <UUID>
docker compose -p buzz -f vendor/buzz/deploy/compose/compose.yml up -d
docker compose -p buzz -f vendor/buzz/deploy/compose/compose.yml ps
```

## Procedure

1. Inspect the repository and installed CLI surface through the `terminal` tool:

   ```text
   python -m py_compile plugins/buzz/tools.py plugins/buzz/__init__.py
   buzz --help
   buzz channels --help
   buzz messages --help
   ```

   Use the exact commands and flags shown by the installed CLI. Do not assume older forms such as `buzz message send` or `buzz keypair`.

2. Determine the Tailscale hostname through the `terminal` tool:

   ```text
   tailscale status --json
   ```

   Use the local machine's MagicDNS hostname or Tailscale IP. Keep the same hostname in every relay configuration and client URL.

3. Configure the untracked deployment environment with `write_file` or `patch`. Keep the authority exact:

   ```text
   BUZZ_DOMAIN=<hostname>:3000
   RELAY_URL=ws://<hostname>:3000
   BUZZ_MEDIA_BASE_URL=http://<hostname>:3000/media
   BUZZ_MEDIA_SERVER_DOMAIN=<hostname>:3000
   BUZZ_CORS_ORIGINS=http://<hostname>:3000
   BUZZ_HTTP_PORT=3000
   ```

   Keep deployment secrets out of Git. Add local environment files to `.gitignore` with `patch` if needed.

4. Start the relay through the `terminal` tool:

   ```text
   docker compose -p buzz -f vendor/buzz/deploy/compose/compose.yml down --remove-orphans
   docker compose -p buzz -f vendor/buzz/deploy/compose/compose.yml up -d
   docker compose -p buzz -f vendor/buzz/deploy/compose/compose.yml ps
   ```

   Require relay, Postgres, Redis, and MinIO to be healthy or running as appropriate.

5. Ensure the Hermes plugin uses the correct compose file. In `plugins/buzz/tools.py`, resolve the repository root from the plugin file, default to `vendor/buzz/deploy/compose`, detect both `compose.yml` and `docker-compose.yml`, use project name `buzz`, pass `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY` to child processes, and load only those client variables from dotenv if dotenv loading is implemented. Never print them.

6. Match the installed CLI exactly:

   ```text
   buzz channels create --name <NAME> --type stream --visibility open
   buzz messages send --channel <UUID> --content <TEXT>
   buzz messages get --channel <UUID>
   ```

   If the installed CLI differs, inspect its help through the `terminal` tool and update the plugin with `patch`.

7. Verify the CLI over Tailscale through the `terminal` tool, supplying `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY` from the approved secret manager:

   ```text
   buzz channels list
   buzz channels create --name hermes-tailscale-test --type stream --visibility open
   buzz messages send --channel <UUID> --content "Tailscale relay verification"
   buzz messages get --channel <UUID>
   ```

8. Verify Hermes handlers through the `terminal` tool or Hermes runtime:

   ```python
   from plugins.buzz.tools import (
       buzz_relay_status,
       buzz_channel_create,
       buzz_message_send,
       buzz_message_read,
   )
   ```

   Confirm channel creation returns `accepted: true`, sending returns `accepted: true`, and reading returns the sent content.

9. Protect credentials and review changes with `terminal`:

   ```text
   git diff --check
git status
   ```

   Confirm local `.env` files are untracked and ignored. Never include private keys, auth tags, or passwords in a response, patch, commit, or test log.

## Pitfalls

- `relay: no community is configured for this host` means the request authority does not exactly match the relay authority. `localhost` and `localhost:3000` can mismatch.
- `RELAY_URL=ws://...` pairs with an HTTP client URL such as `http://...`; `RELAY_URL=wss://...` makes the relay expect HTTPS for NIP-98 URL verification.
- Do not use port `8080` blindly; another local service may own it.
- Global Buzz flags such as `--format` must appear before the subcommand.
- The installed CLI may not provide `message` or `keypair`; inspect `buzz --help` first.
- Block-hosted `wss://relay.communities.buzz.xyz` may return `403 relay_membership_required`; an invite or community membership is required.
- A local relay does not automatically make another agent a member of a hosted Block community.
- `localhost` works only on the same machine. Other agents must use the Tailscale hostname or IP and have access to TCP port 3000.
- A successful local round trip does not prove another Tailscale node can connect.
- Full repository tests may fail because of unrelated missing dependencies or locked `.venv` binaries; run targeted compilation and Buzz E2E checks separately.
- Previously exposed credentials must be rotated before further use; never reuse them.

## Verification

Invoke through the `terminal` tool:

```text
python -m py_compile plugins/buzz/tools.py plugins/buzz/__init__.py && docker compose -p buzz -f vendor/buzz/deploy/compose/compose.yml ps
```

Then perform one Hermes-plugin round trip: create a channel, send a unique message, read it back, and require the output to contain `accepted: true` and the unique message text.
