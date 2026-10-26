---
name: hermes-gateway-line-platform
description: Use when recovering Hermes LINE Gateway on Windows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, gateway, line, windows, platform, webhook, aiohttp]
    related_skills: [line-platform-integration, line-api-credential-verification, hermes-runtime-operations]
---

# Hermes Gateway LINE Platform Operations

## Trigger

Use this class-level skill when enabling, recovering, or verifying the official Hermes `line-platform` adapter on Windows, especially when the Gateway appears to run but the LINE webhook port is absent.

## Boundaries

Keep these completion gates separate:

1. Plugin registration and configuration.
2. Gateway runtime dependency availability.
3. Local webhook listener and signature verification.
4. Public tunnel routing.
5. LINE API authentication.
6. Actual LINE message receipt and reply.

Success at one boundary does not prove the others.

## Runtime interpreter rule

A background Gateway may run under a different Python interpreter from `py -3` or the repository `.venv`. Before installing a missing adapter dependency:

1. Inspect the Gateway process command line (`wmic process` or an equivalent process inspection).
2. Probe `aiohttp` using that exact executable.
3. Install the pinned messaging dependency into that exact environment. For the current Hermes messaging extra, use `aiohttp==3.14.3`.
4. Restart the Gateway and inspect fresh logs. Installing into another Python environment does not satisfy the adapter's dependency gate.

Do not turn a transient missing-package error into a permanent claim that the adapter is unsupported; capture and apply the environment-specific fix.

## Configuration

Represent `platforms.line` as a structured YAML mapping, not a JSON-encoded scalar. Prefer supported CLI setters:

```bash
hermes config set platforms.line.enabled true
hermes config set platforms.line.extra.host 127.0.0.1
hermes config set platforms.line.extra.port 8646
```

Keep `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_CHANNEL_SECRET` in `.env`, never in YAML or logs. The public URL and tunnel settings are operational configuration and should be checked independently.

## Verification sequence

After restarting the Gateway, require all of the following for listener recovery:

1. Fresh startup log contains `LINE: webhook listening on 127.0.0.1:8646/line/webhook`.
2. Fresh startup log contains `✓ line connected`.
3. `netstat` shows `127.0.0.1:8646 LISTENING`.
4. `GET http://127.0.0.1:8646/line/webhook/health` returns HTTP 200 with `status: ok` and `platform: line`.
5. The public Tailscale Funnel health URL returns HTTP 200 with the same JSON.
6. An unsigned POST to the webhook returns HTTP 401 with `invalid signature`. This is positive evidence that the request reached the adapter and HMAC verification is active.

Use the reproducible command sequence in `references/gateway-runtime-verification.md`.

## Reporting standard

Report separately: plugin loaded, Gateway connected, local listener healthy, public tunnel correctly routed, LINE API authenticated, and actual user-message reply verified. Do not claim end-to-end completion when only health checks passed.

## Overlap note

`line-platform-integration` remains the broader LINE webhook workflow, while `line-api-credential-verification` covers token/API checks. This umbrella focuses on Windows Gateway interpreter selection, dependency placement, structured config, and listener evidence; do not duplicate credential procedures here.
