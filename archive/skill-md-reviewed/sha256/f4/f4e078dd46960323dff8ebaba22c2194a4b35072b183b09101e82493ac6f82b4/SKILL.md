---
name: airi-hermes-auto-recovery
description: Recover AIRI and reseed Hermes AI and Irodori TTS.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [AIRI, Hermes, Irodori, TTS, Recovery]
---

# AIRI Hermes Provider/TTS Auto-Recovery

This skill starts AIRI as a Hermes-managed worker, synchronizes the Hermes `hermes-agent` model and Irodori TTS settings through CDP, and verifies the live services. It also installs a quiet two-minute watchdog for AIRI crashes and provider/TTS reseeding. It does not expose services publicly, create credentials, or print API keys; authentication is sourced from the existing Hermes `API_SERVER_KEY` configuration.

## When to Use

- The user says AIRI crashed, disappeared, or needs to be restarted.
- AIRI does not recognize `hermes-agent`.
- AIRI speech is not using `irodori-tts` or voice `hakua`.
- The user asks for automatic AIRI provider/TTS authentication or reseeding.
- AIRI and Hermes Desktop must run side by side.

## Prerequisites

- Windows host.
- AIRI checkout: `%USERPROFILE%\Documents\New project\hermes-agent\vendor\airi`.
- Hermes API server reachable at `http://127.0.0.1:8642/v1/`.
- Hermes authentication already configured in `%USERPROFILE%\.hermes\.env` as `API_SERVER_KEY`; never read or print the raw value.
- AIRI plugin tools available: `airi_status`, `airi_start`, `airi_stop`, and `airi_restart`.
- Irodori TTS endpoint expected at `http://127.0.0.1:8088/v1/`.
- AIRI worker CDP port `9455`.
- The project Python environment is `.venv/Scripts/python.exe`; the Windows Apps `python` shim may return exit 49 and must not be used.

## How to Run

Use Hermes tools rather than manually starting Electron:

1. Invoke `airi_status` first.
2. If the Hermes probe is live/authenticated, invoke `airi_start` with the default AIRI repository, Hermes base URL, model, and CDP port.
3. Invoke `airi_status` again and require both worker and provider/TTS readiness.
4. For persistent recovery, create or verify the `AIRI provider/TTS auto-recovery` `cronjob`.

## Quick Reference

- AIRI repository: `%USERPROFILE%\Documents\New project\hermes-agent\vendor\airi`
- Hermes base URL: `http://127.0.0.1:8642/v1/`
- Hermes model: `hermes-agent`
- Irodori base URL: `http://127.0.0.1:8088/v1/`
- Irodori model: `irodori-tts`
- Irodori voice: `hakua`
- AIRI CDP: `9455`
- AIRI chat page: `http://localhost:5173/#/chat`
- Provider file: `%USERPROFILE%\.hermes\airi\hermes-provider.json`
- TTS file: `%USERPROFILE%\.hermes\airi\hermes-tts.json`
- Watchdog script: `%USERPROFILE%\.hermes\scripts\airi-provider-tts-watchdog.py`
- Watchdog schedule: `every 2m`
- Watchdog job: `972800a0eb47`

## Procedure

1. **Inspect the current state.** Invoke `airi_status`. Record only sanitized fields. Confirm whether `worker.running`, `worker.healthy`, `hermes_probe.live`, `hermes_probe.auth_ok`, and `hermes_probe.status` are ready. Do not treat an old PID or provider file alone as proof of health.

2. **Start and synchronize AIRI.** Invoke `airi_start` with:
   - `repo_root`: `%USERPROFILE%\Documents\New project\hermes-agent\vendor\airi`
   - `hermes_base_url`: `http://127.0.0.1:8642/v1/`
   - `hermes_model`: `hermes-agent`
   - `cdp_port`: `9455`

   Require `ok: true`, `sync.ok: true`, `sync.synced: true`, and a live authenticated `/v1/models` probe. AIRI startup merges provider credentials and seeds the renderer through CDP; do not manually copy secrets into localStorage or files.

3. **Verify AI synchronization.** From the `airi_start` or final `airi_status` result, require:
   - `provider.ready: true`
   - `provider.definition_id: openai-compatible`
   - `provider.base_url: http://127.0.0.1:8642/v1/`
   - `provider.model: hermes-agent`
   - `provider.api_key_configured: true`
   - `provider.cdp_seeded: true`
   - `last_cdp_seed_ok: true`
   - readback `consciousnessProvider: openai-compatible`
   - readback `consciousnessModel: hermes-agent`
   - readback `openaiCompatibleHasKey: true`

4. **Verify Irodori TTS synchronization.** Require:
   - `tts.ready: true`
   - `tts.synced_provider: openai-compatible-audio-speech`
   - `tts.hermes_provider: irodori-tts`
   - `tts.base_url: http://127.0.0.1:8088/v1/`
   - `tts.model: irodori-tts`
   - `tts.voice: hakua`
   - `tts.server_live: true`
   - `tts.server_status: 200`
   - `tts.cdp_seeded: true`
   - readback `speechProvider: openai-compatible-audio-speech`
   - readback `speechModel: irodori-tts`

5. **Install the crash watchdog.** Use `write_file` only if the script is missing at `%USERPROFILE%\.hermes\scripts\airi-provider-tts-watchdog.py`. The script must stay quiet when healthy. When unhealthy it starts Irodori first if its health endpoint is down, then invokes the AIRI core start path, which reseeds Hermes and TTS. It may print only sanitized recovery fields such as `actions`, `airi_healthy`, `cdp_seeded`, `model`, `tts_server_live`, and `tts_provider`.

