---
name: airi-start-hermes-worker
description: Use when starting AIRI through Hermes.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [AIRI, Hermes, Windows, Startup, Verification]
---

# Start AIRI Through Hermes

This skill starts AIRI as a Hermes-managed desktop-shell worker, synchronizes Hermes authentication, and verifies the AIRI process, CDP page, and Hermes AI-core probe. It does not configure credentials, modify AIRI source code, or enable VRChat autonomy; existing authentication and local services are treated as prerequisites.

## When to Use

- The user says `hermes airi start`.
- AIRI is stopped and should run beside Hermes Desktop.
- AIRI needs to reconnect to the local Hermes AI core.
- A prior AIRI start needs health verification.

## Prerequisites

- Windows host.
- The AIRI submodule exists at `%USERPROFILE%\Documents\New project\hermes-agent\vendor\airi`.
- Hermes API server is reachable at `http://127.0.0.1:8642/v1/`.
- Hermes API authentication is already configured; do not read, print, or copy secret values.
- The AIRI plugin is available and exposes `airi_status` and `airi_start`.
- The default AIRI worker uses isolated userdata at `%USERPROFILE%\.hermes\airi\userdata` and CDP port `9455` when started by the worker.

## How to Run

Invoke the `airi_status` tool first, then invoke the `airi_start` tool. Use the defaults unless the user supplies a different repository root, Hermes base URL, Hermes model, or CDP port. After startup, invoke `airi_status` again through the Hermes tool interface.

## Quick Reference

- Status tool: `airi_status`
- Start tool: `airi_start`
- Default AIRI repository: `%USERPROFILE%\Documents\New project\hermes-agent\vendor\airi`
- Default Hermes OpenAI-compatible base URL: `http://127.0.0.1:8642/v1/`
- Default Hermes model: `hermes-agent`
- Worker role: `airi-desktop-shell`
- AIRI VRChat OSC endpoint: `127.0.0.1:9000`
- Started worker CDP port: `9455`
- AIRI target page after startup: `http://localhost:5173/beat-sync.html`
- Provider file: `%USERPROFILE%\.hermes\airi\hermes-provider.json`

## Procedure

1. Invoke `airi_status`.
   - Confirm whether `worker.running` and `worker.healthy` are already true.
   - Confirm `hermes_probe.live: true`, `hermes_probe.auth_ok: true`, and HTTP `status: 200` before attempting startup.
   - If the probe is not live or authenticated, report that the Hermes AI core is not ready instead of claiming AIRI started.

2. Invoke `airi_start` with no arguments unless an override is explicitly required.
   - The successful response must show `ok: true`.
   - Confirm `sync.ok: true` and `sync.synced: true`.
   - Confirm the sync probe reaches `http://127.0.0.1:8642/v1/models` with `status: 200` and model `hermes-agent`.

3. Inspect the returned `worker` object.
   - Confirm `running: true` and `healthy: true`.
   - Record the returned PID only as transient run output; do not save it as durable memory.
   - Confirm a non-null `cdp_page`, normally `http://localhost:5173/beat-sync.html`, and a positive `cdp_targets` count.
   - Confirm `last_cdp_seed_ok: true`.

4. Confirm side-by-side isolation.
   - AIRI should report `concurrent_with_hermes_desktop: true`.
   - Confirm AIRI and Hermes Desktop use distinct app/userdata isolation as reported by the tool; do not stop Hermes Desktop merely to start AIRI.

5. Invoke `airi_status` once more.
   - Treat the operation as complete only when the final status reports the worker as both running and healthy, Hermes authentication as ready, and the Hermes probe as live/authenticated with HTTP 200.

## Pitfalls

- A stale PID in the initial status does not mean the worker is running; use `worker.running` and `worker.healthy` as the source of truth.
- `provider_file_exists: true` alone does not prove that AIRI can call Hermes; verify the live authenticated `/v1/models` probe.
- AIRI and Hermes Desktop are both Electron applications. Do not infer a conflict when the worker reports distinct userdata/app IDs and the CDP port is available.
- The initial status may show CDP port `9333` while the newly started worker reports `9455`; use the post-start worker result for the active run.
- Do not expose API keys or provider-file contents in logs or replies. Report only readiness, source labels, HTTP status, URLs, and health fields.
- Starting AIRI does not itself enable VRChat autonomy. Use a separate explicit control operation only when the user asks for it.
- Do not report success from the start call alone if the returned worker health or the final status check is unhealthy.

## Verification

Invoke `airi_status` and require all of these results: `worker.running: true`, `worker.healthy: true`, `hermes_probe.status: 200`, `hermes_probe.auth_ok: true`, `auth.ready: true`, and a non-null `cdp_page` with `cdp_targets` greater than zero.