6. **Create or verify the `cronjob`.** Use `cronjob(action='list')` before creating a duplicate. The canonical job is:
   - name: `AIRI provider/TTS auto-recovery`
   - job ID: `972800a0eb47`
   - schedule: `every 2m`
   - `script`: `airi-provider-tts-watchdog.py`
   - `no_agent`: `true`
   - `deliver`: `local`
   - workdir: `%USERPROFILE%\Documents\New project\hermes-agent`

   If the canonical job exists, do not create another. If it is paused, resume it with `cronjob`. If it is missing, create it with the same script, schedule, workdir, no-agent mode, and local delivery.

7. **Exercise recovery.** If AIRI is currently stopped, invoke the watchdog through the `terminal` tool using the project Python executable:
   `cd /c/Users/downl/Documents/New\ project/hermes-agent && .venv/Scripts/python.exe '%USERPROFILE%/.hermes/scripts/airi-provider-tts-watchdog.py'`

   The expected sanitized recovery output includes `airi-start-and-seed`, `airi_healthy: true`, `cdp_seeded: true`, and `tts_server_live: true`. Do not use the Windows Apps `python` shim.

8. **Run the cron once.** Invoke `cronjob(action='run', job_id='972800a0eb47')`. Require `execution_success: true` and `last_status: ok` from the returned job state.

9. **Configure browser chat safety.** For AIRI's Electron renderer origin, require these non-secret API server settings and restart the gateway from an external context:
   - `gateway.api_server.cors_origins: http://localhost:5173`
   - `gateway.api_server.tool_free_origins: http://localhost:5173`
   - `gateway.api_server.model_routes.hermes-agent.model`: a known responsive model
   - `gateway.api_server.model_routes.hermes-agent.provider`: its configured provider

   `tool_free_origins` reduces only matching browser requests to `enabled_toolsets=[]`; other API clients keep their configured tools. This prevents the AIRI chat agent from calling `airi_restart` and disconnecting its own SSE stream.

10. **Use a fresh AIRI conversation after transport or tool failures.** In the real AIRI UI, open `Conversations` and select `+ New`. Old interrupted tool-call history can otherwise derive the same Hermes API session and reproduce a broken turn even after the runtime is fixed. Do not clear localStorage or edit runtime storage directly.

11. **Run real UI E2E.** Type a unique short prompt into the actual AIRI textarea and submit it with Enter. Require all of:
   - network `POST http://127.0.0.1:8642/v1/chat/completions` returns HTTP 200;
   - renderer reports no exception;
   - an assistant message body becomes visible in the AIRI chat UI;
   - Hermes session history contains the corresponding assistant response.

   Health, typecheck, provider readback, and backend-only curl do not satisfy this E2E requirement.

12. **Final status.** Invoke `airi_status` once more. Treat the operation as complete only when `worker.running: true`, `worker.healthy: true`, `provider.cdp_seeded: true`, `tts.cdp_seeded: true`, `hermes_probe.status: 200`, `hermes_probe.auth_ok: true`, the CDP page is non-null, and the real UI E2E passed.

## Pitfalls

- `airi_status` can show a stale PID while `worker.running` is false. Trust live process/CDP fields, not the PID.
- CDP `localStorage.setItem()` in the same renderer does not emit a native `storage` event. A seed can read back correctly while Pinia/VueUse still holds an empty provider/model. The Hermes AIRI seed path must dispatch a matching `StorageEvent` after each write; never treat raw localStorage readback alone as proof that the active store updated.
- AIRI's parent `pnpm` PID can exit while the Electron/CDP process tree remains live. Worker detection must accept either a live tracked PID or live CDP targets; otherwise the two-minute watchdog can start duplicate workers.
- Browser preflight 403 means AIRI never reached the agent. Configure `cors_origins` and verify OPTIONS returns 200 with `Access-Control-Allow-Origin` before investigating the model.
- An HTTP 200 stream followed by `Failed to fetch` can be self-interruption: inspect the Hermes API session for `airi_restart` or other lifecycle tool calls. Use `tool_free_origins` for AIRI rather than globally removing tools from all API clients.
- `provider_file_exists: true` and `tts_file_exists: true` do not prove AIRI can use either backend. Require the live probes and CDP readback.
- `airi_start` is the canonical synchronization path. Starting `pnpm dev:tamagotchi` directly skips the Hermes-managed seed and can leave AIRI without `hermes-agent` or Irodori settings.
- Do not use `taskkill /F /IM electron.exe`; it can kill unrelated Electron applications, including Hermes Desktop. Use `airi_stop` or `airi_restart`.
- Do not manually edit or print `hermes-provider.json`, `hermes-tts.json`, `.env`, localStorage credentials, or CDP payloads containing keys.
- AIRI and Hermes Desktop are both Electron applications. They are expected to coexist with isolated userdata and app IDs; do not stop Hermes Desktop merely to start AIRI.
- Irodori TTS health can be good while AIRI is dead. The watchdog checks and repairs both layers independently.
- `show: true` and BeatSync non-blocking initialization are source-level UI fixes, not substitutes for provider synchronization. If the window remains invisible, inspect AIRI renderer logs and CDP targets separately.
- The watchdog is a local recovery loop, not a proof that an AIRI chat message succeeded. A real chat send/response remains a separate E2E check.

## Verification

Invoke `airi_status` and require all of: `worker.running: true`, `worker.healthy: true`, `provider.model: hermes-agent`, `provider.cdp_seeded: true`, `tts.hermes_provider: irodori-tts`, `tts.voice: hakua`, `tts.server_status: 200`, `tts.cdp_seeded: true`, `hermes_probe.status: 200`, and a non-null `worker.cdp_page`.
